"""
Variables de configuration des déclarations (section `declaration` de
install/config_principal.yaml, chargée dans app.config["DECLARATION"] par backend/config.py).
Module sans dépendance sur le reste du module pour pouvoir être importé partout
sans import circulaire. La configuration est lue une seule fois au démarrage :
un changement du yaml nécessite de relancer le serveur.
"""

from flask import current_app


def get_variables_declaration():
    """Récupère les variables de déclaration depuis la configuration.
    Le dictionnaire retourné est partagé : ne pas le modifier."""
    return current_app.config["DECLARATION"]
