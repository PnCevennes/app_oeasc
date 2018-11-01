echo create schema oeasc >> $log_file
$psqla -f $dir_script/oeasc/oeasc.sql >> $log_file

cp $dir_data/csv/user/*.csv /tmp/.
echo oeasc_populate_organismes >> $log_file
$psqla -f $dir_script/oeasc/oeasc_populate_organismes.sql >> $log_file

cp $dir_data/csv/foret/*.csv /tmp/.
echo oeasc_populate_frt >> $log_file
$psqla -f $dir_script/oeasc/oeasc_populate_frt.sql >> $log_file
