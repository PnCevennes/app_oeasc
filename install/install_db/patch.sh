# patch.sh
. install/install_db/pgsqla.sh

echo "
 UPDATE utilisateurs.bib_organismes
 SET nom_organisme='Autre (préciser)' WHERE nom_organisme LIKE '- A%'
;



" | $psqla
