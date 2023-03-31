# import markdown
from flask import Blueprint, render_template

from pypnusershub import routes as fnauth
from app.modules.oeasc.user.utils import check_auth_redirect_login

# from .declaration_sample import test

from utils_flask_sqla.response import json_resp


# from .commons.repository import get_text

bp = Blueprint("test", __name__)
# md = markdown.Markdown()


@bp.route("/carte/", defaults={"id_areas": "", "type_code": "OEASC_COMMUNE"})
@bp.route("/carte/<string:type_code>", defaults={"id_areas": ""})
@bp.route("/carte/<string:type_code>/<string:id_areas>")
def carte(type_code, id_areas):
    """
    test cartes

    """

    areas_container = []

    for id_area in id_areas.split(","):
        if id_area != "":
            areas_container.append({"id_area": int(id_area)})

    data = {
        "type_code": type_code,
        "areas_container": areas_container,
    }

    return render_template("modules/oeasc/test/carte.html", data=data)


# @bp.route('/test_connexion', methods=['GET', 'POST'])
# @fnauth.check_auth(1)
# @bp.route('/md/<string:code>')
# @check_auth_redirect_login(1)
# def test_md(code):
#     '''
#         test md
#     '''

#     text = get_text(code)

#     if not text:
#         return None


#     md.reset()
#     md_html = md.convert(text['md'])

#     return render_template('modules/oeasc/test/md.html', md_html=md_html)
#     '''
# @bp.route('/md/<string:code>')
# @check_auth_redir
#     md.reset()
#     md_html = md.convert(text['md'])

#     return render_template('modules/oeasc/test/md.html', md_html=md_html)
# @bp.route('/md/<string:code>')
# @check_auth_redirect_login(1)
# def test_md(code):
#     '''
#         test md
#     '''

#     text = get_text(code)

#     if not text:
#         return None


#     md.reset()
#     md_html = md.convert(text['md'])

#     return render_template('modules/oeasc/test/md.html', md_html=md_html)

#     text = get_text(code)

#     if not text:
#         return None


#     md.reset()
#     md_html = md.convert(text['md'])

#     return render_template('modules/oeasc/test/md.html', md_html=md_html)
# @bp.route('/md/<string:code>')
# @check_auth_redirect_login(1)
# def test_md(code):
#     '''
#         test md
#     '''

#     text = get_text(code)

#     if not text:
#         return None


#     md.reset()
#     md_html = md.convert(text['md'])

#     return render_template('modules/oeasc/test/md.html', md_html=md_html)
