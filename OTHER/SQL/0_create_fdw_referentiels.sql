
CREATE EXTENSION IF NOT EXISTS postgres_fdw;

CREATE SERVER referentiels_server  
      FOREIGN DATA WRAPPER postgres_fdw 
      OPTIONS (host 'referentiels', dbname 'referentiels', port '5432');

CREATE USER MAPPING  
        FOR dbadmin
        SERVER referentiels_server
        OPTIONS (password '64QT94C',user 'dataadmin');
