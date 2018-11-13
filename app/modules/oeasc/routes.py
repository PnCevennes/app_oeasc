from flask import (
    Blueprint, render_template, request, session, g, redirect, url_for
)

from .models import (
    TDeclaration,
)

from .repository import (
    nomenclature_oeasc,
    get_liste_organismes_oeasc,
    get_users,
    get_user,
    dfpu_as_dict_from_id_declaration,
    get_declarations,
    test_db,
)

from config import config

from .utils import check_auth_redirect_login

from .utils import (
    get_listes_essences,
    # check_foret,
)






bp = Blueprint('oeasc', __name__)


@bp.route('/users')
@check_auth_redirect_login(4)
def users():
    '''

    '''

    users = get_users()

    return render_template('modules/oeasc/pages/users.html', users=users)


@bp.route('/user')
@check_auth_redirect_login(1)
def user():
    '''

    '''

    if session.get('current_user', None):

        id_declarant = session['current_user']['id_role']

    user = get_user(id_declarant)

    return render_template('modules/oeasc/pages/user.html', user=user)


@bp.route('/login')
def login():
    '''
        page de connection
    '''

    redirect_url = request.args.get('redirect', "")
    validation_compte = request.args.get('validation_compte', "")
    identifiant = request.args.get('identifiant', "")
    type = request.args.get('type', "")

    return render_template('modules/oeasc/pages/login.html', config=config, id_app=config.ID_APP, redirect_url=redirect_url, validation_compte=validation_compte, identifiant=identifiant, type=type)


@bp.route('/reset_password/', defaults={'token': ""}, methods=['GET'])
@bp.route('/reset_password/<string:token>', methods=['GET'])
def reset_password(token):
    '''
        page pour recreer un mot de passe
    '''

    return render_template('modules/oeasc/pages/reset_password.html', token=token)


@bp.route('/register')
def register():
    '''
        page d'inscription
    '''

    liste_organismes_oeasc = get_liste_organismes_oeasc()
    nomenclature = nomenclature_oeasc()

    return render_template('modules/oeasc/pages/register.html', config=config, id_app=config.ID_APP, liste_organismes_oeasc=liste_organismes_oeasc, nomenclature=nomenclature)


@bp.route('/')
@bp.route('/accueil/')
def accueil():
    '''
        page d'accueil de l'OEASC, description synthetique
    '''

    test_db()


    return render_template('modules/oeasc/pages/accueil.html')


@bp.route('/presentation')
def presentation():
    '''
        presentation du projet OEASC
    '''
    return render_template('modules/oeasc/pages/presentation/presentation.html')


@bp.route('/pourquoi')
def pourquoi():
    '''
        pourquoi du projet OEASC
    '''
    return render_template('modules/oeasc/pages/presentation/pourquoi.html')


@bp.route('/perimetre_etude')
def perimetre_etude():
    '''
        pourquoi du projet OEASC
    '''
    return render_template('modules/oeasc/pages/presentation/perimetre_etude.html')


@bp.route('/objectifs')
def objectifs():
    '''
        objectifs du projet OEASC
    '''
    return render_template('modules/oeasc/pages/presentation/objectifs.html')


@bp.route('/contenu')
def contenu():
    '''
        contenu du projet OEASC
    '''
    return render_template('modules/oeasc/pages/presentation/contenu.html')


@bp.route('/signalement_degats_forestiers')
def signalement_degats_forestiers():
    '''
        accueil pour les signalement de degat forestiers
    '''
    return render_template('modules/oeasc/pages/declaration/systeme_alerte.html')


@bp.route('informations_declaration')
@check_auth_redirect_login(1)
def informations_declaration():
    '''
        page d'informations, en prélude au formulaire
    '''

    return render_template("modules/oeasc/pages/declaration/informations_declaration.html")


@bp.route('/modifier_ou_creer_declaration/', defaults={'id_declaration': -1})
@bp.route('/modifier_ou_creer_declaration/<int:id_declaration>')
@check_auth_redirect_login(1)
def modifier_declaration(id_declaration):
    '''
        page de declaration ou modification de degats forestiers

        :param id_declaration: identifiant en base de l'object declaration
        :type  id_declaration: integer ou None
    '''

    declaration_dict = dfpu_as_dict_from_id_declaration(id_declaration)

    if((not declaration_dict.get('id_declaration', None)) and (id_declaration != -1)):

        return "la declaration id_declaration : " + str(id_declaration) + " n'existe pas"

    nomenclature = nomenclature_oeasc()

    listes_essences = get_listes_essences(declaration_dict)

    id_form = request.args.get("id_form", "form_foret_statut")

    # check_foret(declaration_dict)

    return render_template('modules/oeasc/pages/declaration/modifier_ou_creer_declaration.html', declaration=declaration_dict, nomenclature=nomenclature, listes_essences=listes_essences, id_form=id_form)


@bp.route('/declaration/<int:id_declaration>')
def declaration(id_declaration):
    '''
        page affichant une declaration

        TODO
    '''
    declaration_dict = dfpu_as_dict_from_id_declaration(id_declaration)

    if((not declaration_dict.get('id_declaration', None)) and (id_declaration != -1)):

        return "la declaration id_declaration : " + str(id_declaration) + " n'existe pas"

    nomenclature = nomenclature_oeasc()

    return render_template('modules/oeasc/pages/declaration/declaration.html', declaration=declaration_dict, nomenclature=nomenclature)


@bp.route('/declarations')
@check_auth_redirect_login(1)
def declarations():
    '''
        page affichant la liste de declaration d'un utilisateur et de sa strucutre
        (sauf le cas ou structure = 'Particulier')
        les roles animateurs et administrateur peuvent tout voir
    '''

    id_declarant = None

    if session.get('current_user', None):

        id_declarant = session['current_user']['id_role']

    nomenclature = nomenclature_oeasc()

    declarations = get_declarations(False, id_declarant)

    return render_template('modules/oeasc/pages/declaration/declarations.html', declarations=declarations, nomenclature=nomenclature)


@bp.route('/degats_grand_gibier')
def degats_gibier():
    '''
        page du suvi de l'équilibre ASC

        TODO
    '''

    return render_template('modules/oeasc/pages/declaration/degats_gibier.html')

@bp.route('/suivi_equilibre_ASC')
def resultats():
    '''
        page du suvi de l'équilibre ASC

        TODO
    '''

    return render_template('modules/oeasc/pages/resultats/resultats.html')


@bp.route('/plan_site')
def plan_site():
    '''
        plan du site
        TODO
    '''

    return render_template('modules/oeasc/pages/plan_site.html')


@bp.route('/contact')
def contact():
    '''
        page de contact
        TODO
    '''

    return render_template('modules/oeasc/pages/contact.html')


@bp.route('/documentation')
def documentation():
    '''
        page de lien vers de la documentation concernant l'oeasc
        TODO
    '''

    return render_template('modules/oeasc/pages/documentation.html')


@bp.route('/partenaires')
def partenaires():
    '''
        liens des partenaires du projet oeasc
        TODO
    '''

    return render_template('modules/oeasc/pages/partenaires.html')


@bp.route('/resultats/degats_forestiers')
def resultats_degats_forestiers():
    '''
        resultats pour les degats_forestiers
        TODO
    '''

    nomenclature = nomenclature_oeasc()

    declarations = get_declarations(True)

    return render_template('modules/oeasc/pages/resultats/degats_forestiers.html', nomenclature=nomenclature, declarations=declarations)


@bp.route('/resultats/diagnostics_sylvicoles')
def resultats_diagnostics_sylvicoles():
    '''
        resultats pour les diagnostics_sylvicoles
        TODO
    '''

    return render_template('modules/oeasc/pages/resultats/diagnostics_sylvicoles.html')


@bp.route('/resultats/donnees_cynegetiques')
def resultats_donnees_cynegetiques():
    '''
        resultats pour les donnees_cynegetiques
        TODO
    '''

    return render_template('modules/oeasc/pages/resultats/donnees_cynegetiques.html')


@bp.route('/resultats/ice')
def resultats_ice():
    '''
        resultats pour les ice
        TODO
    '''

    return render_template('modules/oeasc/pages/resultats/ice.html')


@bp.route('/resultats/peuplements_degradables')
def resultats_peuplements_degradables():
    '''
        resultats pour les peuplements_degradables
        TODO
    '''

    return render_template('modules/oeasc/pages/resultats/peuplements_degradables.html')


@bp.route('/resultats/degats_agricoles')
def resultats_degats_agricoles():
    '''
        resultats pour les degats_agricoles
        TODO
    '''

    return render_template('modules/oeasc/pages/resultats/degats_agricoles.html')


@bp.route('/resultats/mont_aigoual')
def resultats_mont_aigoual():
    '''
        resultats pour les mont_aigoual
        TODO
    '''

    return render_template('modules/oeasc/pages/resultats/mont_aigoual.html')


@bp.route('/resultats/vallees_cevenoles')
def resultats_vallees_cevenoles():
    '''
        resultats pour les vallees_cevenoles
        TODO
    '''

    return render_template('modules/oeasc/pages/resultats/vallees_cevenoles.html')


@bp.route('/resultats/mont_lozere')
def resultats_mont_lozere():
    '''
        resultats pour les mont_lozere
        TODO
    '''

    return render_template('modules/oeasc/pages/resultats/mont_lozere.html')


@bp.route('/resultats/causses_gorges')
def resultats_causses_gorges():
    '''
        resultats pour les causses_gorges
        TODO
    '''

    return render_template('modules/oeasc/pages/resultats/causses_gorges.html')
