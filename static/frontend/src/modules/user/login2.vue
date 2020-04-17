<template>
  <div>
    <h1>Connexion</h1>
    <div v-if="redirect">
      <p>
        Vous n'avez pas les droits requis pour accéder à la page :
        <b>
          {{ redirect }}
        </b>
      </p>
    </div>

    <div v-if="bValidToken">
      Votre compte a bien été validé. Veuillez vous connecter avec votre
      identifiant et votre mot de passe.
    </div>

    <p>Veuillez vous identifier avant de poursuivre votre navigation</p>

    <p>
      Si vous n'êtes pas inscrit, vous pouvez
      <v-btn to="/user/creer_utilisateur" color="primary"
        >Créer un compte</v-btn
      >
    </p>
    <v-form v-model="formValid" ref="form">
      <dynamic-form-group :config="configForm" :baseModel="form">
      </dynamic-form-group>
      <v-btn absolute right color="success" @click="login()">
        Se Connecter
      </v-btn>
    </v-form>

    <v-progress-linear
      indeterminate
      color="green"
      v-if="sending"
    ></v-progress-linear>

    <v-snackbar
      :color="error ? 'error' : 'success'"
      v-model="bMsg"
      :timeout="error ? 5000 : 1000"
      >{{ msg }}</v-snackbar
    >


    <a href="#/user/nouveau_mot_de_passe">Mot de passe oublié ?</a>
  </div>
</template>

<script>
import { config } from "@/config/config.js";
import { apiRequest } from "@/core/js/data/api.js";

import dynamicFormGroup from "@/components/form/dynamic-form-group";

export default {
  name: "login",
  components: { dynamicFormGroup },
  data: () => ({
    formValid: null,
    bValidToken: false,
    form: {
      login: null,
      password: null,
      id_application: config.ID_APPLICATION
    },
    configForm: {
      forms: {
        login: {
          type: "text",
          required: true,
          label: "Identifiant",
          help: true
        },
        password: {
          type: "password",
          required: true,
          label: "Mot de passe"
        }
      }
    },
    sending: false,
    msg: null,
    bMsg: false,
    error: null
  }),
  computed: {
    redirect() {
      return this.$route.params.redirect;
    },
    token() {
      return this.$route.query.token;
    }
  },
  methods: {
    login() {
      this.$refs.form.validate();
      if (!this.formValid) {
        return;
      }
      this.sending = true;
      // Instead of this timeout, here you can call your API
      apiRequest("POST", "pypn/auth/login", { data: this.form }).then(
        data => {
          const user = { ...data.user, expires: data.expires };
          this.$session.set("user", user);
          this.$store.commit("user", user);
          this.sending = false;
          this.msg = `Connexion réussie : ${data.user.nom_role} ${data.user.prenom_role}`;
          this.bMsg = true;
          this.error = false;

          setTimeout(() => {
            this.$router.push(this.redirect || "/");
          }, 1000);
        },
        error => {
          this.sending = false;
          this.msg = `Erreur de connexion : ${error.msg}`;
          this.bMsg = true;
          this.error = true;
        }
      );
    }
  },
  mounted() {
    console.log(this.$route.query.token)
    if (this.token) {
      console.log('token')
      apiRequest("POST", "pypn/register/post_usershub/valid_temp_user", {
        data: {
          id_application: config.ID_APPLICATION,
          token: this.token
        }
      }).then(
        data => {
          console.log('success valid user', data)
          this.bValidToken = true;
          this.form.login = data.identifiant;
        },
        error => {
          console.log('fail valid user', error)
          this.error = true;
          this.bMsg = true;
          this.msg = `Erreur dans la validation du compte : ${error.msg}`;
        }
      );
    }
  }
};
</script>

<style lang="scss" scoped>
.md-progress-bar {
  position: absolute;
  top: 0;
  right: 0;
  left: 0;
}

.form-login {
  width: 100%;
}
</style>
