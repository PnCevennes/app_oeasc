"""
Cache applicatif partagé (Flask-Caching, stockage fichier).

Le stockage fichier est partagé entre les workers gunicorn ET la ligne de commande (flask ...),
contrairement à un dict en mémoire propre à chaque process (ancien système : `config["_areas"]`,
`config["_nomenclature"]`, jamais invalidé).

- données de référence (nomenclatures, aires) : TTL long + suppression explicite
  (`flask clear-cache`, fin de `flask refresh-ref-geo`)
- résultats calculés (ex. bilan de chasse) : clé versionnée par `data_version()`, que toute
  écriture API / fin d'import incrémente via `invalidate_data()`.
"""

import time
from pathlib import Path

from flask_caching import Cache

cache = Cache()

TTL_REFERENCE = 3600  # nomenclatures, aires
TTL_RESULTATS = 600  # résultats calculés (filet de sécurité en plus de l'invalidation)

KEY_VERSION = "data_version"
KEY_NOMENCLATURE = "nomenclature_oeasc"


def init_cache(app):
    base = Path(app.root_path).parent / "data" / "cache" / "app"
    base.mkdir(parents=True, exist_ok=True)
    app.config.setdefault("CACHE_TYPE", "FileSystemCache")
    app.config.setdefault("CACHE_DIR", str(base))
    app.config.setdefault("CACHE_DEFAULT_TIMEOUT", TTL_REFERENCE)
    app.config.setdefault("CACHE_THRESHOLD", 1000)
    cache.init_app(app)


def data_version():
    """Version courante des données : change à chaque écriture (invalide les résultats calculés)."""
    version = cache.get(KEY_VERSION)
    if version is None:
        version = time.time_ns()
        cache.set(KEY_VERSION, version, timeout=0)
    return version


def invalidate_data():
    """À appeler après toute écriture en base qui modifie des résultats calculés."""
    cache.set(KEY_VERSION, time.time_ns(), timeout=0)


def clear_all():
    cache.clear()
