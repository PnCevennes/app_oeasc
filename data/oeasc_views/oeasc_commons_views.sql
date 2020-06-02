DROP VIEW IF EXISTS oeasc_commons.v_users CASCADE;
CREATE VIEW oeasc_commons.v_users AS
SELECT 
	r.id_role,
	r.identifiant,
	r.email,
	UPPER(r.nom_role)  || ' ' || r.prenom_role AS nom_complet,
	r.nom_role, 
	r.prenom_role,
	r.desc_role,
    r.id_organisme,
    (r.champs_addi ->> 'accept_email')::boolean AS accept_email,
    r.champs_addi ->> 'organisme' AS autre_organisme,
	CASE
	WHEN r.champs_addi ->> 'organisme' != '' THEN r.champs_addi ->> 'organisme'
	ELSE o.nom_organisme 
	END AS organisme,
    CASE
	WHEN o.nom_organisme LIKE '%Autre%' THEN 'Autre'
	ELSE o.nom_organisme 
	END AS organisme_group,
    CASE
    WHEN r.champs_addi ->> 'organisme' != '' AND o.mnemo IS NULL THEN r.champs_addi ->> 'organisme'
    WHEN o.mnemo IS NOT NULL THEN o.mnemo
    ELSE o.nom_organisme 
	END     AS org_mnemo,
	(SELECT COUNT(*)
		FROM oeasc_declarations.t_declarations d 
		WHERE d.id_declarant = r.id_role
	) AS nb_declarations, 
	TO_CHAR(r.date_insert, 'DD/MM/YYYY') AS create_date,
	p.code_profil::integer AS id_droit_max
	
	
	FROM utilisateurs.t_roles r
	JOIN utilisateurs.bib_organismes o ON r.id_organisme = o.id_organisme
	JOIN utilisateurs.t_applications a ON code_application = 'OEASC'
	JOIN utilisateurs.cor_roles cr ON id_role_utilisateur = r.id_role
	JOIN utilisateurs.cor_role_app_profil crap ON crap.id_role = cr.id_role_groupe AND crap.id_application = a.id_application
	JOIN utilisateurs.t_profils p ON crap.id_profil = p.id_profil;
