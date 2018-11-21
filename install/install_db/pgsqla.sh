# pgsqla.sh

if [[ "$ROOT_DIR" = "" ]]; then
    ROOT_DIR=$(readlink -e "${0%/*}")/../..
fi

setting_file=${ROOT_DIR}/config/settings.ini

. $setting_file

psqla=$(echo "psql -d $db_name -h $db_host -U $user_pg")

export PGPASSWORD="$user_pg_pass"
