# pgsqla.sh

. config/settings.ini

psqla=$(echo "psql -d $db_name -h $db_host -U $user_pg")

export PGPASSWORD="$user_pg_pass"
