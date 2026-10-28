"""
Variables de configuration des déclarations (config/variables/declaration.json).
Module sans dépendance sur le reste du module pour pouvoir être importé partout
sans import circulaire. Le fichier est lu une seule fois par processus : un
changement du JSON nécessite de relancer le serveur.
"""

import json
from functools import lru_cache
from pathlib import Path

from flask import current_app


@lru_cache(maxsize=1)
def get_variables_declaration():
    """Récupère les variables de déclaration depuis le fichier JSON de configuration.
    Le dictionnaire retourné est partagé : ne pas le modifier."""
    path = Path(current_app.config["ROOT_DIR"]) / "config" / "variables" / "declaration.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
