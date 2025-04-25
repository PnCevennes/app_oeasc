from __future__ import with_statement

import logging
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Ceci est l'objet de configuration Alembic, qui fournit
# l'accès aux valeurs du fichier .ini utilisé.
config = context.config

# Interpréter le fichier de configuration pour la journalisation Python.
# Cette ligne configure essentiellement les loggers.
fileConfig(config.config_file_name)
logger = logging.getLogger("alembic.env")

# Configuration de la connexion à la base de données.
from flask import current_app

config.set_main_option(
    "sqlalchemy.url",
    str(current_app.extensions["migrate"].db.engine.url).replace("%", "%%"),
)
target_metadata = current_app.extensions["migrate"].db.metadata

# D'autres valeurs de la configuration, définies par les besoins de env.py,
# peuvent être acquises :
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline():
    """Exécuter les migrations en mode 'offline'.

    Cela configure le contexte avec juste une URL
    et non un Engine, bien qu'un Engine soit acceptable
    ici aussi. En évitant la création de l'Engine,
    nous n'avons même pas besoin d'un DBAPI disponible.

    Les appels à context.execute() ici émettent la chaîne donnée à la
    sortie du script.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Exécuter les migrations en mode 'online'.

    Dans ce scénario, nous devons créer un Engine
    et associer une connexion avec le contexte.

    """

    # Ce callback est utilisé pour empêcher la génération d'une auto-migration
    # lorsqu'il n'y a pas de changements dans le schéma
    # référence : http://alembic.zzzcomputing.com/en/latest/cookbook.html
    def process_revision_directives(context, revision, directives):
        if getattr(config.cmd_opts, "autogenerate", False):
            script = directives[0]
            if script.upgrade_ops.is_empty():
                directives[:] = []
                logger.info("Aucun changement dans le schéma détecté.")

    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            process_revision_directives=process_revision_directives,
            **current_app.extensions["migrate"].configure_args
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
