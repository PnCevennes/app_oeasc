<template>
<div class="form-realisation">

    <v-progress-linear  v-if="!displayForm"  indeterminate></v-progress-linear>
{{$refs.form && $refs.form.baseModel.attribution && $refs.form.baseModel.attribution.numero_bracelet}}
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


    <div v-if="displayForm"
    >
        <generic-form
            ref="form"
            :config=config
            @onSuccess="onSuccess($event)"
        ></generic-form>
    </div>


</div>
</template>


<script>
import genericForm from "@/components/form/generic-form";

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

        // (re) initialisation du formulaire
        initForm(realisation=null) {


            // this.config.value = realisation
            // suppression du composant generic-form
            this.displayForm = false;

            // temporiser pour laisser le temps de recréer le formulaire
            setTimeout(
                () => {

                    // creation du formulaire
                    this.displayForm = true;

                    // attribution des valeurs
                    this.$nextTick(() => {
                        this.$refs.form.updateBaseModel(realisation)
                    });

                    // focus sur les bracelets
                    this.$store.dispatch("focus", "#form-attribution");
                },
                1000
            )
        },

        // quand la requete du formulaire est terminée
        onSuccess(event) {


            // si c'est un ajout :
            // on ajoute la realisation à la liste des realisations saisie
            if (!this.realisations.find( r => r.attribution.numero_bracelet == event.attribution.numero_bracelet)) {
                this.realisations.push(event)
            }

            // sinon c'est un update on modifie la réalisation concernée
            else {
                this.realisations = this.realisations.map( r =>
                    r.attribution.numero_bracelet == event.attribution.numero_bracelet
                        ? event
                        : r
                );



            }

            // nouveau formulaire
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