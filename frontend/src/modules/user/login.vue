<template>
  <div>
    <generic-form
      :config="config"
      ref="form"
    >
      <template #prependForm>
      <div>
        <div v-if="redirect">
          <p>Vous n'avez pas les droits requis pour accéder à cette page.</p>
        </div>

        <div v-if="bValidToken">
          <p>
            Votre compte a bien été validé. Veuillez vous connecter avec votre identifiant et votre
            mot de passe.
          </p>
        </div>

        <div v-else>
          <p>Veuillez vous identifier avant de poursuivre votre navigation</p>
        </div>

        <p>
          Si vous n'êtes pas inscrit, vous pouvez
          <v-btn
            to="/user/creer_utilisateur"
            color="primary"
          >
            Créer un compte
          </v-btn>
        </p>
      </div>
      </template>
      <template #appendForm>
        <router-link class="d-inline-block mt-4" to="/user/change_password">
          Mot de passe oublié ?
        </router-link>
      </template>
    </generic-form>
  </div>
</template>

<script>
import genericForm from '@/components/form/generic-form';
import { config } from '@/config/config.js';
import { apiRequest } from '@/core/js/data/api.js';
import configFormLogin from './config/form-login';

export default {
  name: 'login',
  components: { genericForm },
  computed: {
    redirect() {
      return this.$route.query.redirect;
    },
    token() {
      return this.$route.query.token;
    },
  },
  data() {
    return {
      bValidToken: null,
      config: configFormLogin,
    };
  },
  mounted() {
    if (this.token) {
      apiRequest('POST', 'register/post_usershub/valid_temp_user', {
        postData: {
          id_application: config.ID_APPLICATION,
          token: this.token,
        },
      }).then(
        (data) => {
          this.bValidToken = true;
          this.$refs.form.baseModel.login = data.identifiant;
        },
        (error) => {
          this.$refs.form.msgError = `Erreur dans la validation du compte : ${error.msg}`;
          this.$refs.form.bError = true;
        }
      );
    }
  },
};
</script>
