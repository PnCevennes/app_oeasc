settings=$1

if [ -z "$1" ];
then 
echo 'Veuillez specifier un fichier settings.ini'
exit 1
fi

log_file=/tmp/init_view_oeasc.log
echo 'init_view oeasc' > $log_file
. $settings

cat $settings

for file in $(echo \
    "oeasc_commons_views.sql" \
    "oeasc_declarations_views.sql" \
    "oeasc_declarations_resultats_views.sql" \
    )
do

EXEC_DIR=$(readlink -e "${0%/*}")

sql_file=${EXEC_DIR}/$file
echo "exec $sql_file" >> $log_file
echo "export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name -f $sql_file  &>> $log_file"
export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name -f $sql_file  &>> $log_file
done

echo "process data oeasc done" &>> $log_file

# cat $log_file

cat $log_file | grep 'ERROR'

exit 0
