<template>
  <div>
    <h1>Espace utilisateur</h1>
    <generic-form :config="config" ref="form"> </generic-form>
  </div>
</template>

<script>
import genericForm from "@/components/form/generic-form";
import { formFunctions } from "@/components/form/functions.js";
// import { apiRequest } from "@/core/js/data/api.js";
import { config } from "@/config/config.js";

export default {
  name: "userPage",
  components: { genericForm },
  data: function() {
    return {
      config: {
        preLoadData: () => {
          return new Promise(resolve => {
            Promise.all([
              this.$store.dispatch(
                "userInfo",
                this.$store.getters.user.id_role
              ),
              this.$store.dispatch("organismes")
            ]).then(data => {
              this.config.value = data[0];
              resolve();
            });
          });
        },
        switchDisplay: true,
        displayValue: true,
        title: "Informations",
        request: {
          url: "pypn/register/post_usershub/update_user",
          method: "POST",
          label: "Valider",
          preProcess: ({ baseModel }) => {
            baseModel.groupe = false;
            baseModel.id_application = config.ID_APPLICATION;
            baseModel.pn = true;
            baseModel.identifiant = baseModel.email;
            baseModel.remarques = "Créé depuis le site de l'OEASC";
            baseModel.champs_addi = {};
            if (baseModel.autre_organisme) {
              baseModel.champs_addi.organisme = baseModel.autre_organisme;
            }
            if (baseModel.accept_email) {
              baseModel.champs_addi.accept_email = baseModel.accept_email;
            }

            return baseModel;
          }
        },

        display: "table",
        forms: {
          nom_role: {
            type: "text",
            required: true,
            label: "Nom"
          },
          prenom_role: {
            type: "text",
            required: true,
            label: "Prenom"
          },
          email: {
            required: true,
            rules: [formFunctions.rules.email],
            type: "text",
            label: "E-mail",
            disabled: true
          },
          id_organisme: {
            type: "list_form",
            required: true,
            label: "Organisme",
            display: "select",
            url: "api/user/organismes",
            textFieldName: "nom_organisme",
            valueFieldName: "id_organisme",
            disabled: true
          },
          autre_organisme: {
            type: "text",
            required: true,
            label: "Préciser organisme",
            condition: ({ baseModel, $store }) => {
              const organisme = $store.getters.organismes.find(
                o => o.id_organisme == baseModel.id_organisme
              );
              return !!(
                organisme && organisme.nom_organisme == "Autre (préciser)"
              );
            },
            disabled: true
          },
          desc_role: {
            type: "list_form",
            required: true,
            label: "Rôle",
            display: "select",
            items: [
              "Propriétaire forestier privé",
              "Salarié, agent, fonctionnaire",
              "Expert forestier indépendant",
              "Autre"
            ]
          },
          accept_email: {
            type: "bool_switch",
            label:
              "Acceptez vous de recevoir des nouvelles de l'OEASC par email ?",
            required: true
          }
        }
      }
    };
  }
};
</script>

<style lang="scss" scoped></style>
