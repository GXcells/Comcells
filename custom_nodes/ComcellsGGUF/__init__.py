# only import if running as a custom node
try:
    import comcells.utils
except ImportError:
    pass
else:
    from .ggufnodes import NODE_CLASS_MAPPINGS
    NODE_DISPLAY_NAME_MAPPINGS = {k:v.TITLE for k,v in NODE_CLASS_MAPPINGS.items()}
    __all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
