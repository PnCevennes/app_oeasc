<template>
  <div class="pa-6 text-center">
    <v-progress-circular indeterminate color="primary" />
    <p class="mt-4">Connexion en cours…</p>
  </div>
</template>

<script>
import { termineOidc, memoriseSonde, connecteOidc, ouvreSession } from './oidc.js';

// Page sur laquelle Échange renvoie le navigateur (/oidc/retour?code=…&state=… ou ?error=…&state=…)
export default {
  name: 'oidc-retour',
  async mounted() {
    const { code, state } = this.$route.query;
    const demande = termineOidc(state);
    if (!demande) {
      this.$router.replace({ name: 'user.login', query: { oidc: 'refus' } });
      return;
    }

    // sonde silencieuse : on retient juste si la personne est connectée à Échange
    if (demande.silencieux) {
      if (code) memoriseSonde('ok', { code, verifier: demande.verifier });
      else memoriseSonde('non');
      this.$router.replace(demande.retour);
      return;
    }

    // connexion complète (code de la sonde périmé : l'utilisateur s'est authentifié chez Échange)
    if (!code) {
      this.$router.replace({ name: 'user.login', query: { oidc: 'refus' } });
      return;
    }
    try {
      const data = await connecteOidc(code, demande.verifier);
      ouvreSession(this, data, demande.retour);
    } catch (err) {
      const motif = err && err.status === 403 ? 'inconnu' : 'injoignable';
      this.$router.replace({ name: 'user.login', query: { oidc: motif } });
    }
  },
};
</script>
