#!/bin/bash
# À sourcer (`. install/load_config.sh [fichier.yaml]`) : charge la configuration de
# install/config_principal.yaml dans des variables bash (db_host, user_pg, user_pg_pass, ...).
# Remplace `. config/settings.ini`. Nécessite python3 avec PyYAML (le venv du projet est utilisé s'il existe).

_lc_dir=$(readlink -e "$(dirname "${BASH_SOURCE[0]}")")
_lc_python=python3
[ -x "${_lc_dir}/../venv/bin/python" ] && _lc_python="${_lc_dir}/../venv/bin/python"

_lc_vars=$("${_lc_python}" "${_lc_dir}/load_config.py" "$@") || {
    echo "Erreur de lecture de la configuration (config_principal.yaml, PyYAML installé ?)" >&2
    return 1 2>/dev/null || exit 1
}
eval "${_lc_vars}"
unset _lc_dir _lc_python _lc_vars
