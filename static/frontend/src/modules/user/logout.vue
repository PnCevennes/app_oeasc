<template>
<div>
  
    <md-snackbar :md-active.sync="bMsg">{{ msg }}</md-snackbar>
</div>
</template>

<script>
import { apiRequest } from '@/core/js/data/api.js';

export default {
  name: 'logout',
  data: () => ({
    msg: '',
    bMsg: false
  }),
  created: function() {
    apiRequest('GET', 'pypn/auth/logout?redirect=/api/user/logout_external', {
      acceptedStatus: [200, 302]
    }).then(
      () => {
        this.msg = "Déconnexion réussie, redirection vers la page d'accueil";
        this.$session.set('user', null)
        this.$store.commit('setUser', null)
        this.bMsg = true;
        setTimeout(() => {
          this.$router.push('content/accueil');
        }, 1000);
      },
      error => {
        this.msg = `Error logout : ${error}`;
        this.bMsg = true;
      }
    );
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
