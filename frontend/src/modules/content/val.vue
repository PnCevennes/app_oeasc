<template>
  <span>
    <span>{{ val }}</span>
  </span>
</template>

<script>
export default {
  name: 'val',
  // Déclaration des props reçues du composant parent
  props: ['action', 'value', 'fieldName', 'storeName'],
  data: () => ({
    // Variable locale pour stocker la valeur à afficher
    val: null,
  }),
  methods: {
    // Méthode pour traiter et récupérer la valeur à afficher
    processVal() {
      // Si storeName et value sont définis, on récupère la valeur via le store
      if (this.storeName && this.value) {
        const configStore = this.$store.getters.configStore(this.storeName);
        const value = this.value;
        const fieldName = this.fieldName;
        // Appel d'une action du store pour obtenir la valeur
        this.$store.dispatch(configStore.get, { value, fieldName }).then((val) => {
          this.val = val[configStore.displayFieldName];
        });
      }
      // Si action et value sont définis, on exécute l'action pour obtenir la valeur
      if (this.action && this.value) {
        this.$store.dispatch(this.action, this.value).then((val) => {
          this.val = val;
        });
      }
    },
  },
  watch: {
    // Surveille les changements de la prop value pour relancer processVal
    value: {
      handler() {
        this.processVal();
      },
      deep: true,
    },
  },
  // Appelé lors du montage du composant pour initialiser la valeur
  mounted() {
    this.processVal();
  },
};
</script>
