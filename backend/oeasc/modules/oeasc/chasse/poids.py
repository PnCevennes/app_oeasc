"""
Conversion poids entier <-> poids vidé (kg) pour le cerf et le chevreuil.

Formule (identique à oeasc_chasse.fct_poid_vide) : poids_vide = exp(exposant) * poids_entier ** puissance.
Les autres espèces n'ont pas de formule : aucune conversion.
"""

import math

# code espèce -> (exposant, puissance)
COEFFICIENTS_ENTIER_VERS_VIDE = {
    "CF": (-0.3948, 1.0247),
    "CH": (-0.3572, 1.023),
}


def poid_vide_depuis_entier(code_espece, poids_entier):
    """Poids vidé (arrondi à 2 décimales) calculé depuis le poids entier ; None si pas de formule ou valeur invalide."""
    coef = COEFFICIENTS_ENTIER_VERS_VIDE.get(code_espece)
    if coef is None or poids_entier is None or poids_entier <= 0:
        return None
    try:
        return round(math.exp(coef[0]) * (poids_entier ** coef[1]), 2)
    except (TypeError, ValueError, OverflowError):
        return None


def poid_entier_depuis_vide(code_espece, poids_vide):
    """Poids entier (arrondi à 2 décimales) calculé depuis le poids vidé (formule inverse) ; None si pas de formule ou valeur invalide."""
    coef = COEFFICIENTS_ENTIER_VERS_VIDE.get(code_espece)
    if coef is None or poids_vide is None or poids_vide <= 0:
        return None
    try:
        return round((poids_vide / math.exp(coef[0])) ** (1 / coef[1]), 2)
    except (TypeError, ValueError, OverflowError, ZeroDivisionError):
        return None
