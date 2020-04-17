<template>
  <div>
    <h1>Changment de mot de passe</h1>

    <generic-form :config="configEmail" ref="form" v-if="!token">
      <div slot="success">
        <p>
          Votre demande de changement de mot de passe.
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
          afin de procéder au changement de mot de passe.
        </p>
      </div>
      <div slot="prependForm">
        <div>
          <p>
            Entrez votre identifiant (e-mail utilisé pour la création du compte)
            et appuyez sur <b>modifier le mot de passe</b>.
          </p>
        </div>
      </div>
    </generic-form>
    <generic-form :config="configPassword" ref="form" v-if="token">
      <div slot="success">
        <p>
          Votre mot de passe à été modifié.
        </p>
        <p>
          Vous pouvez désormais vous identifier sur la
          <a href="/#/login">
            page de connexion
          </a>
        </p>
      </div>
    </generic-form>
  </div>
</template>

<script>
import genericForm from "@/components/form/generic-form";
import { formFunctions } from "../../components/form/functions";

export default {
  name: "change-password",
  components: { genericForm },
  computed: {
    token() {
      return this.$route.query.token;
    }
  },
  data() {
    return {
      configEmail: {
        request: {
          url: "pypn/register/post_usershub/create_cor_role_token",
          method: "POST",
          label: "Modifier votre mot de passe",
          
        },
        forms: {
          email: {
            type: "text",
            required: true,
            label: "E-mail",
            rules: [formFunctions.rules.email]
          }
        }
      },
      configPassword: {
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
        request: {
          url: "pypn/register/post_usershub/change_password",
          method: "POST",
          label: "Modifier votre mot de passe",
          preProcess: ({ baseModel }) => ({ ...baseModel, token: this.token })
        },
        forms: {
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
  },
  mounted() {
    this.$refs.form.baseModel = {
      email: "joelclems@gmail.com",
      password_confirmation: "1234",
      password: "1234"
    };
  }
};
</script>
