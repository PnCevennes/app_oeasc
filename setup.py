import setuptools
from pathlib import Path


root_dir = Path(__file__).absolute().parent
with (root_dir / "VERSION").open() as f:
    version = f.read().strip()
with (root_dir / "README.md").open() as f:
    long_description = f.read()

### Méta-données du package ###
setuptools.setup(
    name="oeasc",
    description="",
    long_description=long_description,
    long_description_content_type="text/markdown",
    maintainer="Parc national des Cévennes",
    maintainer_email="admin_si@cevennes-parcnational.fr",
    url="https://github.com/PnX-SI/GeoNature/",
    python_requires=">=3.8",
    version=version,
    packages=setuptools.find_packages(where="backend", include=["oeasc"]),
    package_dir={
        "": "backend",
    },
    package_data={
        "oeasc": ["**/templates/**/*.html", "**/static/**/*"],
        "oeasc.migrations": ["alembic.ini", "script.py.mako", "data/*.sql"],
    },
    entry_points={
        "alembic": [
            "migrations = oeasc.migrations:versions",
        ],
    },
    install_requires=list(
        open("requirements.txt", "r"),
    ),
    extras_require={
        "tests": [
            "pytest",
            "pytest-flask",
            "pytest-benchmark",
            "pytest-cov",
        ],
        "doc": [],
    },
    classifiers=[
        "Framework :: Flask",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
    ],
)
