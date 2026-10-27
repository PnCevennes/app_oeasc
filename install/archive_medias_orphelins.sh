#!/usr/bin/env bash
#
# Archive les médias orphelins de static/medias/{img,doc} dans archive/media_orphelins/
#
# Un média est considéré comme utilisé si son nom (avec ou sans extension,
# éventuellement encodé en URL) apparaît :
#   - dans le contenu éditorial en base (oeasc_commons.t_contents.md)
#   - dans le code (frontend/src ou frontend/dist, backend/oeasc, config)
# Les fichiers logos_* sont toujours conservés : leur nom est construit
# dynamiquement par le frontend (liste-partenaire.vue).
#
# Rien n'est supprimé : les fichiers sont déplacés en conservant leur
# sous-dossier (img/ ou doc/), donc réversible par un simple mv inverse.
#
# Usage :
#   ./install/archive_medias_orphelins.sh            # simulation (dry-run)
#   ./install/archive_medias_orphelins.sh --apply    # déplace réellement
#
# Prérequis : psql, python3, SQLALCHEMY_DATABASE_URI dans config/config.py

set -eo pipefail

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
BASE_DIR=$(dirname "${SCRIPT_DIR}")

APPLY=0
case "${1:-}" in
    "") ;;
    --apply) APPLY=1 ;;
    *) echo "Usage : $0 [--apply]" >&2; exit 1 ;;
esac

CONFIG_FILE="${BASE_DIR}/config/config.py"
DB_URI=$(sed -nE 's/^SQLALCHEMY_DATABASE_URI\s*=\s*"(.*)"/\1/p' "${CONFIG_FILE}" | head -1)
if [ -z "${DB_URI}" ]; then
    echo "SQLALCHEMY_DATABASE_URI introuvable dans ${CONFIG_FILE}" >&2
    exit 1
fi

TMP_MD=$(mktemp)
trap 'rm -f "${TMP_MD}"' EXIT

echo "Lecture du contenu éditorial en base…"
psql "${DB_URI}" -At -c "select md from oeasc_commons.t_contents" > "${TMP_MD}"
if [ ! -s "${TMP_MD}" ]; then
    echo "Contenu éditorial vide : arrêt par sécurité (aucun média ne serait référencé)." >&2
    exit 1
fi

BASE_DIR="${BASE_DIR}" TMP_MD="${TMP_MD}" APPLY="${APPLY}" python3 -I - <<'EOF'
import os
import shutil
import subprocess
import unicodedata
import urllib.parse
from pathlib import Path

base = Path(os.environ["BASE_DIR"])
apply = os.environ["APPLY"] == "1"
medias = base / "static" / "medias"
archive = base / "archive" / "media_orphelins"


def norm(s):
    return unicodedata.normalize("NFC", s)


md = norm(urllib.parse.unquote(Path(os.environ["TMP_MD"]).read_text(errors="replace")))

# Texte du code : concaténation des sources susceptibles de citer un média
code_dirs = [
    base / "frontend" / "src",
    base / "frontend" / "dist",
    base / "backend" / "oeasc",
    base / "config",
]
code = []
for d in code_dirs:
    if not d.is_dir():
        continue
    for p in d.rglob("*"):
        if p.is_file() and p.suffix in {".vue", ".js", ".py", ".html", ".json", ".md", ".css"}:
            if "node_modules" in p.parts or "__pycache__" in p.parts:
                continue
            code.append(p.read_text(errors="replace"))
code = norm("\n".join(code))

orphelins = []
for sous_dossier in ("img", "doc"):
    d = medias / sous_dossier
    if not d.is_dir():
        continue
    for f in sorted(d.iterdir()):
        if not f.is_file() or f.name.startswith("."):
            continue
        nom = norm(f.name)
        racine = norm(f.stem)
        if nom.startswith("logos_"):
            continue
        if nom in md or nom in code or racine in md:
            continue
        orphelins.append(f)

taille = sum(f.stat().st_size for f in orphelins)
print(f"{len(orphelins)} média(s) orphelin(s), {taille / 1e6:.1f} Mo")
for f in orphelins:
    print(f"  {f.parent.name}/{f.name}  ({f.stat().st_size / 1e3:.0f} Ko)")

if not apply:
    print("\nSimulation : rien n'a été déplacé. Relancer avec --apply pour archiver.")
elif orphelins:
    for f in orphelins:
        dest_dir = archive / f.parent.name
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / f.name
        i = 1
        while dest.exists():
            dest = dest_dir / f"{f.stem}.{i}{f.suffix}"
            i += 1
        shutil.move(str(f), str(dest))
    print(f"\nDéplacé dans {archive}")
EOF
