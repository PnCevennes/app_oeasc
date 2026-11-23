<template>
  <div></div>
</template>

<script>
import { apiRequest } from '@/core/js/data/api.js';

export default {
  name: 'logout',
  data: () => ({
    msg: '',
    bMsg: false,
  }),
  created: function () {
    // quel que soit le résultat de l'appel (la redirection 302 du backend peut faire échouer
    // la lecture JSON), on vide l'utilisateur du store et on retourne à l'accueil
    apiRequest('GET', 'auth/logout?redirect=/api/user/logout_external', {
      acceptedStatus: [200, 302],
    })
      .catch((error) => {
        console.error(`Erreur logout : ${error}`);
      })
      .finally(() => {
        this.$store.commit('user', null);
        this.$router.push('/');
      });
  },
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
