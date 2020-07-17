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
// import { formFunctions } from "@/components/form/functions.js";
import genericForm from "@/components/form/generic-form";
import configFormUser from "./config/form-user.js";

export default {
  name: "createUser",
  components: { genericForm },
  data() {
    return {
      config: configFormUser
    };
  }
};
</script>
