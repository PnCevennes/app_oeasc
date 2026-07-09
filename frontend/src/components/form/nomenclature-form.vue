<!--
  Composant Vue.js pour gérer un formulaire de nomenclature.
  Ce composant utilise un sous-composant "listForm" pour afficher une liste basée sur une configuration dynamique.
-->

<template>
  <div>
    <!-- Affiche le composant list-form uniquement si la configuration est prête -->
    <list-form
      v-if="configList"
      :config="configList"
      :baseModel="baseModel"
    ></list-form>
  </div>
</template>

<script>
import listForm from './list-form.vue';

export default {
  name: 'nomenclatureForm',
  components: { listForm },
  props: ['config', 'baseModel'],
  data: () => ({
    configList: null,
  }),

  created: function () {
    // Définition de l'URL pour récupérer les nomenclatures selon le type spécifié
    this.config.url = `api/oeasc/nomenclatures/${this.config.nomenclatureType}`;
    // Nom du champ utilisé pour la valeur dans la liste
    this.config.valueFieldName = 'id_nomenclature';
    // Nom du champ utilisé pour l'affichage dans la liste
    this.config.displayFieldName = 'label_fr';

    // Récupération des nomenclatures depuis le store Vuex
    this.$store.dispatch('nomenclatures').then(() => {
      // Filtre les nomenclatures selon le type demandé
      this.config.items = this.$store.getters.nomenclaturesOfType(this.config.nomenclatureType);

      // Si une liste de codes est fournie, on filtre les items pour ne garder que ceux correspondant aux codes
      if (this.config.codes) {
        this.config.items = this.config.codes.map((cd_nomenclature) =>
          this.config.items.find((item) => item.cd_nomenclature == cd_nomenclature)
        );
      }

      // Cas particulier pour le type "OEASC_PEUPLEMENT_TYPE" : on impose un ordre et une sélection précise des codes
      if (this.config.nomenclatureType == 'OEASC_PEUPLEMENT_TYPE') {
        this.config.items = ['FREG', 'FIRR', 'TAIL', 'MEL', 'NSP'].map((cd_nomenclature) =>
          this.config.items.find((item) => item.cd_nomenclature == cd_nomenclature)
        );
      }

      // On assigne la configuration finale à configList pour affichage dans le composant enfant
      this.configList = this.config;
    });
  },
};
</script>

<style lang="scss" scoped>
.md-checkbox,
.md-radio {
  display: flex;
}
</style>
