"""
Commande Flask CLI : flask init-db

Crée la base de données de l'application sur une base PostgreSQL vide
(la base et l'utilisateur doivent exister, cf. install/config_principal.yaml).

Étapes :
  1. extensions PostgreSQL (postgis, uuid-ossp, ...)
  2. schémas des dépendances, via leurs migrations Alembic :
     utilisateurs (pypnusershub), ref_nomenclatures (pypnnomenclature), ref_geo
  3. tables de l'application (schémas oeasc_*, ref_geo.cor_*) créées depuis les modèles
     SQLAlchemy, puis la branche Alembic « oeasc » est marquée à jour (stamp)
  4. fonctions et vues SQL (data/oeasc_views/ et install/data/)
  5. données initiales : nomenclatures OEASC, organismes, application, groupes et administrateur

Usage :
    flask init-db [--skip-views] [--skip-data]

La commande peut être relancée : chaque étape ne fait que ce qui manque.
Si les tables de l'application existent déjà, elles ne sont pas touchées
(utiliser `flask db upgrade <révision>` pour les faire évoluer).
"""

import csv
import logging
from pathlib import Path

import bcrypt
import click
from flask import current_app
from flask.cli import with_appcontext
from flask_migrate import stamp, upgrade
from sqlalchemy import inspect, text

LOG = logging.getLogger(__name__)

SRID_LOCAL = 2154

EXTENSIONS = [
    "uuid-ossp",
    "postgis",
    "postgis_raster",
    "unaccent",
    "intarray",
    "pg_trgm",
    "plr",  # fonctions de régression de l'indice ICE (oeasc_chasse.fct_calcul_ice_mc)
]

# branches Alembic des dépendances (installées avec les paquets pypn*)
BRANCHES_DEPENDANCES = ["sql_utils@head", "utilisateurs@head", "nomenclatures@head"]

# schémas dont les tables sont créées depuis les modèles
SCHEMAS_OEASC = [
    "oeasc_commons",
    "oeasc_forets",
    "oeasc_declarations",
    "oeasc_in",
    "oeasc_chasse",
    "oeasc_agricole",
]
# tables de ref_geo propres à l'application (le reste de ref_geo vient du paquet ref_geo)
TABLES_REF_GEO_OEASC = {"communes_aoa", "cor_area_intersect", "cor_hierarchie_area"}

# fichiers SQL (fonctions et vues), relatifs à la racine du projet, dans l'ordre d'exécution
FICHIERS_SQL = [
    "install/data/functions/generic.sql",
    "install/data/functions/nomenclatures.sql",
    "install/data/functions/ref_geo.sql",
    "install/data/oeasc_schemas/oeasc_functions.sql",
    "data/oeasc_views/oeasc_commons_views.sql",
    "data/oeasc_views/oeasc_chasse_views.sql",
]

# groupes d'utilisateurs de l'application : (nom, id_profil)
# tables de l'application avec trigger de mise à jour des dates (chasse : dans oeasc_chasse_views.sql)
TABLES_META_DATES = ["oeasc_commons.t_contents", "oeasc_declarations.t_declarations"]

GROUPES = [
    ("Grp OEASC Administrateur", 6),
    ("Grp OEASC Validateur", 5),
    ("Grp OEASC Moderateur", 4),
    ("Grp OEASC Referent", 3),
    ("Grp OEASC Redacteur", 2),
    ("Grp OEASC Lecteur", 1),
]

PROFIL_ADMIN = 6
ID_APP_USERSHUB = 1


def _etape(message):
    click.echo(f"==> {message}")


def _racine():
    return Path(current_app.config["ROOT_DIR"])


def _migrations_dir():
    return current_app.extensions["migrate"].directory


def _db():
    return current_app.config["DB"]


def _tables_oeasc():
    """Tables des modèles SQLAlchemy qui appartiennent à l'application (hors vues mappées)."""
    tables = []
    for table in _db().metadata.sorted_tables:
        if table.name.startswith(("v_", "vm_")):
            continue  # vues et vues matérialisées mappées sur des modèles
        if table.schema in SCHEMAS_OEASC or (
            table.schema == "ref_geo" and table.name in TABLES_REF_GEO_OEASC
        ):
            tables.append(table)
    return tables


def creer_extensions():
    _etape("Extensions PostgreSQL")
    db = _db()
    for extension in EXTENSIONS:
        try:
            db.session.execute(text(f'CREATE EXTENSION IF NOT EXISTS "{extension}"'))
            db.session.commit()
        except Exception as e:  # droits insuffisants, extension absente du serveur...
            db.session.rollback()
            raise click.ClickException(
                f"Extension {extension} impossible à créer ({e.__class__.__name__}). "
                "Elle doit être créée par un superutilisateur PostgreSQL : "
                f'psql -d <base> -c \'CREATE EXTENSION "{extension}"\''
            )


def creer_schemas_dependances():
    _etape("Schémas utilisateurs, ref_nomenclatures, ref_geo (migrations Alembic)")
    for revision in BRANCHES_DEPENDANCES:
        upgrade(directory=_migrations_dir(), revision=revision)
    upgrade(
        directory=_migrations_dir(),
        revision="ref_geo@head",
        x_arg=[f"local-srid={SRID_LOCAL}"],
    )
    # colonne ajoutée par UsersHub, utilisée par la vue oeasc_commons.v_users
    _db().session.execute(
        text("ALTER TABLE utilisateurs.bib_organismes ADD COLUMN IF NOT EXISTS mnemo varchar")
    )
    _db().session.commit()


def creer_tables_oeasc():
    """Crée les tables depuis les modèles. Retourne True si c'est une installation neuve."""
    _etape("Tables de l'application (modèles SQLAlchemy)")
    db = _db()
    tables = _tables_oeasc()

    inspecteur = inspect(db.engine)
    existantes = [
        t.fullname
        for t in tables
        if inspecteur.has_table(t.name, schema=t.schema)
    ]
    if existantes:
        click.echo(
            f"    {len(existantes)} table(s) de l'application existent déjà : "
            "création des tables et stamp Alembic ignorés "
            "(utiliser `flask db upgrade <révision>` pour les faire évoluer)."
        )
        return False

    for schema in SCHEMAS_OEASC:
        db.session.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema}"))
    db.session.commit()

    db.metadata.create_all(db.engine, tables=tables)
    click.echo(f"    {len(tables)} tables créées")

    # geom est déclarée en 4326 dans le modèle mais contient du Lambert-93 (geom_4326 est la version WGS84)
    db.session.execute(
        text(
            "ALTER TABLE oeasc_declarations.t_declarations "
            "ALTER COLUMN geom TYPE geometry(MultiPolygon, 2154) USING ST_SetSRID(geom, 2154)"
        )
    )
    db.session.commit()

    # le schéma correspond aux modèles actuels : la branche oeasc est à jour
    stamp(directory=_migrations_dir(), revision="oeasc@head")
    return True


def executer_fichier_sql(chemin):
    """Exécute un fichier SQL en une seule fois (psycopg2 gère le multi-instructions)."""
    contenu = Path(chemin).read_text(encoding="utf-8")
    connexion = _db().engine.raw_connection()
    try:
        with connexion.cursor() as curseur:
            curseur.execute(contenu)
        connexion.commit()
    except Exception:
        connexion.rollback()
        raise
    finally:
        connexion.close()


def creer_fonctions_et_vues():
    _etape("Fonctions et vues SQL")
    for fichier in FICHIERS_SQL:
        chemin = _racine() / fichier
        if not chemin.exists():
            raise click.ClickException(f"Fichier SQL absent : {chemin}")
        click.echo(f"    {fichier}")
        try:
            executer_fichier_sql(chemin)
        except Exception as e:
            raise click.ClickException(f"Erreur dans {fichier} : {e}")

    db = _db()
    for table in TABLES_META_DATES:
        nom = "tri_meta_dates_change_" + table.split(".")[1]
        db.session.execute(text(f"DROP TRIGGER IF EXISTS {nom} ON {table}"))
        db.session.execute(
            text(
                f"CREATE TRIGGER {nom} BEFORE INSERT OR UPDATE ON {table} "
                "FOR EACH ROW EXECUTE FUNCTION fct_trg_meta_dates_change()"
            )
        )
    db.session.commit()


def _lire_csv(chemin, delimiteur=";"):
    with open(chemin, encoding="utf-8", newline="") as f:
        return list(csv.reader(f, delimiter=delimiteur, quotechar="'"))


def inserer_nomenclatures():
    _etape("Nomenclatures OEASC")
    dossier = _racine() / "install" / "data" / "csv" / "nomenclature"
    types = _lire_csv(dossier / "oeasc_bib_nomenclature.csv")
    nomenclatures = _lire_csv(dossier / "oeasc_nomenclature.csv")
    session = _db().session

    for mnemonique, label, definition in types:
        session.execute(
            text(
                """
                INSERT INTO ref_nomenclatures.bib_nomenclatures_types
                    (mnemonique, label_default, definition_default, label_fr, definition_fr, source)
                SELECT :m, :l, :d, :l, :d, 'OEASC'
                WHERE NOT EXISTS (
                    SELECT 1 FROM ref_nomenclatures.bib_nomenclatures_types WHERE mnemonique = :m
                )
                """
            ),
            {"m": mnemonique, "l": label, "d": definition},
        )

    for type_code, cd, mnemonique, label, definition in nomenclatures:
        session.execute(
            text(
                """
                INSERT INTO ref_nomenclatures.t_nomenclatures
                    (id_type, cd_nomenclature, mnemonique, label_default, definition_default,
                     label_fr, definition_fr, source)
                SELECT t.id_type, :cd, :m, :l, :d, :l, :d, 'OEASC'
                FROM ref_nomenclatures.bib_nomenclatures_types t
                WHERE t.mnemonique = :type_code
                AND NOT EXISTS (
                    SELECT 1 FROM ref_nomenclatures.t_nomenclatures n
                    WHERE n.id_type = t.id_type AND n.cd_nomenclature = :cd
                )
                """
            ),
            {"type_code": type_code, "cd": cd, "m": mnemonique, "l": label, "d": definition},
        )
    session.commit()
    click.echo(f"    {len(types)} types, {len(nomenclatures)} nomenclatures")


def inserer_organismes():
    _etape("Organismes")
    chemin = _racine() / "install" / "data" / "csv" / "user" / "organismes.csv"
    session = _db().session
    noms = [ligne.strip() for ligne in chemin.read_text(encoding="utf-8").splitlines() if ligne.strip()]
    for nom in noms:
        session.execute(
            text(
                """
                INSERT INTO utilisateurs.bib_organismes (nom_organisme)
                SELECT :nom
                WHERE NOT EXISTS (
                    SELECT 1 FROM utilisateurs.bib_organismes WHERE nom_organisme = :nom
                )
                """
            ),
            {"nom": nom},
        )
    session.commit()
    click.echo(f"    {len(noms)} organismes")


def inserer_application_et_administrateur():
    _etape("Application, groupes et administrateur")
    session = _db().session
    config = current_app.config
    id_app = config["ID_APP"]
    login = config["ADMIN_APPLICATION_LOGIN"]
    mail = config["ADMIN_APPLICATION_MAIL"]
    mot_de_passe = config["ADMIN_APPLICATION_PASSWORD"]

    # application OEASC et profils disponibles pour elle
    session.execute(
        text(
            """
            INSERT INTO utilisateurs.t_applications (id_application, code_application, nom_application, desc_application)
            VALUES (:id_app, 'OEASC', 'OEASC', 'application oeasc')
            ON CONFLICT (id_application) DO NOTHING
            """
        ),
        {"id_app": id_app},
    )
    session.execute(
        text(
            """
            INSERT INTO utilisateurs.cor_profil_for_app (id_profil, id_application)
            SELECT p.id_profil, :id_app FROM utilisateurs.t_profils p
            ON CONFLICT DO NOTHING
            """
        ),
        {"id_app": id_app},
    )

    # groupes de droits
    for nom, id_profil in GROUPES:
        session.execute(
            text(
                """
                INSERT INTO utilisateurs.t_roles (groupe, nom_role)
                SELECT true, :nom
                WHERE NOT EXISTS (
                    SELECT 1 FROM utilisateurs.t_roles WHERE groupe AND nom_role = :nom
                )
                """
            ),
            {"nom": nom},
        )
        session.execute(
            text(
                """
                INSERT INTO utilisateurs.cor_role_app_profil (id_role, id_application, id_profil, is_default_group_for_app)
                SELECT id_role, :id_app, :id_profil, false
                FROM utilisateurs.t_roles WHERE groupe AND nom_role = :nom
                ON CONFLICT DO NOTHING
                """
            ),
            {"nom": nom, "id_app": id_app, "id_profil": id_profil},
        )

    # administrateur : droits maximum sur l'application et sur UsersHub
    pass_plus = bcrypt.hashpw(mot_de_passe.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    session.execute(
        text(
            """
            INSERT INTO utilisateurs.t_roles (groupe, identifiant, nom_role, pass_plus, email, id_organisme)
            SELECT false, :login, 'Admin_OEASC', :pass_plus, :mail,
                (SELECT id_organisme FROM utilisateurs.bib_organismes
                 WHERE nom_organisme = 'Parc national des Cévennes' LIMIT 1)
            WHERE NOT EXISTS (
                SELECT 1 FROM utilisateurs.t_roles WHERE identifiant = :login
            )
            """
        ),
        {"login": login, "pass_plus": pass_plus, "mail": mail},
    )
    for app in (id_app, ID_APP_USERSHUB):
        session.execute(
            text(
                """
                INSERT INTO utilisateurs.cor_role_app_profil (id_role, id_application, id_profil, is_default_group_for_app)
                SELECT r.id_role, :app, :profil, false
                FROM utilisateurs.t_roles r
                WHERE r.identifiant = :login
                AND EXISTS (SELECT 1 FROM utilisateurs.t_applications WHERE id_application = :app)
                ON CONFLICT DO NOTHING
                """
            ),
            {"app": app, "profil": PROFIL_ADMIN, "login": login},
        )
    session.commit()
    click.echo(f"    administrateur : {login}")


@click.command("init-db")
@click.option("--skip-views", is_flag=True, help="Ne pas créer les fonctions et vues SQL")
@click.option("--skip-data", is_flag=True, help="Ne pas insérer les données initiales")
@with_appcontext
def init_db_cmd(skip_views, skip_data):
    """Crée la base de données de l'application (voir doc/install_db.md)."""
    creer_extensions()
    creer_schemas_dependances()
    creer_tables_oeasc()
    if not skip_views:
        creer_fonctions_et_vues()
    if not skip_data:
        inserer_nomenclatures()
        inserer_organismes()
        inserer_application_et_administrateur()
    click.echo("Base de données initialisée.")
