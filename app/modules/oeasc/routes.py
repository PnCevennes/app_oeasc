from flask import (
    Blueprint, render_template, request
)

from .models import (
    TDeclaration,
)

from pypnusershub import routes as fnauth

from .repository import (
    nomenclature_oeasc,
    get_liste_organismes_oeasc,
    get_users,
    declaration_dict_sample,
    get_declaration
)

from config import config

from .utils import (
    get_listes_essences,
    check_foret
)

from app.utils.env import (
    DB, URL_REDIRECT
)


bp = Blueprint('oeasc', __name__)


@fnauth.check_auth(4, False, URL_REDIRECT)
@bp.route('/users')
def users():
    '''
        page de connection

    '''

    users = get_users()

    return render_template('modules/oeasc/pages/users.html', users=users)


@bp.route('/login')
def login():
    '''
        page de connection
    '''
    return render_template('modules/oeasc/pages/login.html', config=config, id_app=config.ID_APP)


@bp.route('/register')
def register():
    '''
        page d'inscription
    '''

    liste_organismes_oeasc = get_liste_organismes_oeasc()

    return render_template('modules/oeasc/pages/register.html', config=config, id_app=config.ID_APP, liste_organismes_oeasc=liste_organismes_oeasc)


@bp.route('/')
@bp.route('/accueil/')
def accueil():
    '''
        page d'accueil de l'OEASC, description synthetique
    '''
    return render_template('modules/oeasc/pages/accueil.html')


@bp.route('/description')
def description():
    '''
        description du projet OEASC
    '''
    return render_template('modules/oeasc/pages/description.html')


@bp.route('/signalement_degats_forestiers')
def signalement_degats_forestiers():
    '''
        accueil pour les signalement de degat forestiers
    '''
    return render_template('modules/oeasc/pages/systeme_alerte.html')


@bp.route('/creer_declaration/', defaults={'id_declaration': -1})
@bp.route('/modifier_declaration/<int:id_declaration>')
@fnauth.check_auth(1, False, URL_REDIRECT)
def modifier_declaration(id_declaration):
    '''
        page de declaration ou modification de degats forestiers

        :param id_declaration: identifiant en base de l'object declaration
        :type  id_declaration: integer ou None
    '''
    declaration, foret, proprietaire, declaration_dict = get_declaration(id_declaration)

    declaration_dict = declaration_dict_sample()
    return str(declaration_dict)

    nomenclature = nomenclature_oeasc()
    listes_essences = get_listes_essences(declaration_dict)

    id_form = request.args.get("id_form", "form_foret_statut")

    check_foret(declaration_dict)


    return render_template('modules/oeasc/pages/modifier_ou_creer_declaration.html', declaration=declaration_dict, nomenclature=nomenclature, listes_essences=listes_essences, id_form=id_form)


@bp.route('/declaration/<int:id_declaration>')
def declaration(id_declaration):
    '''
        page affichant une declaration

        TODO
    '''

    declaration = DB.session.query(TDeclaration).filter(id_declaration == TDeclaration.id_declaration).first()

    declaration_dict = declaration.as_dict(True)
    nomenclature = nomenclature_oeasc()

    check_foret(declaration_dict)


    return render_template('modules/oeasc/pages/declaration.html', declaration=declaration_dict, nomenclature=nomenclature)


@bp.route('/declarations')
def declarations():
    '''
        page affichant une liste de declaration

        TODO
    '''

    declarations = DB.session.query(TDeclaration)

    declarations_array = [declaration.as_dict(True) for declaration in declarations]

    return render_template('modules/oeasc/pages/declarations.html', declarations=declarations_array)


@bp.route('/suivi_equilibre_ASC')
def suivi():
    '''
        page du suvi de l'équilibre ASC

        TODO
    '''

    return render_template('modules/oeasc/pages/suivi.html')


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

    return render_template('modules/oeasc/pages/resultats/degats_forestiers.html')


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
