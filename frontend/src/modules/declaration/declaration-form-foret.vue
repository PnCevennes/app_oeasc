<!-- Sections « déclarant », « forêt » et « propriétaire » du formulaire de déclaration. Extraites de
modifier-declaration.vue. Modifie directement les champs de l'objet `declaration_data` fourni par le
parent (v-model sur ses propriétés), comme degats_declaration_form.vue. -->
<template>
    <!-- -------------  informations sur le declarant ---------------- -->
    <div
      style="margin-top: 30px"
      v-if="$store.getters.droitMax >= 5 && liste_declarants.length > 0"
    >
      <h3>Informations sur le déclarant</h3>
      <div>
        <div
          style="
            margin-top: 10px;
            border: 1px solid #ccc;
            padding: 20px;
            border-radius: 5px;
          "
        >
          <v-autocomplete
            v-model="declaration_data.id_declarant"
            :items="liste_declarants"
            :item-title="formatDeclarantLabel"
            item-value="id_role"
            label="Déclarant"
          ></v-autocomplete>
        </div>
      </div>
    </div>

    <!-- -------------  informations sur la foret ---------------- -->

    <div
      style="margin-top: 30px"
      v-if="declaration_data.b_document === false"
    >
      <h3>Informations sur la forêt</h3>
      <div>
        <p>
          Le nom de la forêt et sa superficie sont issues des données transmises par
          l’ONF. Ces informations ne peuvent être modifiées. Si vous constatez une
          erreur, merci de l’indiquer dans le cadre dédié aux commentaires libres en fin
          de formulaire ou de contacter l’animateur de l’Observatoire.
        </p>
        Veuillez cliquer sur « Suivant ».

        <div
          style="
            margin-top: 10px;
            border: 1px solid #ccc;
            padding: 20px;
            border-radius: 5px;
          "
        >
          <div
            class="d-flex align-center"
            style="gap: 8px"
          >
            <v-text-field
              v-model="declaration_data.label_foret"
              label="Nom de la forêt"
              :disabled="declaration_data.b_document === true"
              style="max-width: 400px"
            ></v-text-field>
            <help><helpContent helpID="form_nom_foret"></helpContent></help>
          </div>
          <div
            class="d-flex align-center"
            style="gap: 8px"
          >
            <v-text-field
              v-model="declaration_data.surface_renseignee"
              :rules="[rules.required]"
              label="Total de la surface (en ha)"
              :disabled="declaration_data.b_document === true"
              style="max-width: 400px"
            ></v-text-field>
            <help><helpContent helpID="form_superficie_foret"></helpContent></help>
          </div>
        </div>
      </div>
    </div>

    <!-- ------------- informations sur le propriétaire, modifiable unique si document de gestion à false ---------------- -->

    <div
      style="margin-top: 30px"
      v-if="declaration_data.b_document === false"
    >
      <h3>Informations sur le propriétaire</h3>
      <p>
        Le nom de la forêt et sa superficie sont issues des données transmises par
        l’ONF. Ces informations ne peuvent être modifiées. Si vous constatez une erreur,
        merci de l’indiquer dans le cadre dédié aux commentaires libres en fin de
        formulaire ou de contacter l’animateur de l’Observatoire. Veuillez cliquer sur «
        Suivant ».
      </p>

      <div
        style="
          margin-top: 10px;
          border: 1px solid #ccc;
          padding: 20px;
          border-radius: 5px;
          display: flex;
        "
      >
        <div style="width: 100%; padding-right: 20px">
          <v-text-field
            v-model="declaration_data.nom_proprietaire"
            label="Nom du propriétaire"
            :disabled="declaration_data.b_document === true"
          ></v-text-field>
          <v-text-field
            v-model="declaration_data.telephone"
            :rules="[rules.telephone]"
            :disabled="declaration_data.b_document === true"
            label="Teléphone"
          ></v-text-field>
          <v-text-field
            v-model="declaration_data.email"
            :rules="[rules.email]"
            :disabled="declaration_data.b_document === true"
            label="Email"
          ></v-text-field>
        </div>
      </div>
    </div>
</template>

<script>
import help from '@/components/form/help_static.vue';
import helpContent from '@/modules/declaration/help-content.vue';
import { formFunctions } from '@/components/form/functions/form.js';

export default {
  name: 'DeclarationFormForet',
  components: { help, helpContent },
  props: {
    declaration_data: { type: Object, required: true },
    // utilisateurs proposés dans le choix du déclarant (admins uniquement, droit >= 5)
    liste_declarants: { type: Array, default: () => [] },
  },
  data: () => ({
    rules: formFunctions.rules,
  }),
  methods: {
    formatDeclarantLabel(item) {
      if (!item) return '';
      const nom = item.nom_complet || '';
      const org = item.org_mnemo ? ` (${item.org_mnemo})` : '';
      return `${nom}${org}`;
    },
  },
};
</script>
