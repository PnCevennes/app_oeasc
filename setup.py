import setuptools
from pathlib import Path

# Définition du répertoire racine du projet (là où se trouve ce fichier setup.py)
root_dir = Path(__file__).absolute().parent

# Lecture du numéro de version depuis le fichier VERSION
with (root_dir / "VERSION").open() as f:
    version = f.read().strip()

# Lecture du contenu du fichier README.md pour la description longue du package
readme_path = root_dir / "README.md"
long_description = readme_path.read_text() if readme_path.exists() else ""

### Méta-données et configuration du package ###
setuptools.setup(
    name="oeasc",  # Nom du package
    description="",  # Courte description (à compléter)
    long_description=long_description,  # Description longue (affichée sur PyPI)
    long_description_content_type="text/markdown",  # Format du README
    maintainer="Parc national des Cévennes",  # Nom du mainteneur
    maintainer_email="admin_si@cevennes-parcnational.fr",  # Email du mainteneur
    url="https://github.com/PnX-SI/GeoNature/",  # URL du projet
    python_requires=">=3.8",  # Version minimale de Python requise
    version=version,  # Version du package (lue dans VERSION)
    # Recherche des packages dans le dossier 'backend', incluant uniquement 'oeasc'
    packages=setuptools.find_packages(where="backend", include=["oeasc"]),
    package_dir={
        "": "backend",  # Indique que les packages sont dans le dossier 'backend'
    },
    # Fichiers supplémentaires à inclure dans le package (templates, static, migrations, etc.)
    package_data={
        "oeasc": ["**/templates/**/*.html", "**/static/**/*"],
        "oeasc.migrations": ["alembic.ini", "script.py.mako", "data/*.sql"],
    },
    # Points d'entrée pour l'intégration avec Alembic (utilisé lors des migrations de base de données)
    entry_points={
        "alembic": [
            "migrations = oeasc.migrations:versions",
        ],
    },
    # Dépendances du package (lues depuis requirements.txt)
    install_requires=list(
        open("requirements.txt", "r"),
    ),
    # Dépendances optionnelles pour les tests et la documentation
    extras_require={
        "tests": [
            "pytest",
            "pytest-flask",
            "pytest-benchmark",
            "pytest-cov",
        ],
        "doc": [],
    },
    # Classificateurs pour PyPI (indiquent le framework, la version de Python, etc.)
    classifiers=[
        "Framework :: Flask",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
    ],
)

# Ce fichier setup.py est utilisé lors de l'installation ou la distribution du package.
# Il est exécuté par la commande 'pip install .' ou 'python setup.py install'.
