-- groups for oeasc in t_roles
INSERT INTO utilisateurs.t_roles(
            groupe, nom_role, prenom_role, active)
	VALUES 
		(TRUE, 'Grp OEASC Administrateur', '6', TRUE),
		(TRUE, 'Grp OEASC Validateur', '5', TRUE),
		(TRUE, 'Grp OEASC Moderateur', '4', TRUE),
		(TRUE, 'Grp OEASC Referent', '3', TRUE),
		(TRUE, 'Grp OEASC Redacteur', '2', TRUE),
		(TRUE, 'Grp OEASC Lecteur', '1', TRUE)
;

-- group for oeasc in cor_role_app_profil
INSERT INTO utilisateurs.cor_role_app_profil(
	id_role, id_profil, id_application, is_default_group_for_app
	)
SELECT id_role, id_profil, 500, code_profil='1'
FROM utilisateurs.t_roles r
JOIN utilisateurs.t_profils 
	ON code_profil = r.prenom_role
WHERE r.nom_role LIKE '%OEASC%'

-- cor_roles
INSERT INTO utilisateurs.cor_roles (id_role_groupe, id_role_utilisateur)
SELECT c.id_role AS id_role_group, ci.id_role--, ci.id_droit, p.code_profil, r.nom_role, r.prenom_role
	FROM import_utilisateurs.cor_role_droit_application ci
	JOIN utilisateurs.t_profils p ON 
		p.code_profil = ci.id_droit::text
	JOIN utilisateurs.cor_role_app_profil c
		ON c.id_application = 500 AND c.id_profil = p.id_profil
	JOIN utilisateurs.t_roles r 
		ON r.id_role = ci.id_role	
	WHERE ci.id_application = 500
	ORDER BY ci.id_droit desc
