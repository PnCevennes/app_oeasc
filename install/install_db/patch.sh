# patch.sh
. install/install_db/psqla.sh

dir_script=install/install_db

$psqla -f $dir_script/oeasc/oeasc_views.sql
