<template>
  <div class="page-login">
    <v-alert
      v-if="messageOidc"
      type="error"
      variant="tonal"
      class="mb-4"
    >
      {{ messageOidc }}
    </v-alert>

    <!-- /login?diag=1 : état de la connexion via Échange, pour comprendre l'absence du bouton -->
    <v-alert v-if="$route.query.diag" type="info" variant="tonal" density="compact" class="mb-4">
      Diagnostic Échange : {{ diagOidc }}
    </v-alert>

    <generic-form
      :config="config"
      ref="form"
    >
      <template #prependForm>
        <div>
          <!-- affiché seulement si la sonde silencieuse a montré que la personne est connectée à Échange -->
          <v-card
            v-if="echangeConnecte"
            class="carte-echange mt-3 mb-2"
            variant="tonal"
            color="primary"
            rounded="lg"
          >
            <v-card-text class="text-center">
              <v-icon size="40" class="mb-2">mdi-account-check-outline</v-icon>
              <div class="text-h6">Vous êtes connecté à {{ nomFournisseur }}</div>
              <div class="text-body-2 mb-4">Accédez à OEASC en un clic, sans mot de passe.</div>
              <v-btn
                color="primary"
                variant="elevated"
                size="x-large"
                block
                prepend-icon="mdi-login-variant"
                :loading="oidcEnCours"
                @click="connexionEchange"
              >
                Se connecter via {{ nomFournisseur }}
              </v-btn>
            </v-card-text>
          </v-card>

          <div v-if="echangeConnecte" class="separateur-ou my-4">
            <span>ou avec votre identifiant OEASC</span>
          </div>

          <v-alert v-if="redirect" type="warning" variant="tonal" density="compact" class="mb-4">
            Vous n'avez pas les droits requis pour accéder à cette page.
          </v-alert>

          <v-alert v-if="bValidToken" type="success" variant="tonal" density="compact" class="mb-4">
            Votre compte a bien été validé. Veuillez vous connecter avec votre identifiant et votre
            mot de passe.
          </v-alert>

          <p v-else-if="!echangeConnecte" class="mb-4">
            Veuillez vous identifier avant de poursuivre votre navigation.
          </p>
        </div>
      </template>
      <template #appendForm>
        <div class="liens-login mt-4">
          <router-link to="/user/change_password">Mot de passe oublié ?</router-link>
          <v-divider class="my-4" />
          <span class="mr-2">Pas encore inscrit ?</span>
          <v-btn
            to="/user/creer_utilisateur"
            color="primary"
            variant="outlined"
            size="small"
          >
            Créer un compte
          </v-btn>
        </div>
      </template>
    </generic-form>
  </div>
</template>

<script>
import genericForm from '@/components/form/generic-form';
import { config } from '@/config/config.js';
import { apiRequest } from '@/core/js/data/api.js';
import configFormLogin from './config/form-login';
import {
  configOidc,
  demarreOidc,
  etatSonde,
  diagnosticSonde,
  prendCodeSonde,
  connecteOidc,
  ouvreSession,
} from './oidc.js';

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
      echangeConnecte: false,
      nomFournisseur: 'Échange',
      oidcEnCours: false,
      messageOidc: '',
      diagOidc: 'en cours…',
      sondeLancee: false,
    };
  },
  methods: {
    // sonde silencieuse : le bouton n'apparaît que si la personne est connectée à Échange
    async initOidc() {
      const motifs = {
        refus: "La connexion via Échange a été refusée ou interrompue.",
        inconnu:
          "Votre compte Échange n'est rattaché à aucun compte OEASC actif. Connectez-vous avec votre identifiant OEASC ou contactez l'administrateur.",
        injoignable: "Échange est injoignable pour le moment. Réessayez plus tard.",
      };
      this.messageOidc = motifs[this.$route.query.oidc] || '';

      const conf = await configOidc();
      if (!conf || !conf.enabled) {
        this.diagOidc = conf
          ? "connexion via Échange désactivée dans la configuration du serveur (section oidc)"
          : "l'API api/user/oidc/config ne répond pas";
        return;
      }
      this.nomFournisseur = conf.provider;
      // pas de sonde pendant la validation d'un compte (?token=…) ni juste après un échec
      if (this.token || this.$route.query.oidc) {
        this.diagOidc = 'sonde non lancée (paramètre token ou oidc dans l\'URL) — ' + diagnosticSonde();
        return;
      }

      const etat = etatSonde();
      this.diagOidc = diagnosticSonde();
      if (etat === 'ok' || etat === 'consentement') {
        this.echangeConnecte = true;
      } else if (etat === null) {
        // une seule sonde à la fois (focus et visibilitychange peuvent se déclencher ensemble)
        if (this.sondeLancee) return;
        this.sondeLancee = true;
        this.diagOidc = 'lancement de la sonde vers Échange…';
        try {
          // revient sur cette même page (query comprise) avec le résultat de la sonde
          await demarreOidc(this.$route.fullPath, { silencieux: true });
        } catch (err) {
          this.sondeLancee = false;
          // stockage refusé ou Échange injoignable : simplement pas de bouton
          this.diagOidc = 'sonde impossible : ' + ((err && (err.message || err.err)) || 'erreur inconnue');
        }
      }
    },
    surRetourOnglet() {
      if (document.visibilityState === 'visible' && !this.echangeConnecte && !this.oidcEnCours) {
        this.initOidc();
      }
    },
    async connexionEchange() {
      this.oidcEnCours = true;
      this.messageOidc = '';
      const retour = this.$route.fullPath;
      const sonde = prendCodeSonde();
      try {
        if (!sonde) throw { status: 'expire' };
        ouvreSession(this, await connecteOidc(sonde.code, sonde.verifier), retour);
      } catch (err) {
        if (err && err.status === 403) {
          this.messageOidc = "Votre compte Échange n'est rattaché à aucun compte OEASC actif. Connectez-vous avec votre identifiant OEASC ou contactez l'administrateur.";
        } else {
          // code périmé ou déjà utilisé : on repasse par Échange (sans page s'il est toujours connecté)
          try {
            await demarreOidc(retour);
            return;
          } catch (e) {
            this.messageOidc = 'Échange est injoignable pour le moment. Réessayez plus tard.';
          }
        }
        this.echangeConnecte = false;
      } finally {
        this.oidcEnCours = false;
      }
    },
  },
  beforeUnmount() {
    document.removeEventListener('visibilitychange', this.surRetourOnglet);
    window.removeEventListener('focus', this.surRetourOnglet);
  },
  mounted() {
    this.initOidc();
    // on revient sur cet onglet après s'être connecté à Échange ailleurs : nouvelle sonde
    document.addEventListener('visibilitychange', this.surRetourOnglet);
    window.addEventListener('focus', this.surRetourOnglet);
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

<style scoped>
.page-login {
  max-width: 560px;
  margin: 0 auto;
  padding: 16px;
}

/* generic-form impose min-width: 800px : on l'annule ici pour que la page tienne sur mobile */
.page-login :deep(.form-container) {
  min-width: 0;
}

.carte-echange {
  border: 2px solid rgb(var(--v-theme-primary));
}

/* « ou avec votre identifiant OEASC » : trait de part et d'autre du texte */
.separateur-ou {
  display: flex;
  align-items: center;
  gap: 12px;
  color: rgba(var(--v-theme-on-surface), 0.6);
  font-size: 0.875rem;
}

.separateur-ou::before,
.separateur-ou::after {
  content: '';
  flex: 1;
  border-top: 1px solid rgba(var(--v-theme-on-surface), 0.2);
}
</style>
