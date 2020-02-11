UPDATE utilisateurs.t_roles r
SET champs_addi = a.champs_addi
FROM (
	SELECT ir.id_role, ir.nom_role, ir.prenom_role, ir.id_organisme, ir.organisme, json_build_object('organisme', TRIM(organisme)) As champs_addi
		FROM import_utilisateurs.t_roles ir
		JOIN utilisateurs.t_roles r ON r.id_organisme = 602 AND ir.id_role = r.id_role
		WHERE ir.id_organisme = 602

)a
WHERE a.id_role = r.id_role
