"""
    Fonctions de traitement de données pour les déclarations
"""

from flask import session, current_app
from utils_flask_sqla_geo.generic import GenericQueryGeo
from utils_flask_sqla.generic import GenericQuery

from app.modules.oeasc.nomenclature import get_nomenclature_from_id, get_dict_nomenclature_areas
from app.modules.oeasc.user.repository import get_user, get_id_organismes

from .models import TDeclaration, TForet, TProprietaire

config = current_app.config
DB = config['DB']


def get_foret_type(id_foret):
    """
        Retourne le type de forêt
    """

    foret, proprietaire = get_foret(id_foret)

    if not foret:

        return

    if not proprietaire.id_nomenclature_proprietaire_type:

        return "Indéterminé"

    proprietaire_type = (
        get_nomenclature_from_id(
            proprietaire.id_nomenclature_proprietaire_type
        )['label_fr']
    )

    d_prop_foret_type = {

        'État': 'Domaniale',
        'Centre hospitalier': 'Autre forêt publique',
        'EP PNC': 'Autre forêt publique',
        'Commune': 'Communale',
        'Groupement forestier': 'Groupement forestier',
        'Section / hameau': 'Sectionale',
        'Privé': 'Privée'

    }

    foret_type = d_prop_foret_type.get(proprietaire_type, "Indeterminé")

    return foret_type


def dfpu_as_dict(declaration, foret, proprietaire, declarant, b_resolve=True):
    """
        Retourne une declaration
        avec foret proprietaire, declarant
        en dictionnaire
    """
    if not declaration:

        declaration = TDeclaration()

    if not foret:

        foret = TForet()

    if not proprietaire:

        proprietaire = TProprietaire()

    if not declarant:

        declarant = get_user()

    declaration_dict = declaration.as_dict(True)
    declaration_dict["foret"] = foret.as_dict(True)
    declaration_dict["declarant"] = declarant
    declaration_dict['foret']['proprietaire'] = proprietaire.as_dict(True)

    if b_resolve:
        get_dict_nomenclature_areas(declaration_dict)
        get_foret_type(declaration_dict.get("id_foret"))
    return declaration_dict


def resolve_declaration(declaration_dict):
    """
        transforme les id nomenclature, area en données
    """
    get_dict_nomenclature_areas(declaration_dict)
    get_foret_type(declaration_dict.get("foret"))
    resume_gravite(declaration_dict)

    return declaration_dict


def dfpu_as_dict_from_id_declaration(id_declaration, b_resolve=True):
    """
        retourne une declaration (avec infos foret proprio etc)
        sous forme de dictionnaire
    """
    declaration, foret, proprietaire, declarant = get_dfpu(id_declaration)
    declaration_dict = dfpu_as_dict(declaration, foret, proprietaire, declarant, b_resolve)
    return declaration_dict


def get_foret(id_foret):
    '''
        renvoie object foret et propietaire
    '''
    foret = proprietaire = None

    foret = DB.session.query(TForet).filter(id_foret == TForet.id_foret).first()

    if foret:

        id_proprietaire = foret.id_proprietaire

        if id_proprietaire:

            proprietaire = (
                DB.session.query(TProprietaire)
                .filter(id_proprietaire == TProprietaire.id_proprietaire)
                .first()
            )
    return foret, proprietaire


def get_dfpu(id_declaration):
    '''
        renvoie (declaration, foret, proprietaire, declarant)
    '''

    declaration = foret = proprietaire = declarant = None

    declaration = (
        DB.session.query(TDeclaration)
        .filter(id_declaration == TDeclaration.id_declaration)
        .first()
    )

    if declaration:

        id_declarant = declaration.id_declarant

        if id_declarant:

            declarant = get_user(id_declarant)
        id_foret = declaration.id_foret

        if id_foret:

            foret, proprietaire = get_foret(id_foret)

    return (declaration, foret, proprietaire, declarant)


def create_or_modify(model, key, val, dict_in):
    """
        fonction generique de creation ou modification
    """
    elem = None

    if key:

        elem = DB.session.query(model).filter(getattr(model, key) == val).first()

    if elem is None:
        elem = model()
        DB.session.add(elem)

    elem.from_dict(dict_in, True)

    DB.session.commit()

    return elem


def patch_areas_declarations(id_declaration):
    '''
        Ajoute les aire des secteurs, communes forets, sections
    '''

    txt = (
        '''
    DELETE FROM oeasc_declarations.cor_areas_declarations c
	USING ref_geo.l_areas l
	WHERE l.id_area=c.id_area AND l.id_type in (
	ref_geo.get_id_type('OEASC_SECTEUR'),
	ref_geo.get_id_type('OEASC_COMMUNE'),
	ref_geo.get_id_type('OEASC_SECTION'),
	ref_geo.get_id_type('OEASC_ONF_FRT'),
	ref_geo.get_id_type('OEASC_DGD')
	)
	AND c.id_declaration = {0}
   ;

    INSERT INTO oeasc_declarations.cor_areas_declarations

    WITH geom AS ( SELECT 	
        c.id_declaration,
        ST_MULTI(ST_UNION(l.geom)) AS geom
        FROM oeasc_declarations.cor_areas_declarations c
        JOIN ref_geo.l_areas l
            ON l.id_area = c.id_area
            AND l.id_type IN (
                ref_geo.get_id_type('OEASC_ONF_UG'),
                ref_geo.get_id_type('OEASC_CADASTRE')
            )
        GROUP BY c.id_declaration
    ),
    selected_types AS (SELECT UNNEST(ARRAY [          
             'OEASC_SECTEUR',
             'OEASC_COMMUNE',
             'OEASC_SECTION',
             'OEASC_ONF_FRT',
             'OEASC_DGD'
         ]) AS id_type)
        
         SELECT 
             {0},
             ref_geo.intersect_geom_type_tol(geom.geom, selected_types.id_type, 0.05) as id_area
             FROM selected_types
             JOIN geom ON geom.id_declaration = {0}
        RETURNING *;

'''
        .format(id_declaration)
    )

    a = DB.engine.execute(txt)

    return a

def f_create_or_update_declaration(declaration_dict):
    """
        creation ou modification de declaration
    """

    declaration = proprietaire = foret = None

    id_declaration = declaration_dict.get("id_declaration", None)

    # on n'écrit la foret ou le proprietaire dans la base
    # que dans le cas d'une foret non documentée
    if not declaration_dict["foret"]["b_document"]:

        id_foret = declaration_dict["foret"].get("id_foret", None)
        id_proprietaire = declaration_dict["foret"]["proprietaire"].get("id_proprietaire", None)

        proprietaire = create_or_modify(
            TProprietaire,
            'id_proprietaire',
            id_proprietaire,
            declaration_dict["foret"]["proprietaire"]
        )

        declaration_dict['foret']['id_proprietaire'] = proprietaire.id_proprietaire

        foret = create_or_modify(TForet, 'id_foret', id_foret, declaration_dict["foret"])

        declaration_dict['id_foret'] = foret.id_foret

    else:

        proprietaire = TProprietaire().from_dict(declaration_dict["foret"]["proprietaire"], True)
        foret = TForet().from_dict(declaration_dict["foret"], True)

    # pour le cas ou on veut generer une create date en random :
    # - elle sera crée un fois avec la date courante
    # - puis modifiée pour lui donner la date choisie aléatoirement
    if declaration_dict.get("meta_create_date", None):

        declaration = create_or_modify(
            TDeclaration,
            'id_declaration',
            id_declaration,
            declaration_dict
        )

        id_declaration = declaration.id_declaration

    # geom

    declaration = create_or_modify(TDeclaration, 'id_declaration', id_declaration, declaration_dict)

    # patch cor areas
    DB.session.commit()

    a = patch_areas_declarations(declaration.id_declaration)
    [print(b) for b in a]

    d = dfpu_as_dict(declaration, foret, proprietaire, None)

    return d


def get_declaration(id_declaration):
    '''
        verifie les droit de l'utilisateur et renvoie la declaration
    '''

    res = get_declarations(
        user=get_user(session['current_user']['id_role']),
        id_declaration=id_declaration
    )

    if res and res[0]:
        return res[0]

    return None


def get_declarations(user=None, type_export=None, type_out=None, id_declaration=None):
    '''
        retourne une liste de declaration sous forme de tableau de dictionnaire
        type_export : shape csv (dict par defaut)
        type_out : 1 ligne par declaration ou une ligne par degat
        user : dictionnaire contenant les informations sur l'utilisateur, nottament ses droits
    '''

    liste_id_organismes_solo = get_id_organismes(['Autre (préciser)', "Pas d'organisme"])

    view_names = {
        'csv': 'v_export_declarations_csv',
        'csv_deg': 'v_export_declaration_degats_csv',
        'shape': 'v_export_declarations_shape',
        'shape_deg': 'v_export_declaration_degats_shape',
        'default': 'v_declarations',
        'default_deg': 'v_declaration_degats'
    }

    # choix de la vue selon les paramètres
    if type_export in ['csv', 'shape']:
        view_key = type_export
    else:
        view_key = 'default'

    if type_out == 'degat':
        view_key += '_deg'

    view_name = view_names[view_key]

    # choix des filtrers selon les droits de l'utilisateur
    filters = {}
    if user:

        # administrateur et animateur >=5
        if user["id_droit_max"] >= 5:
            pass

        # les declarant de la meme structure (sauf les particuliers) >=)2
        elif user["id_droit_max"] >= 2 and user['id_organisme'] not in liste_id_organismes_solo:
            filters = {"organisme": user['organisme']}

        # les personnes de droit 1 (leurs alertes seulement)
        elif user["id_droit_max"] >= 1:
            filters = {"id_declarant": user['id_declarant']}

    # cas où on veut une seule declaration
    if id_declaration:
        filters['id_declaration'] = id_declaration

    geometry_field = None
    if type_export == 'shape':
        geometry_field = 'geom'

    # requête
    data = None
    gq = GenericQueryGeo(
        DB,
        view_name,
        'oeasc_declarations',
        geometry_field=geometry_field,
        filters=filters,
        limit=1e6
    )

    if type_export == 'shape':
        return gq.query()[0]

    data = gq.return_query()

    if not (data and data.get('items')):
        return []

    declarations = data.get('items')

    for d in declarations:
        for e in d:
            if d[e] is None:
                d[e] = ''

    if view_key != 'default':
        return declarations

    # TODO a partir de la vue avec degats ??
    add_degats(declarations)

    # pre_get_dict_nomenclature_areas(declarations)
    # declarations = [resolve_declaration(d) for d in declarations]

    return declarations


def add_degats(declarations):
    """
        ajoute un object degats aux declarations
    """
    data_degats = GenericQuery(
        DB,
        'v_degats',
        'oeasc_declarations',
        limit=1e6
    ).return_query()['items']

    degats_declarations = {}

    for deg in data_degats:

        dd = degats_declarations.get(deg['id_declaration_degat'])
        if not dd:
            dd = degats_declarations[deg['id_declaration_degat']] = []

        d_cur = None
        for d in dd:
            if d['degat_type_mnemo'] == deg['degat_type_mnemo']:
                d_cur = d
                break

        if not d_cur:
            d_cur = {
                'degat_type_mnemo': deg['degat_type_mnemo'],
                'degat_type_label': deg['degat_type_label'],
                'degat_type_code': deg['degat_type_code'],
            }
            # if deg.get('degat_essence_mnemo'):
            d_cur['degat_essences'] = []
            dd.append(d_cur)

        if deg.get('degat_essence_mnemo'):
            d_cur['degat_essences'].append({
                'degat_essence_mnemo': deg['degat_essence_mnemo'],
                'degat_anteriorite_mnemo': deg['degat_anteriorite_mnemo'],
                'degat_gravite_mnemo': deg['degat_gravite_mnemo'],
                'degat_etendue_mnemo': deg['degat_etendue_mnemo'],
                'degat_essence_label': deg['degat_essence_label'],
                'degat_anteriorite_label': deg['degat_anteriorite_label'],
                'degat_gravite_label': deg['degat_gravite_label'],
                'degat_etendue_label': deg['degat_etendue_label'],
                'degat_essence_code': deg['degat_essence_code'],
                'degat_anteriorite_code': deg['degat_anteriorite_code'],
                'degat_gravite_code': deg['degat_gravite_code'],
                'degat_etendue_code': deg['degat_etendue_code'],
            })

    for d in declarations:
        d['degats'] = degats_declarations[d['id_declaration']]


def resume_gravite(declaration_dict):
    '''
        Donne la pire gravité d'une déclaration
    '''
    gravite = None
    if not declaration_dict.get('degats'):
        return
    for degat in declaration_dict.get('degats'):
        for degat_essence in degat['degat_essences']:

            if not degat_essence['id_nomenclature_degat_gravite']:
                continue

            if not degat_essence['id_nomenclature_degat_gravite']['cd_nomenclature']:
                continue
            gravite_ = degat_essence['id_nomenclature_degat_gravite']

            if not gravite:
                gravite = gravite_

            if gravite_['cd_nomenclature'] == "DG_IMPT" or \
               gravite['cd_nomenclature'] == "DG_FLB" and \
               gravite['cd_nomenclature'] == "DG_MOY":
                gravite = gravite_

    declaration_dict['gravite'] = gravite


def nomenclatures_to_str(nomenclatures, field_name="mnemonique"):
    """
        TODO a remplacer par les vues
    """
    if not nomenclatures:
        return ""

    return " ,".join(e[field_name] for e in nomenclatures)


def id_nomenclature_to_str(id_nomenclature, field_name="mnemonique"):
    """
        TODO a remplacer par les vues
    """
    if not id_nomenclature:
        return ""

    return id_nomenclature[field_name]


def get_declaration_table(declaration_dict):
    '''
        get_declaration_table
    '''
    if declaration_dict['id_declaration']:
        return get_declaration(declaration_dict['id_declaration'])

    else:

        d = {}
        d['declaration_date'] = declaration_dict.get('meta_create_date') or ''
        d['b_autorisation'] = declaration_dict.get('b_autorisation')
        d['peuplement_acces_label'] = (
            (declaration_dict.get('id_nomenclature_peuplement_acces') or {})
            .get('label_fr', '')
        )
        d['espece_label'] = (
            ' ,'.join(
                [
                    n['label_fr']
                    for n in declaration_dict.get('nomenclatures_peuplement_espece', [])
                ]
            )
        )

        d['label_foret'] = declaration_dict['foret']['label_foret']
        d['statut_public'] = "Public" if declaration_dict['foret'].get('b_statut_public') \
            else "Privé"
        d['b_document'] = declaration_dict['foret'].get('b_document')
        d['b_statut_public'] = declaration_dict['foret'].get('b_statut_public')
        d['id_foret'] = declaration_dict['foret'].get('id_foret')
        d['communes'] = ' ,'.join(
            [
                l['area_name']
                for l in declaration_dict['foret']['areas_foret']
                if l['type_code'] == 'OEASC_COMMUNE'
            ]
        )
        d['secteur'] = ' ,'.join(
            [
                l['area_name']
                for l in declaration_dict['areas_localisation']
                if l['type_code'] == 'OEASC_SECTEUR'
            ]
        )
        d['parcelles'] = ' ,'.join(
            [
                l['area_name']
                for l in declaration_dict['areas_localisation']
                if l['type_code'] in ['OEASC_ONF_UG', 'OEASC_CADASTRE']
            ]
        )
        d['peuplement_ess_1_label'] = (
            (declaration_dict.get('id_nomenclature_peuplement_essence_principale') or {})
            .get('label_fr', '')
        )
        d['peuplement_ess_2_label'] = (
            ' ,'.join([n['label_fr'] for n in declaration_dict.get(
                'nomenclatures_peuplement_essence_secondaire', [])])
        )
        d['peuplement_ess_3_label'] = (
            ' ,'.join([n['label_fr'] for n in declaration_dict.get(
                'nomenclatures_peuplement_essence_complementaire', [])])
        )
        d['peuplement_surface'] = declaration_dict['peuplement_surface']
        d['peuplement_origine_label'] = (
            (declaration_dict.get('id_nomenclature_peuplement_origine') or {})
            .get('label_fr', '')
        )
        d['peuplement_type_label'] = (
            (declaration_dict.get('id_nomenclature_peuplement_type') or {})
            .get('label_fr', '')
        )
        d['peuplement_maturite_label'] = (
            ' ,'.join([n['label_fr'] for n in declaration_dict.get(
                'nomenclatures_peuplement_maturite', [])])
        )

        d['b_peuplement_protection_existence'] = (
            declaration_dict.get('b_peuplement_protection_existence')
        )
        d['peuplement_protection_type_label'] = (
            ' ,'.join([n['label_fr'] for n in declaration_dict.get(
                'nomenclatures_peuplement_protection_type', [])])
        )
        d['autre_protection'] = declaration_dict['autre_protection']

        d['precision_localisation'] = declaration_dict['precision_localisation']

        d['b_peuplement_paturage_presence'] = declaration_dict.get('b_peuplement_paturage_presence')
        d['peuplement_paturage_type_label'] = (
            ' ,'.join([n['label_fr'] for n in declaration_dict.get(
                'nomenclatures_peuplement_paturage_type', [])])
        )
        d['peuplement_paturage_statut_label'] = (
            (declaration_dict.get('id_nomenclature_peuplement_paturage_statut') or {})
            .get('label_fr', '')
        )
        d['peuplement_paturage_frequence_label'] = (
            (declaration_dict.get('id_nomenclature_peuplement_paturage_frequence') or {})
            .get('label_fr', '')
        )
        d['peuplement_paturage_saison_label'] = (
            ' ,'.join([n['label_fr'] for n in declaration_dict.get(
                'nomenclatures_peuplement_paturage_saison', [])])
        )
        d['commentaire'] = declaration_dict['commentaire']

        d['degats'] = [
            {
                'degat_type_label': d['id_nomenclature_degat_type']['label_fr'],
                'degat_type_mnemo': d['id_nomenclature_degat_type']['mnemonique'],
                'degat_essences': [
                    {
                        'degat_essence_label': (
                            de.get('id_nomenclature_degat_essence', {})
                            .get('label_fr')
                        ),
                        'degat_gravite_label': (
                            (de.get('id_nomenclature_degat_gravite') or {})
                            .get('label_fr')
                        ),
                        'degat_anteriorite_label': (
                            (de.get('id_nomenclature_degat_anteriorite') or {})
                            .get('label_fr')
                        ),
                        'degat_etendue_label': (
                            (de.get('id_nomenclature_degat_etendue') or {})
                            .get('label_fr')
                        ),
                    }
                    for de in d.get('degat_essences', [])
                ]
            }
            for d in declaration_dict.get('degats', [])
        ]

    return d
