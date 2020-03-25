<template>
  <form novalidate class="md-layout" @submit.prevent="validateUser">
    <md-card class="md-layout-item form-login md-size-100">
      <md-card-header>
        <div class="md-title">Connexion</div>
      </md-card-header>

      <md-card-content>
        <md-field :class="getValidationClass('login')">
          <label for="login">Identifiant</label>
          <md-input
            name="login"
            id="login"
            autocomplete="given-name"
            v-model="form.login"
            :disabled="sending"
          />
          <span class="md-error" v-if="!$v.form.login.required"
            >Veuillez renseigner un login</span
          >
        </md-field>

        <md-field :class="getValidationClass('password')">
          <label for="password">password</label>
          <md-input
            name="password"
            id="password"
            type="password"            
            v-model="form.password"
            :disabled="sending"
          />
          <span class="md-error" v-if="!$v.form.password.required"
            >Veuillez renseigner un mot de passe</span
          >
        </md-field>
      </md-card-content>

      <md-progress-bar md-mode="indeterminate" v-if="sending" />

      <md-card-actions>
        <md-button type="submit" class="md-primary" :disabled="sending"
          >Envoyer</md-button
        >
      </md-card-actions>
    </md-card>

    <md-snackbar :md-active.sync="bMsg">{{ msg }}</md-snackbar>
  </form>
</template>

<script>
import { validationMixin } from 'vuelidate';
import { required, minLength } from 'vuelidate/lib/validators';

import { config } from '@/config/config.js';
import { apiRequest } from '@/core/js/data/api.js';

export default {
  name: 'login',
  mixins: [validationMixin],
  data: () => ({
    form: {
      login: 'admin_oeasc',
      password: 'admin_oeasc_2019',
      id_application: config.ID_APPLICATION
    },
    sending: false,
    msg: null,
    bMsg: false
  }),
  validations: {
    form: {
      login: {
        required
      },
      password: {
        required,
        minLength: minLength(3)
      }
    }
  },
  methods: {
    getValidationClass(fieldName) {
      const field = this.$v.form[fieldName];

      if (field) {
        return {
          'md-invalid': field.$invalid && field.$dirty
        };
      }
    },
    clearForm() {
      this.$v.$reset();
      this.form.login = null;
      this.form.password = null;
    },
    saveUser() {
      this.sending = true;

      // Instead of this timeout, here you can call your API
      apiRequest('POST', 'pypn/auth/login', { data:this.form }).then(
        data => {
          this.$session.set('user', data.user);
          this.$store.commit('setUser', data.user);
          this.sending = false;
          this.msg = `Connexion réussie : ${data.user.nom_role} ${data.user.prenom_role}`;
          this.bMsg = true;

          setTimeout(() => {
            this.$router.push('content/accueil');
          }, 1000);
        },
        error => {
          this.sending = false;
          this.msg = `Erreur de connexion : ${error.msg}`;
          this.bMsg = true;
          console.log('error', this.msg);
        }
      );
    },
    validateUser() {
      this.$v.$touch();

      if (!this.$v.$invalid) {
        this.saveUser();
      }
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

.error {
  background-color: white;
  color: red;
}
</style>
