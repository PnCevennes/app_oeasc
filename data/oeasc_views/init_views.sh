settings=$1

set -eo pipefail
if [ -z "$1" ];
then
echo 'Veuillez specifier un fichier settings.ini'
exit 1
fi

log_file=/tmp/init_view_oeasc.log
echo 'init_view oeasc' > $log_file
. $settings

# cat $settings
for file in $(echo \
    "../oeasc_schemas/oeasc_functions.sql" \
    "oeasc_commons_views.sql" \
    "oeasc_declarations_views.sql" \
    "../in/oeasc_in_views.sql" \
    "../chasse/views_chasse.sql" \
    "../chasse/result_ice.sql" \
    "../chasse/views_export_chasse.sql" \
    )
do

EXEC_DIR=$(readlink -e "${0%/*}")

sql_file=${EXEC_DIR}/$file
echo "exec $sql_file" >> $log_file
echo "export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name -f $sql_file  &>> $log_file"

export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name -f $sql_file -v ON_ERROR_STOP=ON
done

echo "process data oeasc done" &>> $log_file

# cat $log_file

cat $log_file | grep 'ERR' || echo 'creation des vues ok'

exit 0
