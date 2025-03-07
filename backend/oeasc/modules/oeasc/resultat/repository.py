from sqlalchemy import text, func
from flask import current_app
from ..nomenclature import nomenclature_oeasc
from utils_flask_sqla.generic import GenericTable

cache_generic_table = {}

config = current_app.config
DB = config["DB"]


def data_to_chart_data(data):
    keys = data.keys()
    datasets = [
        {"label": key, "data": data[key]}
        for key in filter(lambda k: k != "label", keys)
    ]

    out = {"labels": data["label"], "datasets": datasets}

    return out


def data_to_dict(data):
    """
    transforme le resultat de la requete en dictionnaire
    """
    out = {}
    ind = 0
    v = [d for d in data]
    for key in data.keys():
        out[key] = [e[ind] for e in v]
        ind += 1

    return out


def nb_declarations():
    """
    renvoie le nombre de déclarations
    """
    r = """
        SELECT COUNT(*) FROM oeasc_declarations.t_declarations
    """

    data = DB.engine.execute(text(r)).first()
    out = data[0]
    return out


def req_degats(name, var_name="", id_nomenclature_degat_type="", multi=False):
    r = """
SELECT
    n.mnemonique as label,
    a.nb as {}

    FROM (SELECT
        id_nomenclature_degat_type as id,
        COUNT(*) as nb
        FROM oeasc_declarations.t_degats d
        JOIN ref_nomenclatures.t_nomenclatures
            ON d.id_nomenclature_degat_type = id_nomenclature
        """.format(
        name
    )

    if var_name and not multi:
        r += """
        JOIN oeasc_declarations.t_declarations dec ON d.id_declaration=dec.id_declaration
        WHERE id_nomenclature_{} = {}
        """.format(
            var_name, id_nomenclature_degat_type
        )

    if var_name and multi:
        r += """
        JOIN oeasc_declarations.cor_nomenclature_declarations_{} cor ON d.id_declaration=cor.id_declaration
        WHERE cor.id_nomenclature = {}
        """.format(
            var_name, id
        )

    r += """
        GROUP BY id)a
    JOIN ref_nomenclatures.t_nomenclatures n
        ON id_nomenclature = a.id
        ORDER BY label
    """
    # .format(name, type, id)

    data = DB.engine.execute(text(r))

    return data_to_dict(data)


def req_degats_type(type_degat=""):
    """
    test pour les graphique
    ici requete pour un barchart sur les dégâts
    """
    nb = nb_declarations()
    title = ["Répartition des types de dégâts pour " + str(nb) + " déclarations"]

    data = req_degats("total")

    var_name = ""
    multi = False

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

    if type_degat in [
        "OEASC_PEUPLEMENT_PATURAGE_TYPE",
        "OEASC_PEUPLEMENT_MATURITE",
        "OEASC_PEUPLEMENT_PROTECTION_TYPE",
    ]:
        multi = True

    title.append(d.get(type_degat, ""))

    if type_degat:
        var_name = type_degat.lower()[6:]
        if multi:
            var_name = var_name[11:]
        if type_degat == "OEASC_PEUPLEMENT_ESSENCE_PRINCIPALE":
            type_degat = "OEASC_PEUPLEMENT_ESSENCE"
        for elem in nomenclature_oeasc()[type_degat]["values"]:
            data2 = req_degats(
                '"' + elem["mnemonique"] + '"', var_name, elem["id_nomenclature"], multi
            )
            data[elem["mnemonique"]] = data2[elem["mnemonique"]]

        data.pop("total", None)

    out = {"data": data_to_chart_data(data), "title": title}

    return out


def req_timeline():
    r = """
SELECT
    CONCAT(to_char(meta_create_date,'YYYY-MM'), '-01') as date,
    COUNT(*) as nb
    FROM oeasc_declarations.t_declarations
    GROUP BY 1
    ORDER BY 1
    """

    data = DB.engine.execute(text(r))

    data_array = [
        {
            "x": d.date,
            "y": d.nb,
        }
        for d in data
    ]

    out = {"data": {"datasets": [{"label": "nbs déclarations", "data": data_array}]}}

    return out


def result_custom(params):
    schema_name = params["view"].split(".")[0]
    table_name = params["view"].split(".")[1]
    if not cache_generic_table.get(params["view"]):
        cache_generic_table[params["view"]] = GenericTable(
            table_name, schema_name, DB.engine
        )

    view = cache_generic_table.get(params["view"])

    query = DB.session.query(
        getattr(view.tableDef.columns, params["field_name"]), func.count("*")
    )

    # filter
    for filter_key, filter_value in params.get("filters", {}).items():
        query = query.filter(
            getattr(view.tableDef.columns, filter_key).in_(filter_value)
        )

    group_bys = [params["field_name"]]
    order_by = "COUNT(*) DESC"

    if params.get("sort"):
        field_sort = params["sort"]
        dir = "ASC"
        if field_sort[-1] in "+-":
            if field_sort[-1] == "-":
                dir = "DESC"
            field_sort = field_sort[:-1]

        if field_sort != params["field_name"]:
            group_bys.append(field_sort)

        order_by = field_sort

        if "-" == params["sort"][-1]:
            order_by += f" {dir}"

    query = query.group_by(text(", ".join(group_bys)))
    query = query.order_by(text(order_by))
    res = query.all()
    return [{"text": r[0], "count": r[1]} for r in res]
