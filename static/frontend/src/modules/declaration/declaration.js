// import moment from "moment";
import {copy} from '@/core/js/util/util'

const getNomenclature = function(n, $store, key = "label_fr") {
  if (!n) {
    return "";
  }

  if (!Array.isArray(n)) {
    const nomenclature = $store.getters.nomenclature(n);
    return nomenclature[key].toLowerCase();
  } else {
    return n.map(id => $store.getters.nomenclature(id)[key].toLowerCase()).join(", ");
  }
};

const rawToDisplay = function({ declaration, $store }) {
  const d = copy(declaration);

  d.valide =
    declaration.b_valid == true
      ? "Validé"
      : declaration.b_valid == false
      ? "Non validé"
      : "En attente";

  d.declaration_date = new Date(d.meta_create_date).toLocaleDateString();

  d.peuplement_acces_label = getNomenclature(
    d.id_nomenclature_peuplement_acces,
    $store
  );

  d.espece_label = getNomenclature(d.nomenclatures_peuplement_espece, $store);

  d.statut_public =
    d.b_statut_public == true
      ? "Public"
      : d.b_statut_public == false
      ? "Privé"
      : "Indéfini";

  d.foret_type_label = getNomenclature(
    d.id_nomenclature_proprietaire_type,
    $store
  );

  d.peuplement_ess_1_label = getNomenclature(
    d.id_nomenclature_peuplement_essence_principale,
    $store
  );

  d.peuplement_ess_2_label = getNomenclature(
    d.nomenclatures_peuplement_essence_secondaire,
    $store
  );
  d.peuplement_ess_3_label = getNomenclature(
    d.nomenclatures_peuplement_essence_complementaire,
    $store
  );

  d.peuplement_origine_label = getNomenclature(
    d.id_nomenclature_peuplement_origine,
    $store
  );
  d.peuplement_origine2_label = getNomenclature(
    d.nomenclatures_peuplement_origine2,
    $store
  );

  d.peuplement_type_label = getNomenclature(
    d.id_nomenclature_peuplement_type,
    $store
  );
  d.peuplement_maturite_label = getNomenclature(
    d.nomenclatures_peuplement_maturite,
    $store
  );

  d.peuplement_protection_type_label = getNomenclature(
    d.nomenclatures_peuplement_protection_type,
    $store
  );
  if (d.autre_protection) {
    d.peuplement_protection_type_label = d.peuplement_protection_type_label.replace(
      "Autre (préciser)",
      d.autre_protection
    );
  }

  d.peuplement_paturage_type_label = getNomenclature(
    d.nomenclatures_peuplement_paturage_type,
    $store
  );

  d.peuplement_paturage_statut_label = getNomenclature(
    d.id_nomenclature_peuplement_paturage_statut,
    $store
  );

  d.peuplement_paturage_frequence_label = getNomenclature(
    d.id_nomenclature_peuplement_paturage_frequence,
    $store
  );

  d.peuplement_paturage_saison_label = getNomenclature(
    d.nomenclatures_peuplement_paturage_saison,
    $store
  );

  for (const degat of d.degats) {
    degat.degat_type_label = getNomenclature(
      degat.id_nomenclature_degat_type,
      $store
    );
    degat.degat_type_mnemo = getNomenclature(
      degat.id_nomenclature_degat_type,
      $store,
      'mnemonique'
    );

    for (const degatEssence of degat.degat_essences) {
      degatEssence.degat_essence_label = getNomenclature(
        degatEssence.id_nomenclature_degat_essence,
        $store
      );
      degatEssence.degat_gravite_label = getNomenclature(
        degatEssence.id_nomenclature_degat_gravite,
        $store
      );
      degatEssence.degat_anteriorite_label = getNomenclature(
        degatEssence.id_nomenclature_degat_anteriorite,
        $store
      );
      degatEssence.degat_etendue_label = getNomenclature(
        degatEssence.id_nomenclature_degat_etendue,
        $store
      );

    }
  }



  return d;
};

export { rawToDisplay };
