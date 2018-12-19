# pgsqla.sh

. config/settings.ini

if [ "$user_install" != "" ] && [ "$user_install_pass" != "" ]
then

    user_pg_save=$user_pg
    user_pg=$user_install
    export PGPASSWORD="$user_install_pass"

else

    export PGPASSWORD="$user_pg_pass"

fi

psqla=$(echo "psql -d $db_name -h $db_host -U $user_pg")

