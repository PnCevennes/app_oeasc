settings=$1

if [ -z "$1" ];
then 
echo 'Veuillez specifier un fichier settings.ini'
exit 1
fi

log_file=/tmp/init_view_oeasc.log
echo 'init_view oeasc' > $log_file
. $settings

# cat $settings
    
EXEC_DIR=$(readlink -e "${0%/*}")

pwd
cp $EXEC_DIR/oeasc_in.csv /tmp/.

for file in $(echo \
    "../oeasc_schemas/oeasc_in.sql" \
    "../oeasc_schemas/oeasc_in_import_data.sql" \
    "../oeasc_views/oeasc_in_views.sql" \
    )
do


sql_file=${EXEC_DIR}/$file
echo "exec $sql_file" >> $log_file
echo "export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name -f $sql_file  &>> $log_file"
export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name -f $sql_file  &>> $log_file
done

echo "process data oeasc done" &>> $log_file

# cat $log_file

cat $log_file | grep 'ERR'

exit 0
