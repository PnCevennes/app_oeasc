<!-- formulaire de saisie données chasse -->

<template>
<div class="form-realisation"  style="padding-top: 50px;">
    <!-- Affiche une barre de progression pendant l'initialisation du formulaire -->
    <v-progress-linear  v-if="!displayForm"  indeterminate></v-progress-linear>

    <!-- Affiche le numéro de bracelet actuellement sélectionné dans le formulaire -->
    <!-- {{$refs.form && $refs.form.baseModel.attribution && $refs.form.baseModel.attribution.numero_bracelet}} -->

    <!-- Liste des réalisations déjà saisies, permet de les éditer en cliquant dessus -->
    <div v-if="realisations.length">
        <h4>Réalisations effectuées</h4>

        <v-chip
            v-for="realisation of realisations"
            :key="realisation.id_realisation"
            @click="initForm(realisation)"
            title="Modifier la réalisation"
        >
            {{ realisation.attribution.numero_bracelet }}
        </v-chip>
    </div>

    <!-- Affiche le formulaire de saisie lorsque displayForm est à true -->
    <div v-if="displayForm">
        <generic-form
            ref="form"
            :config="config"
            @onSuccess="onSuccess($event)"
        ></generic-form>
    </div>
</div>  
</template>


<script>
import genericForm from "@/components/form/generic-form.vue";

export default {
    name: 'form-realisation-chasse',
    components: { genericForm },
    data:() => ({
        config: {
            storeName: 'chasseRealisation',
        },
        realisations: [],
        displayForm: false,
    }),
    methods: {

        /**
         * (re) initialisation du formulaire de réalisation de chasse.
         * 
         * Cette fonction est utilisée pour réinitialiser et recharger le formulaire, 
         * par exemple lors de la création d'une nouvelle réalisation ou de la modification d'une réalisation existante.
         * 
         * @param {Object|null} realisation - Les données de la réalisation à charger dans le formulaire. 
         *                                    Si null, le formulaire sera vide (création).
         * 
         * Étapes :
         * 1. Cache le composant de formulaire (`displayForm = false`) pour forcer sa recréation.
         * 2. Utilise un setTimeout pour temporiser la réaffichage du formulaire (permet de "reset" le composant).
         * 3. Après le délai, réaffiche le formulaire (`displayForm = true`).
         * 4. Utilise $nextTick pour s'assurer que le formulaire est bien recréé avant d'appeler la méthode `updateBaseModel` 
         *    sur le composant enfant référencé par `form`, afin d'y injecter les données de la réalisation.
         * 5. Déclenche une action Vuex pour mettre le focus sur l'élément d'attribution des bracelets dans le formulaire.
         * 
         * Cette méthode est particulièrement utile pour garantir que le formulaire est proprement réinitialisé 
         * lors d'un changement de réalisation ou lors de la création d'une nouvelle entrée.
         */
        // (re) initialisation du formulaire
        initForm(realisation=null) {

            // this.config.value = realisation
            // suppression du composant generic-form pour forcer sa recréation
            this.displayForm = false;

            // temporiser pour laisser le temps de recréer le formulaire
            setTimeout(
                () => {

                    // création du formulaire
                    this.displayForm = true;

                    // attribution des valeurs à la baseModel du formulaire
                    this.$nextTick(() => {
                        if(this.$refs.form) {
                            // Injecte les données de la réalisation dans le formulaire (mode édition)
                            this.$refs.form.updateBaseModel(realisation)
                        }
                    });

                    // focus sur le champ d'attribution des bracelets
                    this.$store.dispatch("focus", "#form-attribution");
                },
                1000
            )
        },

        /**
         * Fonction appelée lors de la soumission réussie du formulaire.
         * 
         * @param {Object} event - Les données de la réalisation soumise.
         * 
         * Cas d'utilisation :
         * - Si la réalisation n'existe pas encore (ajout), elle est ajoutée à la liste.
         * - Si la réalisation existe déjà (modification), elle est mise à jour dans la liste.
         * - Le formulaire est ensuite réinitialisé pour permettre une nouvelle saisie.
         */
        onSuccess(event) {

            // si c'est un ajout :
            // on ajoute la realisation à la liste des realisations saisies
            if (!this.realisations.find( r => r.attribution.numero_bracelet == event.attribution.numero_bracelet)) {
                this.realisations.push(event)
            }

            // sinon c'est un update : on modifie la réalisation concernée
            else {
                this.realisations = this.realisations.map( r =>
                    r.attribution.numero_bracelet == event.attribution.numero_bracelet
                        ? event
                        : r
                );

            }

            // réinitialise le formulaire pour une nouvelle saisie
            this.initForm();
        },
    },


    mounted() {
        this.initForm()
    }
    
}
</script>

<style>
.form-realisation {
    width: 1000px
}
</style>