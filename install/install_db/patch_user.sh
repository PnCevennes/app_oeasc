. install/install_db/psqla.sh

echo "
INSERT INTO utilisateurs.t_role(identidiant, nom_role, prenom_role, desc_role, pass, passplus, email, id_organisme, organisme, remarques)
VALUES
('richard.scherrer@cevennes-parcnational.fr', 'scherrer', 'richard', 'Salarié, agent, fonctionnaire', 'bcfd77fd0f1fadaa210ab968dbc1a16a', '$2b$12$m4bx/hfsS/CMhEN3oyl8QODkCGmRCO2g6vkz2/CHd0j4EfkpK5SsG', 'richard.scherrer@cevennes-parcnational.fr', 594, 'Parc national des Cévennes', 'creé depuis le site OEASC'),

('baptiste.algoet@cevennes-parcnational.fr', 'Algoët', 'Baptiste', 'Salarié, agent, fonctionnaire', '8eaef7b88801281643b000f4dc16f74e', '$2b$12$.qaI8n0Xpw9jSt/v2DlkEOZloLHXZGIH2N2qdVdWY/caSCBxMNqDC', 'baptiste.algoet@cevennes-parcnational.fr', 594, 'Parc national des Cévennes', 'creé depuis le site OEASC'),

('loic.molines@crpf.fr', 'Molines', 'Loïc', 'Salarié, agent, fonctionnaire', '08f481b53c98605d63cd91c4720c2742', '$2b$12$8yNtNDfSuVTWOg3SF2mbJuHwqMrkkDkVnuO53bFiNVXm5x8BCO41C', 'loic.molines@crpf.fr', 592, 'CRPF Occitanie', 'creé depuis le site OEASC'),

('joel.clement@cevennes-parcnational.fr', 'CLEMENT', 'Joël', 'Salarié, agent, fonctionnaire', '81dc9bdb52d04dc20036dbd8313ed055, '$2b$12$UYDOxgxJQQFJ1c7Y085zsuPf6sFAVVTLFO/fz3XEP64rWH9v6Tml6', 'joel.clement@cevennes-parcnational.fr', 602, 'Jubil Interim', 'creé depuis le site OEASC'),

('joelclems@gmail.com', 'CLEMENT', 'Joël', 'Salarié, agent, fonctionnaire', '81dc9bdb52d04dc20036dbd8313ed055', '$2b$12$Mhf54DNYwpYHJ9GY5SNTlu29Xe0dR.bob7cveGjn8WwVT5P.4c26W', 'joelclems@gmail.com', 594, 'Parc national des Cévennes', 'creé depuis le site OEASC'),
('danny.laybourne@cevennes-parcnational.fr', 'Laybourne', 'Danny', 'Autre', '4d3a2b3af18ff2d53c8cb0d554e35ec5', '$2b$12$NkCagYQsxE0/Y6.tWGaNm.fsXN8NdUgqg2Dl.8NroYfsCSHTeOrp.', 'danny.laybourne@cevennes-parcnational.fr', 594, 'Parc national des Cévennes', 'creé depuis le site OEASC'),

('sandrine.descaves@cevennes-parcnational.fr', 'DESCAVES', 'Sandrine', 'Autre', '739bf8c9ad52a591a3e10aefb957225c', '$2b$12$N1p9JXyd/PSSUrCWaek/tO0s2TL0y2/iSLwJwTKM39U1CQMtdmLva', 'sandrine.descaves@cevennes-parcnational.fr', 594, 'Parc national des Cévennes', 'creé depuis le site OEASC'),

('frederic.fidon@cevennes-parcnational.fr', 'FIDON', 'Frédéric', 'Expert forestier indépendant', 'a3de1698563eb47caa93593f19a21266', '$2b$12$z/tccmOHRM.6Sndn2qbHue9rLpb0liU8rzs60gyY3gyO2Mx4.ikM.', 'frederic.fidon@cevennes-parcnational.fr', 594, 'Parc national des Cévennes', 'creé depuis le site OEASC'),

('herve.caroff@cevennes-parcnational.fr', 'CAROFF', 'Hervé', 'Salarié, agent, fonctionnaire', '0dc1487211223881830b5e8ce0cecaf9', '$2b$12$LumYA7GthXtIWd1rqQht9uh12w.CkJW25di4gGniG.3VPGBY2ufIa', 'herve.caroff@cevennes-parcnational.fr', 594, 'Parc national des Cévennes', 'creé depuis le site OEASC'),

('jpl.48@orange.fr', 'LAFONT', 'Jean-Pierre', 'Propriétaire forestier privé', '106cb2c606810308cf1936208764d979', '$2b$12$kS4R4sOv18qiLP9kkrJPEeLHZdfuuWYTNqkDYkUpZA6QWtYYgrj7m', 'jpl.48@orange.fr', 601, Syndic. forestiers privés 48, 'creé depuis le site OEASC'),

('jean-pierre.hamard@irstea.fr', 'HAMARD', 'Jean-Pierre', 'Autre', '7e338292c913d8c2a16458178abae8dd', '$2b$12$t/1ifQcUILLeVr3Biz6p3.ZP8q/dva6R7UCebxOu7uiHWzB5vpD7S', 'jean-pierre.hamard@irstea.fr', 602, 'Irstea - EFNO', 'creé depuis le site OEASC'),

('isa.corre83@gmail.com', 'CORRE', 'Isabelle', 'Propriétaire forestier privé', '54a9fc48a5b664772e2ca06d1e0772d9', '$2b$12$igzWHSJtrYT0bFA7y02wOOOdBgsOtTkYiYW9MuyCcflv6JpytKjnS', 'isa.corre83@gmail.com', 600, 'Syndic. forestiers privés 30', 'creé depuis le site OEASC');
" | $psqla

echo "
DELETE FROM utilisateurs.bib_organismes WHERE id_organisme > 1 AND id organisme < 50
" |$psqla

echo "
INSERT INTO utilisateur.cor_role_droit_application(id_role, id_application, id_droit)
SELECT id_role, 500, 1
FROM utilisateurs.t_role
WHERE remarques like 'crée depuis%';
"| $psqla
