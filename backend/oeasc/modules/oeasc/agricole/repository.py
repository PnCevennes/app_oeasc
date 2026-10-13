"""
Requêtes d'agrégation des dégâts agricoles (restitution : graphiques et carte).

Toutes les données concernent la zone OEASC (communes de `ref_geo.communes_aoa`).
"""

import json

from flask import current_app
from sqlalchemy import case, distinct, func, select, text

from .models import TSaisonAgricole, TCulture, TDeclarationAgricole

config = current_app.config
DB = config["DB"]

ZONE = "OEASC"

# tolérance (en mètres, les géométries sont en Lambert-93) de simplification des
# contours de communes envoyés à la carte
TOLERANCE_SIMPLIFICATION = 50


def _surface_ha(colonne):
    """Somme d'une surface limitée aux lignes exprimées en hectares.

    Quelques déclarations (arbres fruitiers, plants maraîchers, récoltes au kg)
    portent dans la colonne « surface » un nombre de plants ou un poids, signalé
    par `unit_quantite_detruite` : elles ne sont pas des hectares.
    """
    return func.coalesce(
        func.sum(
            case(
                (
                    func.lower(TDeclarationAgricole.unit_quantite_detruite) == "ha",
                    colonne,
                ),
                else_=0,
            )
        ),
        0,
    )


def get_saison(id_saison):
    return DB.session.get(TSaisonAgricole, id_saison)


def get_bilan_saisons():
    """Indicateurs par saison, de la plus ancienne à la plus récente."""
    D = TDeclarationAgricole
    rows = DB.session.execute(
        select(
            TSaisonAgricole.id_saison,
            TSaisonAgricole.nom_saison,
            TSaisonAgricole.date_debut,
            TSaisonAgricole.current,
            func.count(D.id_declaration),
            func.count(distinct(D.numero_dossier)),
            func.coalesce(func.sum(D.montant_total_paye), 0),
            _surface_ha(D.surface_detruite),
            _surface_ha(D.surface_ressemis),
        )
        .join(D, D.id_saison == TSaisonAgricole.id_saison)
        .group_by(TSaisonAgricole.id_saison)
        .order_by(TSaisonAgricole.date_debut, TSaisonAgricole.nom_saison)
    ).all()
    return [
        {
            "id_saison": r[0],
            "nom_saison": r[1],
            "annee_debut": r[2].year if r[2] else None,
            "current": bool(r[3]),
            "nb_declarations": r[4],
            "nb_dossiers": r[5],
            "montant_total": float(r[6]),
            "surface_detruite": float(r[7]),
            "surface_ressemis": float(r[8]),
        }
        for r in rows
    ]


def get_bilan_cultures(id_saison=None):
    """Indicateurs par culture pour une saison.
    Sans `id_saison`, les indicateurs sont cumulés sur toutes les saisons."""
    D = TDeclarationAgricole
    nom_culture = func.coalesce(TCulture.nom_culture, "Non renseignée")
    query = (
        select(
            nom_culture,
            func.count(D.id_declaration),
            func.coalesce(func.sum(D.montant_total_paye), 0),
            _surface_ha(D.surface_detruite),
        )
        .outerjoin(TCulture, TCulture.id_culture == D.id_culture)
        .group_by(nom_culture)
        .order_by(func.count(D.id_declaration).desc(), nom_culture)
    )
    if id_saison is not None:
        query = query.where(D.id_saison == id_saison)
    rows = DB.session.execute(query).all()
    return [
        {
            "nom_culture": r[0],
            "nb_declarations": r[1],
            "montant_total": float(r[2]),
            "surface_detruite": float(r[3]),
        }
        for r in rows
    ]


def get_bilan_communes_geojson(id_saison=None):
    """FeatureCollection des communes de la zone OEASC avec, pour la saison :
    surface détruite (ha), montant total indemnisé et nombre de dossiers.
    Sans `id_saison`, les indicateurs sont cumulés sur toutes les saisons.
    Les communes sans déclaration sont présentes avec des valeurs à 0.

    Les géométries de `communes_aoa` sont en Lambert-93 (EPSG:2154) : elles sont
    simplifiées puis transformées en WGS84 pour Leaflet.
    """
    rows = DB.session.execute(
        text("""
            SELECT
                c.id,
                c.insee_com,
                c.nom,
                COALESCE(b.surface_detruite, 0),
                COALESCE(b.montant_total, 0),
                COALESCE(b.nb_dossiers, 0),
                COALESCE(b.nb_declarations, 0),
                ST_AsGeoJSON(
                    ST_Transform(
                        ST_SimplifyPreserveTopology(c.geom, :tolerance), 4326
                    ),
                    5
                )
            FROM ref_geo.communes_aoa c
            LEFT JOIN (
                SELECT
                    id_commune,
                    SUM(surface_detruite) FILTER (
                        WHERE lower(unit_quantite_detruite) = 'ha'
                    ) AS surface_detruite,
                    SUM(montant_total_paye) AS montant_total,
                    COUNT(DISTINCT numero_dossier) AS nb_dossiers,
                    COUNT(*) AS nb_declarations
                FROM oeasc_agricole.t_declaration_agricole
                WHERE CAST(:id_saison AS integer) IS NULL OR id_saison = :id_saison
                GROUP BY id_commune
            ) b ON b.id_commune = c.id
            ORDER BY c.nom
            """),
        {"id_saison": id_saison, "tolerance": TOLERANCE_SIMPLIFICATION},
    ).all()
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "id": r[0],
                "properties": {
                    "insee_com": r[1],
                    "nom": r[2],
                    "surface_detruite": float(r[3]),
                    "montant_total": float(r[4]),
                    "nb_dossiers": r[5],
                    "nb_declarations": r[6],
                },
                "geometry": json.loads(r[7]) if r[7] else None,
            }
            for r in rows
        ],
    }
