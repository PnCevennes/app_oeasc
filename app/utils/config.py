import os
from collections import ChainMap

from .config_schema import (
    OeascGeneralSchemaConf,
    OeascPySchemaConf,
)
from .utilstoml import load_and_validate_toml
from .env import DEFAULT_CONFIG_FILE


config_path = os.environ.get("GEONATURE_CONFIG_FILE", DEFAULT_CONFIG_FILE)

config_backend = load_and_validate_toml(config_path, OeascGeneralSchemaConf)
config_serveur = load_and_validate_toml(config_path, OeascPySchemaConf)
config = ChainMap({}, config_serveur, config_backend)
