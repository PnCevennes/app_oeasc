<!--
  Sélecteur de saison : un champ numérique sur l'année de début de la saison
  (2024 pour la saison 2024-2025). v-model = id_saison (null si aucune saison
  ne commence l'année choisie).
  Le nom de la saison est affiché juste à droite du champ, suivi du slot par défaut ;
  `disabled` grise le champ et masque le nom de la saison (la saison choisie ne
  s'applique alors plus).
-->
<template>
  <div class="selecteur-saison">
    <v-number-input
      v-model="annee"
      control-variant="stacked"
      label="Saison (année de début)"
      variant="outlined"
      density="compact"
      hide-details
      :min="anneeMin"
      :max="anneeMax"
      :disabled="disabled"
      style="max-width: 220px"
    ></v-number-input>
    <template v-if="!disabled">
      <span
        v-if="saison"
        class="nom-saison"
      >
        Saison {{ saison.nom_saison }}
      </span>
      <span
        v-else
        class="nom-saison aucune"
      >
        Aucune donnée pour cette saison
      </span>
    </template>
    <slot></slot>
  </div>
</template>

<script>
export default {
  name: 'selecteur-saison',
  props: {
    modelValue: { default: null }, // id_saison
    saisons: { default: () => [] }, // [{ id_saison, nom_saison, annee_debut }]
    disabled: { default: false },
  },
  emits: ['update:modelValue'],
  data: () => ({
    annee: null,
  }),
  computed: {
    annees() {
      return this.saisons.map((s) => s.annee_debut).filter((a) => a != null);
    },
    anneeMin() {
      return this.annees.length ? Math.min(...this.annees) : undefined;
    },
    anneeMax() {
      return this.annees.length ? Math.max(...this.annees) : undefined;
    },
    saison() {
      return this.saisons.find((s) => s.annee_debut === this.annee) || null;
    },
  },
  watch: {
    // saison choisie de l'extérieur (valeur initiale) -> année affichée
    modelValue: {
      handler(id_saison) {
        const saison = this.saisons.find((s) => s.id_saison === id_saison);
        if (saison && saison.annee_debut !== this.annee) {
          this.annee = saison.annee_debut;
        }
      },
      immediate: true,
    },
    saison(saison) {
      const id_saison = saison ? saison.id_saison : null;
      if (id_saison !== this.modelValue) {
        this.$emit('update:modelValue', id_saison);
      }
    },
  },
};
</script>

<style scoped>
.selecteur-saison {
  display: flex;
  align-items: center;
  gap: 16px;
  margin: 8px 0 16px 0;
}
.nom-saison {
  font-weight: bold;
}
.nom-saison.aucune {
  font-weight: normal;
  color: #888;
}
</style>
