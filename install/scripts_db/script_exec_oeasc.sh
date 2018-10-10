if [[ "$ROOT_DIR" = "" ]]; then
    ROOT_DIR=$(readlink -e "${0%/*}")/../..
fi
config_file=${ROOT_DIR}/install/scripts_db/script_config.sh
. $config_file

echo ${0##/*/}

file_SQL_OEASC=$ROOT_DIR/$sql_dir/SQL/oeasc.sql

echo process file $file_SQL_OEASC

#functions
cat $ROOT_DIR/$sql_dir/SQL/functions.sql | psql -d $db_name -h $db_host -U $user_pg

#schema oeasc
cat $ROOT_DIR/$sql_dir/SQL/oeasc_create_schema.sql |psql -d $db_name -h $db_host -U $user_pg

#populature organismes
dir_data_user=$ROOT_DIR/data/csv/user
cp $dir_data_user/*.csv /tmp/.
cat $ROOT_DIR/$sql_dir/SQL/oeasc_populate_organismes.sql | sed -e s,"__ROOT_DIR__","${ROOT_DIR}",g | psql -d $db_name -h $db_host -U $user_pg

# populate oeasc.t_forets
dir_data_foret=$ROOT_DIR/data/csv/foret
cp $dir_data_foret/*.csv /tmp/.
cat $ROOT_DIR/$sql_dir/SQL/oeasc_populate_frt.sql | sed -e s,"__ROOT_DIR__","${ROOT_DIR}",g | psql -d $db_name -h $db_host -U $user_pg

${ROOT_DIR}/install/scripts_db/script_init_users.sh
