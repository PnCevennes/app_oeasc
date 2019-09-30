from flask import Blueprint, render_template

from .repository import (
    test_db,
)


bp = Blueprint('oeasc', __name__)


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

@bp.route('/perimetre_etude_carte')
def perimetre_etude_carte():
    '''
        pourquoi du projet OEASC
    '''
    return render_template('modules/oeasc/pages/presentation/perimetre_etude_carte.html')

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
