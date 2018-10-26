if [[ "$ROOT_DIR" = "" ]]; then
    ROOT_DIR=$(readlink -e "${0%/*}")/../..
fi
config_file=${ROOT_DIR}/install/scripts_db/script_config.sh
. $config_file

echo ${0##/*/}
echo psql -b -d $db_name -h $db_host -U $user_pg 

cat <<EOF | psql -b -d $db_name -h $db_host -U $user_pg 
DROP TABLE IF EXISTS temp;

CREATE TABLE temp (nom_organisme text, adresse_organisme text, cp_organisme text,
            ville_organisme text, tel_organisme text, email_organisme text);

\\COPY temp FROM '/tmp/organismes.csv' WITH DELIMITER ';' CSV QUOTE AS '''';

EOF

exit 1

