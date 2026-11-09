<!--
  Filtres des graphiques par saison : trois listes déroulantes à choix multiples
  (communes, types de culture, espèces). v-model = { communes, typesCulture, especes },
  trois tableaux d'identifiants. Tout est sélectionné par défaut (par le parent).
  Les communes sont triées par département (48 puis 30) puis par nom, chaque
  département étant introduit par un intitulé et une couleur distincte.
-->
<template>
  <div class="filtres-graphiques">
    <v-select
      v-if="!sansCommunes"
      :model-value="modelValue.communes"
      @update:model-value="maj('communes', $event)"
      :items="itemsCommunes"
      item-title="title"
      item-value="value"
      label="Communes"
      multiple
      variant="outlined"
      density="compact"
      hide-details
      :menu-props="{ maxHeight: 400 }"
    >
      <template #item="{ item, props }">
        <v-list-item
          v-bind="props"
          :class="`commune-dep-${item.raw.departement}`"
        >
          <template #prepend="{ isSelected }">
            <v-checkbox-btn
              :model-value="isSelected"
              readonly
              density="compact"
            ></v-checkbox-btn>
          </template>
        </v-list-item>
      </template>
      <template #selection="{ index }">
        <span v-if="index === 0">{{ resume('communes', options.communes) }}</span>
      </template>
      <template #prepend-item>
        <v-list-item
          title="Tout sélectionner / désélectionner"
          @click="basculer('communes', options.communes)"
        ></v-list-item>
        <v-divider></v-divider>
      </template>
    </v-select>

    <v-select
      v-if="!sansTypesCulture"
      :model-value="modelValue.typesCulture"
      @update:model-value="maj('typesCulture', $event)"
      :items="options.types_culture"
      item-title="nom"
      item-value="id"
      label="Types de culture"
      multiple
      variant="outlined"
      density="compact"
      hide-details
    >
      <template #selection="{ index }">
        <span v-if="index === 0">{{ resume('typesCulture', options.types_culture) }}</span>
      </template>
    </v-select>

    <v-select
      :model-value="modelValue.especes"
      @update:model-value="maj('especes', $event)"
      :items="options.especes"
      item-title="nom"
      item-value="id"
      label="Espèces"
      multiple
      variant="outlined"
      density="compact"
      hide-details
    >
      <template #selection="{ index }">
        <span v-if="index === 0">{{ resume('especes', options.especes) }}</span>
      </template>
    </v-select>
  </div>
</template>

<script>
// ordre d'affichage et intitulé des départements
const DEPARTEMENTS = [
  { code: '48', nom: 'Lozère (48)' },
  { code: '30', nom: 'Gard (30)' },
];

export default {
  name: 'filtres-graphiques',
  props: {
    modelValue: { required: true }, // { communes, typesCulture, especes }
    // { communes: [{ id, nom, departement }], types_culture: [{ id, nom }], especes: [{ id, nom }] }
    options: { required: true },
    sansCommunes: { type: Boolean, default: false }, // masque le filtre des communes
    sansTypesCulture: { type: Boolean, default: false }, // masque le filtre des types de culture
  },
  emits: ['update:modelValue'],
  computed: {
    // communes groupées par département (48 puis 30, puis autres), par ordre alphabétique
    itemsCommunes() {
      const items = [];
      const codes = [
        ...DEPARTEMENTS.map((d) => d.code),
        ...new Set(
          this.options.communes
            .map((c) => c.departement)
            .filter((d) => !DEPARTEMENTS.some((x) => x.code === d))
        ),
      ];
      for (const code of codes) {
        const communes = this.options.communes
          .filter((c) => c.departement === code)
          .sort((a, b) => a.nom.localeCompare(b.nom, 'fr'));
        if (!communes.length) {
          continue;
        }
        const dep = DEPARTEMENTS.find((d) => d.code === code);
        items.push({ type: 'subheader', title: dep ? dep.nom : `Département ${code}` });
        for (const c of communes) {
          items.push({ title: c.nom, value: c.id, departement: code });
        }
      }
      return items;
    },
  },
  methods: {
    maj(champ, valeur) {
      this.$emit('update:modelValue', { ...this.modelValue, [champ]: valeur });
    },
    basculer(champ, liste) {
      const toutes = this.modelValue[champ].length === liste.length;
      this.maj(champ, toutes ? [] : liste.map((o) => o.id));
    },
    resume(champ, liste) {
      const n = this.modelValue[champ].length;
      if (n === liste.length) {
        return `Tous (${n})`;
      }
      return n ? `${n} sur ${liste.length} sélectionné${n > 1 ? 's' : ''}` : 'Aucun';
    },
  },
};
</script>

<style scoped>
.filtres-graphiques {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 16px;
  margin: 8px 0 16px 0;
}
@media (max-width: 900px) {
  .filtres-graphiques {
    grid-template-columns: minmax(0, 1fr);
  }
}
/* teinte de fond par département pour les distinguer dans la liste */
.commune-dep-48 {
  background-color: rgba(33, 150, 243, 0.08);
}
.commune-dep-30 {
  background-color: rgba(255, 152, 0, 0.1);
}
</style>
