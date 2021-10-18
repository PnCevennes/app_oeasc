<template>
<div>
    <div v-if="bracelets.length">
        <h4>Bracelets Effectués</h4>
        {{bracelets}}
    </div>


    <div v-if="displayForm" 
            class="form-realisation"
    >
        <generic-form
            class="form-realisation"
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
            this.displayForm = true;
            this.$store.dispatch("focus", {id:"form-attribution", t:600})
        },
        onSuccess(event) {
            console.log(event)
            this.bracelets.push(event.attribution.numero_bracelet)
            this.displayForm = false;
            setTimeout(() => { this.initForm(), 100})
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