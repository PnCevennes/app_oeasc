"""
Données cartographiques des lieux de tir (page admin « Gestion des lieux de tirs »).

Les géométries `oeasc_chasse.*.geom` sont stockées en Lambert-93 (EPSG:2154) alors que les
modèles les déclarent en 4326 : on reprojette ici en SQL vers WGS84 pour Leaflet.
"""

import json

from sqlalchemy import text

from oeasc.utils.env import db as DB

# id_type de ref_geo.bib_areas_types pour les communes de la zone OEASC
ID_TYPE_COMMUNE = 327

# rayon (mètres) de la zone tampon dessinée autour d'un lieu de 1 ou 2 points
RAYON_ENVELOPPE_M = 100

# tolérance (mètres, Lambert-93) de simplification des contours
TOLERANCE_CONTOUR = 30

TYPES_CONTOUR = ("commune", "zone_indicative", "zone_cynegetique")


def get_carte_lieux_tir():
    """Lieux de tir (FeatureCollection WGS84, avec zones et synonymes) et listes des filtres."""
    rows = DB.session.execute(
        text("""
            SELECT
                lt.id_lieu_tir,
                lt.code_lieu_tir,
                lt.nom_lieu_tir,
                la.id_area,
                la.area_name,
                lt.id_zone_indicative,
                zi.nom_zone_indicative,
                COALESCE(lt.id_zone_cynegetique, zi.id_zone_cynegetique),
                zc.nom_zone_cynegetique,
                COALESCE(
                    (
                        SELECT array_agg(s.nom_lieu_tir_synonyme ORDER BY s.nom_lieu_tir_synonyme)
                        FROM oeasc_chasse.t_lieu_tir_synonymes s
                        WHERE s.id_lieu_tir = lt.id_lieu_tir
                    ),
                    ARRAY[]::varchar[]
                ),
                ST_AsGeoJSON(ST_Transform(ST_SetSRID(lt.geom, 2154), 4326), 6),
                -- enveloppe : zone tampon autour du point (1 pt) ou du segment (2 pts),
                -- enveloppe convexe à partir de 3 points (si elle est bien un polygone)
                ST_AsGeoJSON(
                    ST_Transform(
                        ST_SetSRID(
                            CASE
                                WHEN ST_NumGeometries(lt.geom) >= 3
                                    AND GeometryType(ST_ConvexHull(lt.geom)) = 'POLYGON'
                                THEN ST_ConvexHull(lt.geom)
                                ELSE ST_Buffer(ST_ConvexHull(lt.geom), :rayon, 'quad_segs=4')
                            END,
                            2154
                        ),
                        4326
                    ),
                    6
                )
            FROM oeasc_chasse.t_lieu_tirs lt
            -- commune déterminée par la position du lieu : t_lieu_tirs.id_area_commune est
            -- incohérent avec la géométrie (cf. docs), on ne s'en sert pas
            LEFT JOIN LATERAL (
                SELECT a.id_area, a.area_name
                FROM ref_geo.l_areas a
                WHERE a.id_type = :id_type
                    AND ST_Intersects(a.geom, ST_SetSRID(lt.geom, 2154))
                ORDER BY a.id_area
                LIMIT 1
            ) la ON TRUE
            LEFT JOIN oeasc_chasse.t_zone_indicatives zi
                ON zi.id_zone_indicative = lt.id_zone_indicative
            LEFT JOIN oeasc_chasse.t_zone_cynegetiques zc
                ON zc.id_zone_cynegetique = COALESCE(lt.id_zone_cynegetique, zi.id_zone_cynegetique)
            WHERE lt.geom IS NOT NULL
            ORDER BY lt.nom_lieu_tir
            """),
        {"id_type": ID_TYPE_COMMUNE, "rayon": RAYON_ENVELOPPE_M},
    ).all()

    lieux = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "id": r[0],
                "properties": {
                    "id_lieu_tir": r[0],
                    "code_lieu_tir": r[1],
                    "nom_lieu_tir": r[2],
                    "id_area_commune": r[3],
                    "nom_commune": r[4],
                    "id_zone_indicative": r[5],
                    "nom_zone_indicative": r[6],
                    "id_zone_cynegetique": r[7],
                    "nom_zone_cynegetique": r[8],
                    "synonymes": list(r[9]),
                    # polygone (WGS84) entourant le ou les points du lieu
                    "enveloppe": json.loads(r[11]),
                },
                "geometry": json.loads(r[10]),
            }
            for r in rows
        ],
    }

    # communes ayant au moins un lieu de tir, triées par nom
    communes = sorted(
        {(f["properties"]["id_area_commune"], f["properties"]["nom_commune"]) for f in lieux["features"]
         if f["properties"]["id_area_commune"] is not None},
        key=lambda c: c[1],
    )
    zones_indicatives = DB.session.execute(
        text("""
            SELECT id_zone_indicative, nom_zone_indicative, id_zone_cynegetique
            FROM oeasc_chasse.t_zone_indicatives
            ORDER BY nom_zone_indicative
            """)
    ).all()
    zones_cynegetiques = DB.session.execute(
        text("""
            SELECT id_zone_cynegetique, nom_zone_cynegetique
            FROM oeasc_chasse.t_zone_cynegetiques
            ORDER BY nom_zone_cynegetique
            """)
    ).all()

    return {
        "lieux": lieux,
        "communes": [{"id": r[0], "nom": r[1]} for r in communes],
        "zones_indicatives": [
            {"id": r[0], "nom": r[1], "id_zone_cynegetique": r[2]} for r in zones_indicatives
        ],
        "zones_cynegetiques": [{"id": r[0], "nom": r[1]} for r in zones_cynegetiques],
    }


def get_contour_geojson(type_contour, id_objet):
    """Contour (Feature WGS84 simplifié) d'une commune, d'une zone indicative ou d'une zone
    cynégétique (union de ses zones indicatives, qui n'a pas de géométrie propre).
    Retourne None si l'objet n'existe pas ou n'a pas de géométrie."""
    if type_contour not in TYPES_CONTOUR:
        raise ValueError(f"type de contour inconnu : {type_contour}")

    if type_contour == "commune":
        sql = """
            SELECT area_name, ST_Union(geom)
            FROM ref_geo.l_areas
            WHERE id_area = :id AND id_type = :id_type
            GROUP BY area_name
            """
    elif type_contour == "zone_indicative":
        sql = """
            SELECT nom_zone_indicative, ST_Union(geom)
            FROM oeasc_chasse.t_zone_indicatives
            WHERE id_zone_indicative = :id AND geom IS NOT NULL
            GROUP BY nom_zone_indicative
            """
    else:
        sql = """
            SELECT zc.nom_zone_cynegetique, ST_Union(zi.geom)
            FROM oeasc_chasse.t_zone_cynegetiques zc
            JOIN oeasc_chasse.t_zone_indicatives zi
                ON zi.id_zone_cynegetique = zc.id_zone_cynegetique
            WHERE zc.id_zone_cynegetique = :id AND zi.geom IS NOT NULL
            GROUP BY zc.nom_zone_cynegetique
            """

    # ST_Union renvoie la géométrie telle quelle (SRID 2154 dans les tables, même si typée 4326)
    row = DB.session.execute(
        text(f"""
            SELECT nom, ST_AsGeoJSON(
                ST_Transform(
                    ST_SimplifyPreserveTopology(ST_SetSRID(g, 2154), :tolerance), 4326
                ), 5
            )
            FROM ({sql}) AS t(nom, g)
            """),
        {"id": id_objet, "id_type": ID_TYPE_COMMUNE, "tolerance": TOLERANCE_CONTOUR},
    ).first()
    if not row or not row[1]:
        return None
    return {
        "type": "Feature",
        "properties": {"type": type_contour, "id": id_objet, "nom": row[0]},
        "geometry": json.loads(row[1]),
    }


class LieuTirErreur(Exception):
    """Erreur de validation / de contrainte, avec le code HTTP à renvoyer."""

    def __init__(self, message, code=400):
        super().__init__(message)
        self.message = message
        self.code = code


def _nettoie_synonymes(synonymes):
    vus, res = set(), []
    for s in synonymes or []:
        s = (s or "").strip()
        if s and s.lower() not in vus:
            vus.add(s.lower())
            res.append(s)
    return res


def modifier_lieu_tir(id_lieu_tir, data):
    """Met à jour un lieu de tir : nom, code, zone indicative, synonymes et points (MultiPoint
    GeoJSON WGS84 dans data['geometry']). Les synonymes absents de la liste sont supprimés
    (refusé s'ils sont utilisés par des réalisations)."""
    from sqlalchemy.exc import IntegrityError

    nom = (data.get("nom_lieu_tir") or "").strip()
    if not nom:
        raise LieuTirErreur("Le nom du lieu de tir est obligatoire.")
    geometry = data.get("geometry") or {}
    points = geometry.get("coordinates") or []
    if geometry.get("type") != "MultiPoint" or not points:
        raise LieuTirErreur("Le lieu de tir doit comporter au moins un point.")

    existe = DB.session.execute(
        text("SELECT 1 FROM oeasc_chasse.t_lieu_tirs WHERE id_lieu_tir = :id"),
        {"id": id_lieu_tir},
    ).first()
    if not existe:
        raise LieuTirErreur("Lieu de tir introuvable.", 404)

    id_zi = data.get("id_zone_indicative") or None
    try:
        # SRID conservé tel quel (stockage Lambert-93 sous un typage 4326, cf. docstring du module)
        DB.session.execute(
            text("""
                UPDATE oeasc_chasse.t_lieu_tirs
                SET nom_lieu_tir = :nom,
                    code_lieu_tir = :code,
                    id_zone_indicative = :id_zi,
                    geom = ST_SetSRID(
                        ST_Multi(ST_Transform(
                            ST_SetSRID(ST_GeomFromGeoJSON(:geom), 4326), 2154)),
                        ST_SRID(geom))
                WHERE id_lieu_tir = :id
                """),
            {
                "nom": nom,
                "code": (data.get("code_lieu_tir") or "").strip() or None,
                "id_zi": id_zi,
                "geom": json.dumps({"type": "MultiPoint", "coordinates": points}),
                "id": id_lieu_tir,
            },
        )

        voulus = _nettoie_synonymes(data.get("synonymes"))
        actuels = DB.session.execute(
            text("""SELECT id_lieu_tir_synonyme, nom_lieu_tir_synonyme
                    FROM oeasc_chasse.t_lieu_tir_synonymes WHERE id_lieu_tir = :id"""),
            {"id": id_lieu_tir},
        ).all()
        voulus_min = {s.lower() for s in voulus}
        actuels_min = {a[1].lower() for a in actuels}
        for id_syn, nom_syn in actuels:
            if nom_syn.lower() not in voulus_min:
                DB.session.execute(
                    text("""DELETE FROM oeasc_chasse.t_lieu_tir_synonymes
                            WHERE id_lieu_tir_synonyme = :id"""),
                    {"id": id_syn},
                )
        for s in voulus:
            if s.lower() not in actuels_min:
                DB.session.execute(
                    text("""INSERT INTO oeasc_chasse.t_lieu_tir_synonymes
                            (id_lieu_tir, nom_lieu_tir_synonyme) VALUES (:id, :nom)"""),
                    {"id": id_lieu_tir, "nom": s},
                )
        DB.session.commit()
    except IntegrityError:
        DB.session.rollback()
        raise LieuTirErreur(
            "Modification impossible : un synonyme retiré est utilisé par des réalisations.", 409
        )
    except Exception:
        DB.session.rollback()
        raise


def supprimer_lieu_tir(id_lieu_tir):
    """Supprime un lieu de tir et ses synonymes (refusé si des réalisations les utilisent)."""
    from sqlalchemy.exc import IntegrityError

    try:
        DB.session.execute(
            text("DELETE FROM oeasc_chasse.t_lieu_tir_synonymes WHERE id_lieu_tir = :id"),
            {"id": id_lieu_tir},
        )
        res = DB.session.execute(
            text("DELETE FROM oeasc_chasse.t_lieu_tirs WHERE id_lieu_tir = :id"),
            {"id": id_lieu_tir},
        )
        if res.rowcount == 0:
            DB.session.rollback()
            raise LieuTirErreur("Lieu de tir introuvable.", 404)
        DB.session.commit()
    except IntegrityError:
        DB.session.rollback()
        n = DB.session.execute(
            text("""SELECT count(*) FROM oeasc_chasse.t_realisations r
                    JOIN oeasc_chasse.t_lieu_tir_synonymes s USING (id_lieu_tir_synonyme)
                    WHERE s.id_lieu_tir = :id"""),
            {"id": id_lieu_tir},
        ).scalar()
        raise LieuTirErreur(
            f"Suppression impossible : {n} réalisation(s) sont rattachées à ce lieu de tir "
            "(via ses synonymes).",
            409,
        )
