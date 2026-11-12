"""
SEO : robots.txt et sitemap.xml

Ces routes sont publiques et servies à la racine du blueprint (`/seo/...`), sans préfixe `/api` :
Apache les expose sous les URLs attendues par les moteurs de recherche (voir
install/assets/apache2/oeasc.conf et install/docs/seo.md).

Le sitemap liste les pages publiques du frontend (chemins en dur ci-dessous, à tenir à jour avec les
routes sans `access` des modules frontend) et les contenus CMS de `t_contents` (actualités).
"""

from datetime import datetime
from urllib.parse import urlsplit
from xml.sax.saxutils import escape

from flask import Blueprint, Response, current_app
from sqlalchemy import select

from oeasc.utils.env import db as DB
from oeasc.modules.oeasc.commons.models import TContents

bp = Blueprint("seo_api", __name__)

# Pages publiques du frontend (routes sans `access`, avec contenu indexable).
# (chemin, priorité, fréquence de mise à jour)
PAGES_PUBLIQUES = [
    ("", 1.0, "weekly"),
    ("observatoire/presentation", 0.9, "monthly"),
    ("observatoire/justification", 0.7, "monthly"),
    ("observatoire/objectifs", 0.7, "monthly"),
    ("observatoire/perimetre", 0.7, "monthly"),
    ("observatoire/contenu", 0.7, "monthly"),
    ("resultats", 0.9, "monthly"),
    ("chasse/restitution_gd_public", 0.8, "monthly"),
    ("chasse/restitution_indices_performances", 0.8, "monthly"),
    ("icia/restitution_gd_public", 0.8, "monthly"),
    ("sylviculture/restitution_diagnostics_sylvicoles", 0.8, "monthly"),
    ("sylviculture/restitution_suivi_peuplements_sensibles", 0.8, "monthly"),
    ("declaration/systeme_alerte", 0.8, "monthly"),
    ("declaration/degat_grand_gibier", 0.8, "monthly"),
    ("declaration/signaler_degat_explication", 0.6, "monthly"),
    ("actualites", 0.8, "weekly"),
    ("page/documentation", 0.6, "monthly"),
    ("page/partenaires", 0.5, "monthly"),
    ("page/contact", 0.5, "yearly"),
]

# Chemins du frontend à ne pas faire explorer (relatifs à URL_FRONTEND)
CHEMINS_PRIVES = [
    "login",
    "user/",
    "content/",
    "declaration/declarer_en_ligne",
    "declaration/modifier_declaration",
    "declaration/actualisation_declaration",
    "declaration/liste",
    "declaration/voir_declaration/",
]


def _url_frontend():
    """URL publique du frontend, avec un « / » final (ex: https://domaine/front/)."""
    return current_app.config["URL_FRONTEND"]


def _lastmod(date):
    return date.strftime("%Y-%m-%d") if isinstance(date, datetime) else None


@bp.route("sitemap.xml", methods=["GET"])
def sitemap():
    base = _url_frontend()
    urls = []

    for chemin, priorite, frequence in PAGES_PUBLIQUES:
        urls.append((base + chemin, None, priorite, frequence))

    contenus = DB.session.scalars(
        select(TContents).where(
            TContents.type_page == "actualite", TContents.code.isnot(None)
        )
    ).all()
    for contenu in contenus:
        urls.append(
            (
                f"{base}actualite/{contenu.code}",
                _lastmod(contenu.meta_update_date or contenu.meta_create_date),
                0.6,
                "yearly",
            )
        )

    lignes = ['<?xml version="1.0" encoding="UTF-8"?>']
    lignes.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    for loc, lastmod, priorite, frequence in urls:
        lignes.append("  <url>")
        lignes.append(f"    <loc>{escape(loc)}</loc>")
        if lastmod:
            lignes.append(f"    <lastmod>{lastmod}</lastmod>")
        lignes.append(f"    <changefreq>{frequence}</changefreq>")
        lignes.append(f"    <priority>{priorite:.1f}</priority>")
        lignes.append("  </url>")
    lignes.append("</urlset>")

    return Response("\n".join(lignes), mimetype="application/xml")


@bp.route("robots.txt", methods=["GET"])
def robots():
    base = _url_frontend()
    chemin_front = urlsplit(base).path  # ex: /front/

    lignes = ["User-agent: *"]
    # l'API n'a pas à être explorée
    lignes.append("Disallow: /oeasc/")
    for chemin in CHEMINS_PRIVES:
        lignes.append(f"Disallow: {chemin_front}{chemin}")
    lignes.append("")
    lignes.append(f"Sitemap: {base}sitemap.xml")

    return Response("\n".join(lignes) + "\n", mimetype="text/plain")
