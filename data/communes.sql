-- curl -X GET "https://geo.api.gouv.fr/communes?fields=nom,code,codesPostaux,codeDepartement,codeRegion,population&format=json&geometry=centre" -H  "accept: application/json" > /tmp/communes.json

create temporary table temp_json (values text) on commit drop;
copy temp_json from '/tmp/communes.json';

drop table oeasc_commons.t_communes;
create Table oeasc_commons.t_communes AS
select values->>'nom' AS nom,
	values->>'code' AS code,
	json_array_elements_text(values->'codesPostaux') AS cp,
	CASE WHEN values->>'population' IS NULL THEN 0
	ELSE (values->>'population')::integer 
	END as population 

	from   (
           select json_array_elements(replace(values,'\','\\')::json) as values 
           from   temp_json
       ) a;

select * from oeasc_commons.t_communes 
ORDER BY population DESC 
--ORDER BY cp
LIMIT 10;
