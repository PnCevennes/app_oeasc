-- insert_data_chasse.sql

CREATE EXTENSION IF NOT EXISTS postgres_fdw;

DROP SERVER IF EXISTS chasse CASCADE;
CREATE SERVER chasse  
      FOREIGN DATA WRAPPER postgres_fdw 
      OPTIONS (host :'chasse_db_host', dbname :'chasse_db_name', port :'chasse_db_port');

CREATE USER MAPPING  
        FOR :user_pg
        SERVER chasse
        OPTIONS (password :'chasse_user_pg_pass',user :'chasse_user_pg');

DROP SCHEMA IF EXISTS import_chasse;
CREATE SCHEMA IF NOT EXISTS import_chasse;
IMPORT FOREIGN SCHEMA chasse
      FROM SERVER chasse INTO import_chasse;
