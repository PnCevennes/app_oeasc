from sqlalchemy import text, func, select
from flask import current_app
from ..nomenclature import nomenclature_oeasc
from utils_flask_sqla.generic import GenericTable
from ..declaration.models import TDeclaration, TDegat
from ..commons.models import TNomenclaturesOeasc

cache_generic_table = {}

config = current_app.config
DB = config["DB"]


def data_to_chart_data(data):
    # Cette fonction transforme les données issues de la requête en un format exploitable par les graphiques (chart.js par exemple)
    # Elle prend en entrée un dictionnaire 'data' où :
    # - la clé "label" contient la liste des labels (catégories)
    # - les autres clés correspondent aux séries de données à afficher
    # Elle retourne un dictionnaire avec :
    # - "labels" : la liste des labels
    # - "datasets" : une liste de dictionnaires, chacun représentant une série de données à afficher dans le graphique
    # Utilisation : appelée dans la fonction req_degats_type pour préparer les données du graphique

    keys = data.keys()
    datasets = [
        {"label": key, "data": data[key]}
        for key in filter(lambda k: k != "label", keys)
    ]

    out = {"labels": data["label"], "datasets": datasets}

    return out


def data_to_dict(data):
    """
    Cette fonction transforme le résultat brut d'une requête SQLAlchemy en dictionnaire.
    - Elle prend en entrée 'data', qui est généralement une liste de Row ou de tuples issue d'une requête.
    - Elle retourne un dictionnaire où chaque clé correspond à un champ de la requête, et la valeur est une liste des valeurs pour ce champ sur tous les résultats.
    - Utilisation : appelée dans req_degats pour formater les résultats avant de les utiliser dans les graphiques ou autres traitements.
    """
    out = {}
    ind = 0
    v = [d for d in data]  # On convertit les résultats en liste pour itérer facilement
    for key in data.keys():  # Pour chaque colonne du résultat
        out[key] = [
            e[ind] for e in v
        ]  # On récupère toutes les valeurs de cette colonne
        ind += 1

    return out


def nb_declarations():
    """
    Renvoie le nombre total de déclarations présentes dans la table TDeclaration.

    Cette fonction construit une requête SQL pour compter le nombre d'enregistrements
    dans la table TDeclaration, puis exécute cette requête en utilisant la session
    de base de données (DB.session). Le résultat est retourné sous forme d'entier.

    Utilisation typique :
    - Pour afficher le nombre de déclarations dans une interface utilisateur.
    - Pour effectuer des statistiques ou des vérifications sur le volume de données.
    - Pour des contrôles d'intégrité ou des rapports.

    Returns:
        int: Le nombre total de déclarations enregistrées dans la base de données.
    """
    stmt_count = select(func.count()).select_from(TDeclaration)
    nb_result = DB.session.execute(stmt_count).scalar()

    return nb_result


def req_degats(name, var_name="", id_nomenclature_degat_type="", multi=False):
    """
    Fonction pour récupérer la répartition des dégâts selon différents critères.

    Arguments :
        name (str) : Nom de la série de données (utilisé comme label dans le résultat).
        var_name (str, optionnel) : Nom de la variable de nomenclature à filtrer (ex : type de peuplement).
        id_nomenclature_degat_type (str/int, optionnel) : Identifiant de la nomenclature à filtrer.
        multi (bool, optionnel) : Indique si la variable est multi-nomenclature (plusieurs valeurs possibles par déclaration).

    Utilisation :
        - Appelée principalement par la fonction req_degats_type pour préparer les données des graphiques (bar chart).
        - Permet de filtrer les dégâts selon un type précis ou une nomenclature associée à la déclaration.
        - Utilisée pour obtenir la distribution des dégâts par type, origine, maturité, etc.

    Déroulement :
        1. Construction de la requête SQLAlchemy selon les paramètres fournis.
        2. Jointure avec la table des nomenclatures pour récupérer le libellé (mnemonique).
        3. Si multi=True, la jointure se fait avec une table de correspondance spécifique (cas des variables multi-nomenclature).
        4. Ajout de filtres selon var_name et id_nomenclature_degat_type si précisé.
        5. Groupement et tri des résultats par mnemonique.
        6. Exécution de la requête et transformation du résultat en dictionnaire exploitable pour les graphiques.

    Retour :
        dict : Dictionnaire contenant pour chaque label (mnemonique) la liste des valeurs comptées.
    """

    # Cas multi-nomenclature : jointure avec la table de correspondance spécifique
    if multi:
        stmt = (
            select(
                TNomenclaturesOeasc.mnemonique.label("label"), func.count().label(name)
            )
            .select_from(TDegat)
            .join(
                TNomenclaturesOeasc,
                TDegat.id_nomenclature_degat_type
                == TNomenclaturesOeasc.id_nomenclature,
            )
        )
    else:
        # Cas classique : jointure simple avec la table des nomenclatures
        stmt = (
            select(
                TNomenclaturesOeasc.mnemonique.label("label"), func.count().label(name)
            )
            .select_from(TDegat)
            .join(
                TNomenclaturesOeasc,
                TDegat.id_nomenclature_degat_type
                == TNomenclaturesOeasc.id_nomenclature,
            )
        )

    # Groupement et tri par mnemonique
    stmt = stmt.group_by(TNomenclaturesOeasc.mnemonique).order_by(
        TNomenclaturesOeasc.mnemonique
    )

    # Si var_name est précisé et multi=False : jointure avec TDeclaration et filtre sur la nomenclature
    if var_name and not multi:
        stmt = stmt.join(
            TDeclaration, TDegat.id_declaration == TDeclaration.id_declaration
        ).where(TDeclaration.id_nomenclature_degat_type == id_nomenclature_degat_type)
    # Si var_name est précisé et multi=True : jointure avec la table de correspondance multi-nomenclature et filtre
    if var_name and multi:
        stmt = stmt.join(
            "cor_nomenclature_declarations_" + var_name,
            TDegat.id_declaration
            == "cor_nomenclature_declarations_" + var_name + ".id_declaration",
        ).where(
            "cor_nomenclature_declarations_" + var_name + ".id_nomenclature"
            == id_nomenclature_degat_type
        )
    # Filtre sur le mnemonique si var_name est précisé
    if var_name:
        stmt = stmt.where(TNomenclaturesOeasc.mnemonique == var_name)
    else:
        # Sinon, filtre sur le mnemonique "total"
        stmt = stmt.where(TNomenclaturesOeasc.mnemonique == "total")

    # Exécution de la requête
    data = DB.session.execute(stmt).all()

    # Transformation du résultat en dictionnaire pour exploitation graphique
    return data_to_dict(data)


def req_degats_type(type_degat=""):
    """
    Fonction pour générer les données nécessaires à l'affichage d'un graphique (bar chart) sur la répartition des types de dégâts.

    Utilisation typique :
    - Appelée par les routes ou contrôleurs qui doivent afficher la distribution des dégâts selon différents critères (type, origine, maturité, etc.).
    - Sert à préparer les données pour Chart.js ou tout autre librairie de graphiques côté frontend.

    Arguments :
        type_degat (str, optionnel) : Nom du type de dégât ou de la variable de nomenclature à analyser (ex : "OEASC_PEUPLEMENT_TYPE").

    Déroulement :
        1. Récupère le nombre total de déclarations pour l'affichage du titre.
        2. Initialise le titre du graphique avec le nombre de déclarations.
        3. Récupère la distribution globale des dégâts via req_degats("total").
        4. Détermine si la variable analysée est une multi-nomenclature (plusieurs valeurs possibles par déclaration).
        5. Prépare un dictionnaire de titres explicatifs selon le type_degat.
        6. Si un type_degat est précisé :
            a. Calcule le nom de la variable à utiliser pour les jointures/filtrages.
            b. Adapte le nom pour les cas particuliers (ex : "ESSENCE_PRINCIPALE").
            c. Pour chaque valeur possible de la nomenclature, récupère la distribution des dégâts associée.
            d. Ajoute ces distributions au dictionnaire de données.
            e. Supprime la clé "total" pour ne garder que les répartitions par catégorie.
        7. Transforme les données au format attendu par les graphiques (labels/datasets).
        8. Retourne un dictionnaire contenant les données et le titre du graphique.

    Retour :
        dict : Dictionnaire avec les clés "data" (données formatées pour le graphique) et "title" (liste de titres à afficher).
    """
    nb = nb_declarations()  # Récupère le nombre total de déclarations
    title = [
        "Répartition des types de dégâts pour " + str(nb) + " déclarations"
    ]  # Titre principal du graphique

    data = req_degats("total")  # Récupère la distribution globale des dégâts

    var_name = ""  # Nom de la variable de nomenclature à filtrer (initialisé à vide)
    multi = False  # Indique si la variable est multi-nomenclature

    # Dictionnaire associant chaque type_degat à un titre explicatif
    d = {
        "OEASC_PEUPLEMENT_ORIGINE": "Distribution par origine du peuplement",
        "OEASC_PEUPLEMENT_TYPE": "Distribution par type de peuplement",
        "OEASC_PEUPLEMENT_MATURITE": "Distribution par maturité du peuplement",
        "OEASC_PEUPLEMENT_PATURAGE_STATUT": "Distribution par statut de paturage",
        "OEASC_PEUPLEMENT_PATURAGE_TYPE": "Distribution par type de paturage",
        "OEASC_PEUPLEMENT_PATURAGE_FREQUENCE": "Distribution par fréquence de paturage",
        "OEASC_PEUPLEMENT_PROTECTION_TYPE": "Distribution par type de protection",
        "OEASC_PEUPLEMENT_ESSENCE_PRINCIPALE": "Distribution par essence principale",
    }

    # Détermine si le type_degat correspond à une variable multi-nomenclature
    if type_degat in [
        "OEASC_PEUPLEMENT_PATURAGE_TYPE",
        "OEASC_PEUPLEMENT_MATURITE",
        "OEASC_PEUPLEMENT_PROTECTION_TYPE",
    ]:
        multi = True

    title.append(
        d.get(type_degat, "")
    )  # Ajoute le sous-titre correspondant au type_degat

    if type_degat:
        # Calcule le nom de la variable à utiliser pour les jointures/filtrages
        var_name = type_degat.lower()[6:]
        if multi:
            var_name = var_name[11:]  # Pour les multi-nomenclatures, adapte le nom
        # Cas particulier pour l'essence principale
        if type_degat == "OEASC_PEUPLEMENT_ESSENCE_PRINCIPALE":
            type_degat = "OEASC_PEUPLEMENT_ESSENCE"
        # Pour chaque valeur possible de la nomenclature, récupère la distribution des dégâts associée
        for elem in nomenclature_oeasc()[type_degat]["values"]:
            data2 = req_degats(
                '"' + elem["mnemonique"] + '"', var_name, elem["id_nomenclature"], multi
            )
            data[elem["mnemonique"]] = data2[elem["mnemonique"]]
        # Supprime la clé "total" pour ne garder que les répartitions par catégorie
        data.pop("total", None)

    # Transforme les données au format attendu par les graphiques (labels/datasets)
    out = {"data": data_to_chart_data(data), "title": title}

    return out  # Retourne les données et le titre du graphique


def req_timeline():
    """
    Fonction pour récupérer la répartition temporelle des déclarations (timeline).

    Cette fonction exécute une requête SQL brute qui :
    - Agrège les déclarations par mois (en format 'YYYY-MM-01').
    - Compte le nombre de déclarations pour chaque mois.
    - Retourne les résultats triés par date croissante.

    Utilisation typique :
    - Affichage d'un graphique de type "timeline" ou "courbe" montrant l'évolution du nombre de déclarations au fil du temps.
    - Analyse statistique de la saisonnalité ou des tendances dans les déclarations.

    Retour :
        dict : Dictionnaire contenant les données formatées pour un graphique (ex : Chart.js), avec pour chaque point :
            - "x" : la date (mois, au format 'YYYY-MM-01')
            - "y" : le nombre de déclarations pour ce mois
    """

    # Requête SQL pour agréger les déclarations par mois
    r = """
    SELECT
        CONCAT(to_char(meta_create_date,'YYYY-MM'), '-01') as date,  -- Formatage de la date au premier jour du mois
        COUNT(*) as nb                                              -- Nombre de déclarations pour ce mois
    FROM oeasc_declarations.t_declarations
    GROUP BY 1
    ORDER BY 1
    """

    # Exécution de la requête SQL
    data = DB.session.execute(text(r))

    # Transformation des résultats en liste de dictionnaires pour le graphique
    data_array = [
        {
            "x": d.date,  # Date au format 'YYYY-MM-01'
            "y": d.nb,  # Nombre de déclarations pour ce mois
        }
        for d in data
    ]

    # Formatage final pour Chart.js ou autre librairie de graphiques
    out = {"data": {"datasets": [{"label": "nbs déclarations", "data": data_array}]}}

    return out  # Retourne les données prêtes à être utilisées pour l'affichage d'une timeline


def result_custom(params):
    # Cette fonction permet d'effectuer des requêtes personnalisées sur une vue ou une table SQL,
    # en regroupant et en comptant les occurrences d'une colonne donnée, avec possibilité de filtrer et trier les résultats.
    # Elle est utilisée pour générer des statistiques dynamiques sur n'importe quelle table ou vue, par exemple pour des dashboards ou des interfaces de reporting.

    # Récupère le nom du schéma et de la table à partir du paramètre "view" (ex: "schema.table")
    schema_name = params["view"].split(".")[0]
    table_name = params["view"].split(".")[1]

    # Met en cache l'objet GenericTable pour éviter de le recréer à chaque appel
    if not cache_generic_table.get(params["view"]):
        cache_generic_table[params["view"]] = GenericTable(
            table_name, schema_name, DB.engine
        )

    view = cache_generic_table.get(params["view"])

    # Prépare la requête SQLAlchemy pour sélectionner la colonne d'intérêt et compter les occurrences
    stmt_view = select(
        getattr(view.tableDef.columns, params["field_name"]),  # Colonne à analyser
        func.count("*").label("count"),  # Nombre d'occurrences
    )

    # Applique les filtres éventuels transmis dans params["filters"]
    for filter_key, filter_value in params.get("filters", {}).items():
        stmt_view = stmt_view.where(
            getattr(view.tableDef.columns, filter_key).in_(filter_value)
        )

    # Prépare la liste des colonnes pour le group by (par défaut la colonne analysée)
    group_bys = [params["field_name"]]
    order_by = "COUNT(*) DESC"  # Tri par nombre d'occurrences décroissant par défaut

    # Si un tri personnalisé est demandé via params["sort"]
    if params.get("sort"):
        field_sort = params["sort"]
        dir = "ASC"
        # Détermine le sens du tri (ASC ou DESC) selon le suffixe + ou -
        if field_sort[-1] in "+-":
            if field_sort[-1] == "-":
                dir = "DESC"
            field_sort = field_sort[:-1]

        # Si le champ de tri est différent du champ analysé, on l'ajoute au group by
        if field_sort != params["field_name"]:
            group_bys.append(field_sort)

        order_by = field_sort

        # Ajoute la direction du tri si spécifiée
        if "-" == params["sort"][-1]:
            order_by += f" {dir}"

    # Applique le group by sur les colonnes choisies
    stmt_view = stmt_view.group_by(text(", ".join(group_bys)))
    # Applique le tri sur la colonne choisie
    stmt_view = stmt_view.order_by(text(order_by))

    # Exécute la requête et récupère tous les résultats
    res = DB.session.execute(stmt_view).all()

    # Formate le résultat sous forme de liste de dictionnaires {"text": valeur, "count": nombre}
    return [{"text": r[0], "count": r[1]} for r in res]
