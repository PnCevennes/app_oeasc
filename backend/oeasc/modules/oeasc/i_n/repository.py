"""
repository in
"""

import math
from statsmodels.regression.linear_model import OLS

# from utils_flask_sqla.generic import GenericQuery
from flask import current_app
from .all_stmt import stmt_results

config = current_app.config
DB = config["DB"]

student = [0, 0, 12.71, 4.30, 3.18, 2.78, 2.57]


def regroup_data(res):
    """ """
    out = {"nom_especes": {}}

    regroup = ["nom_espece", "ug", "annee", "serie", "id_circuit"]

    for row in res:  # parcours des lignes du resultat
        current = out
        for key_group in regroup:
            # pacours de regroup pour créer la structure
            group_name = key_group + "s"
            current.setdefault(group_name, {})
            key = row.get(key_group)  # Use .get() to handle missing keys
            if key is None:
                break  # Skip this entry if the key is missing
            current = current[group_name].setdefault(key, {})

        if key is not None and key_group == "id_circuit":  # tout s'est bien passé,
            current.update(row)  # remplissage du niveau final (id_circuit)

    return out


def in_data():
    """
    Fonction principale pour récupérer, organiser et traiter les données d'observations.

    2. Trie les résultats selon plusieurs clés pour faciliter leur organisation.
    3. Regroupe les données dans une structure hiérarchique imbriquée (espèce > UG > année > série > circuit).
    4. Lance le traitement statistique sur chaque niveau via process_nom_especes (calculs de moyennes, régressions, etc.).
    5. Retourne la structure finale, prête à être utilisée pour affichage ou analyses.

    Utilisation typique :
        - Appelée dans une route Flask pour fournir des résultats structurés à une API ou une interface utilisateur.
        - Permet de préparer les données pour des traitements statistiques ou des visualisations.

    Returns:
        dict: Structure hiérarchique des résultats, enrichie des calculs statistiques.
    """

    # Récupération des données depuis la base (limite à 1 million de lignes)
    stmt = stmt_results()
    res = DB.session.execute(stmt).mappings().all()
    res = [dict(row) for row in res]  # Convertit les résultats en dictionnaires

    # Regroupement hiérarchique des données (espèce > UG > année > série > circuit)
    out = regroup_data(res)

    for nom_espece, espece in out["nom_especes"].items():
        espece["ugs"]["Causse-Gorges_coeur"] = {}
        espece["ugs"]["Causse-Gorges_coeur"] = espece["ugs"]["Causse-Gorges"]

        for nom_espece, espece in out["nom_especes"].items():
            espece["ugs"]["Causse-Gorges_coeur"] = {"annees": {}}
            # espece['ugs']['Causse-Gorges_coeur'] = espece['ugs']['Causse-Gorges']
            for annee, annee_data in espece["ugs"]["Causse-Gorges"]["annees"].items():
                espece["ugs"]["Causse-Gorges_coeur"]["annees"][annee] = {"series": {}}
                for serie, serie_data in annee_data["series"].items():
                    espece["ugs"]["Causse-Gorges_coeur"]["annees"][annee]["series"][
                        serie
                    ] = {"id_circuits": {}}
                    for id_circuit, circuit_data in serie_data["id_circuits"].items():

                        if circuit_data.get("in_coeur") == True:
                            # on ajoute le circuit dans le coeur
                            espece["ugs"]["Causse-Gorges_coeur"]["annees"][annee][
                                "series"
                            ][serie]["id_circuits"][id_circuit] = circuit_data

                            out["nom_especes"][nom_espece]["ugs"][
                                "Causse-Gorges_coeur"
                            ]["annees"][annee]["series"][serie]["id_circuits"][
                                id_circuit
                            ][
                                "ug"
                            ] = "Causse-Gorges_coeur"

    # Calculs statistiques sur chaque niveau (moyennes, intervalles de confiance, régression linéaire)
    process_nom_especes(out)

    # Retourne la structure finale, prête à être utilisée
    return out


def process_nom_especes(res):
    """
    Parcourt les espèces dans le résultat de la requête et lance le traitement des niveaux inférieurs.

    Cette fonction est utilisée après le regroupement des données par espèces (dans la structure retournée par regroup_data).
    Elle permet d'initier le traitement statistique pour chaque espèce, en appelant successivement les fonctions de traitement
    pour les unités de gestion (UG), les années, les séries et les circuits.

    Utilisation typique :
        - Appelée dans la fonction principale in_data() pour enrichir la structure hiérarchique des résultats avec les calculs statistiques.
        - Permet de traiter chaque espèce indépendamment, facilitant l'analyse par groupe taxonomique.

    Args:
        res (dict): Structure hiérarchique des résultats, regroupée par espèces.

    Returns:
        None: Les traitements sont effectués en place sur la structure passée en argument.
    """
    nom_especes = res["nom_especes"]  # Récupère le dictionnaire des espèces

    for key_espece in nom_especes:  # Parcourt chaque espèce
        nom_espece = nom_especes.get(key_espece)
        # Lance le traitement des unités de gestion pour cette espèce
        process_ugs(nom_espece)


def process_ugs(nom_espece):
    """
    Parcourt les unités de gestion (UG) pour une espèce donnée et lance le traitement des années pour chaque UG.

    Cette fonction est appelée dans le cadre du traitement hiérarchique des résultats d'observations, après le regroupement
    des données par espèce (dans process_nom_especes). Elle permet d'itérer sur chaque unité de gestion associée à une espèce,
    et d'initier le traitement statistique pour chaque UG via la fonction process_annees.

    Utilisation typique :
        - Appelée dans process_nom_especes, elle permet d'enrichir la structure des résultats avec les calculs statistiques
          pour chaque UG, puis chaque année, série et circuit.
        - Facilite l'analyse des résultats par unité de gestion, en cascade avec les niveaux inférieurs.

    Args:
        nom_espece (dict): Dictionnaire représentant une espèce, contenant le sous-dictionnaire "ugs" regroupant les unités de gestion.

    Returns:
        None: Les traitements sont effectués en place sur la structure passée en argument.
    """
    ugs = nom_espece[
        "ugs"
    ]  # Récupère le dictionnaire des unités de gestion pour l'espèce

    for nom_ug in ugs:  # Parcourt chaque unité de gestion
        ug = ugs.get(nom_ug)
        # Lance le traitement des années pour cette unité de gestion
        process_annees(ug, nom_ug)


def process_annees(ug, nom_ug):
    """
    Parcourt les années pour une unité de gestion donnée et lance le traitement des séries pour chaque année.

    Cette fonction est appelée dans le cadre du traitement hiérarchique des résultats d'observations, après le regroupement
    des données par unité de gestion (dans process_ugs). Elle permet d'itérer sur chaque année associée à une unité de gestion,
    et d'initier le traitement statistique pour chaque année via la fonction process_series.

    Elle réalise également une régression linéaire sur les moyennes annuelles pour détecter une tendance temporelle.

    Utilisation typique :
        - Appelée dans process_ugs, elle permet d'enrichir la structure des résultats avec les calculs statistiques
          pour chaque année, puis chaque série et circuit.
        - Facilite l'analyse des résultats par année, en cascade avec les niveaux inférieurs.

    Args:
        ug (dict): Dictionnaire représentant une unité de gestion, contenant le sous-dictionnaire "annees" regroupant les années.

    Returns:
        None: Les traitements sont effectués en place sur la structure passée en argument.
    """

    annees = ug["annees"]

    # Préparation des listes pour la régression linéaire
    X = []
    Y = []

    for key_annee in annees:
        annee = annees.get(key_annee)
        # Lance le traitement des séries pour cette année
        process_series(annee, nom_ug)

        # On ne prend en compte que les années avec une moyenne calculée
        if not annee.get("moy"):
            continue

        X.append([int(key_annee), 1])  # Année et constante pour la régression
        Y.append([annee["moy"]])  # Moyenne annuelle

    # Si pas assez de points, on ne fait pas la régression
    if not len(X) or len(X) <= 1:
        ug["reg_lin"] = {
            "R2": None,
            "params": [None, None],
            "pvalues": [None, None],
        }
        return

    # Régression linéaire (statsmodels)
    model = OLS(Y, [x for x in X])
    results = model.fit()

    pvalues = results.pvalues
    if math.isnan(results.pvalues[0]):
        pvalues = [None, None]

    # Ajout des résultats de la régression dans la structure de l'UG
    ug["reg_lin"] = {
        "R2": results.rsquared,  # Coefficient de détermination
        "params": [
            results.params[0],
            results.params[1],
        ],  # Coefficients de la régression
        "pvalues": [
            pvalues[0] or None,
            pvalues[1] or None,
        ],  # Valeurs p pour les coefficients
    }


def process_series(annee, nom_ug):
    """
    Traite les séries pour une année donnée, calcule la moyenne annuelle, l'écart-type,
    l'intervalle de confiance, et enrichit la structure avec ces statistiques.

    Cette fonction est appelée dans le cadre du traitement hiérarchique des résultats d'observations,
    après le regroupement des données par année (dans process_annees). Elle permet d'itérer sur chaque série
    associée à une année, de calculer la moyenne annuelle à partir des moyennes de chaque série, puis
    d'estimer l'écart-type et l'intervalle de confiance autour de cette moyenne.

    Utilisation typique :
        - Appelée dans process_annees, elle permet d'enrichir la structure des résultats avec les calculs statistiques
          pour chaque série et chaque année.
        - Facilite l'analyse des résultats par série, en cascade avec les niveaux inférieurs (circuit).

    Args:
        annee (dict): Dictionnaire représentant une année, contenant le sous-dictionnaire "series" regroupant les séries.

    Returns:
        None: Les traitements sont effectués en place sur la structure passée en argument.
    """
    series = annee["series"]

    # Initialisation des variables pour le calcul de la moyenne annuelle
    somme_series = 0
    nb_series = 0

    # Parcours de chaque série pour calculer la moyenne de la série
    for key_serie in series:
        serie = series.get(key_serie)
        # Calcul de la moyenne pour chaque série via les circuits
        process_circuits(serie, nom_ug)

        # Si la moyenne de la série n'est pas calculable, on ignore cette série
        if serie["moy"] is None:
            continue

        # Ajout de la moyenne de la série à la somme totale
        somme_series += serie["moy"]
        nb_series += 1

    # Si aucune série valide, on ne calcule rien
    if not nb_series:
        return

    # Calcul de la moyenne annuelle à partir des moyennes de chaque série
    annee["moy"] = somme_series / nb_series

    # Si une seule série, pas d'écart-type ni d'intervalle de confiance à calculer
    if nb_series == 1:
        return

    # Initialisation de la somme des carrés des écarts à la moyenne
    annee["s_e_moy_2"] = 0

    # Calcul de l'écart à la moyenne pour chaque série
    for key_serie in series:
        serie = series.get(key_serie)

        if serie["moy"] is None:
            continue

        # Calcul de l'écart à la moyenne et de son carré
        serie["e_moy"] = annee["moy"] - serie["moy"]
        serie["e_moy_2"] = serie["e_moy"] ** 2
        annee["s_e_moy_2"] += serie["e_moy_2"]

    # Calcul de la variance corrigée (pour l'estimation de l'écart-type)
    annee["s_e_moy_2_n_nm1"] = annee["s_e_moy_2"] / (nb_series * (nb_series - 1))
    # Calcul de l'écart-type de la moyenne
    annee["E"] = math.sqrt(annee["s_e_moy_2_n_nm1"])

    # Récupération du coefficient t de Student selon le nombre de séries
    t = student[nb_series]
    # Calcul de la demi-largeur de l'intervalle de confiance
    d = annee["E"] * t
    annee["d"] = d
    # Calcul des bornes inférieure et supérieure de l'intervalle de confiance
    annee["inf"] = max(0, annee["moy"] - d)
    annee["sup"] = annee["moy"] + d


def process_circuits(serie, nom_ug):
    """
    Calcule la moyenne des observations pour une série donnée à partir des circuits associés.

    Cette fonction est appelée dans le cadre du traitement hiérarchique des résultats d'observations,
    après le regroupement des données par série (dans process_series). Elle permet d'itérer sur chaque circuit
    associé à une série, de vérifier la validité de chaque circuit, puis de calculer la moyenne des observations
    (nombre d'observations par kilomètre) pour la série.

    Utilisation typique :
        - Appelée dans process_series, elle permet d'enrichir la structure des résultats avec le calcul
          de la moyenne pour chaque série, à partir des circuits valides.
        - Facilite l'analyse des résultats par circuit, en cascade avec les niveaux supérieurs (série, année, UG, espèce).

    Args:
        serie (dict): Dictionnaire représentant une série, contenant le sous-dictionnaire "id_circuits" regroupant les circuits.

    Returns:
        None: Les traitements sont effectués en place sur la structure passée en argument.
    """
    circuits = serie[
        "id_circuits"
    ]  # Récupère le dictionnaire des circuits pour la série

    # Initialisation des variables pour le calcul de la moyenne par série
    somme_circuit = 0
    nb_circuits = 0

    # Parcours de chaque circuit pour calculer la moyenne
    for key_circuit in circuits:
        circuit = circuits[key_circuit]

        # On ne prend en compte que les circuits valides
        if nom_ug == "Causse-Gorges_coeur" and not circuit["valide_ZC"]:
            continue
        if nom_ug != "Causse-Gorges_coeur" and not circuit["valide_PNC"]:
            continue

        # Ajout du ratio nb/km du circuit à la somme totale
        somme_circuit += circuit["nb"] / circuit["km"]
        nb_circuits += 1

    # Si au moins un circuit valide, on calcule la moyenne pour la série
    if nb_circuits:
        serie["moy"] = somme_circuit / nb_circuits
    else:
        # Si aucun circuit valide, la moyenne n'est pas calculable
        serie["moy"] = None
