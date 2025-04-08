

<template>
  <!-- formulaire de modification de page -->
  <!-- <v-progress-linear  v-if="!displayForm"  indeterminate></v-progress-linear> -->
  <div>
    
    <!-- <div v-if="realisations.length">
        <h4>Réalisations effectuées</h4>

        <v-chip
            v-for="realisation of realisations"
            :key="realisation.id_realisation"
            @click="initForm(realisation)"
            title="Modifier la réalisation"
        >
            {{ realisation.attribution.numero_bracelet }}
        </v-chip>
    </div> -->


    <div v-if="displayForm">
        <generic-form
            ref="form"
            :config=config
            @onSuccess="onSuccess($event)"
        ></generic-form>
    </div>
 
    <div v-else>
      <h2>Tableau de valeurs</h2>
    </div>

  </div>
</template>

<script>
import dynamicForm from "./dynamic-form.vue";
import { apiRequest, url } from "@/core/js/data/api.js";

// import help from "./help";

export default {
  name: "formRealisation",
  components: {
    //dynamicForm,
    // help
  },
  data: () => ({
    displayForm: false,

    fields: [
      "saison.id_saison", "saison.nom_saison",
      "attribution.id_attribution", "attribution.numero_bracelet",
      "auteur_tir.id_personne", "auteur_tir.nom_personne", "auteur_constat.id_personne", "auteur_constat.nom_personne",
      "zone_cynegetique_realisee.id_zone_cynegetique", "zone_cynegetique_realisee.nom_zone_cynegetique",
      "zone_indicative_realisee.id_zone_indicative", "zone_indicative_realisee.nom_zone_indicative",
      "lieu_tir_synonyme.id_lieu_tir_synonyme", "lieu_tir_synonyme.lieu_tir_synonyme_display",
      "nomenclature_sexe.id_nomenclature", "nomenclature_sexe.label_fr",
      "nomenclature_classe_age.id_nomenclature", "nomenclature_classe_age.label_fr",
      "nomenclature_mode_chasse.id_nomenclature", "nomenclature_mode_chasse.label_fr",
      ]
    
  }),


  props: ["config", "baseModel", "depthIn"],


  computed: {
    depth() {
      return this.depthIn || 0;
    },
    formList() {
      return this.computeFormList(this.config);
    },
    hasForms() {
      return this.computeHasForms(this.config);
    },
    displayGroup() {
      return this.computeDisplayGroup(this.config);
    },
    groupList() {
      return this.computeGroupList(this.config);
    }
  },


  methods: {
    computeDisplayGroup(config) {
      return (
        !config.condition ||
        config.condition({ baseModel: this.baseModel, $store: this.$store })
      );
    },

    // renvoie la liste des formulaires filtrée par condition
    computeFormList(config) {
      // si config.forms n'est pas défini, on prend tous les form de formDefs
      const forms =
        config.forms ||
        (!config.groups && Object.keys(config.formDefs || {})) ||
        [];

      return forms
        .filter(keyForm => {
          const formDef = config.formDefs[keyForm];
          return (
            !formDef.condition ||
            formDef.condition({
              baseModel: this.baseModel,
              $store: this.$store
            })
          );
        })
        .map(keyForm => {
          const formDef = config.formDefs[keyForm];
          return {
            ...formDef,
            formDefs: config.formDefs,
            name: keyForm,
            displayValue: this.config.displayValue,
            displayLabel: this.config.displayLabel
          };
        });
    },

    // renvoie la liste des groupes
    computeGroupList(config) {
      return (config.groups || []).map(group => ({
        ...group,
        formDefs: config.formDefs,
        displayLabel: this.config.displayLabel,
        displayValue: this.config.displayValue
      }));
    },

    // renvoie si la config possède au moins un formulaire
    computeHasForms(config) {
      if (config.forms) {
        return this.computeFormList(config).length;
      }
      if (this.config.groups) {
        return this.config.groups.some(group => this.computeHasForms(group));
      }
    }
  }
};

</script>







<style scoped>
.form-group.border {
  border: 1px solid lightgrey;
  border-radius: 10px;
}

.form-group.margin {
  margin: 10px;
}

.form-group.padding {
  padding: 10px;
}
</style>
