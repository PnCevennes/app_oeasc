CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";
--------------------
--PUBLIC FUNCTIONS--
--------------------
CREATE OR REPLACE FUNCTION public.fct_trg_meta_dates_change()
  RETURNS trigger AS
$BODY$
begin
        if(TG_OP = 'INSERT') THEN
                NEW.meta_create_date = NOW();
        ELSIF(TG_OP = 'UPDATE') THEN
                NEW.meta_update_date = NOW();
                if(NEW.meta_create_date IS NULL) THEN
                        NEW.meta_create_date = NOW();
                END IF;
        end IF;
        return NEW;
end;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
