<template>
  <div>
    <h1>Inscription</h1>
    <generic-form ref="form" :config="config">
      <div slot="success">
        <p>
          Votre demande d'inscription est bien prise en compte.
        </p>
        <p>
          Un e-mail de vérification vous a été envoyé.
        </p>

        <p>
          Il est possible que celui-ci ait été placé par votre boite mail dans
          votre dossier "spam" ou "courrier indésirable". Pensez donc à vérifier
          celui-ci si vous ne trouvez pas notre e-mail dans votre boîte de
          réception habituelle.
        </p>
        <p>
          Veuillez cliquer sur le lien de confirmation présent dans cet e-mail
          afin de valider votre compte.
        </p>
      </div>
      <div slot="prependForm"></div>
    </generic-form>
  </div>
</template>

<script>
import { formFunctions } from "@/components/form/functions.js";
import genericForm from "@/components/form/generic-form";
import { config } from "@/config/config.js";

export default {
  name: "createUser",
  components: { genericForm },
  data() {
    return {
      config: {
        watchBaseModel({ config, baseModel }) {
          if (!(config && baseModel)) {
            return;
          }
          config.forms.password_confirmation.rules = [
            v => {
              return (
                v === baseModel.password ||
                "Les mot de passe doivent être identiques"
              );
            }
          ];
        },
        display: "table",
        preLoadData: () => {
          return new Promise(resolve => {
            this.$store.dispatch("organismes").then(() => {
              resolve();
            });
          });
        },
        request: {
          method: "POST",
          url: "pypn/register/post_usershub/create_temp_user",
          label: "S'inscrire",
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

        dense: true,
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
            label: "E-mail"
          },
          id_organisme: {
            type: "list_form",
            required: true,
            label: "Organisme",
            display: "select",
            url: "api/user/organismes",
            textFieldName: "nom_organisme",
            valueFieldName: "id_organisme"
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
            }
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
            ]
          },
          accept_email: {
            type: 'bool_switch',
            label: "Rester informé des principales évolutions du dispositif (envoi ponctuel d’e-mails)",
            required: true, 
          },
          password: {
            type: "password",
            label: "Mot de passe",
            required: true,
            counter: true
          },
          password_confirmation: {
            type: "password",
            label: "Mot de passe (confirmation)",
            required: true,
            counter: true
          }
        }
      }
    };
  }
};
</script>
