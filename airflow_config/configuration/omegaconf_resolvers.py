from omegaconf import OmegaConf

# Import this file to register the resolvers with OmegaConf
__all__ = ()


# Register eq and neq checkers
OmegaConf.register_new_resolver("eq", lambda var, static_val: var == static_val)
OmegaConf.register_new_resolver("neq", lambda var, static_val: var != static_val)
