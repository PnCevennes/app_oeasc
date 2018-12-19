# patch.sh
. install/install_db/psqla.sh

dir_script=install/install_db

$psqla -f $dir_script/oeasc/oeasc_views.sql

echo "GRANT USAGE ON SCHEMA oeasc TO $user_pg_save;
    GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA oeasc TO $user_pg_save;
    GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA oeasc TO $user_pg_save;
    GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA ref_geo TO $user_pg_save;
    GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA ref_geo TO $user_pg_save;
    GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA utilisateurs TO $user_pg_save;
    GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA utilisateurs TO $user_pg_save;
    " | $psqla

echo | $psqla
