t1=${1}s
id1=id_${1}
t2=ref_nomenclatures.t_nomenclatures
id2=id_nomenclature
nom_type=$2
nom_add=$3
nom_suppr=$4


t_cor=cor_nomenclature_${t1}${nom_add}


echo "
DROP TABLE IF EXISTS oeasc.${t_cor} CASCADE;

CREATE TABLE IF NOT EXISTS oeasc.${t_cor}
(
    ${id1} integer NOT NULL,
    ${id2} integer NOT NULL,

    CONSTRAINT pk_${t_cor} PRIMARY KEY (${id1}, ${id2}),

    CONSTRAINT fk_${t_cor}_${id1} FOREIGN KEY (${id1})
        REFERENCES oeasc.t_${t1} (${id1}) MATCH SIMPLE
        ON UPDATE NO ACTION ON DELETE CASCADE,

    CONSTRAINT fk_${t_cor}_${id2} FOREIGN KEY (${id2})
        REFERENCES ${t2} (${id2}) MATCH SIMPLE
        ON UPDATE NO ACTION ON DELETE NO ACTION,

    CONSTRAINT check_${t_cor}_mnemonique CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(
        ${id2}, '${nom_type}')) NOT VALID
);
"

