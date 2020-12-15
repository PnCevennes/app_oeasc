<template>
  <div>
    <h1>Changment de mot de passe</h1>

    <generic-form :config="configFormEmail" ref="form" v-if="!token">
      <div slot="success">
        <p>Votre demande de changement de mot de passe.</p>
        <p>Un e-mail de vérification vous a été envoyé.</p>

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
            et appuyez sur
            <b>modifier le mot de passe</b>.
          </p>
        </div>
      </div>
    </generic-form>
    <generic-form :config="computedConfigFormPassword" ref="form" v-if="token">
      <div slot="success">
        <p>Votre mot de passe à été modifié.</p>
        <p>
          Vous pouvez désormais vous identifier sur la
          <a href="/#/login">page de connexion</a>
        </p>
      </div>
    </generic-form>
  </div>
</template>

<script>
import genericForm from "@/components/form/generic-form";
import configFormEmail from "./config/form-email.js";
import configFormPassword from "./config/form-password.js";

export default {
  name: "change-password",
  components: { genericForm },
  computed: {
    token() {
      return this.$route.query.token;
    },
    computedConfigFormPassword() {
      return {
        ...this.configFormPassword,
        token: this.token,
      }
    },
  },
  data: () => ({
    configFormEmail,
    configFormPassword
  }),
  mounted() {}
};
</script>
