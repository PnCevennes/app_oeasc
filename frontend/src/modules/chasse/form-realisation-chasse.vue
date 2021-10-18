<template>
<div class="form-realisation">

    <v-progress-linear  v-if="!displayForm"  indeterminate></v-progress-linear>

    <div v-if="bracelets.length">
        <h4>Bracelets Effectués</h4>
        {{bracelets}}
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
        bracelets: [],
        displayForm: false,
    }),
    methods: {
        initForm(dt) {
            setTimeout(
                () => {
                    this.displayForm = true;
                    this.$store.dispatch("focus", {id:"form-attribution", t: dt});
                },
                1000
            )

        },
        onSuccess(event) {
            this.bracelets.push(event.attribution.numero_bracelet)
            this.displayForm = false;
            this.initForm(500);
        }
    },
    mounted() {
        this.initForm(2000)
    }
}
</script>

<style>
.form-realisation {
    width: 1000px
}
</style>