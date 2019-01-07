from flask import Blueprint, render_template

bp = Blueprint('resultat', __name__)


# tests
@bp.route('/test/d3')
def test_d3():
    '''
        page du suvi de l'équilibre ASC

        TODO
    '''

    return render_template('modules/oeasc/test/d3.html')


# tests
@bp.route('/test/chart')
def test_chart():
    '''
        page du suvi de l'équilibre ASC

        TODO
    '''

    return render_template('modules/oeasc/test/chart.html')


@bp.route('/suivi_equilibre_ASC')
def resultats():
    '''
        page du suvi de l'équilibre ASC

        TODO
    '''

    return render_template('modules/oeasc/pages/resultats/resultats.html')


@bp.route('/degats_forestiers')
def degats_forestiers():
    '''
        resultats pour les degats_forestiers
        TODO
    '''

    return render_template('modules/oeasc/pages/resultats/degats_forestiers.html')


@bp.route('/diagnostics_sylvicoles')
def diagnostics_sylvicoles():
    '''
        resultats pour les diagnostics_sylvicoles
        TODO
    '''

    return render_template('modules/oeasc/pages/resultats/diagnostics_sylvicoles.html')


@bp.route('/donnees_cynegetiques')
def donnees_cynegetiques():
    '''
        resultats pour les donnees_cynegetiques
        TODO
    '''

    return render_template('modules/oeasc/pages/resultats/donnees_cynegetiques.html')


@bp.route('/ice')
def ice():
    '''
        resultats pour les ice
        TODO
    '''

    return render_template('modules/oeasc/pages/resultats/ice.html')


@bp.route('/peuplements_degradables')
def peuplements_degradables():
    '''
        resultats pour les peuplements_degradables
        TODO
    '''

    return render_template('modules/oeasc/pages/resultats/peuplements_degradables.html')


@bp.route('/degats_agricoles')
def degats_agricoles():
    '''
        resultats pour les degats_agricoles
        TODO
    '''

    return render_template('modules/oeasc/pages/resultats/degats_agricoles.html')


@bp.route('/mont_aigoual')
def mont_aigoual():
    '''
        resultats pour les mont_aigoual
        TODO
    '''

    return render_template('modules/oeasc/pages/resultats/mont_aigoual.html')


@bp.route('/vallees_cevenoles')
def vallees_cevenoles():
    '''
        resultats pour les vallees_cevenoles
        TODO
    '''

    return render_template('modules/oeasc/pages/resultats/vallees_cevenoles.html')


@bp.route('/mont_lozere')
def mont_lozere():
    '''
        resultats pour les mont_lozere
        TODO
    '''

    return render_template('modules/oeasc/pages/resultats/mont_lozere.html')


@bp.route('/causses_gorges')
def causses_gorges():
    '''
        resultats pour les causses_gorges
        TODO
    '''

    return render_template('modules/oeasc/pages/resultats/causses_gorges.html')
