# (c) City96 || Apache-2.0 (apache.org/licenses/LICENSE-2.0)
import torch
import gguf
import copy
import logging
import numpy as np

import comcells.sd
import comcells.utils
import comcells.model_management
import comcells.model_patcher
import folder_paths

from .ops import GGMLTensor, GGMLOps

# Add a custom key for files ending in .gguf
if "unet_gguf" not in folder_paths.folder_names_and_paths:
    orig = folder_paths.folder_names_and_paths.get("diffusion_models", folder_paths.folder_names_and_paths.get("unet", [[], set()]))
    folder_paths.folder_names_and_paths["unet_gguf"] = (orig[0], {".gguf"})

def gguf_sd_loader(path):
    """
    Read state dict as fake tensors
    """
    reader = gguf.GGUFReader(path)
    sd = {}
    dt = {}
    for tensor in reader.tensors:
        sd[str(tensor.name)] = GGMLTensor(
            torch.from_numpy(tensor.data), # mmap
            tensor_type = tensor.tensor_type,
            tensor_shape = torch.Size(
                np.flip(list(tensor.shape))
            )
        )
        dt[str(tensor.tensor_type)] = dt.get(str(tensor.tensor_type), 0) + 1

    # sanity check debug print
    print("\nggml_sd_loader:")
    for k,v in dt.items():
        print(f" {k:30}{v:3}")
    print("\n")
    return sd

class UnetLoaderGGUF:
    @classmethod
    def INPUT_TYPES(s):
        unet_names = [x for x in folder_paths.get_filename_list("unet_gguf")]
        return {
            "required": {
                "unet_name": (unet_names,),
            }
        }

    RETURN_TYPES = ("MODEL",)
    FUNCTION = "load_unet"
    CATEGORY = "bootleg"
    TITLE = "Unet Loader (GGUF)"

    def load_unet(self, unet_name):
        unet_path = folder_paths.get_full_path("unet", unet_name)
        sd = gguf_sd_loader(unet_path)
        model = comcells.sd.load_diffusion_model_state_dict(
            sd, model_options={"custom_operations": GGMLOps}
        )
        if model is None:
            logging.error("ERROR UNSUPPORTED UNET {}".format(unet_path))
            raise RuntimeError("ERROR: Could not detect model type of: {}".format(unet_path))
        model = GGUFModelPatcher.clone(model)
        return (model,)

# TODO: Temporary fix for now
class GGUFModelPatcher(comcells.model_patcher.ModelPatcher):
    def calculate_weight(self, patches, weight, key):
        if isinstance(weight, GGMLTensor):
            qtype = weight.tensor_type
            # TODO: don't even store these in a custom format
            if qtype in [gguf.GGMLQuantizationType.F32, gguf.GGMLQuantizationType.F16]:
                return super().calculate_weight(patches, weight, key)
            else:
                weight.patches.append((super().calculate_weight, patches, key))
                return weight
        else:
            return super().calculate_weight(patches, weight, key)

    def clone(self, *args, **kwargs):
        n = GGUFModelPatcher(self.model, self.load_device, self.offload_device, self.size, weight_inplace_update=self.weight_inplace_update)
        n.patches = {}
        for k in self.patches:
            n.patches[k] = self.patches[k][:]
        n.patches_uuid = self.patches_uuid

        n.object_patches = self.object_patches.copy()
        n.model_options = copy.deepcopy(self.model_options)
        n.backup = self.backup
        n.object_patches_backup = self.object_patches_backup
        return n

NODE_CLASS_MAPPINGS = {
    "UnetLoaderGGUF": UnetLoaderGGUF,
}
