<template>
  <div>
    <h1>Connexion</h1>
    <generic-form :config="config" ref="form">
      <div slot="prependForm">
        <div v-if="redirect">
          <p>
            Vous n'avez pas les droits requis pour accéder à la page :
            <b>
              {{ redirect }}
            </b>
          </p>
        </div>

        <div v-if="bValidToken">
          <p>
            Votre compte a bien été validé. Veuillez vous connecter avec votre
            identifiant et votre mot de passe.
          </p>
        </div>

        <div v-else>
          <p>Veuillez vous identifier avant de poursuivre votre navigation</p>
        </div>

        <p>
          Si vous n'êtes pas inscrit, vous pouvez
          <v-btn to="/user/creer_utilisateur" color="primary">
            Créer un compte
          </v-btn>
        </p>
      </div>
      <div slot="appendForm">
        
        <a href="#/user/change_password">Mot de passe oublié ?</a>
      </div>
    </generic-form>
  </div>
</template>

<script>
import genericForm from "@/components/form/generic-form";
import { config } from "@/config/config.js";
import { apiRequest } from "@/core/js/data/api.js";

export default {
  name: "login2",
  components: { genericForm },
  computed: {
    redirect() {
      return this.$route.query.redirect;
    },
    token() {
      return this.$route.query.token;
    }
  },
  data() {
    return {
      bValidToken: null,
      config: {
        request: {
          url: "pypn/auth/login",
          method: "POST",
          label: "Se connecter",
          preProcess: ({ baseModel }) => ({
            ...baseModel,
            id_application: config.ID_APPLICATION
          }),
          onSuccess: data => {
            const user = { ...data.user, expires: data.expires };
            this.$session.set("user", user);
            this.$store.commit("user", user);
            setTimeout(() => {
              this.$router.push(this.redirect || "/");
            }, 1000);
          }
        },
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
      }
    };
  },
  mounted() {
    console.log(this.token);
    if (this.token) {
      apiRequest("POST", "pypn/register/post_usershub/valid_temp_user", {
        data: {
          id_application: config.ID_APPLICATION,
          token: this.token
        }
      }).then(
        data => {
          console.log("success valid user", data);
          this.bValidToken = true;
          this.$refs.form.baseModel.login = data.identifiant;
        },
        error => {
          console.log("fail valid user", error);
          this.$refs.form.msgError = `Erreur dans la validation du compte : ${error.msg}`;
          this.$refs.form.bError = true;
        }
      );
    }
  }
};
</script>
