"""
    Fonctions utilisés pour l'installation et le chargement
    d'un nouveau module geonature
"""
import inspect
import subprocess
import logging
import os
import json
import sys
import shutil


from pathlib import Path
from packaging import version
from sqlalchemy.orm.exc import NoResultFound


from geonature.utils.config_schema import (
    GnGeneralSchemaConf,
    ManifestSchemaProdConf,
    GnModuleProdConf,
)
from geonature.utils import utilstoml
from geonature.utils.errors import GeoNatureError
from geonature.utils.command import (
    build_geonature_front,
    frontend_routes_templating,
)
from geonature.utils.command import get_app_for_cmd

from geonature.utils.env import (
    GEONATURE_VERSION,
    GN_MODULE_FILES,
    GN_EXTERNAL_MODULE,
    GN_MODULE_FE_FILE,
    ROOT_DIR,
    DB,
    DEFAULT_CONFIG_FIlE,
    load_config,
    import_requirements,
)
from geonature.utils.config_schema import ManifestSchemaConf
from geonature.core.users.models import TApplications
from geonature.core.gn_commons.models import TModules

log = logging.getLogger(__name__)


def check_gn_module_file(module_path):
    log.info("checking file")
    for file in GN_MODULE_FILES:
        if not (Path(module_path) / file).is_file():
            raise GeoNatureError("Missing file {}".format(file))
    log.info("...ok\n")


def check_manifest(module_path):
    """
    Verification de la version de geonature par rapport au manifest
    Retourne le nom du module
    """
    log.info("checking manifest")
    configs_py = utilstoml.load_and_validate_toml(
        str(Path(module_path) / "manifest.toml"), ManifestSchemaConf
    )

    gn_v = version.parse(GEONATURE_VERSION)
    if gn_v < version.parse(
        configs_py["min_geonature_version"]
    ) and gn_v > version.parse(configs_py["max_geonature_version"]):
        raise GeoNatureError(
            "Geonature version {} is imcompatible with module".format(GEONATURE_VERSION)
        )
    for e_gn_v in configs_py["exclude_geonature_versions"]:
        if gn_v == version.parse(e_gn_v):
            raise GeoNatureError(
                "Geonature version {} is imcompatible with module".format(
                    GEONATURE_VERSION
                )
            )
    log.info("...ok\n")
    return configs_py["module_name"]


def copy_in_external_mods(module_path, module_name):
    """
    Cree un lien symbolique du module dans GN_EXTERNAL_MODULE
    """
    cmd = "ln -s {} {}/{}".format(
        module_path, GN_EXTERNAL_MODULE.resolve(), module_name
    )
    try:
        assert subprocess.call(cmd.split(" ")) == 0
    except AssertionError as e:
        raise GeoNatureError(e)


def gn_module_register_config(module_name, url, id_app):
    """
    Création du fichier de configuration et
    enregistrement des variables du module dans
    le fichier conf_gn_module.toml du module

    """
    log.info("Register module")
    module_path = str(GN_EXTERNAL_MODULE / module_name)
    conf_gn_module_path = str(
        GN_EXTERNAL_MODULE / module_name / "config/conf_gn_module.toml"
    )
    conf_gn_module_file = open(conf_gn_module_path, "w")

    exist_config = utilstoml.load_toml(conf_gn_module_path)
    cmds = []
    if not "api_url" in exist_config:
        cmds.append(
            {
                "cmd": "sudo tee -a {}".format(conf_gn_module_path),
                "msg": "api_url = '/{}'\n".format(url.lstrip("/")).encode("utf8"),
            }
        )
    if not "id_application" in exist_config:
        cmds.append(
            {
                "cmd": "sudo tee -a {}".format(conf_gn_module_path),
                "msg": "id_application = {}\n".format(id_app).encode("utf-8"),
            }
        )
    for cmd in cmds:
        proc = subprocess.Popen(
            cmd["cmd"].split(" "), stdin=subprocess.PIPE, stdout=subprocess.DEVNULL
        )
        proc.stdin.write(cmd["msg"])
        proc.stdin.close()
        proc.wait()

    log.info("...ok\n")


def gn_module_import_requirements(module_path):
    req_p = Path(module_path) / "requirements.txt"
    if req_p.is_file():
        log.info("import_requirements")
        import_requirements(str(req_p))
        log.info("...ok\n")


def gn_module_activate(module_name, activ_front, activ_back):
    # TODO utiliser les commande os de python
    log.info("Activate module")

    # TODO gestion des erreurs
    if not (GN_EXTERNAL_MODULE / module_name).is_dir():
        raise GeoNatureError(
            "Module {} is not activated (Not in external_module directory)".format(
                module_name
            )
        )
    else:
        app = get_app_for_cmd(DEFAULT_CONFIG_FIlE)
        with app.app_context():
            try:
                module = (
                    DB.session.query(TModules)
                    .filter(TModules.module_name == module_name)
                    .one()
                )
                module.active_frontend = activ_front
                module.active_backend = activ_back
                DB.session.merge(module)
                DB.session.commit()
            except NoResultFound:
                raise GeoNatureError(
                    "The module does not exist. \n Check the gn_commons.t_module to get the module name"
                )
    log.info("Generate frontend routes")
    try:
        frontend_routes_templating()
        log.info("...ok\n")
    except Exception:
        log.error("Error while generating frontend routing")
        raise


def gn_module_deactivate(module_name, activ_front, activ_back):
    log.info("Desactivate module")
    try:
        app = get_app_for_cmd(DEFAULT_CONFIG_FIlE)
        with app.app_context():
            module = (
                DB.session.query(TModules)
                .filter(TModules.module_name == module_name)
                .one()
            )
            module.active_frontend = not activ_front
            module.active_backend = not activ_back
            DB.session.merge(module)
            DB.session.commit()
    except NoResultFound:
        raise GeoNatureError(
            "The module does not exist. \n Check the gn_commons.t_module to get the module name"
        )
    log.info("Regenerate frontend routes")
    try:
        frontend_routes_templating()
        log.info("...ok\n")
    except Exception as e:
        raise GeoNatureError(e)


def check_codefile_validity(module_path, module_name):
    """
    Vérification que les fichiers nécessaires
        au bon fonctionnement du module soient bien présents
        et avec la bonne signature
    """
    log.info("Checking file conformity")
    # Installation
    gn_file = Path(module_path) / "install_gn_module.py"
    if gn_file.is_file():
        try:
            from install_gn_module import gnmodule_install_app as fonc

            if not inspect.getargspec(fonc).args == ["gn_db", "gn_app"]:
                raise GeoNatureError("Invalid variable")
            log.info("      install_gn_module  OK")
        except (ImportError, GeoNatureError):
            raise GeoNatureError(
                """Module {}
                    File {} must have a function call :
                        gnmodule_install_app
                        with 2 parameters :
                        gn_db  :  database
                        gn_app :  application reference
                """.format(
                    module_name, gn_file
                )
            )
    # Backend
    gn_file = Path(module_path) / "backend/blueprint.py"
    if gn_file.is_file():
        try:
            from backend.blueprint import blueprint
        except (ImportError, GeoNatureError):
            raise GeoNatureError(
                """Module {}
                    File {} must have a variable call :
                        blueprint instance of Blueprint
                """.format(
                    module_name, gn_file
                )
            )
        from flask import Blueprint

        if isinstance(blueprint, Blueprint) is False:
            raise GeoNatureError(
                """Module {}
                        File {} :
                            blueprint is not an instance of Blueprint
                """.format(
                    module_name, gn_file
                )
            )
        log.info("      backend/blueprint/blueprint.py  OK")
    # Font-end
    gn_file = Path(module_path) / "{}.ts".format(GN_MODULE_FE_FILE)
    if gn_file.is_file():
        if "export class GeonatureModule" in open(str(gn_file)).read():
            log.info("      {}  OK".format(GN_MODULE_FE_FILE))
        else:
            raise GeoNatureError(
                """Module {} ,
                    File {} must have a function call :
                        export class GeonatureModule
                """.format(
                    module_name, gn_file
                )
            )
    # Config
    gn_dir = Path(module_path) / "config"
    if gn_dir.is_dir():
        log.info("Config directory ...ok")
    else:
        raise GeoNatureError(
            """Module {} ,
                    No config directory
                """.format(
                module_name, gn_file
            )
        )
    log.info("...ok\n")


def create_external_assets_symlink(module_path, module_name):
    """
    Create a symlink for the module assets
    """
    module_assets_dir = os.path.join(module_path, "frontend/assets")

    # test if module have frontend
    if not Path(module_assets_dir).is_dir():
        log.info("no frontend for this module \n")
        return

    geonature_asset_symlink = os.path.join(
        str(ROOT_DIR), "frontend/src/external_assets", module_name
    )
    # create the symlink if not exist
    try:
        if not os.path.isdir(geonature_asset_symlink):
            log.info("Create a symlink for assets \n")
            subprocess.call(
                ["ln", "-s", module_assets_dir, module_name],
                cwd=str(ROOT_DIR / "frontend/src/external_assets"),
            )
        else:
            log.info("symlink already exist \n")

        log.info("...ok \n")
    except Exception as e:
        log.info("...error when create symlink externalassets \n")
        raise GeoNatureError(e)


def add_application_db(module_name, url, module_id=None):
    log.info("Register the module in t_application ... \n")
    app_conf = load_config(DEFAULT_CONFIG_FIlE)
    id_application_geonature = app_conf["ID_APPLICATION_GEONATURE"]
    app = get_app_for_cmd(DEFAULT_CONFIG_FIlE)
    try:
        with app.app_context():
            # if module_id: try to insert in t_application
            # check if the module in TApplications
            if module_id is None:
                try:
                    exist_app = None
                    exist_app = (
                        DB.session.query(TApplications)
                        .filter(TApplications.nom_application == module_name)
                        .one()
                    )
                except NoResultFound:
                    # if no result, write in TApplication
                    new_application = TApplications(
                        nom_application=module_name, id_parent=id_application_geonature
                    )
                    DB.session.add(new_application)
                    DB.session.commit()
                    DB.session.flush()
                    module_id = new_application.id_application
                else:
                    log.info("the module is already in t_application")
                finally:
                    module_id = (
                        module_id if module_id is not None else exist_app.id_application
                    )
            # try to write in gn_commons.t_module if not exist
            try:
                module = (
                    DB.session.query(TModules)
                    .filter(TModules.module_name == module_name)
                    .one()
                )
            except NoResultFound:
                update_url = "{}/#/{}".format(app_conf["URL_APPLICATION"], url)
                new_module = TModules(
                    id_module=module_id,
                    module_name=module_name,
                    module_label=module_name.title(),
                    module_url=update_url,
                    module_target="_self",
                    module_picto="extension",
                    active_frontend=True,
                    active_backend=True,
                )
                DB.session.add(new_module)
                DB.session.commit()
            else:
                log.info("the module is already in t_module, reactivate it")
                module.active = True
                DB.session.merge(module)
                DB.session.commit()

    except Exception as e:
        raise GeoNatureError(e)

    log.info("... ok \n")
    return module_id


def create_module_config(module_name, mod_path=None, build=True):
    """
    Create the frontend config
    """
    if not mod_path:
        mod_path = str(GN_EXTERNAL_MODULE / module_name)
    manifest_path = os.path.join(mod_path, "manifest.toml")
    """ Create the frontend config for a module and rebuild if build=True"""
    conf_manifest = utilstoml.load_and_validate_toml(
        manifest_path, ManifestSchemaProdConf
    )

    # import du module dans le sys.path
    module_parent_dir = str(Path(mod_path).parent)
    module_schema_conf = "{}.config.conf_schema_toml".format(Path(mod_path).name)
    sys.path.insert(0, module_parent_dir)
    module = __import__(module_schema_conf, globals=globals())
    front_module_conf_file = os.path.join(mod_path, "config/conf_gn_module.toml")
    config_module = utilstoml.load_and_validate_toml(
        front_module_conf_file, module.config.conf_schema_toml.GnModuleSchemaConf
    )

    frontend_config_path = os.path.join(mod_path, "frontend/app/module.config.ts")
    with open(str(ROOT_DIR / frontend_config_path), "w") as outputfile:
        outputfile.write("export const ModuleConfig = ")
        json.dump(config_module, outputfile, indent=True, sort_keys=True)
    if build:
        build_geonature_front()
