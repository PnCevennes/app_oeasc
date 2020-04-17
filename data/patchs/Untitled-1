UPDATE utilisateurs.t_roles r SET champs_addi = a.champs_addi
FROM (
SELECT 
	t.id_role,
	CASE 
		WHEN champs_addi IS NOT NULL THEN jsonb '{}' || champs_addi - 'accept_email' || jsonb '{"accept_email": true}'
		ELSE jsonb '{"accept_email": true}'
	END AS champs_addi
FROM utilisateurs.t_roles t
JOIN oeasc_commons.v_users  vu ON vu.id_role = t.id_role
) a
WHERE a.id_role = r.id_role;

SELECT champs_addi FROM utilisateurs.t_roles;
