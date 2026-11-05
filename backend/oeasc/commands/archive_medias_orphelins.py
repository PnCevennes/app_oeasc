"""
Commande Flask CLI : flask archive-medias-orphelins

Archive les médias orphelins de static/medias/{img,doc} dans
archive/media_orphelins/

Un média est considéré comme utilisé si son nom (avec ou sans extension,
éventuellement encodé en URL) apparaît :
  - dans le contenu éditorial en base (oeasc_commons.t_contents.md)
  - dans le code (frontend/src, frontend/dist, backend/oeasc)
Les fichiers logos_* sont toujours conservés : leur nom est construit
dynamiquement par le frontend (liste-partenaire.vue).

Rien n'est supprimé : les fichiers sont déplacés en conservant leur
sous-dossier (img/ ou doc/), donc réversible par un simple mv inverse.

Usage :
    flask archive-medias-orphelins            # simulation (dry-run)
    flask archive-medias-orphelins --apply    # déplace réellement
"""

import shutil
import unicodedata
import urllib.parse
from pathlib import Path

import click
from flask.cli import with_appcontext
from sqlalchemy import text

BASE_DIR = Path(__file__).resolve().parents[3]
CODE_DIRS = ("frontend/src", "frontend/dist", "backend/oeasc")
CODE_SUFFIXES = {".vue", ".js", ".py", ".html", ".json", ".md", ".css"}
IGNORED_PARTS = {"node_modules", "__pycache__"}


def _norm(s):
    return unicodedata.normalize("NFC", s)


def _read_code(base):
    """Concatène les sources susceptibles de citer un média."""
    code = []
    for rel in CODE_DIRS:
        d = base / rel
        if not d.is_dir():
            continue
        for p in d.rglob("*"):
            if not p.is_file() or p.suffix not in CODE_SUFFIXES:
                continue
            if IGNORED_PARTS & set(p.parts):
                continue
            code.append(p.read_text(errors="replace"))
    return _norm("\n".join(code))


def _find_orphans(medias, md, code):
    orphelins = []
    for sous_dossier in ("img", "doc"):
        d = medias / sous_dossier
        if not d.is_dir():
            continue
        for f in sorted(d.iterdir()):
            if not f.is_file() or f.name.startswith("."):
                continue
            nom = _norm(f.name)
            racine = _norm(f.stem)
            if nom.startswith("logos_"):
                continue
            if nom in md or nom in code or racine in md:
                continue
            orphelins.append(f)
    return orphelins


@click.command("archive-medias-orphelins")
@click.option(
    "--apply",
    "apply_",
    is_flag=True,
    default=False,
    help="Déplace réellement les fichiers (sinon simulation).",
)
@with_appcontext
def archive_medias_orphelins_cmd(apply_):
    """Archive les médias orphelins de static/medias/{img,doc} dans archive/media_orphelins/."""
    from oeasc.utils.env import db

    medias = BASE_DIR / "static" / "medias"
    archive = BASE_DIR / "archive" / "media_orphelins"

    click.echo("Lecture du contenu éditorial en base…")
    rows = db.session.execute(
        text("select md from oeasc_commons.t_contents")
    ).fetchall()
    md_raw = "\n".join(r[0] for r in rows if r[0])
    if not md_raw.strip():
        raise click.ClickException(
            "Contenu éditorial vide : arrêt par sécurité "
            "(aucun média ne serait référencé)."
        )

    md = _norm(urllib.parse.unquote(md_raw))
    code = _read_code(BASE_DIR)
    orphelins = _find_orphans(medias, md, code)

    taille = sum(f.stat().st_size for f in orphelins)
    click.echo(f"{len(orphelins)} média(s) orphelin(s), {taille / 1e6:.1f} Mo")
    for f in orphelins:
        click.echo(f"  {f.parent.name}/{f.name}  ({f.stat().st_size / 1e3:.0f} Ko)")

    if not apply_:
        click.echo(
            "\nSimulation : rien n'a été déplacé. "
            "Relancer avec --apply pour archiver."
        )
        return

    for f in orphelins:
        dest_dir = archive / f.parent.name
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / f.name
        i = 1
        while dest.exists():
            dest = dest_dir / f"{f.stem}.{i}{f.suffix}"
            i += 1
        shutil.move(str(f), str(dest))
    if orphelins:
        click.echo(f"\nDéplacé dans {archive}")
