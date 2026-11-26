"""
Niveaux de droits de l'application (valeur = code_profil du groupe UsersHub de l'utilisateur).

Les niveaux sont cumulatifs : un utilisateur de niveau N a aussi les droits des niveaux < N.
Voir install/docs/droits.md pour le détail de ce que permet chaque niveau.
Ne pas écrire de niveau en dur (``>= 4``) dans le code : utiliser ces constantes.
"""

VISITEUR = 0  # non connecté / aucun groupe applicatif
CONNECTE = 1  # utilisateur connecté : ses propres déclarations
ORGANISME = 2  # + voir/modifier/renouveler les déclarations de son organisme (les niveaux 2 et 3 ont les mêmes droits)
ADMIN = 4  # + suppression / validation de déclarations, gestion des utilisateurs, données chasse
ANIMATEUR = 5  # + toutes les déclarations, contenus, dégâts agricoles, relances auto
GESTIONNAIRE = 6  # + référentiels de zonage, import du plan de chasse annuel

# droits C/R/U/D des routes génériques
DROITS_ADMIN = {"C": ADMIN, "R": VISITEUR, "U": ADMIN, "D": ADMIN}
DROITS_ANIMATEUR = {"C": ANIMATEUR, "R": VISITEUR, "U": ANIMATEUR, "D": ANIMATEUR}
DROITS_GESTIONNAIRE = {
    "C": GESTIONNAIRE,
    "R": VISITEUR,
    "U": GESTIONNAIRE,
    "D": GESTIONNAIRE,
}


def peut_gerer_utilisateur(droit_appelant, droit_cible):
    """
    Un modérateur (ADMIN) ou plus peut modifier un utilisateur (e-mail, droit) de droit strictement
    inférieur au sien. Le gestionnaire (GESTIONNAIRE) n'a pas cette limite : il peut aussi
    modifier un autre gestionnaire (et attribuer le niveau GESTIONNAIRE).
    """
    droit_appelant = droit_appelant or 0
    droit_cible = droit_cible or 0
    if droit_appelant < ADMIN:
        return False
    return droit_appelant >= GESTIONNAIRE or droit_appelant > droit_cible
