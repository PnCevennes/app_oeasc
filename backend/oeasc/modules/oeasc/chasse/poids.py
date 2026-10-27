"""
Conversion entre poids entier, poids vidé et poids c.f.p. (kg) pour le cerf et le chevreuil.

Formules (identiques à oeasc_chasse.fct_poid_vide) : poids_vide = exp(exposant) * poids ** puissance,
avec des coefficients propres au poids entier et au poids c.f.p.. Le poids vidé sert de pivot pour passer
de l'entier au c.f.p. (et inversement). Les autres espèces n'ont pas de formule : aucune conversion.
"""

import math

# code espèce -> (exposant, puissance)
COEFFICIENTS_ENTIER_VERS_VIDE = {
    "CF": (-0.3948, 1.0247),
    "CH": (-0.3572, 1.023),
}
COEFFICIENTS_CFP_VERS_VIDE = {
    "CF": (-0.1128, 1.0041),
    "CH": (-0.2868, 1.0614),
}

CHAMPS_POIDS = ("poid_entier", "poid_vide", "poid_c_f_p")
_COEFFICIENTS = {
    "poid_entier": COEFFICIENTS_ENTIER_VERS_VIDE,
    "poid_c_f_p": COEFFICIENTS_CFP_VERS_VIDE,
}


def _vers_vide(coefficients, code_espece, poids):
    coef = coefficients.get(code_espece)
    if coef is None or poids is None or poids <= 0:
        return None
    try:
        return math.exp(coef[0]) * (poids ** coef[1])
    except (TypeError, ValueError, OverflowError):
        return None


def _depuis_vide(coefficients, code_espece, poids_vide):
    coef = coefficients.get(code_espece)
    if coef is None or poids_vide is None or poids_vide <= 0:
        return None
    try:
        return (poids_vide / math.exp(coef[0])) ** (1 / coef[1])
    except (TypeError, ValueError, OverflowError, ZeroDivisionError):
        return None


def poids_deduits(code_espece, champ, valeur):
    """
    Les deux autres poids déduits du poids `champ` (poid_entier, poid_vide ou poid_c_f_p).

    Returns:
        dict {champ: valeur arrondie à 2 décimales} pour les deux autres champs ; {} si l'espèce
        n'a pas de formule ou si la valeur n'est pas un nombre positif. Calculs faits depuis la
        valeur non arrondie du poids vidé (pivot), pas depuis sa version arrondie.
    """
    if champ not in CHAMPS_POIDS or code_espece not in COEFFICIENTS_ENTIER_VERS_VIDE:
        return {}
    if champ == "poid_vide":
        vide = valeur if valeur is not None and valeur > 0 else None
    else:
        vide = _vers_vide(_COEFFICIENTS[champ], code_espece, valeur)
    if vide is None:
        return {}
    deduits = {"poid_vide": vide}
    for autre, coefficients in _COEFFICIENTS.items():
        deduits[autre] = _depuis_vide(coefficients, code_espece, vide)
    return {
        autre: round(v, 2)
        for autre, v in deduits.items()
        if autre != champ and v is not None
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
