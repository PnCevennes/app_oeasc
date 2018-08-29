if [[ "$ROOT_DIR" = "" ]]; then
    ROOT_DIR=$(readlink -e "${0%/*}")/../..
fi
config_file=${ROOT_DIR}/install/scripts_db/script_config.sh
. $config_file

echo ${0##/*/}

${ROOT_DIR}/install/scripts_db/script_create_all.sh
${ROOT_DIR}/install/scripts_db/script_exec_all.sh
