# from sqlalchemy import event, DDL, Table, MetaData, Column, Integer, String, DateTime
# # from sqlalchemy.orm import declarative_base
# from sqlalchemy.sql import func
# from sqlalchemy.orm import registry, relationship
# #

# mapper_reg = registry()
# Base = mapper_reg.generate_base()
# # Base = declarative_base()


# # pour la migration sqlalchemy 1.4 vers 2.0. A retirer lorsqu'on est passé en 2.0 et que tous les models sont réécrits
# # avec Mapped
# Base.__allow_unmapped__ = True

# class TMedias(Base):
#     __tablename__ = 't_medias'
#     __table_args__ = {'schema': 'public'}  # Ensure the schema is 'public'

#     id = Column(Integer, primary_key=True)
#     name = Column(String)
#     meta_create_date = Column(DateTime, nullable=True)
#     meta_update_date = Column(DateTime, nullable=True)

# # Define the trigger function
# trigger_function = DDL("""
#     CREATE OR REPLACE FUNCTION public.fct_trg_meta_dates_change()
#     RETURNS trigger
#     LANGUAGE plpgsql
#     AS $function$
#     BEGIN
#         IF (TG_OP = 'INSERT') THEN
#             NEW.meta_create_date = NOW();
#         ELSIF (TG_OP = 'UPDATE') THEN
#             NEW.meta_update_date = NOW();
#             IF (NEW.meta_create_date IS NULL) THEN
#                 NEW.meta_create_date = NOW();
#             END IF;
#         END IF;
#         RETURN NEW;
#     END;
#     $function$;
#     """)

# # Define the trigger
# trigger = DDL("""
#     CREATE TRIGGER tri_meta_dates_change_t_medias
#     BEFORE INSERT OR UPDATE
#     ON gn_commons.t_medias
#     FOR EACH ROW
#     EXECUTE FUNCTION public.fct_trg_meta_dates_change();
#     """)

# # Attach the DDL to the table
# event.listen(TMedias.__table__, 'after_create', trigger_function)
# event.listen(TMedias.__table__, 'after_create', trigger)
