# patch.sh
echo "
UPDATE utilisateurs.bib_organismes
SET nom_organisme='Aucun' WHERE nom_organisme LIKE 'Pas d%'
;

" | $psqla
