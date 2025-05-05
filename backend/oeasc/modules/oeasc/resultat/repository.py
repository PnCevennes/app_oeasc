from sqlalchemy import text, func, select

from flask import current_app
from ..nomenclature import nomenclature_oeasc
from utils_flask_sqla.generic import GenericTable
from ..declaration.models import TDeclaration, TDegat
# from pypnnomenclature.models import TNomenclatures
from ..commons.models import TNomenclatures_oeasc

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

    stmt_count = select(func.count()).select_from(TDeclaration)
    nb_result = DB.session.execute(stmt_count).scalar()

    return nb_result


def req_degats(name, var_name="", id_nomenclature_degat_type="", multi=False):

    """semble ne pas être utilisé"""

    if multi:
        stmt = select(
            TNomenclatures_oeasc.mnemonique.label('label'),
            func.count().label(name)
        ).select_from(
            TDegat
        ).join(
            TNomenclatures_oeasc,
            TDegat.id_nomenclature_degat_type == TNomenclatures_oeasc.id_nomenclature
        )
    else:
        stmt = select(
            TNomenclatures_oeasc.mnemonique.label('label'),
            func.count().label(name)
        ).select_from(
            TDegat
        ).join(
            TNomenclatures_oeasc,
            TDegat.id_nomenclature_degat_type == TNomenclatures_oeasc.id_nomenclature
        )

    stmt = stmt.group_by(
        TNomenclatures_oeasc.mnemonique
    ).order_by(
        TNomenclatures_oeasc.mnemonique
    )
    if var_name and not multi:
        stmt = stmt.join(
            TDeclaration,
            TDegat.id_declaration == TDeclaration.id_declaration
        ).where(
            TDeclaration.id_nomenclature_degat_type == id_nomenclature_degat_type
        )
    if var_name and multi:
        stmt = stmt.join(
            "cor_nomenclature_declarations_" + var_name,
            TDegat.id_declaration == "cor_nomenclature_declarations_" + var_name + ".id_declaration"
        ).where(
            "cor_nomenclature_declarations_" + var_name + ".id_nomenclature" == id_nomenclature_degat_type
        )
    if var_name:
        stmt = stmt.where(
            TNomenclatures_oeasc.mnemonique == var_name
        )
    else:
        stmt = stmt.where(
            TNomenclatures_oeasc.mnemonique == "total"
        )


    print(stmt)
    data = DB.session.execute(stmt).all()

    # r = """
    # SELECT
    #     n.mnemonique as label,
    #     a.nb as :name

    #     FROM (SELECT
    #         id_nomenclature_degat_type as id,
    #         COUNT(*) as nb
    #         FROM oeasc_declarations.t_degats d
    #         JOIN ref_nomenclatures.t_nomenclatures
    #             ON d.id_nomenclature_degat_type = id_nomenclature
    #         """

    # if var_name and not multi:
    #     r += """
    #     JOIN oeasc_declarations.t_declarations dec ON d.id_declaration=dec.id_declaration
    #     WHERE id_nomenclature_:varname = :id_nomenclature_degat_type
    #     """
    # if var_name and multi:
    #     r += """
    #     JOIN oeasc_declarations.cor_nomenclature_declarations_:varname cor ON d.id_declaration=cor.id_declaration
    #     WHERE cor.id_nomenclature = :id_nomemclature
    #     """

    # r += """
    #     GROUP BY id)a
    # JOIN ref_nomenclatures.t_nomenclatures n
    #     ON id_nomenclature = a.id
    #     ORDER BY label
    # """
    # .format(name, type, id)

    # text_stmt = text(r).bindparams(
    #     name=name,
    #     var_name=var_name,
    #     id_nomenclature_degat_type=id_nomenclature_degat_type,
    #     id_nomenclature=id,
    # )

    # data = DB.session.execute(text_stmt)
    
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


    data = DB.session.execute(text(r))

    # data = DB.engine.execute(text(r))

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

    stmt_view = select(
        getattr(view.tableDef.columns, params["field_name"]),
        func.count("*").label("count"),
    )

    # filter
    for filter_key, filter_value in params.get("filters", {}).items():
        stmt_view = stmt_view.where(
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



    stmt_view = stmt_view.group_by(text(", ".join(group_bys)))
    stmt_view = stmt_view.order_by(text(order_by))

    res = DB.session.execute(stmt_view).all()

    return [{"text": r[0], "count": r[1]} for r in res]
