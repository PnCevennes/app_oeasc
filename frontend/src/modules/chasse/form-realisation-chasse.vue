<template>
<div class="form-realisation">

    <v-progress-linear  v-if="!displayForm"  indeterminate></v-progress-linear>

    <div v-if="bracelets.length">
        <h4>Bracelets Effectués</h4>
        {{(bracelets || []).join(', ')}}
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
        initForm() {
            setTimeout(
                () => {
                    this.displayForm = true;
                    this.$store.dispatch("focus", "#form-attribution");
                },
                1000
            )

        },
        onSuccess(event) {
            this.bracelets.push(event.attribution.numero_bracelet)
            this.displayForm = false;
            this.initForm();
        }
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