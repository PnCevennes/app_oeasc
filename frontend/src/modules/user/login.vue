<template>
  <div>
    <v-alert
      v-if="messageOidc"
      type="error"
      variant="tonal"
      class="mb-4"
    >
      {{ messageOidc }}
    </v-alert>

    <!-- affiché seulement si la sonde silencieuse a montré que la personne est connectée à Échange -->
    <div v-if="echangeConnecte" class="mb-4">
      <v-btn
        color="primary"
        size="large"
        prepend-icon="mdi-cloud-outline"
        :loading="oidcEnCours"
        @click="connexionEchange"
      >
        Se connecter via {{ nomFournisseur }}
      </v-btn>
      <p class="text-caption mt-1">Vous êtes connecté à {{ nomFournisseur }} : un clic suffit.</p>
    </div>

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
import {
  configOidc,
  demarreOidc,
  etatSonde,
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
      if (!conf || !conf.enabled) return;
      this.nomFournisseur = conf.provider;
      // pas de sonde pendant la validation d'un compte (?token=…) ni juste après un échec
      if (this.token || this.$route.query.oidc) return;

      const etat = etatSonde();
      if (etat === 'ok') {
        this.echangeConnecte = true;
      } else if (etat === null) {
        try {
          // revient sur cette même page (query comprise) avec le résultat de la sonde
          await demarreOidc(this.$route.fullPath, { silencieux: true });
        } catch (err) {
          // stockage refusé ou Échange injoignable : simplement pas de bouton
        }
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
  mounted() {
    this.initOidc();
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
