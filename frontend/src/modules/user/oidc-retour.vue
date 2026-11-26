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
      else {
        // visible dans la console du navigateur : login_required = pas connecté à Échange,
        // consent_required / invalid_* = problème de configuration du client Nextcloud
        console.info('[OIDC Échange] sonde sans code :', this.$route.query.error, this.$route.query.error_description);
        const { error, error_description: detail } = this.$route.query;
        const erreur = [error, detail].filter(Boolean).join(' : ') || 'aucun code ni erreur';
        // consent_required / interaction_required : la personne EST connectée à Échange, qui a
        // seulement besoin d'afficher une page (accord pour OEASC) : le bouton s'affiche et son
        // clic lance la connexion avec page
        const connecte = ['consent_required', 'interaction_required'].includes(error);
        memoriseSonde(connecte ? 'consentement' : 'non', { erreur });
      }
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
