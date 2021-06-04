// import moment from "moment";
import { copy } from "@/core/js/util/util";

const declarationLocalisationAreas = function(d) {
  return d.b_statut_public === true && d.b_document == true
    ? d.areas_localisation_onf_ug
    : d.areas_localisation_cadastre;
};

const declarationForetAreas = function(d) {
  return d.b_document == false
    ? d.areas_foret_section
    : d.b_statut_public
    ? [d.areas_foret_onf]
    : [d.areas_foret_dgd];
};

const getDeclarationData = function({ declaration, $store }) {
  return new Promise(resolve => {
    $store
      .dispatch("areas", declarationLocalisationAreas(declaration))
      .then(() => {
        resolve();
      });
  });
};

const rawToDisplay = function({ declaration, $store }) {
  const d = copy(declaration);

  d.valide =
    declaration.b_valid === true
      ? "Validé"
      : declaration.b_valid === false
      ? "Non validé"
      : "En attente";

  if (d.meta_create_date) {
    d.declaration_date = new Date(d.meta_create_date).toLocaleDateString();
  }

  d.peuplement_acces_label = $store.getters.nomenclatureString(
    d.id_nomenclature_peuplement_acces
  );

  d.espece_label = $store.getters.nomenclatureString(
    d.nomenclatures_peuplement_espece
  );

  d.statut_public =
    d.b_statut_public === true
      ? "Public"
      : d.b_statut_public === false
      ? "Privé"
      : "Indéfini";

  d.foret_type_label = $store.getters.nomenclatureString(
    d.id_nomenclature_proprietaire_type
  );

  d.peuplement_ess_1_label = $store.getters.nomenclatureString(
    d.id_nomenclature_peuplement_essence_principale
  );

  d.peuplement_ess_2_label = $store.getters.nomenclatureString(
    d.nomenclatures_peuplement_essence_secondaire
  );
  d.peuplement_ess_3_label = $store.getters.nomenclatureString(
    d.nomenclatures_peuplement_essence_complementaire
  );

  d.peuplement_origine_label = $store.getters.nomenclatureString(
    d.id_nomenclature_peuplement_origine
  );
  d.peuplement_origine2_label = $store.getters.nomenclatureString(
    d.nomenclatures_peuplement_origine2
  );

  d.peuplement_type_label = $store.getters.nomenclatureString(
    d.id_nomenclature_peuplement_type
  );
  d.peuplement_maturite_label = $store.getters.nomenclatureString(
    d.nomenclatures_peuplement_maturite
  );

  d.peuplement_protection_type_label = $store.getters.nomenclatureString(
    d.nomenclatures_peuplement_protection_type
  );
  if (d.autre_protection) {
    d.peuplement_protection_type_label = d.peuplement_protection_type_label.replace(
      "Autre (préciser)",
      d.autre_protection
    );
  }

  d.peuplement_paturage_type_label = $store.getters.nomenclatureString(
    d.nomenclatures_peuplement_paturage_type
  );

  d.peuplement_paturage_statut_label = $store.getters.nomenclatureString(
    d.id_nomenclature_peuplement_paturage_statut
  );

  d.peuplement_paturage_frequence_label = $store.getters.nomenclatureString(
    d.id_nomenclature_peuplement_paturage_frequence
  );

  d.peuplement_paturage_saison_label = $store.getters.nomenclatureString(
    d.nomenclatures_peuplement_paturage_saison
  );

  for (const degat of (d.degats||[])) {
    degat.degat_type_label = $store.getters.nomenclatureString(
      degat.id_nomenclature_degat_type
    );
    degat.degat_type_mnemo = $store.getters.nomenclatureString(
      degat.id_nomenclature_degat_type,
      "mnemonique"
    );

    for (const degatEssence of (degat.degat_essences || [])) {
      degatEssence.degat_essence_label = $store.getters.nomenclatureString(
        degatEssence.id_nomenclature_degat_essence
      );
      degatEssence.degat_gravite_label = $store.getters.nomenclatureString(
        degatEssence.id_nomenclature_degat_gravite
      );
      degatEssence.degat_anteriorite_label = $store.getters.nomenclatureString(
        degatEssence.id_nomenclature_degat_anteriorite
      );
      degatEssence.degat_etendue_label = $store.getters.nomenclatureString(
        degatEssence.id_nomenclature_degat_etendue
      );
    }
  }

  const areas_parcelles = declarationLocalisationAreas(d);

  d.parcelles = $store.getters.areaString(areas_parcelles);

  return d;
};

const displayParcelles = function(parcelles) {
  
  const parcellesArray = parcelles.split(", ");
  if ((parcellesArray[0].split("-").length != 3)) {
    return parcelles;
  }

const groups = {};
for (const parcelle of parcellesArray) {
  const parcelleArray = parcelle.split("-");
  const group_key = parcelleArray[0] + '-' + parcelleArray[1];
  if (!Object.keys(groups).includes(group_key)) {
    groups[group_key] = [];
  }
  groups[group_key].push(parcelleArray[2]);
}
return Object.keys(groups).map((group_key) => {
  const group = groups[group_key];
  return group.length == 1 ? `${group_key}-${group[0]}` : `${group_key}-(${group.join(', ')})`;
}).join(', ');
}

export {
  displayParcelles,
  rawToDisplay,
  getDeclarationData,
  declarationForetAreas,
  declarationLocalisationAreas
};
