"""
Commande Flask CLI : flask refresh-ref-geo

Reconstruit entièrement ref_geo.l_areas depuis des fichiers GeoPackage.
Reproductible en dev et en production.

Usage :
    flask refresh-ref-geo [--dry-run] [--skip-load] [--force]

Options :
    --dry-run    Exécute toutes les étapes sauf le swap final
    --skip-load  Saute le chargement GPKG si l_areas_new existe déjà
    --force      Pas de confirmation interactive
"""

import logging
import os
from datetime import datetime

import click
import geopandas as gpd
import psycopg2.extras
from flask.cli import with_appcontext
from shapely.geometry import MultiPolygon
from shapely.wkt import dumps as wkt_dumps
from sqlalchemy import text

LOG = logging.getLogger(__name__)

_report: dict = {}

REQUIRED_REVISION = "a1b2c3d4e5f6"

# ---------------------------------------------------------------------------
# Chemins des fichiers GPKG
# ---------------------------------------------------------------------------
GPKG_CADASTRE = "/home/thibaut/appli/app_oeasc/data/ref_geo/cadastres.gpkg"
GPKG_COMMUNES = "/home/thibaut/appli/app_oeasc/data/ref_geo/communes_aoa.gpkg"
GPKG_DGD = "/home/thibaut/appli/app_oeasc/data/ref_geo/forets_dgd.gpkg"


# GPKG_FORET_ONF = "/home/thibaut/appli/app_oeasc/data/ref_geo/forets_gestion_onf_aoa.gpkg"
GPKG_FORET_ONF = (
    "/home/thibaut/appli/app_oeasc/data/ref_geo/forets_gestion_onf_aoa.gpkg"
)
# GPKG_PARCELLE_ONF = "/home/thibaut/appli/app_oeasc/data/ref_geo/parcelles_forets_onf.gpkg"
GPKG_PARCELLE_ONF = (
    "/home/thibaut/appli/app_oeasc/data/ref_geo/parcelles_forets_onf_new.gpkg"
)
GPKG_UG_ONF = (
    "/home/thibaut/appli/app_oeasc/data/ref_geo/unites_gestion_forets_onf.gpkg"
)


# ---------------------------------------------------------------------------
# id_type (ref_geo.bib_areas_types)
# ---------------------------------------------------------------------------
ID_TYPE_OEASC = 323
ID_TYPE_COEUR = 324
ID_TYPE_ADHESION = 325
ID_TYPE_SECTEUR = 326
ID_TYPE_COMMUNE = 327
ID_TYPE_FORET_ONF = 328
ID_TYPE_PARCELLE_ONF = 329
ID_TYPE_UG_ONF = 330
ID_TYPE_DGD = 331
ID_TYPE_CADASTRE = 332
ID_TYPE_SECTION = 333
ID_TYPE_FORET_PRIVE = (
    33  # type_code = OEASC_FORET_PRIVE (forêts privées sans document DGD)
)

FIXED_ID_TYPES = (ID_TYPE_OEASC, ID_TYPE_COEUR, ID_TYPE_ADHESION, ID_TYPE_SECTEUR)

# Seuil de chevauchement pour la correspondance des déclarations (90 %)
MATCH_THRESHOLD = 0.9

# Nomenclature propriétaire
NOMENCLATURE_PT_PRI = 565  # propriétaire privé (DGD)
NOMENCLATURE_PT_E = 559  # propriétaire public (ONF)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_db():
    from oeasc.utils.env import db

    return db


def _ensure_migrations():
    """Vérifie que la migration REQUIRED_REVISION est appliquée, sinon lance l'upgrade."""
    db = _get_db()
    row = db.session.execute(
        text("SELECT version_num FROM alembic_version WHERE version_num = :rev"),
        {"rev": REQUIRED_REVISION},
    ).fetchone()

    if row is not None:
        return

    LOG.info(
        f"Migration {REQUIRED_REVISION} non appliquée — "
        "lancement automatique de flask db upgrade..."
    )
    from flask_migrate import upgrade as flask_migrate_upgrade

    flask_migrate_upgrade(revision=REQUIRED_REVISION)
    LOG.info(f"Migration {REQUIRED_REVISION} appliquée avec succès.")


def _raw_conn():
    """Retourne une connexion psycopg2 brute depuis le moteur SQLAlchemy."""
    return _get_db().engine.raw_connection()


def _to_multi(geom):
    """Force une géométrie en MultiPolygon."""
    if geom is None:
        return None
    if geom.geom_type == "Polygon":
        return MultiPolygon([geom])
    return geom


def _wkt(geom):
    return wkt_dumps(_to_multi(geom), rounding_precision=3)


def _table_exists(schema, table):
    db = _get_db()
    r = db.session.execute(
        text(
            "SELECT 1 FROM information_schema.tables "
            "WHERE table_schema=:s AND table_name=:t"
        ),
        {"s": schema, "t": table},
    ).fetchone()
    return r is not None


def _column_exists(schema, table, column):
    db = _get_db()
    r = db.session.execute(
        text(
            "SELECT 1 FROM information_schema.columns "
            "WHERE table_schema=:s AND table_name=:t AND column_name=:c"
        ),
        {"s": schema, "t": table, "c": column},
    ).fetchone()
    return r is not None


def _filter_by_oeasc(gdf, oeasc_geom):
    """
    Filtre un GeoDataFrame pour ne garder que les géométries intersectant
    le périmètre OEASC. Retourne le GeoDataFrame filtré en EPSG:2154.
    """
    if gdf.crs is None or gdf.crs.to_epsg() != 2154:
        gdf = gdf.to_crs(epsg=2154)
    oeasc_gdf = gpd.GeoDataFrame(geometry=[oeasc_geom], crs="EPSG:2154")
    filtered = gpd.sjoin(gdf, oeasc_gdf, how="inner", predicate="intersects")
    drop_cols = [c for c in filtered.columns if c.startswith("index_")]
    return filtered.drop(columns=drop_cols).reset_index(drop=True)


def _get_oeasc_geom():
    """Récupère la géométrie du périmètre OEASC depuis l_areas_new ou l_areas."""
    db = _get_db()
    table = "l_areas_new" if _table_exists("ref_geo", "l_areas_new") else "l_areas"
    row = db.session.execute(
        text(
            f"SELECT ST_AsText(geom) FROM ref_geo.{table} WHERE id_type = {ID_TYPE_OEASC} LIMIT 1"
        )
    ).fetchone()
    if row is None:
        raise RuntimeError("Périmètre OEASC (id_type=323) introuvable")
    from shapely.wkt import loads

    return loads(row[0])


def _create_gist_index(conn, table="l_areas_new"):
    """Crée/rafraîchit l'index GIST sur la table après un chargement."""
    cur = conn.cursor()
    cur.execute(
        f"CREATE INDEX IF NOT EXISTS ix_{table}_geom_tmp "
        f"ON ref_geo.{table} USING GIST (geom)"
    )
    conn.commit()
    cur.close()


def _bulk_insert_areas(raw_conn, rows, chunksize=500):
    """
    Insère en masse dans ref_geo.l_areas_new.
    rows : liste de tuples
        (id_type, area_name, area_code, source, enable, meta_create_date,
         geom_wkt_2154, geom4326_wkt, centroid_wkt_2154, proprietaire)
    """
    sql = """
        INSERT INTO ref_geo.l_areas_new
            (id_type, area_name, area_code, source, enable, meta_create_date,
             geom, geom_4326, centroid, proprietaire)
        VALUES %s
    """
    template = (
        "(%s, %s, %s, %s, %s, %s, "
        "ST_GeomFromText(%s, 2154), "
        "ST_GeomFromText(%s, 4326), "
        "ST_GeomFromText(%s, 2154), %s)"
    )
    cur = raw_conn.cursor()
    for i in range(0, len(rows), chunksize):
        chunk = rows[i : i + chunksize]
        psycopg2.extras.execute_values(cur, sql, chunk, template=template)
    raw_conn.commit()
    cur.close()


def _get_area_code_to_id(id_type, proprietaire=None):
    """Retourne un dict {area_code: id_area} pour un id_type donné."""
    db = _get_db()
    extra = f"AND proprietaire = '{proprietaire}'" if proprietaire else ""
    rows = db.session.execute(
        text(
            f"SELECT area_code, id_area FROM ref_geo.l_areas_new "
            f"WHERE id_type = {id_type} {extra}"
        )
    ).fetchall()
    return {r[0]: r[1] for r in rows}


# ---------------------------------------------------------------------------
# Étape 0 — Sauvegarde du type de déclaration
# ---------------------------------------------------------------------------


def step_save_declaration_types():
    LOG.info("Étape 0 : sauvegarde type_declaration dans t_declarations")
    print("Étape 0 : sauvegarde type_declaration dans t_declarations")
    db = _get_db()
    if not _column_exists("oeasc_declarations", "t_declarations", "type_declaration"):
        db.session.execute(
            text(
                "ALTER TABLE oeasc_declarations.t_declarations "
                "ADD COLUMN IF NOT EXISTS type_declaration TEXT"
            )
        )
    db.session.execute(text("""
        UPDATE oeasc_declarations.t_declarations d
        SET type_declaration = CASE
            WHEN f.b_statut_public = TRUE  AND f.b_document = TRUE  THEN 'onf'
            WHEN f.b_statut_public = FALSE AND f.b_document = TRUE  THEN 'dgd'
            WHEN f.b_statut_public = FALSE AND f.b_document = FALSE THEN 'ss_document_prive'
            WHEN f.b_statut_public = TRUE  AND f.b_document = FALSE THEN 'ss_document_public'
        END
        FROM oeasc_forets.t_forets f
        WHERE d.id_foret = f.id_foret
        AND d.type_declaration IS NULL
    """))
    db.session.commit()
    LOG.info("  type_declaration rempli.")

    # Suppression des forêts privées sans déclaration — elles n'ont pas de polygone
    # et ne peuvent pas être reconstruites lors du refresh.
    result = db.session.execute(text("""
        DELETE FROM oeasc_forets.t_forets
        WHERE b_document = FALSE
        AND NOT EXISTS (
            SELECT 1 FROM oeasc_declarations.t_declarations d
            WHERE d.id_foret = t_forets.id_foret
        )
        RETURNING id_foret, nom_foret
    """))
    deleted = result.fetchall()
    if deleted:
        for row in deleted:
            LOG.info(
                f"  Forêt ss_document supprimée : id_foret={row[0]} nom={row[1]!r}"
            )
        LOG.info(
            f"  {len(deleted)} forêt(s) ss_document sans déclaration supprimée(s)."
        )
        _report["anomalies"].append(
            f"[Étape 0] {len(deleted)} forêt(s) ss_document sans déclaration supprimée(s) : "
            + ", ".join(f"{r[1]!r} (id={r[0]})" for r in deleted)
        )
    _report["volumes"]["forets_ss_doc_supprimees"] = len(deleted)
    db.session.commit()


# ---------------------------------------------------------------------------
# Étape 1 — Création de l_areas_new
# ---------------------------------------------------------------------------


def step_create_l_areas_new():
    LOG.info("Étape 1 : création de ref_geo.l_areas_new")
    print("Étape 1 : création de ref_geo.l_areas_new")
    db = _get_db()
    # Nettoyage d'une éventuelle table résiduelle d'une exécution précédente
    db.session.execute(text("DROP TABLE IF EXISTS ref_geo.l_areas_new CASCADE"))
    db.session.execute(text("DROP SEQUENCE IF EXISTS ref_geo.l_areas_new_id_area_seq"))
    db.session.commit()
    db.session.execute(
        text("CREATE TABLE ref_geo.l_areas_new " "(LIKE ref_geo.l_areas INCLUDING ALL)")
    )
    db.session.execute(text("CREATE SEQUENCE ref_geo.l_areas_new_id_area_seq"))
    db.session.execute(
        text(
            "ALTER TABLE ref_geo.l_areas_new "
            "ALTER COLUMN id_area SET DEFAULT nextval('ref_geo.l_areas_new_id_area_seq')"
        )
    )
    # LIKE INCLUDING ALL ne copie pas les FK mais copie les check constraints.
    # On retire la FK copiée si elle existe.
    db.session.execute(
        text(
            "ALTER TABLE ref_geo.l_areas_new "
            "DROP CONSTRAINT IF EXISTS fk_l_areas_id_type"
        )
    )
    if not _column_exists("ref_geo", "l_areas_new", "proprietaire"):
        db.session.execute(
            text(
                "ALTER TABLE ref_geo.l_areas_new ADD COLUMN proprietaire TEXT DEFAULT NULL"
            )
        )
    db.session.commit()
    LOG.info("  l_areas_new créée.")


# ---------------------------------------------------------------------------
# Étape 2 — Création de t_forets_new
# ---------------------------------------------------------------------------


def step_create_t_forets_new():
    LOG.info("Étape 2 : création de oeasc_forets.t_forets_new")
    print("Étape 2 : création de oeasc_forets.t_forets_new")
    db = _get_db()
    # Ces colonnes n'existent dans t_forets qu'après un premier refresh réussi
    # (elles sont ajoutées via t_forets_new et promues lors du swap).
    # Sur une base restaurée avant ce refresh, elles sont absentes — on les ajoute
    # à t_forets AVANT le CREATE TABLE LIKE pour que t_forets_new les hérite.
    for col_def in [
        "id_area INTEGER",
        "nom_proprietaire CHARACTER VARYING(256)",
        "adresse_proprietaire CHARACTER VARYING(256)",
        "cp_proprietaire CHARACTER VARYING(10)",
        "commune_proprietaire CHARACTER VARYING(100)",
        "email_proprietaire CHARACTER VARYING(250)",
        "tel_proprietaire CHARACTER VARYING(20)",
        "id_nomenclature_proprietaire_type INTEGER",
        "id_declarant INTEGER",
    ]:
        col_name = col_def.split()[0]
        if not _column_exists("oeasc_forets", "t_forets", col_name):
            db.session.execute(
                text(f"ALTER TABLE oeasc_forets.t_forets ADD COLUMN {col_def}")
            )
    db.session.commit()
    db.session.execute(text("DROP TABLE IF EXISTS oeasc_forets.t_forets_new CASCADE"))
    db.session.execute(
        text("DROP SEQUENCE IF EXISTS oeasc_forets.t_forets_new_id_foret_seq")
    )
    db.session.commit()
    db.session.execute(
        text(
            "CREATE TABLE oeasc_forets.t_forets_new "
            "(LIKE oeasc_forets.t_forets INCLUDING ALL)"
        )
    )
    db.session.execute(text("CREATE SEQUENCE oeasc_forets.t_forets_new_id_foret_seq"))
    db.session.execute(
        text(
            "ALTER TABLE oeasc_forets.t_forets_new "
            "ALTER COLUMN id_foret SET DEFAULT nextval('oeasc_forets.t_forets_new_id_foret_seq')"
        )
    )
    # Colonne temporaire pour tracer la correspondance old_id_foret → new_id_foret
    # (code_foret peut être NULL ou vide pour certaines forêts ss_document)
    db.session.execute(
        text("ALTER TABLE oeasc_forets.t_forets_new ADD COLUMN old_id_foret INTEGER")
    )
    # Copie des forêts sans document avec nouveaux ids (séquence repart de 1)
    db.session.execute(text("""
        INSERT INTO oeasc_forets.t_forets_new
            (id_proprietaire, b_statut_public, b_document, nom_foret, code_foret, label_foret,
             surface_renseignee, surface_calculee, id_area,
             nom_proprietaire, adresse_proprietaire, cp_proprietaire, commune_proprietaire,
             email_proprietaire, tel_proprietaire, id_nomenclature_proprietaire_type, id_declarant,
             old_id_foret)
        SELECT
            id_proprietaire, b_statut_public, b_document, nom_foret, code_foret, label_foret,
            surface_renseignee, surface_calculee, id_area,
            nom_proprietaire, adresse_proprietaire, cp_proprietaire, commune_proprietaire,
            email_proprietaire, tel_proprietaire, id_nomenclature_proprietaire_type, id_declarant,
            id_foret
        FROM oeasc_forets.t_forets WHERE b_document = FALSE
    """))
    db.session.commit()

    # Copier les polygones des forêts sans document dans l_areas_new avec de nouveaux IDs.
    # On passe par une colonne temporaire _old_id_area pour conserver la correspondance
    # old id_area → new id_area, puis on met à jour t_forets_new.id_area en conséquence.
    db.session.execute(
        text(
            "ALTER TABLE ref_geo.l_areas_new ADD COLUMN IF NOT EXISTS _old_id_area INTEGER"
        )
    )
    db.session.execute(text(f"""
        INSERT INTO ref_geo.l_areas_new
            (id_type, area_name, area_code, source, enable,
             meta_create_date, meta_update_date, geom, geom_4326, centroid, comment, _old_id_area)
        SELECT la.id_type, la.area_name, la.area_code, la.source, la.enable,
            la.meta_create_date, la.meta_update_date, la.geom, la.geom_4326, la.centroid,
            la.comment, la.id_area
        FROM ref_geo.l_areas la
        WHERE la.id_area IN (
            SELECT id_area FROM oeasc_forets.t_forets_new WHERE b_document = FALSE
        )
    """))
    db.session.execute(text(f"""
        UPDATE oeasc_forets.t_forets_new fn
        SET id_area = lan.id_area
        FROM ref_geo.l_areas_new lan
        WHERE lan._old_id_area = fn.id_area AND fn.b_document = FALSE
    """))
    db.session.execute(
        text("ALTER TABLE ref_geo.l_areas_new DROP COLUMN IF EXISTS _old_id_area")
    )
    db.session.commit()

    # Pour les forêts ss_document sans id_area (pas de polygone dans l_areas),
    # construire le polygone par union des géométries des déclarations associées.
    db.session.execute(text(f"""
        INSERT INTO ref_geo.l_areas_new
            (id_type, area_name, area_code, source, enable, meta_create_date,
             geom, geom_4326, centroid)
        SELECT
            {ID_TYPE_FORET_PRIVE},
            COALESCE(NULLIF(TRIM(fn.nom_foret), ''), 'Forêt privée ' || fn.old_id_foret::text),
            'FORET_PRIVE_' || fn.old_id_foret::text,
            'OEASC', TRUE, now(),
            ST_Multi(ST_Union(d.geom)),
            ST_Multi(ST_Union(d.geom_4326)),
            ST_Centroid(ST_Union(d.geom))
        FROM oeasc_forets.t_forets_new fn
        JOIN oeasc_declarations.t_declarations d ON d.id_foret = fn.old_id_foret
        WHERE fn.b_document = FALSE
        AND fn.id_area IS NULL
        AND d.geom IS NOT NULL
        GROUP BY fn.id_foret, fn.old_id_foret, fn.nom_foret
        HAVING ST_Union(d.geom) IS NOT NULL
    """))
    db.session.execute(text(f"""
        UPDATE oeasc_forets.t_forets_new fn
        SET id_area = lan.id_area,
            surface_calculee = ROUND((ST_Area(lan.geom) / 10000)::numeric, 4)
        FROM ref_geo.l_areas_new lan
        WHERE lan.area_code = 'FORET_PRIVE_' || fn.old_id_foret::text
        AND fn.b_document = FALSE
        AND fn.id_area IS NULL
    """))
    db.session.commit()

    n = db.session.execute(
        text("SELECT count(*) FROM oeasc_forets.t_forets_new")
    ).scalar()
    n_with_area = db.session.execute(
        text(
            "SELECT count(*) FROM oeasc_forets.t_forets_new WHERE b_document=FALSE AND id_area IS NOT NULL"
        )
    ).scalar()
    n_without = db.session.execute(
        text(
            "SELECT count(*) FROM oeasc_forets.t_forets_new WHERE b_document=FALSE AND id_area IS NULL"
        )
    ).scalar()
    LOG.info(f"  t_forets_new créée avec {n} forêts sans document (nouveaux ids).")
    LOG.info(
        f"  Forêts ss_document : {n_with_area} avec polygone, {n_without} sans polygone (pas de déclaration géolocalisée)."
    )


# ---------------------------------------------------------------------------
# Étape 3 — Sauvegarde des areas fixes (323, 324, 325, 326)
# ---------------------------------------------------------------------------


def step_save_fixed_areas():
    LOG.info("Étape 3 : copie des areas fixes (OEASC, PNC cœur, adhésion, secteurs)")
    print("Étape 3 : copie des areas fixes (OEASC, PNC cœur, adhésion, secteurs)")
    db = _get_db()
    id_types_str = ",".join(str(t) for t in FIXED_ID_TYPES)
    db.session.execute(text(f"""
        INSERT INTO ref_geo.l_areas_new
            (id_area, id_type, area_name, area_code, source, enable,
             meta_create_date, meta_update_date, geom, geom_4326, centroid,
             comment, proprietaire)
        SELECT
            id_area, id_type, area_name, area_code, source, enable,
            meta_create_date, meta_update_date, geom, geom_4326, centroid,
            comment, 'FIXE'
        FROM ref_geo.l_areas
        WHERE id_type IN ({id_types_str})
        ON CONFLICT DO NOTHING
    """))
    db.session.execute(
        text(
            "SELECT setval('ref_geo.l_areas_new_id_area_seq', "
            "(SELECT MAX(id_area) FROM ref_geo.l_areas_new))"
        )
    )
    db.session.commit()
    n = db.session.execute(text("SELECT count(*) FROM ref_geo.l_areas_new")).scalar()
    LOG.info(f"  {n} areas fixes copiées.")


# ---------------------------------------------------------------------------
# Étape 4a — Communes
# ---------------------------------------------------------------------------


def step_load_communes():
    LOG.info("Étape 4a : chargement des communes depuis communes_aoa.gpkg")
    print("Étape 4a : chargement des communes depuis communes_aoa.gpkg")
    oeasc_geom = _get_oeasc_geom()
    gdf = gpd.read_file(GPKG_COMMUNES)
    gdf = _filter_by_oeasc(gdf, oeasc_geom)
    gdf_4326 = gdf.to_crs(epsg=4326)
    LOG.info(f"  {len(gdf)} communes dans le périmètre OEASC")

    now = datetime.now()
    rows = []
    for i in range(len(gdf)):
        r = gdf.iloc[i]
        geom = _to_multi(r.geometry)
        geom4326 = _to_multi(gdf_4326.iloc[i].geometry)
        rows.append(
            (
                ID_TYPE_COMMUNE,
                str(r["nom"]),
                str(r["code_siren"]),
                "OEASC",
                True,
                now,
                _wkt(geom),
                _wkt(geom4326),
                wkt_dumps(geom.centroid),
                "COMMUNE",
            )
        )

    raw_conn = _raw_conn()
    _bulk_insert_areas(raw_conn, rows)
    raw_conn.close()

    # Mise à jour de communes_aoa
    _update_communes_aoa(gdf)
    LOG.info(f"  {len(rows)} communes insérées.")
    _report["volumes"]["communes"] = len(rows)


def _update_communes_aoa(gdf):
    print("  Mise à jour de ref_geo.communes_aoa")
    db = _get_db()
    db.session.execute(text("TRUNCATE ref_geo.communes_aoa"))
    db.session.commit()

    raw_conn = _raw_conn()
    cur = raw_conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sql = """
        INSERT INTO ref_geo.communes_aoa
            (id, geom, fid, insee_com, nom, insee_dep,
             coeur, aire_adhes, aoa, massif, population,
             siren_epci, nom_ccom, surface_ha, date_creat, date_maj,
             code_siren, code_post)
        VALUES %s
        ON CONFLICT DO NOTHING
    """
    template = (
        "(%s, ST_GeomFromText(%s, 2154), %s, %s, %s, %s, "
        "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    )
    rows = []
    for i in range(len(gdf)):
        r = gdf.iloc[i]
        geom = _to_multi(r.geometry)
        rows.append(
            (
                str(r["code_siren"]),
                _wkt(geom),
                i,  # fid bigint — on utilise l'index car id_municipality est une chaîne
                str(r.get("insee_com") or ""),
                str(r.get("nom") or ""),
                str(r.get("insee_dep") or ""),
                int(r["zc"]) if r.get("zc") is not None else None,
                int(r["aa"]) if r.get("aa") is not None else None,
                int(r["aoa"]) if r.get("aoa") is not None else None,
                str(r.get("massif") or ""),
                int(r["population"]) if r.get("population") is not None else None,
                str(r.get("siren_epci") or ""),
                str(r.get("nom") or ""),  # nom_ccom ← nom (meilleure approx)
                int(r["surface_ha"]) if r.get("surface_ha") is not None else None,
                str(r["date_creat"]) if r.get("date_creat") else now_str,
                str(r["date_maj"]) if r.get("date_maj") else now_str,
                str(r.get("code_siren") or ""),
                str(r.get("code_post") or ""),
            )
        )
    psycopg2.extras.execute_values(cur, sql, rows, template=template, page_size=200)
    raw_conn.commit()
    cur.close()
    raw_conn.close()


# ---------------------------------------------------------------------------
# Étape 4b — Cadastres
# ---------------------------------------------------------------------------


def step_load_cadastres():
    LOG.info("Étape 4b : chargement des cadastres depuis cadastre_pec.gpkg")
    print("Étape 4b : chargement des cadastres depuis cadastre_pec.gpkg")
    oeasc_geom = _get_oeasc_geom()
    gdf = gpd.read_file(GPKG_CADASTRE)
    gdf = _filter_by_oeasc(gdf, oeasc_geom)
    gdf_4326 = gdf.to_crs(epsg=4326)
    LOG.info(f"  {len(gdf)} cadastres dans le périmètre OEASC")

    now = datetime.now()
    rows = []
    for i in range(len(gdf)):
        r = gdf.iloc[i]
        geom = _to_multi(r.geometry)
        geom4326 = _to_multi(gdf_4326.iloc[i].geometry)
        area_code = str(r["id_parcelle"])
        area_name = f"{r['insee_com']}-{r['section']}-{r['num_parc']}"
        rows.append(
            (
                ID_TYPE_CADASTRE,
                area_name,
                area_code,
                "OEASC",
                True,
                now,
                _wkt(geom),
                _wkt(geom4326),
                wkt_dumps(geom.centroid),
                str(r.get("proprietaire") or ""),
            )
        )

    raw_conn = _raw_conn()
    _bulk_insert_areas(raw_conn, rows)
    _create_gist_index(raw_conn)
    raw_conn.close()
    LOG.info(f"  {len(rows)} cadastres insérés.")
    _report["volumes"]["cadastres"] = len(rows)


# ---------------------------------------------------------------------------
# Étape 4c — Sections cadastrales
# ---------------------------------------------------------------------------


def step_build_sections():
    LOG.info("Étape 4c : construction des sections cadastrales par agrégation")
    print("Étape 4c : construction des sections cadastrales par agrégation")
    oeasc_geom = _get_oeasc_geom()
    gdf = gpd.read_file(GPKG_CADASTRE)
    gdf = _filter_by_oeasc(gdf, oeasc_geom)

    # Groupe par code_section = id_parcelle[:11]
    gdf["_sec_code"] = gdf["id_parcelle"].str[:11]

    now = datetime.now()
    rows = []
    for sec_code, grp in gdf.groupby("_sec_code"):
        union_geom = _to_multi(grp.geometry.unary_union)
        geom4326 = _to_multi(gpd.GeoSeries([union_geom], crs=2154).to_crs(4326).iloc[0])
        nom_com = str(grp.iloc[0]["nom_com"]).upper()
        sec_raw = str(grp.iloc[0]["section"])
        area_name = f"{nom_com}-{sec_raw}"
        rows.append(
            (
                ID_TYPE_SECTION,
                area_name,
                sec_code,
                "OEASC",
                True,
                now,
                _wkt(union_geom),
                _wkt(geom4326),
                wkt_dumps(union_geom.centroid),
                "SECTION",
            )
        )

    raw_conn = _raw_conn()
    _bulk_insert_areas(raw_conn, rows)
    raw_conn.close()
    LOG.info(f"  {len(rows)} sections cadastrales créées.")
    _report["volumes"]["sections"] = len(rows)


# ---------------------------------------------------------------------------
# Étape 4d — Forêts DGD
# ---------------------------------------------------------------------------


def step_load_foret_dgd():
    LOG.info("Étape 4d : chargement des forêts DGD depuis data_new.gpkg")
    print("Étape 4d : chargement des forêts DGD depuis data_new.gpkg")
    import fiona

    oeasc_geom = _get_oeasc_geom()
    layers = fiona.listlayers(GPKG_DGD)
    gdf = gpd.read_file(GPKG_DGD, layer=layers[0])
    gdf = _filter_by_oeasc(gdf, oeasc_geom)
    gdf_4326 = gdf.to_crs(epsg=4326)
    LOG.info(f"  {len(gdf)} forêts DGD dans le périmètre OEASC")

    now = datetime.now()
    area_rows = []
    area_codes = []
    for i in range(len(gdf)):
        r = gdf.iloc[i]
        geom = _to_multi(r.geometry)
        geom4326 = _to_multi(gdf_4326.iloc[i].geometry)
        cx = int(round(geom.centroid.x / 10) * 10)
        cy = int(round(geom.centroid.y / 10) * 10)
        area_code = f"DGD_{cx}_{cy}"
        area_name = str(r["Fornom"]).upper()
        area_codes.append(area_code)
        area_rows.append(
            (
                ID_TYPE_DGD,
                area_name,
                area_code,
                "OEASC",
                True,
                now,
                _wkt(geom),
                _wkt(geom4326),
                wkt_dumps(geom.centroid),
                "DGD",
            )
        )

    raw_conn = _raw_conn()
    _bulk_insert_areas(raw_conn, area_rows)
    raw_conn.close()

    # Récupère les id_area par area_code (ordre non garanti par RETURNING)
    code_to_id = _get_area_code_to_id(ID_TYPE_DGD, "DGD")

    # Insertion dans t_forets_new
    raw_conn2 = _raw_conn()
    cur = raw_conn2.cursor()
    sql_foret = """
        INSERT INTO oeasc_forets.t_forets_new
            (b_document, b_statut_public, nom_foret, label_foret, code_foret,
             surface_renseignee, surface_calculee, nom_proprietaire,
             adresse_proprietaire, cp_proprietaire, commune_proprietaire,
             id_nomenclature_proprietaire_type, id_area)
        VALUES %s
    """
    data = []
    for i in range(len(gdf)):
        r = gdf.iloc[i]
        geom = _to_multi(r.geometry)
        area_code = area_codes[i]
        area_name = area_rows[i][1]
        surf_calc = round(geom.area / 10000, 4)
        adresse = " ".join(
            filter(
                None,
                [
                    str(r.get("Perlig1") or ""),
                    str(r.get("Perlig2") or ""),
                    str(r.get("Perlig3") or ""),
                ],
            )
        ).strip()[:255]
        data.append(
            (
                True,
                False,
                area_name,
                f"{area_name.lower()}-{r.get('Procpoid') or ''}",
                area_code,
                float(r["surface"]) if r.get("surface") is not None else None,
                surf_calc,
                str(r.get("proprio") or ""),
                adresse,
                str(r.get("Percp") or "")[:5],
                str(r.get("Perbur") or "")[:255],
                NOMENCLATURE_PT_PRI,
                code_to_id.get(area_code),
            )
        )
    psycopg2.extras.execute_values(cur, sql_foret, data, page_size=200)
    raw_conn2.commit()
    cur.close()
    raw_conn2.close()
    LOG.info(f"  {len(data)} forêts DGD insérées dans l_areas_new et t_forets_new.")
    _report["volumes"]["forets_dgd"] = len(data)


# ---------------------------------------------------------------------------
# Étape 4e — Forêts ONF
# ---------------------------------------------------------------------------


def step_load_foret_onf():
    LOG.info("Étape 4e : chargement des forêts ONF")
    print("Étape 4e : chargement des forêts ONF")
    oeasc_geom = _get_oeasc_geom()
    gdf = gpd.read_file(GPKG_FORET_ONF)
    gdf = _filter_by_oeasc(gdf, oeasc_geom)
    gdf_4326 = gdf.to_crs(epsg=4326)
    LOG.info(f"  {len(gdf)} forêts ONF dans le périmètre OEASC")

    now = datetime.now()
    area_rows = []
    area_codes = []
    for i in range(len(gdf)):
        r = gdf.iloc[i]
        geom = _to_multi(r.geometry)
        geom4326 = _to_multi(gdf_4326.iloc[i].geometry)
        area_code = str(r["iidtn_frt"])
        area_name = str(r["llib_frt"])
        area_codes.append(area_code)
        area_rows.append(
            (
                ID_TYPE_FORET_ONF,
                area_name,
                area_code,
                "OEASC",
                True,
                now,
                _wkt(geom),
                _wkt(geom4326),
                wkt_dumps(geom.centroid),
                "FORET_ONF",
            )
        )

    raw_conn = _raw_conn()
    _bulk_insert_areas(raw_conn, area_rows)
    raw_conn.close()

    code_to_id = _get_area_code_to_id(ID_TYPE_FORET_ONF, "FORET_ONF")

    raw_conn2 = _raw_conn()
    cur = raw_conn2.cursor()
    sql_foret = """
        INSERT INTO oeasc_forets.t_forets_new
            (b_document, b_statut_public, nom_foret, label_foret, code_foret,
             surface_renseignee, surface_calculee, nom_proprietaire,
             id_nomenclature_proprietaire_type, id_area)
        VALUES %s
    """
    data = []
    for i in range(len(gdf)):
        r = gdf.iloc[i]
        geom = _to_multi(r.geometry)
        area_code = area_codes[i]
        surf_calc = round(geom.area / 10000, 4)
        data.append(
            (
                True,
                True,
                str(r["llib_frt"]),
                str(r["llib_frt"]),
                area_code,
                surf_calc,
                surf_calc,
                "ONF",
                NOMENCLATURE_PT_E,
                code_to_id.get(area_code),
            )
        )
    psycopg2.extras.execute_values(cur, sql_foret, data, page_size=200)
    raw_conn2.commit()
    cur.close()
    raw_conn2.close()
    LOG.info(f"  {len(data)} forêts ONF insérées dans l_areas_new et t_forets_new.")
    _report["volumes"]["forets_onf"] = len(data)


# ---------------------------------------------------------------------------
# Étape 4f — Parcelles ONF
# ---------------------------------------------------------------------------


def step_load_parcelle_onf():
    LOG.info("Étape 4f : chargement des parcelles ONF")
    print("Étape 4f : chargement des parcelles ONF")
    oeasc_geom = _get_oeasc_geom()
    gdf = gpd.read_file(GPKG_PARCELLE_ONF)
    gdf = _filter_by_oeasc(gdf, oeasc_geom)
    gdf_4326 = gdf.to_crs(epsg=4326)
    LOG.info(f"  {len(gdf)} parcelles ONF dans le périmètre OEASC")

    now = datetime.now()
    rows = []
    for i in range(len(gdf)):
        r = gdf.iloc[i]
        geom = _to_multi(r.geometry)
        geom4326 = _to_multi(gdf_4326.iloc[i].geometry)
        cinse_dep = str(r["cinse_dep"])
        iidtn_frt = str(r["iidtn_frt"])
        ccod_prf = str(r["ccod_prf"])
        area_code = f"{cinse_dep}-{iidtn_frt}-{ccod_prf}"
        rows.append(
            (
                ID_TYPE_PARCELLE_ONF,
                ccod_prf,
                area_code,
                "OEASC",
                True,
                now,
                _wkt(geom),
                _wkt(geom4326),
                wkt_dumps(geom.centroid),
                "PARCELLE_ONF",
            )
        )
        # Parcelle unique dans la forêt : on crée aussi l'UG correspondante
        if ccod_prf == "U":
            rows.append(
                (
                    ID_TYPE_UG_ONF,
                    f"{ccod_prf}-1",
                    f"{area_code}-1",
                    "OEASC",
                    True,
                    now,
                    _wkt(geom),
                    _wkt(geom4326),
                    wkt_dumps(geom.centroid),
                    "UG_ONF",
                )
            )

    raw_conn = _raw_conn()
    _bulk_insert_areas(raw_conn, rows)
    raw_conn.close()
    n_parcelles = sum(1 for r in rows if r[0] == ID_TYPE_PARCELLE_ONF)
    n_ug_u = sum(1 for r in rows if r[0] == ID_TYPE_UG_ONF)
    LOG.info(f"  {n_parcelles} parcelles ONF insérées, {n_ug_u} UG 'U' créées.")
    _report["volumes"]["parcelles_onf"] = n_parcelles
    _report["volumes"]["ug_u_creees"] = n_ug_u


# ---------------------------------------------------------------------------
# Étape 4g — Unités de gestion ONF
# ---------------------------------------------------------------------------

_CACT_TO_DEP = {8720: 48, 8765: 30, 8775: 12}


def step_load_ug_onf():
    LOG.info("Étape 4g : chargement des unités de gestion ONF")
    print("Étape 4g : chargement des unités de gestion ONF")
    oeasc_geom = _get_oeasc_geom()
    gdf = gpd.read_file(GPKG_UG_ONF)
    # Exclure les UG dont CCOD_PRF n'est pas un entier (parcelles "U" gérées en 4f)
    gdf = gdf[gdf["CCOD_PRF"].apply(lambda x: str(x).strip().isdigit())]
    gdf = _filter_by_oeasc(gdf, oeasc_geom)
    gdf_4326 = gdf.to_crs(epsg=4326)
    LOG.info(f"  {len(gdf)} UG ONF dans le périmètre OEASC")

    now = datetime.now()
    rows = []
    for i in range(len(gdf)):
        r = gdf.iloc[i]
        geom = _to_multi(r.geometry)
        geom4326 = _to_multi(gdf_4326.iloc[i].geometry)
        cinse_dep = _CACT_TO_DEP.get(int(r["CCOD_CACT"]), int(r["CCOD_CACT"]))
        iidtn_frt = str(r["IIDTN_FRT"])
        ccod_prf = str(r["CCOD_PRF"])
        ccod_ug = str(r["CCOD_UG"])
        area_code = f"{cinse_dep}-{iidtn_frt}-{ccod_prf}-{ccod_ug}"
        area_name = f"{ccod_prf}-{ccod_ug}"
        rows.append(
            (
                ID_TYPE_UG_ONF,
                area_name,
                area_code,
                "OEASC",
                True,
                now,
                _wkt(geom),
                _wkt(geom4326),
                wkt_dumps(geom.centroid),
                "UG_ONF",
            )
        )

    raw_conn = _raw_conn()
    _bulk_insert_areas(raw_conn, rows)
    _create_gist_index(raw_conn)
    raw_conn.close()
    LOG.info(f"  {len(rows)} UG ONF insérées.")
    _report["volumes"]["ug_onf"] = len(rows)


# ---------------------------------------------------------------------------
# Étape 4h — Reprise des infos propriétaire ONF depuis t_forets
# ---------------------------------------------------------------------------


def step_copy_onf_proprietaire():
    LOG.info(
        "Étape 4h : reprise des infos propriétaire ONF (b_document=true, b_statut_public=true)"
    )
    print(
        "Étape 4h : reprise des infos propriétaire ONF (b_document=true, b_statut_public=true)"
    )
    db = _get_db()

    # Correspondance spatiale : forêt nouvelle ↔ ancienne si chevauchement ≥ 90 %
    # (le code_foret a changé de format entre l'ancienne et la nouvelle version des données)
    # La sous-requête évite de référencer fn dans le FROM (interdit en PostgreSQL).
    result = db.session.execute(text(f"""
        UPDATE oeasc_forets.t_forets_new fn
        SET
            id_proprietaire                   = match.id_proprietaire,
            nom_proprietaire                  = match.nom_proprietaire,
            adresse_proprietaire              = match.adresse_proprietaire,
            cp_proprietaire                   = match.cp_proprietaire,
            commune_proprietaire              = match.commune_proprietaire,
            email_proprietaire                = match.email_proprietaire,
            tel_proprietaire                  = match.tel_proprietaire,
            id_nomenclature_proprietaire_type = match.id_nomenclature_proprietaire_type,
            id_declarant                      = match.id_declarant
        FROM (
            SELECT
                fn2.id_foret AS new_id_foret,
                f.id_proprietaire,
                f.nom_proprietaire,
                f.adresse_proprietaire,
                f.cp_proprietaire,
                f.commune_proprietaire,
                f.email_proprietaire,
                f.tel_proprietaire,
                f.id_nomenclature_proprietaire_type,
                f.id_declarant
            FROM oeasc_forets.t_forets_new fn2
            JOIN ref_geo.l_areas_new la_new ON la_new.id_area = fn2.id_area
                AND la_new.id_type = {ID_TYPE_FORET_ONF}
            JOIN ref_geo.l_areas la_old ON (
                la_old.id_type = {ID_TYPE_FORET_ONF}
                AND ST_Intersects(la_new.geom, la_old.geom)
                AND ST_Area(ST_Intersection(la_new.geom, la_old.geom))
                    / NULLIF(ST_Area(la_new.geom), 0) >= {MATCH_THRESHOLD}
            )
            JOIN oeasc_forets.t_forets f ON f.id_area = la_old.id_area
                AND f.b_document = TRUE AND f.b_statut_public = TRUE
            WHERE fn2.b_document = TRUE AND fn2.b_statut_public = TRUE
        ) match
        WHERE fn.id_foret = match.new_id_foret
    """))
    db.session.commit()
    n = result.rowcount
    LOG.info(
        f"  {n} forêt(s) ONF mises à jour avec les infos propriétaire de t_forets (correspondance spatiale)."
    )

    # Forêts sans correspondance : on s'assure que nom_proprietaire reste "ONF"
    db.session.execute(text("""
        UPDATE oeasc_forets.t_forets_new
        SET nom_proprietaire = 'ONF'
        WHERE b_document = TRUE AND b_statut_public = TRUE
        AND id_proprietaire IS NULL
        AND (nom_proprietaire IS NULL OR nom_proprietaire != 'ONF')
    """))
    db.session.commit()

    missing = db.session.execute(text("""
        SELECT id_foret, nom_foret, code_foret FROM oeasc_forets.t_forets_new
        WHERE b_document = TRUE AND b_statut_public = TRUE
        AND id_proprietaire IS NULL
        ORDER BY nom_foret
    """)).fetchall()
    n_missing = len(missing)
    if n_missing:
        for row in missing:
            LOG.warning(
                f"  Forêt ONF sans correspondance spatiale : id_foret={row[0]} "
                f"nom={row[1]!r} code_foret={row[2]!r}"
            )
        LOG.warning(
            f"  ATTENTION : {n_missing} forêt(s) ONF sans correspondance spatiale "
            f"dans t_forets — infos propriétaire conservées à 'ONF'."
        )
        _report["anomalies"].append(
            f"[Étape 4h] {n_missing} forêt(s) ONF sans correspondance spatiale dans t_forets "
            f"(infos propriétaire conservées à 'ONF') : "
            + ", ".join(f"{r[1]!r} (id={r[0]})" for r in missing)
        )


# ---------------------------------------------------------------------------
# Étape 5 — Construction de cor_area_intersect
# ---------------------------------------------------------------------------


def step_build_cor_area_intersect():
    LOG.info("Étape 5 : construction de cor_area_intersect")
    print("Étape 5 : construction de cor_area_intersect")
    db = _get_db()
    # On recrée toujours la table depuis zéro (DROP + CREATE) pour éviter
    # les problèmes de FK et de base restaurée sans cette table.
    db.session.execute(text("DROP TABLE IF EXISTS ref_geo.cor_area_intersect"))
    db.session.execute(text("""
        CREATE TABLE ref_geo.cor_area_intersect (
            id                      SERIAL PRIMARY KEY,
            id_parcelle             INTEGER,
            id_type_parcelle        INTEGER,
            id_section_cadastrale   INTEGER,
            id_commune              INTEGER,
            id_foret_dgd            INTEGER,
            id_foret_onf            INTEGER,
            id_foret_prive          INTEGER,
            id_parcelle_onf         INTEGER,
            id_secteur              INTEGER,
            in_coeur                BOOLEAN,
            in_aire_adhesion_pnc    BOOLEAN,
            in_oeasc                BOOLEAN
        )
    """))
    db.session.commit()

    # Index spatial sur l_areas_new pour accélérer les jointures
    raw_conn = _raw_conn()
    cur = raw_conn.cursor()
    cur.execute(
        "CREATE INDEX IF NOT EXISTS ix_l_areas_new_geom_build "
        "ON ref_geo.l_areas_new USING GIST (geom)"
    )
    cur.execute(
        "CREATE INDEX IF NOT EXISTS ix_l_areas_new_id_type "
        "ON ref_geo.l_areas_new (id_type)"
    )
    raw_conn.commit()
    cur.close()
    raw_conn.close()

    # Corriger les géométries invalides avant les opérations d'intersection
    n_invalid = db.session.execute(
        text("SELECT count(*) FROM ref_geo.l_areas_new WHERE NOT ST_IsValid(geom)")
    ).scalar()
    if n_invalid:
        LOG.warning(
            f"  {n_invalid} géométrie(s) invalide(s) dans l_areas_new — correction ST_MakeValid"
        )
        _report["anomalies"].append(
            f"[Étape 5] {n_invalid} géométrie(s) invalide(s) dans l_areas_new corrigées par ST_MakeValid"
        )
        db.session.execute(
            text(
                "UPDATE ref_geo.l_areas_new "
                "SET geom = ST_Multi(ST_CollectionExtract(ST_MakeValid(geom), 3)) "
                "WHERE NOT ST_IsValid(geom)"
            )
        )
        db.session.commit()

    db.session.execute(text(f"""
        INSERT INTO ref_geo.cor_area_intersect
            (id_parcelle, id_type_parcelle, id_section_cadastrale, id_commune,
             id_foret_dgd, id_foret_onf, id_foret_prive, id_parcelle_onf, id_secteur,
             in_coeur, in_aire_adhesion_pnc, in_oeasc)
        SELECT
            p.id_area,
            p.id_type,
            -- section cadastrale (uniquement pour cadastres)
            CASE WHEN p.id_type = {ID_TYPE_CADASTRE} THEN (
                SELECT s.id_area FROM ref_geo.l_areas_new s
                WHERE s.id_type = {ID_TYPE_SECTION}
                AND ST_Intersects(ST_PointOnSurface(p.geom), s.geom)
                ORDER BY ST_Area(ST_Intersection(p.geom, s.geom)) DESC LIMIT 1
            ) END,
            -- commune
            (
                SELECT c.id_area FROM ref_geo.l_areas_new c
                WHERE c.id_type = {ID_TYPE_COMMUNE}
                AND ST_Intersects(ST_PointOnSurface(p.geom), c.geom)
                ORDER BY ST_Area(ST_Intersection(p.geom, c.geom)) DESC LIMIT 1
            ),
            -- forêt DGD (pour cadastres uniquement)
            CASE WHEN p.id_type = {ID_TYPE_CADASTRE} THEN (
                SELECT d.id_area FROM ref_geo.l_areas_new d
                WHERE d.id_type = {ID_TYPE_DGD}
                AND ST_Intersects(p.geom, d.geom)
                ORDER BY ST_Area(ST_Intersection(p.geom, d.geom)) DESC LIMIT 1
            ) END,
            -- forêt ONF
            (
                SELECT f.id_area FROM ref_geo.l_areas_new f
                WHERE f.id_type = {ID_TYPE_FORET_ONF}
                AND ST_Intersects(ST_PointOnSurface(p.geom), f.geom)
                ORDER BY ST_Area(ST_Intersection(p.geom, f.geom)) DESC LIMIT 1
            ),
            -- forêt privée sans document (pour cadastres uniquement)
            CASE WHEN p.id_type = {ID_TYPE_CADASTRE} THEN (
                SELECT fp.id_area FROM ref_geo.l_areas_new fp
                WHERE fp.id_type = {ID_TYPE_FORET_PRIVE}
                AND ST_Intersects(p.geom, fp.geom)
                ORDER BY ST_Area(ST_Intersection(p.geom, fp.geom)) DESC LIMIT 1
            ) END,
            -- parcelle ONF (pour UG ONF uniquement)
            CASE WHEN p.id_type = {ID_TYPE_UG_ONF} THEN (
                SELECT po.id_area FROM ref_geo.l_areas_new po
                WHERE po.id_type = {ID_TYPE_PARCELLE_ONF}
                AND ST_Intersects(ST_PointOnSurface(p.geom), po.geom)
                ORDER BY ST_Area(ST_Intersection(p.geom, po.geom)) DESC LIMIT 1
            ) END,
            -- secteur
            (
                SELECT sec.id_area FROM ref_geo.l_areas_new sec
                WHERE sec.id_type = {ID_TYPE_SECTEUR}
                AND ST_Intersects(ST_PointOnSurface(p.geom), sec.geom)
                ORDER BY ST_Area(ST_Intersection(p.geom, sec.geom)) DESC LIMIT 1
            ),
            -- in_coeur
            EXISTS(SELECT 1 FROM ref_geo.l_areas_new z
                   WHERE z.id_type = {ID_TYPE_COEUR}
                   AND ST_Intersects(p.geom, z.geom)),
            -- in_aire_adhesion_pnc
            EXISTS(SELECT 1 FROM ref_geo.l_areas_new z
                   WHERE z.id_type = {ID_TYPE_ADHESION}
                   AND ST_Intersects(p.geom, z.geom)),
            -- in_oeasc
            EXISTS(SELECT 1 FROM ref_geo.l_areas_new z
                   WHERE z.id_type = {ID_TYPE_OEASC}
                   AND ST_Intersects(p.geom, z.geom))
        FROM ref_geo.l_areas_new p
        WHERE p.id_type IN ({ID_TYPE_CADASTRE}, {ID_TYPE_UG_ONF})
    """))
    db.session.commit()

    _alert_multi_commune()

    n = db.session.execute(
        text("SELECT count(*) FROM ref_geo.cor_area_intersect")
    ).scalar()
    LOG.info(f"  cor_area_intersect remplie avec {n} entrées.")
    _report["volumes"]["cor_area_intersect"] = n


def _alert_multi_commune():
    """Signale les parcelles qui chevauchent plusieurs communes."""
    db = _get_db()
    rows = db.session.execute(text(f"""
        SELECT p.id_area, p.area_code, count(c.id_area) AS nb_communes
        FROM ref_geo.l_areas_new p
        JOIN ref_geo.l_areas_new c ON (
            c.id_type = {ID_TYPE_COMMUNE} AND ST_Intersects(p.geom, c.geom)
        )
        WHERE p.id_type IN ({ID_TYPE_CADASTRE}, {ID_TYPE_UG_ONF})
        GROUP BY p.id_area, p.area_code
        HAVING count(c.id_area) > 1
        LIMIT 20
    """)).fetchall()
    if rows:
        LOG.warning(
            f"  ATTENTION : {len(rows)} parcelle(s) chevauchent plusieurs communes "
            "(on conserve la plus grande intersection) :"
        )
        print(
            "  ATTENTION : certaines parcelles chevauchent plusieurs communes "
            "(on conserve la plus grande intersection) :"
        )
        for r in rows:
            LOG.warning(f"    id_area={r[0]} area_code={r[1]} → {r[2]} communes")
            print(f"    id_area={r[0]} area_code={r[1]} → {r[2]} communes")
        _report["anomalies"].append(
            f"[Étape 5] {len(rows)} parcelle(s) chevauchent plusieurs communes "
            "(correspondance conservée sur la plus grande intersection)"
        )


# ---------------------------------------------------------------------------
# Étape 6 — Mise à jour des déclarations
# ---------------------------------------------------------------------------


def _mark_erreur_refgeo(db, type_declaration):
    """
    Identifie les déclarations d'un type donné dont id_foret n'a pas pu être migré
    vers t_forets_new avec le BON TYPE de forêt, puis :
      - met id_foret à NULL
      - met statut à 999 (Erreur Refgeo)
      - renseigne precision_localisation avec le nom de l'ancienne forêt et ses areas

    Doit être appelé AVANT le swap (t_forets et l_areas sont encore les anciennes tables).

    Le filtre NOT EXISTS vérifie que l'id_foret pointe bien vers une forêt du même type
    (ONF: b_statut_public=TRUE, DGD: b_statut_public=FALSE) dans t_forets_new.
    Sans ce filtre, un id_foret d'une ancienne forêt ONF peut coïncider avec l'id d'une
    nouvelle forêt DGD (les séquences repartent de 1 dans t_forets_new), causant une
    correspondance silencieuse vers le mauvais type.
    """
    if type_declaration == "onf":
        type_filter = "AND fn.b_statut_public = TRUE AND fn.b_document = TRUE"
    elif type_declaration == "dgd":
        type_filter = "AND fn.b_statut_public = FALSE AND fn.b_document = TRUE"
    else:
        type_filter = ""

    unmatched = db.session.execute(
        text(f"""
        SELECT
            d.id_declaration,
            f.nom_foret,
            COALESCE(
                string_agg(
                    la.area_code || ' (' || la.area_name || ')',
                    ', ' ORDER BY la.area_code
                ),
                ''
            ) AS areas_info
        FROM oeasc_declarations.t_declarations d
        JOIN oeasc_forets.t_forets f ON f.id_foret = d._pre_refresh_id_foret
        LEFT JOIN oeasc_declarations.cor_areas_declarations cad
            ON cad.id_declaration = d.id_declaration
        LEFT JOIN ref_geo.l_areas la ON la.id_area = cad.id_area
        WHERE d.type_declaration = :type_decl
        AND d.id_foret IS NOT NULL
        AND d.id_foret = d._pre_refresh_id_foret
        GROUP BY d.id_declaration, f.nom_foret
    """),
        {"type_decl": type_declaration},
    ).fetchall()

    if not unmatched:
        return 0

    for row in unmatched:
        id_decl, nom_foret, areas_info = row
        precision = f"[Erreur RefGeo] Forêt non retrouvée : {nom_foret}"
        if areas_info:
            precision += f" | {areas_info}"
        db.session.execute(
            text("""
            UPDATE oeasc_declarations.t_declarations
            SET id_foret = NULL,
                statut = 999,
                precision_localisation = :precision
            WHERE id_declaration = :id_decl
        """),
            {"precision": precision, "id_decl": id_decl},
        )

    db.session.commit()
    return len(unmatched)


def step_update_declarations():
    LOG.info("Étape 6 : mise à jour des liaisons déclarations ↔ areas")
    print("Étape 6 : mise à jour des liaisons déclarations ↔ areas")
    db = _get_db()
    # Suppression des FK vers l_areas et t_forets :
    # les nouveaux ids viennent de l_areas_new/t_forets_new, seront recréés après le swap.
    for stmt in [
        "ALTER TABLE oeasc_declarations.cor_areas_declarations "
        "DROP CONSTRAINT IF EXISTS fk_cor_areas_declarations_id_area",
        "ALTER TABLE oeasc_declarations.t_declarations "
        "DROP CONSTRAINT IF EXISTS fk_t_declarations_id_foret",
    ]:
        db.session.execute(text(stmt))
    db.session.commit()

    # Colonne temporaire pour détecter les déclarations non mises à jour en step 6.
    # _mark_erreur_refgeo l'utilise pour identifier les déclarations dont id_foret
    # n'a pas changé (= non retrouvées), évitant la confusion avec les nouvelles forêts
    # qui ont le même id numérique par coïncidence (séquences repartant de 1 dans t_forets_new).
    db.session.execute(
        text(
            "ALTER TABLE oeasc_declarations.t_declarations "
            "ADD COLUMN IF NOT EXISTS _pre_refresh_id_foret INTEGER"
        )
    )
    db.session.execute(
        text(
            "UPDATE oeasc_declarations.t_declarations SET _pre_refresh_id_foret = id_foret"
        )
    )
    db.session.commit()

    # 6b : mise à jour id_foret DGD par correspondance spatiale via id_area
    # Les codes DGD changent de format entre anciennes et nouvelles données :
    # on ne peut pas matcher par code_foret. On passe par l_areas (géométrie).
    LOG.info(
        "  6b : mise à jour id_foret pour les déclarations DGD (correspondance spatiale ≥90%)"
    )
    print(
        "  6b : mise à jour id_foret pour les déclarations DGD (correspondance spatiale ≥90%)"
    )
    db.session.execute(text(f"""
        UPDATE oeasc_declarations.t_declarations d
        SET id_foret = fn.id_foret
        FROM oeasc_forets.t_forets f
        JOIN ref_geo.l_areas la_old ON la_old.id_area = f.id_area
        JOIN ref_geo.l_areas_new la_new ON (
            la_new.id_type = {ID_TYPE_DGD}
            AND ST_Intersects(la_old.geom, la_new.geom)
            AND ST_Area(ST_Intersection(la_old.geom, la_new.geom))
                / NULLIF(ST_Area(la_old.geom), 0) >= {MATCH_THRESHOLD}
        )
        JOIN oeasc_forets.t_forets_new fn ON fn.id_area = la_new.id_area
        WHERE d.id_foret = f.id_foret
        AND d.type_declaration = 'dgd'
        AND f.b_document = TRUE
    """))
    db.session.commit()

    # Passage 2 : fallback spatial pour les forêts DGD sans id_area (pas de polygone dans
    # l'ancienne l_areas). Le format area_code des cadastres change entre GPKG successifs,
    # donc on utilise la géométrie des anciennes parcelles pour trouver la nouvelle forêt DGD.
    db.session.execute(text(f"""
        UPDATE oeasc_declarations.t_declarations d
        SET id_foret = match.id_foret
        FROM (
            SELECT DISTINCT ON (d2.id_declaration)
                d2.id_declaration,
                fn.id_foret,
                ST_Area(ST_Intersection(la_cad.geom, la_dgd_new.geom)) AS overlap
            FROM oeasc_declarations.t_declarations d2
            JOIN oeasc_forets.t_forets f2 ON f2.id_foret = d2._pre_refresh_id_foret
                AND f2.b_document = TRUE AND f2.b_statut_public = FALSE
                AND f2.id_area IS NULL
            JOIN oeasc_declarations.cor_areas_declarations cad
                ON cad.id_declaration = d2.id_declaration
            JOIN ref_geo.l_areas la_cad
                ON la_cad.id_area = cad.id_area AND la_cad.id_type = {ID_TYPE_CADASTRE}
            JOIN ref_geo.l_areas_new la_dgd_new
                ON la_dgd_new.id_type = {ID_TYPE_DGD}
                AND ST_Intersects(la_cad.geom, la_dgd_new.geom)
            JOIN oeasc_forets.t_forets_new fn ON fn.id_area = la_dgd_new.id_area
            WHERE d2.type_declaration = 'dgd'
            AND d2.id_foret = d2._pre_refresh_id_foret
            ORDER BY d2.id_declaration, overlap DESC
        ) match
        WHERE d.id_declaration = match.id_declaration
    """))
    db.session.commit()

    n_dgd = db.session.execute(
        text(
            "SELECT count(*) FROM oeasc_declarations.t_declarations d "
            "JOIN oeasc_forets.t_forets_new fn ON fn.id_foret = d.id_foret "
            "WHERE fn.b_statut_public = false AND fn.b_document = true"
        )
    ).scalar()
    LOG.info(f"    {n_dgd} déclarations DGD mises à jour vers t_forets_new")
    _report["volumes"]["decl_dgd_mises_a_jour"] = n_dgd
    n_err_dgd = _mark_erreur_refgeo(db, "dgd")
    if n_err_dgd:
        LOG.warning(
            f"    {n_err_dgd} déclaration(s) DGD marquées Erreur Refgeo (forêt DGD non retrouvée)"
        )
        _report["anomalies"].append(
            f"[Étape 6b] {n_err_dgd} déclaration(s) DGD en Erreur Refgeo (forêt DGD non retrouvée dans le nouveau GPKG)"
        )
    _report["volumes"]["decl_dgd_erreur_refgeo"] = n_err_dgd

    LOG.info("  6c : mise à jour id_foret pour les déclarations ONF")
    print("  6c : mise à jour id_foret pour les déclarations ONF")

    # Passage 1 : correspondance spatiale pour les forêts ONF dont id_area est renseigné
    db.session.execute(text(f"""
        UPDATE oeasc_declarations.t_declarations d
        SET id_foret = fn.id_foret
        FROM oeasc_forets.t_forets f
        JOIN ref_geo.l_areas la_old ON la_old.id_area = f.id_area
            AND la_old.id_type = {ID_TYPE_FORET_ONF}
        JOIN ref_geo.l_areas_new la_new ON (
            la_new.id_type = {ID_TYPE_FORET_ONF}
            AND ST_Intersects(la_old.geom, la_new.geom)
            AND ST_Area(ST_Intersection(la_old.geom, la_new.geom))
                / NULLIF(ST_Area(la_old.geom), 0) >= {MATCH_THRESHOLD}
        )
        JOIN oeasc_forets.t_forets_new fn ON fn.id_area = la_new.id_area
            AND fn.b_document = TRUE AND fn.b_statut_public = TRUE
        WHERE d.id_foret = f.id_foret
        AND d.type_declaration = 'onf'
        AND f.b_document = TRUE AND f.b_statut_public = TRUE
        AND f.id_area IS NOT NULL
    """))
    db.session.commit()

    # Passage 2a : pour les forêts ONF dont id_area est NULL, via correspondance spatiale
    # entre les UG ONF de la déclaration (l_areas) et les nouvelles forêts ONF (l_areas_new).
    # Robuste même si iidtn_frt a changé entre deux versions du GPKG.
    # Note : on filtre sur f2.id_area IS NULL (passage 1 couvre les forêts avec id_area).
    # On n'utilise pas de NOT EXISTS sur t_forets_new car les nouveaux IDs (séquence depuis 1)
    # peuvent coïncider avec d'anciens IDs, créant des faux positifs.
    db.session.execute(text(f"""
        UPDATE oeasc_declarations.t_declarations d
        SET id_foret = match.id_foret
        FROM (
            SELECT DISTINCT ON (d2.id_declaration)
                d2.id_declaration,
                fn.id_foret,
                ST_Area(ST_Intersection(la_ug.geom, la_foret_new.geom)) AS overlap
            FROM oeasc_declarations.t_declarations d2
            JOIN oeasc_forets.t_forets f2 ON f2.id_foret = d2._pre_refresh_id_foret
                AND f2.b_document = TRUE AND f2.b_statut_public = TRUE
                AND f2.id_area IS NULL
            JOIN oeasc_declarations.cor_areas_declarations cad
                ON cad.id_declaration = d2.id_declaration
            JOIN ref_geo.l_areas la_ug
                ON la_ug.id_area = cad.id_area AND la_ug.id_type = {ID_TYPE_UG_ONF}
            JOIN ref_geo.l_areas_new la_foret_new
                ON la_foret_new.id_type = {ID_TYPE_FORET_ONF}
                AND ST_Intersects(la_ug.geom, la_foret_new.geom)
            JOIN oeasc_forets.t_forets_new fn ON fn.id_area = la_foret_new.id_area
                AND fn.b_document = TRUE AND fn.b_statut_public = TRUE
            WHERE d2.type_declaration = 'onf'
            AND d2.id_foret = d2._pre_refresh_id_foret
            ORDER BY d2.id_declaration, overlap DESC
        ) match
        WHERE d.id_declaration = match.id_declaration
    """))
    db.session.commit()

    # Passage 2b : fallback spatial via cadastres — pour les déclarations ONF sans UG
    # (id_area IS NULL sur la forêt, et pas de match en 2a). Le format area_code des
    # cadastres change entre GPKG, donc on utilise la géométrie des anciennes parcelles
    # pour trouver directement la nouvelle forêt ONF qui les contient.
    db.session.execute(text(f"""
        UPDATE oeasc_declarations.t_declarations d
        SET id_foret = match.id_foret
        FROM (
            SELECT DISTINCT ON (d2.id_declaration)
                d2.id_declaration,
                fn.id_foret,
                ST_Area(ST_Intersection(la_cad.geom, la_onf_new.geom)) AS overlap
            FROM oeasc_declarations.t_declarations d2
            JOIN oeasc_forets.t_forets f2 ON f2.id_foret = d2._pre_refresh_id_foret
                AND f2.b_document = TRUE AND f2.b_statut_public = TRUE
                AND f2.id_area IS NULL
            JOIN oeasc_declarations.cor_areas_declarations cad
                ON cad.id_declaration = d2.id_declaration
            JOIN ref_geo.l_areas la_cad
                ON la_cad.id_area = cad.id_area AND la_cad.id_type = {ID_TYPE_CADASTRE}
            JOIN ref_geo.l_areas_new la_onf_new
                ON la_onf_new.id_type = {ID_TYPE_FORET_ONF}
                AND ST_Intersects(la_cad.geom, la_onf_new.geom)
            JOIN oeasc_forets.t_forets_new fn ON fn.id_area = la_onf_new.id_area
                AND fn.b_document = TRUE AND fn.b_statut_public = TRUE
            WHERE d2.type_declaration = 'onf'
            AND d2.id_foret = d2._pre_refresh_id_foret
            ORDER BY d2.id_declaration, overlap DESC
        ) match
        WHERE d.id_declaration = match.id_declaration
    """))
    db.session.commit()

    n_onf = db.session.execute(
        text(
            "SELECT count(*) FROM oeasc_declarations.t_declarations d "
            "JOIN oeasc_forets.t_forets_new fn ON fn.id_foret = d.id_foret "
            "WHERE fn.b_statut_public = true AND fn.b_document = true"
        )
    ).scalar()
    LOG.info(f"    {n_onf} déclarations ONF mises à jour vers t_forets_new")
    _report["volumes"]["decl_onf_mises_a_jour"] = n_onf
    n_err_onf = _mark_erreur_refgeo(db, "onf")
    if n_err_onf:
        LOG.warning(
            f"    {n_err_onf} déclaration(s) ONF marquées Erreur Refgeo (forêt ONF non retrouvée)"
        )
        _report["anomalies"].append(
            f"[Étape 6c] {n_err_onf} déclaration(s) ONF en Erreur Refgeo (forêt ONF non retrouvée dans le nouveau GPKG)"
        )
    _report["volumes"]["decl_onf_erreur_refgeo"] = n_err_onf

    # 6d : mise à jour id_foret pour les déclarations ss_document (via old_id_foret)
    LOG.info(
        "  6d : mise à jour id_foret pour les déclarations ss_document (via old_id_foret)"
    )
    print(
        "  6d : mise à jour id_foret pour les déclarations ss_document (via old_id_foret)"
    )
    db.session.execute(text("""
        UPDATE oeasc_declarations.t_declarations d
        SET id_foret = fn.id_foret
        FROM oeasc_forets.t_forets_new fn
        WHERE d.id_foret = fn.old_id_foret
        AND fn.b_document = FALSE
    """))
    n_ss = db.session.execute(
        text(
            "SELECT count(*) FROM oeasc_declarations.t_declarations d "
            "JOIN oeasc_forets.t_forets_new fn ON fn.id_foret = d.id_foret "
            "WHERE fn.b_document = false"
        )
    ).scalar()
    LOG.info(f"    {n_ss} déclarations ss_document mises à jour vers t_forets_new")
    _report["volumes"]["decl_ss_document_mises_a_jour"] = n_ss
    db.session.commit()

    # 6e : mise à jour id_area_commune dans t_lieu_tirs
    LOG.info("  6e : mise à jour id_area_commune dans t_lieu_tirs")
    print("  6e : mise à jour id_area_commune dans t_lieu_tirs")

    # Passage 1 : correspondance par area_code (code INSEE commune, stable)
    db.session.execute(text(f"""
        UPDATE oeasc_chasse.t_lieu_tirs lt
        SET id_area_commune = la_new.id_area
        FROM ref_geo.l_areas la_old
        JOIN ref_geo.l_areas_new la_new ON (
            la_new.id_type = {ID_TYPE_COMMUNE}
            AND la_new.area_code = la_old.area_code
        )
        WHERE lt.id_area_commune = la_old.id_area
        AND la_old.id_type = {ID_TYPE_COMMUNE}
    """))
    db.session.commit()

    # Passage 2 : fallback spatial pour les lieux dont la commune n'a pas été trouvée
    # (id_area_commune pointe encore vers l'ancienne l_areas)
    n_remaining = db.session.execute(text(f"""
        SELECT count(*) FROM oeasc_chasse.t_lieu_tirs lt
        WHERE lt.id_area_commune IS NOT NULL
        AND NOT EXISTS (
            SELECT 1 FROM ref_geo.l_areas_new la
            WHERE la.id_area = lt.id_area_commune AND la.id_type = {ID_TYPE_COMMUNE}
        )
        AND lt.geom IS NOT NULL
    """)).scalar()

    if n_remaining > 0:
        LOG.info(
            f"    {n_remaining} lieu(x) sans correspondance par code — fallback spatial"
        )
        print(
            f"    {n_remaining} lieu(x) sans correspondance par code — fallback spatial"
        )
        db.session.execute(text(f"""
            UPDATE oeasc_chasse.t_lieu_tirs lt
            SET id_area_commune = (
                SELECT la_new.id_area
                FROM ref_geo.l_areas_new la_new
                WHERE la_new.id_type = {ID_TYPE_COMMUNE}
                AND ST_Intersects(lt.geom, la_new.geom)
                ORDER BY ST_Area(ST_Intersection(lt.geom, la_new.geom)) DESC
                LIMIT 1
            )
            WHERE lt.id_area_commune IS NOT NULL
            AND NOT EXISTS (
                SELECT 1 FROM ref_geo.l_areas_new la
                WHERE la.id_area = lt.id_area_commune AND la.id_type = {ID_TYPE_COMMUNE}
            )
            AND lt.geom IS NOT NULL
        """))
        db.session.commit()

    n_lt = db.session.execute(
        text(
            "SELECT count(*) FROM oeasc_chasse.t_lieu_tirs lt "
            f"JOIN ref_geo.l_areas_new la ON la.id_area = lt.id_area_commune AND la.id_type = {ID_TYPE_COMMUNE}"
        )
    ).scalar()
    n_lt_total = db.session.execute(
        text(
            "SELECT count(*) FROM oeasc_chasse.t_lieu_tirs WHERE id_area_commune IS NOT NULL"
        )
    ).scalar()
    if n_lt < n_lt_total:
        LOG.warning(
            f"  ATTENTION : {n_lt_total - n_lt} lieu(x) de tir sur {n_lt_total} "
            f"sans commune dans l_areas_new (ni par code ni par géométrie)."
        )
        _report["anomalies"].append(
            f"[Étape 6e] {n_lt_total - n_lt} lieu(x) de tir sur {n_lt_total} sans commune dans l_areas_new"
        )
    else:
        LOG.info(f"    {n_lt}/{n_lt_total} lieux de tir mis à jour.")
    _report["volumes"]["lieux_tir_mis_a_jour"] = n_lt
    _report["volumes"]["lieux_tir_total"] = n_lt_total
    db.session.commit()

    # Rapport final
    n_erreur = db.session.execute(
        text(
            "SELECT count(*) FROM oeasc_declarations.t_declarations WHERE statut = 999"
        )
    ).scalar()
    if n_erreur:
        LOG.warning(
            f"  ATTENTION : {n_erreur} déclaration(s) en statut Erreur Refgeo (999) "
            f"— forêt non retrouvée, id_foret mis à NULL, precision_localisation renseignée."
        )
    # Déclarations avec id_foret non null mais absent de t_forets_new (ne devrait pas arriver)
    n_broken = db.session.execute(text("""
        SELECT count(*) FROM oeasc_declarations.t_declarations d
        WHERE d.id_foret IS NOT NULL
        AND NOT EXISTS (SELECT 1 FROM oeasc_forets.t_forets_new fn WHERE fn.id_foret = d.id_foret)
    """)).scalar()
    if n_broken:
        LOG.warning(
            f"  ATTENTION : {n_broken} déclaration(s) ont id_foret non null mais absent de t_forets_new "
            f"(type_declaration non géré ?)."
        )
        _report["anomalies"].append(
            f"[Étape 6] {n_broken} déclaration(s) avec id_foret non null absent de t_forets_new "
            f"(type_declaration non géré ?)"
        )
    LOG.info("  Mise à jour des déclarations terminée.")


# ---------------------------------------------------------------------------
# Étape 7 — Swap t_forets → t_forets_new
# ---------------------------------------------------------------------------


def _get_views_ddl():
    """Récupère les définitions des vues dépendant de t_forets."""
    db = _get_db()
    views_ordered = [
        "v_declarations",
        "v_declaration_degats",
        "v_declaration_degats_restrict",
        "vl_declarations",
        "v_export_declarations_csv",
        "v_export_declaration_degats_csv",
        "v_export_declarations_shape",
        "v_export_declaration_degats_shape",
    ]
    ddls = {}
    for vname in views_ordered:
        # Vérifie que la vue existe avant d'appeler pg_get_viewdef
        exists = db.session.execute(
            text(
                "SELECT 1 FROM pg_views WHERE schemaname='oeasc_declarations' AND viewname=:n"
            ),
            {"n": vname},
        ).fetchone()
        if exists:
            r = db.session.execute(
                text(f"SELECT pg_get_viewdef('oeasc_declarations.{vname}', true)")
            ).fetchone()
            if r:
                ddls[vname] = r[0]
    if not ddls:
        LOG.warning(
            "  Aucune vue trouvée dans oeasc_declarations — "
            "elles seront recréées depuis les définitions intégrées."
        )
    return views_ordered, ddls


def step_swap_t_forets():
    LOG.info("Étape 7 : swap t_forets → t_forets_new")
    print("Étape 7 : swap t_forets → t_forets_new")
    db = _get_db()

    # Sauvegarde puis suppression des vues dépendant de t_forets
    views_ordered, views_ddl = _get_views_ddl()
    db.session.execute(
        text("DROP VIEW IF EXISTS oeasc_declarations.v_declarations CASCADE")
    )
    db.session.commit()

    for stmt in [
        # FKs sur t_forets
        "ALTER TABLE oeasc_forets.t_forets DROP CONSTRAINT IF EXISTS fk_foret_id_declarant",
        "ALTER TABLE oeasc_forets.t_forets DROP CONSTRAINT IF EXISTS fk_foret_id_nomenclature_proprietaire_type",
        "ALTER TABLE oeasc_forets.t_forets DROP CONSTRAINT IF EXISTS fk_t_forets_id_proprietaire",
        # FKs des tables référençant t_forets
        "ALTER TABLE oeasc_forets.cor_areas_forets DROP CONSTRAINT IF EXISTS fk_cor_areas_foret_id_foret",
        "ALTER TABLE oeasc_declarations.t_declarations DROP CONSTRAINT IF EXISTS fk_t_declarations_id_foret",
        # Vider cor_areas_forets (sera reconstruit après cor_hierarchie_area)
        "TRUNCATE oeasc_forets.cor_areas_forets",
        # Supprimer l'ancienne sauvegarde si elle existe, puis renommer l'actuelle
        "DROP TABLE IF EXISTS oeasc_forets.t_forets_ancien CASCADE",
        "DROP SEQUENCE IF EXISTS oeasc_forets.t_forets_ancien_id_foret_seq",
        "ALTER TABLE oeasc_forets.t_forets RENAME TO t_forets_ancien",
        "ALTER SEQUENCE oeasc_forets.t_forets_id_foret_seq RENAME TO t_forets_ancien_id_foret_seq",
        # Promouvoir t_forets_new en t_forets
        "ALTER TABLE oeasc_forets.t_forets_new RENAME TO t_forets",
        "ALTER SEQUENCE oeasc_forets.t_forets_new_id_foret_seq RENAME TO t_forets_id_foret_seq",
        # Recréer FKs sur t_forets
        (
            "ALTER TABLE oeasc_forets.t_forets "
            "ADD CONSTRAINT fk_foret_id_declarant "
            "FOREIGN KEY (id_declarant) REFERENCES utilisateurs.t_roles(id_role)"
        ),
        (
            "ALTER TABLE oeasc_forets.t_forets "
            "ADD CONSTRAINT fk_foret_id_nomenclature_proprietaire_type "
            "FOREIGN KEY (id_nomenclature_proprietaire_type) "
            "REFERENCES ref_nomenclatures.t_nomenclatures(id_nomenclature)"
        ),
        # Recréer FKs depuis les tables référençant t_forets
        (
            "ALTER TABLE oeasc_forets.cor_areas_forets "
            "ADD CONSTRAINT fk_cor_areas_foret_id_foret "
            "FOREIGN KEY (id_foret) REFERENCES oeasc_forets.t_forets(id_foret) "
            "ON UPDATE CASCADE ON DELETE CASCADE"
        ),
        # NOT VALID : on ne vérifie pas les lignes existantes à la création.
        # Les déclarations dont id_foret n'a pas pu être mis à jour (codes DGD
        # changeant de format) sont signalées par step_verify().
        (
            "ALTER TABLE oeasc_declarations.t_declarations "
            "ADD CONSTRAINT fk_t_declarations_id_foret "
            "FOREIGN KEY (id_foret) REFERENCES oeasc_forets.t_forets(id_foret) NOT VALID"
        ),
    ]:
        db.session.execute(text(stmt))
    db.session.commit()

    # Recréation des vues dans l'ordre de dépendance
    for vname in views_ordered:
        if vname in views_ddl:
            db.session.execute(
                text(
                    f"CREATE OR REPLACE VIEW oeasc_declarations.{vname} AS\n{views_ddl[vname]}"
                )
            )
    db.session.commit()
    LOG.info(f"  {len(views_ddl)} vues recréées.")

    n = db.session.execute(text("SELECT count(*) FROM oeasc_forets.t_forets")).scalar()
    LOG.info(
        f"  Swap t_forets terminé. {n} forêts dans la nouvelle table (ancienne conservée sous t_forets_ancien)."
    )
    _report["volumes"]["t_forets"] = n


# ---------------------------------------------------------------------------
# Étape 8 — Swap l_areas → l_areas_new
# ---------------------------------------------------------------------------


def step_swap_l_areas():
    LOG.info("Étape 8 : swap l_areas → l_areas_new")
    print("Étape 8 : swap l_areas → l_areas_new")
    db = _get_db()
    for stmt in [
        # FKs de cor_area_intersect vers l_areas
        "ALTER TABLE ref_geo.cor_area_intersect DROP CONSTRAINT IF EXISTS fk_cor_area_intersect_id_commune",
        "ALTER TABLE ref_geo.cor_area_intersect DROP CONSTRAINT IF EXISTS fk_cor_area_intersect_id_foret_dgd",
        "ALTER TABLE ref_geo.cor_area_intersect DROP CONSTRAINT IF EXISTS fk_cor_area_intersect_id_foret_onf",
        "ALTER TABLE ref_geo.cor_area_intersect DROP CONSTRAINT IF EXISTS fk_cor_area_intersect_id_foret_prive",
        "ALTER TABLE ref_geo.cor_area_intersect DROP CONSTRAINT IF EXISTS fk_cor_area_intersect_id_parcelle",
        "ALTER TABLE ref_geo.cor_area_intersect DROP CONSTRAINT IF EXISTS fk_cor_area_intersect_id_parcelle_onf",
        "ALTER TABLE ref_geo.cor_area_intersect DROP CONSTRAINT IF EXISTS fk_cor_area_intersect_id_secteur",
        "ALTER TABLE ref_geo.cor_area_intersect DROP CONSTRAINT IF EXISTS fk_cor_area_intersect_id_section_cadastrale",
        # Supprimer cor_hierarchie_area
        "DROP TABLE IF EXISTS ref_geo.cor_hierarchie_area",
        # FKs des autres tables vers l_areas
        "ALTER TABLE oeasc_chasse.t_lieu_tirs DROP CONSTRAINT IF EXISTS fk_t_lieu_tirs_l_areas",
        "ALTER TABLE oeasc_declarations.cor_areas_declarations DROP CONSTRAINT IF EXISTS fk_cor_areas_declarations_id_area",
        "ALTER TABLE oeasc_forets.cor_areas_forets DROP CONSTRAINT IF EXISTS fk_cor_areas_foret_id_area",
        # Vue matérialisée
        "DROP MATERIALIZED VIEW IF EXISTS ref_geo.vm_lareas_simples",
        # Supprimer l'ancienne sauvegarde si elle existe, puis renommer l'actuelle
        "DROP TABLE IF EXISTS ref_geo.l_areas_ancien CASCADE",
        "DROP SEQUENCE IF EXISTS ref_geo.l_areas_ancien_id_area_seq",
        "ALTER TABLE ref_geo.l_areas RENAME TO l_areas_ancien",
        "ALTER SEQUENCE ref_geo.l_areas_id_area_seq RENAME TO l_areas_ancien_id_area_seq",
        # Promouvoir l_areas_new en l_areas
        "ALTER TABLE ref_geo.l_areas_new RENAME TO l_areas",
        "ALTER SEQUENCE ref_geo.l_areas_new_id_area_seq RENAME TO l_areas_id_area_seq",
        (
            "ALTER TABLE ref_geo.l_areas ALTER COLUMN id_area "
            "SET DEFAULT nextval('ref_geo.l_areas_id_area_seq')"
        ),
        "ALTER SEQUENCE ref_geo.l_areas_id_area_seq OWNED BY ref_geo.l_areas.id_area",
        # Recréer FKs
        (
            "ALTER TABLE oeasc_chasse.t_lieu_tirs "
            "ADD CONSTRAINT fk_t_lieu_tirs_l_areas "
            "FOREIGN KEY (id_area_commune) REFERENCES ref_geo.l_areas(id_area) ON UPDATE CASCADE"
        ),
        # Sauvegarde de cor_areas_declarations avec géométries avant le TRUNCATE
        # (l_areas_ancien existe déjà à ce stade — le join est valide)
        "DROP TABLE IF EXISTS oeasc_declarations.cor_areas_declarations_ancien",
        (
            "CREATE TABLE oeasc_declarations.cor_areas_declarations_ancien AS "
            "SELECT cad.id_declaration, cad.id_area, "
            "       la.geom, la.area_name, la.area_code, la.id_type "
            "FROM oeasc_declarations.cor_areas_declarations cad "
            "JOIN ref_geo.l_areas_ancien la ON la.id_area = cad.id_area"
        ),
        # cor_areas_declarations sera reconstruite en step 9 — vider avant de recréer la FK
        "TRUNCATE oeasc_declarations.cor_areas_declarations",
        (
            "ALTER TABLE oeasc_declarations.cor_areas_declarations "
            "ADD CONSTRAINT fk_cor_areas_declarations_id_area "
            "FOREIGN KEY (id_area) REFERENCES ref_geo.l_areas(id_area) ON UPDATE CASCADE"
        ),
        (
            "ALTER TABLE oeasc_forets.cor_areas_forets "
            "ADD CONSTRAINT fk_cor_areas_foret_id_area "
            "FOREIGN KEY (id_area) REFERENCES ref_geo.l_areas(id_area) ON UPDATE CASCADE"
        ),
        (
            "ALTER TABLE ref_geo.cor_area_intersect "
            "ADD CONSTRAINT fk_cor_area_intersect_id_commune "
            "FOREIGN KEY (id_commune) REFERENCES ref_geo.l_areas(id_area) ON DELETE CASCADE"
        ),
        (
            "ALTER TABLE ref_geo.cor_area_intersect "
            "ADD CONSTRAINT fk_cor_area_intersect_id_foret_dgd "
            "FOREIGN KEY (id_foret_dgd) REFERENCES ref_geo.l_areas(id_area) ON DELETE CASCADE"
        ),
        (
            "ALTER TABLE ref_geo.cor_area_intersect "
            "ADD CONSTRAINT fk_cor_area_intersect_id_foret_onf "
            "FOREIGN KEY (id_foret_onf) REFERENCES ref_geo.l_areas(id_area) ON DELETE CASCADE"
        ),
        (
            "ALTER TABLE ref_geo.cor_area_intersect "
            "ADD CONSTRAINT fk_cor_area_intersect_id_foret_prive "
            "FOREIGN KEY (id_foret_prive) REFERENCES ref_geo.l_areas(id_area) ON DELETE CASCADE"
        ),
        (
            "ALTER TABLE ref_geo.cor_area_intersect "
            "ADD CONSTRAINT fk_cor_area_intersect_id_parcelle "
            "FOREIGN KEY (id_parcelle) REFERENCES ref_geo.l_areas(id_area) ON DELETE CASCADE"
        ),
        (
            "ALTER TABLE ref_geo.cor_area_intersect "
            "ADD CONSTRAINT fk_cor_area_intersect_id_parcelle_onf "
            "FOREIGN KEY (id_parcelle_onf) REFERENCES ref_geo.l_areas(id_area) ON DELETE CASCADE"
        ),
        (
            "ALTER TABLE ref_geo.cor_area_intersect "
            "ADD CONSTRAINT fk_cor_area_intersect_id_secteur "
            "FOREIGN KEY (id_secteur) REFERENCES ref_geo.l_areas(id_area) ON DELETE CASCADE"
        ),
        (
            "ALTER TABLE ref_geo.cor_area_intersect "
            "ADD CONSTRAINT fk_cor_area_intersect_id_section_cadastrale "
            "FOREIGN KEY (id_section_cadastrale) REFERENCES ref_geo.l_areas(id_area) ON DELETE CASCADE"
        ),
    ]:
        db.session.execute(text(stmt))
    db.session.commit()
    n = db.session.execute(text("SELECT count(*) FROM ref_geo.l_areas")).scalar()
    n_bak = db.session.execute(
        text("SELECT count(*) FROM oeasc_declarations.cor_areas_declarations_ancien")
    ).scalar()
    LOG.info(
        f"  Swap l_areas terminé. {n} areas dans la nouvelle table (ancienne conservée sous l_areas_ancien). "
        f"cor_areas_declarations_ancien sauvegardée ({n_bak} liaisons avec géométries)."
    )
    _report["volumes"]["l_areas"] = n
    _report["volumes"]["cor_areas_declarations_ancien"] = n_bak


# ---------------------------------------------------------------------------
# Étape 9 — Reconstruction de cor_hierarchie_area
# ---------------------------------------------------------------------------


def step_build_cor_hierarchie_area():
    LOG.info("Étape 9 : reconstruction de cor_hierarchie_area")
    print("Étape 9 : reconstruction de cor_hierarchie_area")
    db = _get_db()

    db.session.execute(text("""
        CREATE TABLE ref_geo.cor_hierarchie_area (
            id_area_enfant  INTEGER NOT NULL REFERENCES ref_geo.l_areas(id_area),
            id_type_enfant  INTEGER NOT NULL,
            id_area_parent  INTEGER NOT NULL REFERENCES ref_geo.l_areas(id_area),
            id_type_parent  INTEGER NOT NULL,
            PRIMARY KEY (id_area_enfant, id_type_enfant, id_area_parent, id_type_parent)
        )
    """))
    db.session.execute(
        text(
            "CREATE INDEX cor_hierarchie_area_id_type_enfant_idx "
            "ON ref_geo.cor_hierarchie_area (id_type_enfant, id_type_parent)"
        )
    )

    # 1. Sections → Communes (jointure spatiale)
    db.session.execute(text(f"""
        INSERT INTO ref_geo.cor_hierarchie_area
            (id_area_enfant, id_type_enfant, id_area_parent, id_type_parent)
        SELECT s.id_area, s.id_type, c.id_area, c.id_type
        FROM ref_geo.l_areas s
        JOIN ref_geo.l_areas c ON (
            c.id_type = {ID_TYPE_COMMUNE}
            AND ST_Intersects(ST_PointOnSurface(s.geom), c.geom)
        )
        WHERE s.id_type = {ID_TYPE_SECTION}
        ON CONFLICT DO NOTHING
    """))

    # 2. Cadastres → Sections (par préfixe area_code, 11 premiers chars)
    db.session.execute(text(f"""
        INSERT INTO ref_geo.cor_hierarchie_area
            (id_area_enfant, id_type_enfant, id_area_parent, id_type_parent)
        SELECT cad.id_area, cad.id_type, sec.id_area, sec.id_type
        FROM ref_geo.l_areas cad
        JOIN ref_geo.l_areas sec ON (
            sec.id_type = {ID_TYPE_SECTION}
            AND sec.area_code = LEFT(cad.area_code, 11)
        )
        WHERE cad.id_type = {ID_TYPE_CADASTRE}
        ON CONFLICT DO NOTHING
    """))

    # 3. Cadastres → Forêts DGD (intersection spatiale > 50% de la surface du cadastre)
    db.session.execute(text(f"""
        INSERT INTO ref_geo.cor_hierarchie_area
            (id_area_enfant, id_type_enfant, id_area_parent, id_type_parent)
        SELECT DISTINCT cad.id_area, cad.id_type, dgd.id_area, dgd.id_type
        FROM ref_geo.l_areas cad
        JOIN ref_geo.l_areas dgd ON (
            dgd.id_type = {ID_TYPE_DGD}
            AND ST_Intersects(cad.geom, dgd.geom)
            AND ST_Area(ST_Intersection(cad.geom, dgd.geom))
                / NULLIF(ST_Area(cad.geom), 0) > 0.5
        )
        WHERE cad.id_type = {ID_TYPE_CADASTRE}
        ON CONFLICT DO NOTHING
    """))

    # 4. Parcelles ONF → Forêts ONF
    # area_code parcelle = "{dep}-{iidtn_frt}-{ccod_prf}", area_code forêt = "{iidtn_frt}"
    # → SPLIT_PART(..., '-', 2) extrait iidtn_frt depuis le code parcelle
    db.session.execute(text(f"""
        INSERT INTO ref_geo.cor_hierarchie_area
            (id_area_enfant, id_type_enfant, id_area_parent, id_type_parent)
        SELECT p.id_area, p.id_type, f.id_area, f.id_type
        FROM ref_geo.l_areas p
        JOIN ref_geo.l_areas f ON (
            f.id_type = {ID_TYPE_FORET_ONF}
            AND SPLIT_PART(p.area_code, '-', 2) = f.area_code
        )
        WHERE p.id_type = {ID_TYPE_PARCELLE_ONF}
        ON CONFLICT DO NOTHING
    """))

    # 5. UG ONF → Parcelles ONF (par préfixe area_code)
    db.session.execute(text(f"""
        INSERT INTO ref_geo.cor_hierarchie_area
            (id_area_enfant, id_type_enfant, id_area_parent, id_type_parent)
        SELECT u.id_area, u.id_type, p.id_area, p.id_type
        FROM ref_geo.l_areas u
        JOIN ref_geo.l_areas p ON (
            p.id_type = {ID_TYPE_PARCELLE_ONF}
            AND u.area_code ILIKE p.area_code || '-%'
        )
        WHERE u.id_type = {ID_TYPE_UG_ONF}
        ON CONFLICT DO NOTHING
    """))

    db.session.commit()
    n = db.session.execute(
        text("SELECT count(*) FROM ref_geo.cor_hierarchie_area")
    ).scalar()
    LOG.info(f"  cor_hierarchie_area reconstruite avec {n} entrées.")
    _report["volumes"]["cor_hierarchie_area"] = n

    # Reconstruction de cor_areas_forets depuis la hiérarchie
    db.session.execute(text(f"""
        INSERT INTO oeasc_forets.cor_areas_forets (id_area, id_foret)
        SELECT cha.id_area_enfant, tf.id_foret
        FROM ref_geo.cor_hierarchie_area cha
        JOIN oeasc_forets.t_forets tf ON tf.id_area = cha.id_area_parent
        WHERE cha.id_type_parent IN ({ID_TYPE_DGD}, {ID_TYPE_FORET_ONF})
        AND cha.id_type_enfant IN ({ID_TYPE_UG_ONF}, {ID_TYPE_CADASTRE})
        ON CONFLICT DO NOTHING
    """))
    db.session.commit()

    # Forêts ss_document (b_document=FALSE) : alimenter cor_areas_forets depuis cor_area_intersect.
    # L'étape 5 renseigne id_foret_prive = id_area de la forêt privée pour chaque cadastre
    # qui l'intersecte ; on utilise cette correspondance pour lier cadastre → forêt privée.
    db.session.execute(text("""
        INSERT INTO oeasc_forets.cor_areas_forets (id_area, id_foret)
        SELECT DISTINCT cai.id_parcelle, tf.id_foret
        FROM ref_geo.cor_area_intersect cai
        JOIN oeasc_forets.t_forets tf ON tf.id_area = cai.id_foret_prive
        WHERE cai.id_foret_prive IS NOT NULL
        ON CONFLICT DO NOTHING
    """))
    db.session.commit()
    n_prive = db.session.execute(
        text(
            "SELECT count(*) FROM oeasc_forets.cor_areas_forets caf "
            "JOIN oeasc_forets.t_forets tf ON tf.id_foret = caf.id_foret "
            "WHERE tf.b_document = FALSE"
        )
    ).scalar()
    LOG.info(
        f"  cor_areas_forets reconstruite (dont {n_prive} liaison(s) forêts ss_document)."
    )

    # Reconstruction de cor_areas_declarations par transfert spatial depuis la sauvegarde.
    # On ne conserve que les plus petites unités (UG ONF et parcelles cadastrales).
    # Le seuil 50% gère les fusions et scissions entre ancienne et nouvelle topologie.
    LOG.info(
        "  Reconstruction de cor_areas_declarations par transfert spatial depuis cor_areas_declarations_ancien"
    )
    db.session.execute(text(f"""
        INSERT INTO oeasc_declarations.cor_areas_declarations (id_declaration, id_area)
        SELECT DISTINCT cad_old.id_declaration, la_new.id_area
        FROM oeasc_declarations.cor_areas_declarations_ancien cad_old
        JOIN ref_geo.l_areas la_new ON (
            la_new.id_type = cad_old.id_type
            AND ST_Intersects(cad_old.geom, la_new.geom)
            AND ST_Area(ST_Intersection(cad_old.geom, la_new.geom))
                / NULLIF(ST_Area(cad_old.geom), 0) >= 0.5
        )
        WHERE cad_old.id_type IN ({ID_TYPE_UG_ONF}, {ID_TYPE_CADASTRE})
        ON CONFLICT DO NOTHING
    """))
    db.session.commit()

    # Fallback 1 ONF — meilleur recouvrement sans seuil.
    # Couvre les cas où l'ancienne UG a été subdivisée : aucune nouvelle UG ne dépasse
    # 50% mais le meilleur candidat a un recouvrement positif significatif.
    # On contraint aux UGs de la forêt correcte (via cor_hierarchie_area) pour ne pas
    # attraper des UGs d'une autre forêt qui intersecterait géographiquement.
    db.session.execute(text(f"""
        INSERT INTO oeasc_declarations.cor_areas_declarations (id_declaration, id_area)
        SELECT DISTINCT ON (cad_old.id_declaration, cad_old.id_area)
            cad_old.id_declaration, la_ug.id_area
        FROM oeasc_declarations.cor_areas_declarations_ancien cad_old
        JOIN oeasc_declarations.t_declarations d ON d.id_declaration = cad_old.id_declaration
        JOIN oeasc_forets.t_forets tf ON tf.id_foret = d.id_foret
            AND tf.b_document = TRUE AND tf.b_statut_public = TRUE
        JOIN ref_geo.cor_hierarchie_area cha1 ON cha1.id_area_parent = tf.id_area
        JOIN ref_geo.cor_hierarchie_area cha2 ON cha2.id_area_parent = cha1.id_area_enfant
        JOIN ref_geo.l_areas la_ug ON la_ug.id_area = cha2.id_area_enfant
            AND la_ug.id_type = {ID_TYPE_UG_ONF}
            AND ST_Intersects(cad_old.geom, la_ug.geom)
            AND ST_Area(ST_Intersection(cad_old.geom, la_ug.geom)) >= 100
        WHERE cad_old.id_type = {ID_TYPE_UG_ONF}
        AND NOT EXISTS (
            SELECT 1 FROM oeasc_declarations.cor_areas_declarations cad_new
            WHERE cad_new.id_declaration = cad_old.id_declaration
        )
        ORDER BY cad_old.id_declaration, cad_old.id_area,
                 ST_Area(ST_Intersection(cad_old.geom, la_ug.geom))
                     / NULLIF(ST_Area(cad_old.geom), 0) DESC
        ON CONFLICT DO NOTHING
    """))
    db.session.commit()

    # Fallback 2 ONF — UG la plus proche par centroïde dans la forêt correcte.
    # Couvre les cas de refonte complète du découpage en UG (recouvrement nul).
    # ST_DWithin(5 km) limite le produit cartésien et tire profit de l'index spatial.
    db.session.execute(text(f"""
        INSERT INTO oeasc_declarations.cor_areas_declarations (id_declaration, id_area)
        SELECT DISTINCT ON (cad_old.id_declaration, cad_old.id_area)
            cad_old.id_declaration, la_ug.id_area
        FROM oeasc_declarations.cor_areas_declarations_ancien cad_old
        JOIN oeasc_declarations.t_declarations d ON d.id_declaration = cad_old.id_declaration
        JOIN oeasc_forets.t_forets tf ON tf.id_foret = d.id_foret
            AND tf.b_document = TRUE AND tf.b_statut_public = TRUE
        JOIN ref_geo.cor_hierarchie_area cha1 ON cha1.id_area_parent = tf.id_area
        JOIN ref_geo.cor_hierarchie_area cha2 ON cha2.id_area_parent = cha1.id_area_enfant
        JOIN ref_geo.l_areas la_ug ON la_ug.id_area = cha2.id_area_enfant
            AND la_ug.id_type = {ID_TYPE_UG_ONF}
            AND ST_DWithin(cad_old.geom, la_ug.geom, 5000)
        WHERE cad_old.id_type = {ID_TYPE_UG_ONF}
        AND NOT EXISTS (
            SELECT 1 FROM oeasc_declarations.cor_areas_declarations cad_new
            WHERE cad_new.id_declaration = cad_old.id_declaration
        )
        ORDER BY cad_old.id_declaration, cad_old.id_area,
                 ST_Distance(ST_Centroid(cad_old.geom), ST_Centroid(la_ug.geom)) ASC
        ON CONFLICT DO NOTHING
    """))
    db.session.commit()

    n_missing = db.session.execute(text("""
        SELECT count(DISTINCT id_declaration)
        FROM oeasc_declarations.cor_areas_declarations_ancien
        WHERE id_declaration NOT IN (
            SELECT DISTINCT id_declaration FROM oeasc_declarations.cor_areas_declarations
        )
    """)).scalar()
    if n_missing:
        LOG.warning(
            f"  ATTENTION : {n_missing} déclaration(s) sans aucune area après le transfert spatial "
            f"(UG totalement hors périmètre ou forêt sans UG connue). "
            f"Vérifier cor_areas_declarations_ancien pour correction manuelle."
        )
        _report["anomalies"].append(
            f"[Étape 9] {n_missing} déclaration(s) sans aucune area après le transfert spatial "
            f"(UG hors périmètre ou forêt sans UG connue — vérifier cor_areas_declarations_ancien)"
        )

    n_cor = db.session.execute(
        text("SELECT count(*) FROM oeasc_declarations.cor_areas_declarations")
    ).scalar()
    LOG.info(f"  {n_cor} liaisons reconstruites dans cor_areas_declarations.")
    _report["volumes"]["cor_areas_declarations"] = n_cor
    db.session.commit()


# ---------------------------------------------------------------------------
# Étape 9b — Suppression des forêts hors périmètre OEASC
# ---------------------------------------------------------------------------


def step_prune_forests_outside_oeasc():
    LOG.info("Étape 9b : suppression des forêts sans parcelle dans le périmètre OEASC")
    print("Étape 9b : suppression des forêts sans parcelle dans le périmètre OEASC")
    db = _get_db()

    # Identifie les forêts à supprimer selon leur type.
    # Pour les DGD : on utilise cor_hierarchie_area (seuil 50% de surface) plutôt que
    # cor_area_intersect (toute intersection, même minuscule) afin d'éviter de conserver
    # des forêts dont seules des parcelles à cheval sur la bordure OEASC les référencent.
    to_delete = db.session.execute(text(f"""
        SELECT f.id_foret, f.nom_foret, f.code_foret,
               f.b_document, f.b_statut_public, f.id_area
        FROM oeasc_forets.t_forets f
        WHERE
            -- ONF : pas dans id_foret_onf
            (f.b_document = TRUE AND f.b_statut_public = TRUE
             AND NOT EXISTS (
                 SELECT 1 FROM ref_geo.cor_area_intersect
                 WHERE id_foret_onf = f.id_area
             ))
            OR
            -- DGD : supprimée si aucune parcelle cadastrale avec >50% de surface dans la forêt
            -- (cor_hierarchie_area) OU si aucune parcelle cadastrale n'est du tout associée
            -- (cor_area_intersect). Les deux vérifications sont nécessaires : cor_hierarchie_area
            -- évite de conserver des forêts dont seules des parcelles en bordure les frôlent,
            -- cor_area_intersect confirme l'absence totale de parcelles cadastrales.
            (f.b_document = TRUE AND f.b_statut_public = FALSE
             AND (
                 NOT EXISTS (
                     SELECT 1 FROM ref_geo.cor_hierarchie_area cha
                     JOIN ref_geo.l_areas la ON la.id_area = cha.id_area_enfant
                     WHERE cha.id_area_parent = f.id_area
                     AND la.id_type = {ID_TYPE_CADASTRE}
                 )
                 OR NOT EXISTS (
                     SELECT 1 FROM ref_geo.cor_area_intersect
                     WHERE id_foret_dgd = f.id_area
                 )
             ))
    """)).fetchall()

    if not to_delete:
        LOG.info("  Aucune forêt hors périmètre OEASC à supprimer.")
        _report["volumes"]["forets_prunees"] = 0
        return

    ids_to_delete = [r[0] for r in to_delete]
    for r in to_delete:
        LOG.info(
            f"  Suppression : id_foret={r[0]} nom={r[1]!r} code={r[2]!r} "
            f"b_document={r[3]} b_statut_public={r[4]} id_area={r[5]}"
        )

    _report["volumes"]["forets_prunees"] = len(ids_to_delete)
    _report["anomalies"].append(
        f"[Étape 9b] {len(ids_to_delete)} forêt(s) supprimée(s) (hors périmètre OEASC) : "
        + ", ".join(f"{r[1]!r} (id={r[0]})" for r in to_delete)
    )

    # Nullifie id_foret dans t_declarations (FK sans ON DELETE CASCADE)
    n_decl = db.session.execute(
        text("""
        UPDATE oeasc_declarations.t_declarations
        SET id_foret = NULL
        WHERE id_foret = ANY(:ids)
    """),
        {"ids": ids_to_delete},
    ).rowcount
    if n_decl:
        LOG.warning(
            f"  {n_decl} déclaration(s) ont eu leur id_foret mis à NULL "
            f"(forêt hors périmètre OEASC)."
        )
        _report["anomalies"].append(
            f"[Étape 9b] {n_decl} déclaration(s) avec id_foret mis à NULL (forêt hors périmètre OEASC)"
        )

    # Collecte les id_area non-null avant suppression (pour nettoyer l_areas ensuite)
    id_areas_to_delete = [r[5] for r in to_delete if r[5] is not None]

    # Supprime les forêts (CASCADE → cor_areas_forets)
    db.session.execute(
        text("""
        DELETE FROM oeasc_forets.t_forets WHERE id_foret = ANY(:ids)
    """),
        {"ids": ids_to_delete},
    )
    db.session.commit()
    LOG.info(f"  {len(ids_to_delete)} forêt(s) supprimée(s).")

    # Supprime les polygones correspondants de l_areas
    if id_areas_to_delete:
        # Nullifie d'abord les références dans cor_area_intersect pour éviter que
        # le CASCADE DELETE ne supprime les lignes entières des parcelles voisines
        # (qui conservent des infos valides comme commune, secteur, etc.)
        db.session.execute(
            text("""
            UPDATE ref_geo.cor_area_intersect
            SET id_foret_dgd = NULL WHERE id_foret_dgd = ANY(:ids)
        """),
            {"ids": id_areas_to_delete},
        )
        db.session.execute(
            text("""
            UPDATE ref_geo.cor_area_intersect
            SET id_foret_onf = NULL WHERE id_foret_onf = ANY(:ids)
        """),
            {"ids": id_areas_to_delete},
        )
        db.session.execute(
            text("""
            UPDATE ref_geo.cor_area_intersect
            SET id_foret_prive = NULL WHERE id_foret_prive = ANY(:ids)
        """),
            {"ids": id_areas_to_delete},
        )
        # cor_hierarchie_area n'a pas de CASCADE depuis l_areas
        n_hier = db.session.execute(
            text("""
            DELETE FROM ref_geo.cor_hierarchie_area
            WHERE id_area_parent = ANY(:ids) OR id_area_enfant = ANY(:ids)
        """),
            {"ids": id_areas_to_delete},
        ).rowcount
        # l_areas (le CASCADE sur cor_area_intersect ne supprime plus rien car déjà nullifié)
        n_areas = db.session.execute(
            text("""
            DELETE FROM ref_geo.l_areas WHERE id_area = ANY(:ids)
        """),
            {"ids": id_areas_to_delete},
        ).rowcount
        db.session.commit()
        LOG.info(
            f"  {n_areas} polygone(s) supprimé(s) de l_areas "
            f"(cor_hierarchie_area: {n_hier} entrée(s) supprimée(s))."
        )


# ---------------------------------------------------------------------------
# Étape 9c — Préservation des forêts absentes des nouvelles données
# ---------------------------------------------------------------------------


def step_preserve_unmatched_forests():
    """
    Pour les déclarations dont la forêt n'a pas été retrouvée dans les nouvelles données
    GPKG (marquées statut=999 par _mark_erreur_refgeo), copie l'ancienne forêt et son
    polygon depuis t_forets_ancien / l_areas_ancien avec valide=FALSE / enable=FALSE.
    Ces areas n'ont pas participé à cor_area_intersect (step 5) ni cor_hierarchie_area
    (step 9) car elles sont insérées après ces deux étapes.
    """
    LOG.info(
        "Étape 9c : préservation des forêts non retrouvées dans les nouvelles données"
    )
    print(
        "Étape 9c : préservation des forêts non retrouvées dans les nouvelles données"
    )
    db = _get_db()

    # Forêts distinctes à préserver (toutes catégories : DGD, ONF)
    unmatched_forests = db.session.execute(text("""
        SELECT DISTINCT _pre_refresh_id_foret AS old_id_foret
        FROM oeasc_declarations.t_declarations
        WHERE id_foret IS NULL
          AND _pre_refresh_id_foret IS NOT NULL
          AND statut = 999
    """)).fetchall()

    if not unmatched_forests:
        LOG.info("  Aucune forêt à préserver.")
        _report["volumes"]["forets_preservees"] = 0
        return

    for row in unmatched_forests:
        old_id_foret = row.old_id_foret

        # Déclarations concernées par cette forêt
        decl_rows = db.session.execute(
            text("""
            SELECT id_declaration
            FROM oeasc_declarations.t_declarations
            WHERE _pre_refresh_id_foret = :old_id AND id_foret IS NULL AND statut = 999
        """),
            {"old_id": old_id_foret},
        ).fetchall()
        decl_ids = [r.id_declaration for r in decl_rows]

        # Ancienne forêt
        old_foret = db.session.execute(
            text("""
            SELECT id_foret, id_proprietaire, b_statut_public, b_document,
                   nom_foret, code_foret, label_foret,
                   surface_renseignee, surface_calculee, id_area,
                   nom_proprietaire, adresse_proprietaire, cp_proprietaire,
                   commune_proprietaire, email_proprietaire, tel_proprietaire,
                   id_nomenclature_proprietaire_type, id_declarant
            FROM oeasc_forets.t_forets_ancien
            WHERE id_foret = :id
        """),
            {"id": old_id_foret},
        ).fetchone()

        if not old_foret:
            LOG.warning(
                f"  Forêt ancienne id={old_id_foret} introuvable dans t_forets_ancien — déclarations {decl_ids} ignorées."
            )
            continue

        nom = old_foret.nom_foret or f"id={old_id_foret}"

        # Copier le polygone depuis l_areas_ancien si la forêt en avait un
        new_id_area = None
        if old_foret.id_area:
            old_area = db.session.execute(
                text("""
                SELECT id_type, area_name, area_code, source,
                       meta_create_date, meta_update_date,
                       geom, geom_4326, centroid
                FROM ref_geo.l_areas_ancien
                WHERE id_area = :id
            """),
                {"id": old_foret.id_area},
            ).fetchone()

            if old_area:
                comment = (
                    f"Area sauvegardée pour les déclarations {decl_ids} "
                    f'et la forêt "{nom}" (non retrouvée lors du refresh)'
                )
                result = db.session.execute(
                    text("""
                    INSERT INTO ref_geo.l_areas
                        (id_type, area_name, area_code, source,
                         meta_create_date, meta_update_date,
                         geom, geom_4326, centroid,
                         enable, comment)
                    VALUES
                        (:id_type, :area_name, :area_code, :source,
                         :meta_create_date, :meta_update_date,
                         :geom, :geom_4326, :centroid,
                         FALSE, :comment)
                    RETURNING id_area
                """),
                    {
                        "id_type": old_area.id_type,
                        "area_name": old_area.area_name,
                        "area_code": old_area.area_code,
                        "source": old_area.source,
                        "meta_create_date": old_area.meta_create_date,
                        "meta_update_date": old_area.meta_update_date,
                        "geom": old_area.geom,
                        "geom_4326": old_area.geom_4326,
                        "centroid": old_area.centroid,
                        "comment": comment,
                    },
                )
                new_id_area = result.scalar()

        # Insérer la forêt préservée (valide=FALSE, colonnes listées explicitement)
        new_foret = db.session.execute(
            text("""
            INSERT INTO oeasc_forets.t_forets
                (id_proprietaire, b_statut_public, b_document,
                 nom_foret, code_foret, label_foret,
                 surface_renseignee, surface_calculee, id_area,
                 nom_proprietaire, adresse_proprietaire, cp_proprietaire,
                 commune_proprietaire, email_proprietaire, tel_proprietaire,
                 id_nomenclature_proprietaire_type, id_declarant,
                 valide)
            VALUES
                (:id_proprietaire, :b_statut_public, :b_document,
                 :nom_foret, :code_foret, :label_foret,
                 :surface_renseignee, :surface_calculee, :id_area,
                 :nom_proprietaire, :adresse_proprietaire, :cp_proprietaire,
                 :commune_proprietaire, :email_proprietaire, :tel_proprietaire,
                 :id_nomenclature_proprietaire_type, :id_declarant,
                 FALSE)
            RETURNING id_foret
        """),
            {
                "id_proprietaire": old_foret.id_proprietaire,
                "b_statut_public": old_foret.b_statut_public,
                "b_document": old_foret.b_document,
                "nom_foret": old_foret.nom_foret,
                "code_foret": old_foret.code_foret,
                "label_foret": old_foret.label_foret,
                "surface_renseignee": old_foret.surface_renseignee,
                "surface_calculee": old_foret.surface_calculee,
                "id_area": new_id_area,
                "nom_proprietaire": old_foret.nom_proprietaire,
                "adresse_proprietaire": old_foret.adresse_proprietaire,
                "cp_proprietaire": old_foret.cp_proprietaire,
                "commune_proprietaire": old_foret.commune_proprietaire,
                "email_proprietaire": old_foret.email_proprietaire,
                "tel_proprietaire": old_foret.tel_proprietaire,
                "id_nomenclature_proprietaire_type": old_foret.id_nomenclature_proprietaire_type,
                "id_declarant": old_foret.id_declarant,
            },
        )
        new_id_foret = new_foret.scalar()

        # Rattacher les déclarations à la forêt préservée
        db.session.execute(
            text("""
            UPDATE oeasc_declarations.t_declarations
            SET id_foret = :new_id,
                statut = 0,
                precision_localisation = :precision
            WHERE _pre_refresh_id_foret = :old_id AND id_foret IS NULL AND statut = 999
        """),
            {
                "new_id": new_id_foret,
                "old_id": old_id_foret,
                "precision": f"[Forêt non retrouvée dans les nouvelles données — conservée] (ancien id={old_id_foret})",
            },
        )
        db.session.commit()

        LOG.info(
            f'  Forêt préservée : "{nom}" '
            f"(ancien id={old_id_foret}, nouvel id={new_id_foret}, "
            f"id_area={'NULL' if new_id_area is None else new_id_area}) "
            f"— {len(decl_ids)} déclaration(s) rattachées : {decl_ids}"
        )
        _report["anomalies"].append(
            f'[Étape 9c] Forêt préservée (valide=FALSE) : "{nom}" '
            f"(ancien id={old_id_foret}, nouvel id={new_id_foret}) "
            f"— {len(decl_ids)} déclaration(s) : {decl_ids}"
        )

    _report["volumes"]["forets_preservees"] = len(unmatched_forests)
    LOG.info("  Préservation terminée.")


# ---------------------------------------------------------------------------
# Étape 10 — Nettoyage final
# ---------------------------------------------------------------------------


def step_cleanup():
    LOG.info("Étape 10 : nettoyage final")
    print("Étape 10 : nettoyage final")
    db = _get_db()

    db.session.execute(
        text("DROP MATERIALIZED VIEW IF EXISTS ref_geo.vm_lareas_simples")
    )
    db.session.commit()
    db.session.execute(text("""
        CREATE MATERIALIZED VIEW ref_geo.vm_lareas_simples AS
        SELECT
            l.id_area, l.id_type,
            ST_Transform(ST_SimplifyPreserveTopology(l.geom, 50), 4326) AS geom_4326,
            l.area_code, l.area_name, l.area_name AS label,
            ROUND((ST_Area(l.geom) / 10000)::numeric, 3) AS surface_calculee,
            ROUND((ST_Area(l.geom) / 10000)::numeric, 3) AS surface_renseignee,
            COALESCE(l.source, 'OEASC') AS source,
            COALESCE(l.enable, TRUE) AS enable
        FROM ref_geo.l_areas l
        WITH NO DATA
    """))
    for stmt in [
        "CREATE UNIQUE INDEX ux_vm_lareas_simples_id_area ON ref_geo.vm_lareas_simples (id_area)",
        "CREATE INDEX ix_vm_lareas_simples_geom_4326 ON ref_geo.vm_lareas_simples USING GIST (geom_4326)",
        "CREATE INDEX ix_vm_lareas_simples_id_type ON ref_geo.vm_lareas_simples (id_type)",
        "CREATE INDEX ix_vm_lareas_simples_area_code ON ref_geo.vm_lareas_simples (area_code)",
        # Corriger les géométries invalides (sections issues de ST_Union, données source DGD)
        "UPDATE ref_geo.l_areas SET geom = ST_Multi(ST_CollectionExtract(ST_MakeValid(geom), 3)) WHERE NOT ST_IsValid(geom)",
        "REFRESH MATERIALIZED VIEW ref_geo.vm_lareas_simples",
        "ALTER TABLE ref_geo.l_areas DROP COLUMN IF EXISTS proprietaire",
        "ALTER TABLE oeasc_declarations.t_declarations DROP COLUMN IF EXISTS type_declaration",
        "ALTER TABLE oeasc_declarations.t_declarations DROP COLUMN IF EXISTS _pre_refresh_id_foret",
        "ALTER TABLE oeasc_forets.t_forets DROP COLUMN IF EXISTS old_id_foret",
    ]:
        db.session.execute(text(stmt))
    db.session.commit()
    LOG.info("  vm_lareas_simples recréée, colonnes temporaires supprimées.")


# ---------------------------------------------------------------------------
# Étape 11 — Rapport de vérification
# ---------------------------------------------------------------------------


def step_verify():
    LOG.info("Étape 11 : vérification post-swap")
    print("Étape 11 : vérification post-swap")
    db = _get_db()

    rows = db.session.execute(
        text(
            "SELECT id_type, count(*) FROM ref_geo.l_areas GROUP BY id_type ORDER BY id_type"
        )
    ).fetchall()
    LOG.info("  Comptage par id_type dans l_areas :")
    for r in rows:
        LOG.info(f"    id_type={r[0]} → {r[1]} areas")
    _report["volumes"]["l_areas_par_type"] = {r[0]: r[1] for r in rows}

    invalid = db.session.execute(
        text("SELECT count(*) FROM ref_geo.l_areas WHERE NOT ST_IsValid(geom)")
    ).scalar()
    if invalid:
        LOG.warning(f"  ATTENTION : {invalid} géométrie(s) invalide(s)")
        _report["anomalies"].append(
            f"[Étape 11] {invalid} géométrie(s) invalide(s) restantes dans l_areas"
        )
    else:
        LOG.info("  Toutes les géométries sont valides.")

    no_commune = db.session.execute(
        text("SELECT count(*) FROM ref_geo.cor_area_intersect WHERE id_commune IS NULL")
    ).scalar()
    if no_commune:
        LOG.warning(
            f"  ATTENTION : {no_commune} parcelle(s) sans commune dans cor_area_intersect"
        )
        _report["anomalies"].append(
            f"[Étape 11] {no_commune} parcelle(s) sans commune dans cor_area_intersect"
        )

    no_foret = db.session.execute(
        text(
            "SELECT count(*) FROM oeasc_declarations.t_declarations WHERE id_foret IS NULL"
        )
    ).scalar()
    if no_foret:
        LOG.warning(f"  ATTENTION : {no_foret} déclaration(s) sans id_foret")
        _report["anomalies"].append(
            f"[Étape 11] {no_foret} déclaration(s) sans id_foret après le refresh"
        )

    # Vérifier les déclarations dont id_foret ne correspond à aucune forêt (toutes catégories)
    broken = db.session.execute(text("""
        SELECT count(*)
        FROM oeasc_declarations.t_declarations d
        LEFT JOIN oeasc_forets.t_forets f ON f.id_foret = d.id_foret
        WHERE d.id_foret IS NOT NULL AND f.id_foret IS NULL
    """)).scalar()
    if broken:
        LOG.warning(
            f"  ATTENTION : {broken} déclaration(s) pointent vers un id_foret inexistant "
            f"— à corriger manuellement (probablement des forêts DGD dont la géométrie a trop changé)."
        )
        _report["anomalies"].append(
            f"[Étape 11] {broken} déclaration(s) pointent vers un id_foret inexistant "
            f"(correction manuelle requise)"
        )

    # Vérifier les forêts ss_document dont id_area pointe vers une area inconnue
    bad_ss_area = db.session.execute(text("""
        SELECT count(*)
        FROM oeasc_forets.t_forets f
        LEFT JOIN ref_geo.l_areas la ON la.id_area = f.id_area
        WHERE f.b_document = FALSE AND f.id_area IS NOT NULL AND la.id_area IS NULL
    """)).scalar()
    if bad_ss_area:
        LOG.warning(
            f"  ATTENTION : {bad_ss_area} forêt(s) ss_document ont id_area invalide "
            f"(zone référencée dans l'ancienne l_areas). Leur id_area est remis à NULL."
        )
        _report["anomalies"].append(
            f"[Étape 11] {bad_ss_area} forêt(s) ss_document avec id_area invalide — id_area remis à NULL"
        )
        db.session.execute(text("""
            UPDATE oeasc_forets.t_forets f
            SET id_area = NULL
            WHERE f.b_document = FALSE
            AND f.id_area IS NOT NULL
            AND NOT EXISTS (SELECT 1 FROM ref_geo.l_areas la WHERE la.id_area = f.id_area)
        """))
        db.session.commit()
    else:
        LOG.info("  Forêts ss_document : id_area valides.")

    n_cai = db.session.execute(
        text("SELECT count(*) FROM ref_geo.cor_area_intersect")
    ).scalar()
    n_cha = db.session.execute(
        text("SELECT count(*) FROM ref_geo.cor_hierarchie_area")
    ).scalar()
    LOG.info(f"  cor_area_intersect : {n_cai} entrées")
    LOG.info(f"  cor_hierarchie_area : {n_cha} entrées")
    _report["volumes"]["final_cor_area_intersect"] = n_cai
    _report["volumes"]["final_cor_hierarchie_area"] = n_cha
    LOG.info("  Vérification terminée.")


# ---------------------------------------------------------------------------
# Étape 12 — Rafraîchissement final de la vue matérialisée
# ---------------------------------------------------------------------------


def step_refresh_vm_lareas_simples():
    LOG.info("Étape 12 : rafraîchissement final de ref_geo.vm_lareas_simples")
    print("Étape 12 : rafraîchissement final de ref_geo.vm_lareas_simples")
    db = _get_db()
    db.session.execute(
        text("REFRESH MATERIALIZED VIEW CONCURRENTLY ref_geo.vm_lareas_simples")
    )
    db.session.commit()
    LOG.info("  vm_lareas_simples rafraîchie.")


# ---------------------------------------------------------------------------
# Bilan final
# ---------------------------------------------------------------------------


def _write_bilan_final():
    end_time = datetime.now()
    start_time = _report.get("start_time", end_time)
    duration = end_time - start_time
    minutes, seconds = divmod(int(duration.total_seconds()), 60)

    opts = _report.get("options", {})
    opts_str = (
        " ".join(f"--{k.replace('_', '-')}" for k, v in opts.items() if v) or "(aucune)"
    )

    LOG.info("=" * 60)
    LOG.info("BILAN FINAL — refresh-ref-geo")
    LOG.info("=" * 60)
    LOG.info(f"  Statut  : {'SUCCES' if _report.get('success') else 'ECHEC'}")
    if _report.get("error"):
        LOG.error(f"  Erreur  : {_report['error']}")
    LOG.info(f"  Duree   : {minutes}m {seconds}s")
    LOG.info(f"  Options : {opts_str}")

    v = _report.get("volumes", {})
    if v:
        LOG.info("--- VOLUMES ---")
        for key, val in v.items():
            LOG.info(f"  {key:<40} : {val}")

    anomalies = _report.get("anomalies", [])
    if anomalies:
        LOG.warning("--- ANOMALIES / CAS PARTICULIERS ---")
        for a in anomalies:
            LOG.warning(f"  {a}")
    else:
        LOG.info("--- ANOMALIES : aucune ---")

    LOG.info("=" * 60)


# ---------------------------------------------------------------------------
# Commande principale
# ---------------------------------------------------------------------------


@click.command("refresh-ref-geo")
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Exécute toutes les étapes sauf le swap final",
)
@click.option(
    "--skip-load",
    is_flag=True,
    default=False,
    help="Saute le chargement GPKG si l_areas_new existe déjà",
)
@click.option(
    "--skip-intersect",
    is_flag=True,
    default=False,
    help="Saute la reconstruction de cor_area_intersect (doit être faite au préalable)",
)
@click.option(
    "--force", is_flag=True, default=False, help="Pas de confirmation interactive"
)
@with_appcontext
def refresh_ref_geo_cmd(dry_run, skip_load, skip_intersect, force):
    """Reconstruit ref_geo.l_areas depuis les fichiers GPKG."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    # Initialisation du rapport et du fichier log horodaté
    _report.clear()
    _report["start_time"] = datetime.now()
    _report["options"] = {
        "dry_run": dry_run,
        "skip_load": skip_load,
        "skip_intersect": skip_intersect,
        "force": force,
    }
    _report["volumes"] = {}
    _report["anomalies"] = []
    _report["success"] = False
    _report["error"] = None

    log_dir = os.path.normpath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../logs")
    )
    os.makedirs(log_dir, exist_ok=True)
    ts = _report["start_time"].strftime("%Y-%m-%d-%H-%M-%S")
    log_path = os.path.join(log_dir, f"rapport_refresh_ref_geo_{ts}.log")
    _file_handler = logging.FileHandler(log_path, encoding="utf-8")
    _file_handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    )
    LOG.addHandler(_file_handler)
    LOG.info(f"Rapport enregistré dans : {log_path}")

    _ensure_migrations()

    if dry_run:
        LOG.info("=== MODE DRY-RUN : le swap final ne sera PAS exécuté ===")
    if not force and not dry_run:
        click.confirm(
            "Cette opération va remplacer ref_geo.l_areas et oeasc_forets.t_forets. "
            "Continuer ?",
            abort=True,
        )

    try:
        step_save_declaration_types()

        already_loaded = skip_load and _table_exists("ref_geo", "l_areas_new")

        if not already_loaded:
            step_create_l_areas_new()
            step_create_t_forets_new()
            step_save_fixed_areas()
            step_load_communes()
            step_load_cadastres()
            step_build_sections()
            step_load_foret_dgd()
            step_load_foret_onf()
            step_load_parcelle_onf()
            step_load_ug_onf()
            step_copy_onf_proprietaire()
        else:
            LOG.info("--skip-load : chargement GPKG ignoré (l_areas_new déjà présente)")

        if not skip_intersect:
            step_build_cor_area_intersect()
        else:
            LOG.info("--skip-intersect : étape 5 ignorée")
        step_update_declarations()

        if dry_run:
            LOG.info(
                "=== DRY-RUN terminé. Tables _new disponibles pour inspection. ==="
            )
            _report["success"] = True
            _write_bilan_final()
            LOG.removeHandler(_file_handler)
            return

        step_swap_t_forets()
        step_swap_l_areas()
        step_build_cor_hierarchie_area()
        step_prune_forests_outside_oeasc()
        step_preserve_unmatched_forests()
        step_cleanup()
        step_verify()
        step_refresh_vm_lareas_simples()

        _report["success"] = True
        _write_bilan_final()
        LOG.info("=== refresh-ref-geo terminé avec succès ===")
        LOG.removeHandler(_file_handler)

    except Exception as exc:
        LOG.error(f"ERREUR : {exc}", exc_info=True)
        _report["error"] = str(exc)
        _write_bilan_final()
        LOG.removeHandler(_file_handler)
        _get_db().session.rollback()
        raise SystemExit(1)
