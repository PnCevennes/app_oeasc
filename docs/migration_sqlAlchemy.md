

Dans les models
    - Pour accepter l'ancienne methode de déclaration de classe, le Base.model de chaque classe à été changé pour ajouter   __allow_unmapped__ = True
    En sqlAlchemy 2.0 il faudra utiliser la fonction Mapped or elle n'est pas dans la libraire 1.4
    Lors de l'installation de sqlAlchemy 2.0. Il faudra donc réécrire les classe avec Mapped et column_mapped puis retirer remettre la base DB.Model à la place de customModel
    - Remplacer Base = declarative_base() par :
        mapper_reg = registry()
        Base = mapper_reg.generate_base()
    

Dans config.py
    - Une fois la migration terminé il faudra modifier SQLALCHEMY_ENGINE_OPTIONS pour retirer future: True

Dans App.py
    - Une fois la migration terminé. Retirer la partie qui affichait les warning en haut de page
        import os
        import warnings
        from sqlalchemy import exc
        os.environ["PYTHONWARNINGS"] = "always"
        os.environ["SQLALCHEMY_WARN_20"] = "1"
        warnings.simplefilter("always", exc.SAWarning)

Modifier les as_dict par marshmallow.dump




Dans le les executions de requêtes:
    - les fonction execute doivent être mise dans un contexte engine.begin(). Cela rend les commit moins implicite
    


with Session(DB.engine) as session:
    session.execute(...)


verifier si il y a besoin de créer une instance de Metadata() dans le app.py même avec flasksqlalchemy



pour les requete avec text() utiliser bindparam a la place de format pour eviter les injection sql
text("SELECT * FROM users WHERE name = :name").bindparams(name=user_input)


peut etre remplacer les requête avec _and simples par filter_by()
select(User).filter_by(
    name="spongebob", 
    fullname="Spongebob Squarepants"
)

remplacement subquery() par cte() permetterait une optimisation

Verifier si il est possible de mettre limit(1) pour les requete avec first ou one


verifier si les filter ne doivent pas être remplacer par where

verifier dans les where si il ne faut pas mettre func.lower pour comparer les nom
.where(func.lower(TForet.nom_foret) == func.lower(nom_foret))

verifier les scalars avec les join()




probleme dans déclaration-model. 
alter table oeasc_forets.cor_dgd_cadastre add idtmp serial;

with d as (
	select max(idtmp), array_agg(idtmp), d.area_code_cadastre, d.area_code_dgd
	from oeasc_forets.cor_dgd_cadastre d
	group by d.area_code_cadastre, d.area_code_dgd
)
delete from oeasc_forets.cor_dgd_cadastre 
where idtmp in (select max from d);

alter table oeasc_forets.cor_dgd_cadastre drop  idtmp;

vacuum full;


