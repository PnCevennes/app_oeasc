from sqlalchemy import text
from flask import current_app
from app.utils.utilssqlalchemy import as_dict
from ..nomenclature import nomenclature_oeasc

config = current_app.config
DB = config['DB']


def data_to_chart_data(data):

    keys = data.keys()
    datasets = [{
        'label': key,
        'data': data[key]} for key in filter(lambda k: k != "label", keys)]

    out = {
        'labels': data['label'],
        'datasets': datasets
    }

    return out


def data_to_dict(data):
    '''
        transforme le resultat de la requete en dictionnaire
    '''
    out = {}
    ind = 0
    v = [d for d in data]
    for key in data.keys():
        out[key] = [e[ind] for e in v]
        ind += 1

    return out


def nb_declarations():
    '''
        renvoie le nombre de déclarations
    '''
    r = '''
        SELECT COUNT(*) FROM oeasc.t_declarations
    '''

    data = DB.engine.execute(text(r)).first()
    out = data[0]
    return out


def req_degats(name, var_name="", id=""):
    r = '''
SELECT
    n.mnemonique as label,
    a.nb as {}

    FROM (SELECT
        id_nomenclature_degat_type as id,
        COUNT(*) as nb
        FROM oeasc.t_degats d
        JOIN ref_nomenclatures.t_nomenclatures
            ON d.id_nomenclature_degat_type = id_nomenclature
        '''.format(name)

    if var_name:
        r += '''
        JOIN oeasc.t_declarations dec ON d.id_declaration=dec.id_declaration
        WHERE {} = {}
        '''.format(var_name, id)

    r += '''
        GROUP BY id)a
    JOIN ref_nomenclatures.t_nomenclatures n
        ON id_nomenclature = a.id
        ORDER BY label
    '''
    # .format(name, type, id)

    data = DB.engine.execute(text(r))

    return data_to_dict(data)


def req_test(type=""):
    '''
        test pour les graphique
        ici requete pour un barchart sur les dégâts
    '''
    data = req_degats("total")

    nb = nb_declarations()
    title = ["Répartition des types de dégâts pour " + str(nb) + " déclarations"]
    var_name = ""
    if type == "OEASC_PEUPLEMENT_ORIGINE":
        var_name = "id_nomenclature_peuplement_origine"
        title.append('Distribution par origine du peuplement')
    if type == "OEASC_PEUPLEMENT_TYPE":
        var_name = "id_nomenclature_peuplement_type"
        title.append("Distribution par type de peuplement")
    if type == "OEASC_PEUPLEMENT_PATURAGE_STATUT":
        var_name = "id_nomenclature_peuplement_paturage_statut"
        title.append("Distribution par statut de paturage")


    if type:
        for elem in nomenclature_oeasc()[type]['values']:
            print(elem)
            data2 = req_degats('"' + elem['mnemonique'] + '"', var_name, elem['id_nomenclature'])
            data[elem['mnemonique']] = data2[elem['mnemonique']]

    out = {
        'data': data_to_chart_data(data),
        'title': title
    }

    return out
