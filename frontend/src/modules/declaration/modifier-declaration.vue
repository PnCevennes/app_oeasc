<template>
  <div style="margin: 40px; width: 100%">
    <h1>{{ title }}</h1>
    <h3 v-if="declaration_data.id_declaration_originale">
      Renouvellement de la
      <router-link
        :to="{
          name: 'voir_declaration',
          params: { id: declaration_data.id_declaration_originale },
        }"
      >
        déclaration no {{ declaration_data.id_declaration_originale }}
      </router-link>
    </h3>

    <div>
      <div v-if="etape_affichage === 'AFFICHAGE_FORM'">
        <div v-if="initialized">
          <p>
            Besoin d'aide
            <help style="margin-left: 30px">
              Personnes à contacter
              <tableAide></tableAide>
            </help>
          </p>

          <v-form ref="form">
            <!-- premier encart -->
            <div>
              <h2>Informations sur la forêt</h2>
              <h4>Status</h4>
              <div
                style="margin-top: 10px; border: 1px solid #ccc; padding: 20px; border-radius: 5px"
              >
                <div style="display: flex; align-items: center">
                  <span>Status de la forêt</span>
                  <span class="required">*</span>

                  <v-radio-group
                    v-model="declaration_data.b_statut_public"
                    :rules="[rules.required]"
                    inline
                    density="compact"
                    hide-details="auto"
                    class="flex-grow-0"
                  >
                    <v-radio
                      inline
                      label="Public"
                      :value="true"
                    ></v-radio>
                    <v-radio
                      inline
                      label="Privée"
                      :value="false"
                    ></v-radio>
                  </v-radio-group>

                  <help style="margin-left: 20px">
                    <helpContent helpID="form_statut_foret"></helpContent>
                  </help>
                </div>

                <div style="display: flex; align-items: center">
                  <span v-if="declaration_data.b_statut_public">
                    La forêt relève-t-elle du régime forestier ?
                  </span>
                  <span v-else>
                    La forêt est-elle dotée d'un document de gestion durable (plan simple de gestion
                    ou code de bonnes pratiques sylvicoles) ?
                  </span>
                  <span class="required">*</span>

                  <v-radio-group
                    v-model="declaration_data.b_document"
                    :rules="[rules.required]"
                    inline
                    density="compact"
                    hide-details="auto"
                  >
                    <v-radio
                      inline
                      label="Oui"
                      :value="true"
                    ></v-radio>
                    <v-radio
                      inline
                      label="Non"
                      :value="false"
                    ></v-radio>
                  </v-radio-group>
                </div>
              </div>
            </div>

            <v-fade-transition
              v-if="
                declaration_data &&
                'b_statut_public' in declaration_data &&
                'b_document' in declaration_data
              "
            >
              <div>
                <!-- ------------------  La carte  ---------------------  -->

                <div>
                  <div><h3>Localisation</h3></div>

                  <div style="width: 100%; position: relative">
                    <MapDeclaration
                      :b_statut_public="declaration_data.b_statut_public"
                      :b_document="declaration_data.b_document"
                      :declaration_data="declaration_data"
                      @layer-selected="handleLayerSelect"
                    />
                  </div>

                  <div
                    v-if="
                      areas_infos.forets.length ||
                      areas_infos.secteurs.length ||
                      areas_infos.communes.length
                    "
                    style="
                      margin-top: 12px;
                      border: 1px solid #ccc;
                      padding: 16px;
                      border-radius: 5px;
                    "
                  >
                    <p
                      v-if="areas_infos.forets.length"
                      style="margin: 4px 0"
                    >
                      <strong>Forêt(s) :</strong>
                      {{ areas_infos.forets.map((f) => f.area_name).join(', ') }}
                    </p>
                    <p
                      v-if="areas_infos.secteurs.length"
                      style="margin: 4px 0"
                    >
                      <strong>Secteur(s) :</strong>
                      {{ areas_infos.secteurs.map((s) => s.area_name).join(', ') }}
                    </p>
                    <p
                      v-if="areas_infos.communes.length"
                      style="margin: 4px 0"
                    >
                      <strong>Commune(s) :</strong>
                      {{ areas_infos.communes.map((c) => c.area_name).join(', ') }}
                    </p>
                  </div>
                </div>

                <declaration-form-foret
                  :declaration_data="declaration_data"
                  :liste_declarants="liste_declarants"
                />


                <!-- ---------- Informations sur le peuplement ------------------- -->

                <declaration-form-peuplement
                  :declaration_data="declaration_data"
                  :nomenclature="nomenclature"
                  :form-invalid="!!($refs.form && !$refs.form.valid)"
                />

                <!-- ---------- Informations sur les dégats ------------------- -->

                <div style="margin-top: 30px">
                  <h3>Informations sur les dégats</h3>
                  <div
                    class="encadrer"
                    style="padding-left: 20px"
                  >
                    <degatsForm
                      :declaration_data="declaration_data"
                      :nomenclature="nomenclature"
                    ></degatsForm>
                  </div>
                </div>

                <div style="margin-top: 30px">
                  <h3>Précisions sur la localisation des degats</h3>
                  <div
                    class="encadrer"
                    style="padding-left: 20px"
                  >
                    <v-textarea
                      v-model="declaration_data.precision_localisation"
                      label="Précisions sur la localisation des dégâts"
                      rows="2"
                      auto-grow
                    ></v-textarea>
                  </div>
                </div>

                <div style="margin-top: 30px">
                  <h3>Commentaires</h3>
                  <div
                    class="encadrer"
                    style="padding-left: 20px"
                  >
                    <p>
                      Vous pouvez indiquer ici des informations complémentaires sur la déclaration,
                      par exemple des précisions sur les dégâts constatés, les conditions de la
                      forêt, etc.
                    </p>
                    <v-textarea
                      v-model="declaration_data.commentaire"
                      label="Commentaires"
                      rows="4"
                      auto-grow
                    ></v-textarea>
                  </div>
                </div>

                <!-- --------------------- Bouton de validation --------------------- -->

                <div style="margin-top: 30px; display: flex">
                  <v-btn
                    color="primary"
                    @click="action_terminer_declaration"
                  >
                    Terminer la déclaration
                  </v-btn>
                </div>
              </div>
            </v-fade-transition>
          </v-form>
        </div>

        <div v-else>
          Chargement en cours
          <v-progress-linear
            active
            indeterminate
          ></v-progress-linear>
        </div>
      </div>

      <!-- Lorsque l'utilisateur valide une première fois son formulaire un résumé et un bouton de validation
       apparait -->
      <div v-else-if="initialized && etape_affichage === 'AFFICHAGE_RESUME'">
        <h2>Résumé de la déclaration</h2>
        <div>
          <p>Veuillez vérifier les informations saisies avant de soumettre la déclaration.</p>
          <div style="margin-top: 30px">
            <h3>Résumé et validation</h3>
            <div
              class="encadrer"
              style="padding-left: 20px"
            >
              <!-- --------------------- Résumé de la déclaration --------------------- -->
              <div>
                <resumeDeclaration
                  :declaration_data="declaration_data"
                  :nomenclature="nomenclature"
                ></resumeDeclaration>
              </div>
            </div>
          </div>

          <!-- --------------------- Autorisation de transmission d'informations --------------------- -->
          <div v-if="type_action !== 'CLOTURE'">
            <p>
              J’autorise la transmission des informations fournies aux responsables cynégétiques
              locaux, pour pouvoir adapter la pression de chasse
            </p>
            <v-radio-group
              v-model="declaration_data.b_autorisation"
              :rules="[rules.required]"
              inline
              density="compact"
              hide-details="auto"
            >
              <v-radio
                inline
                label="Oui"
                :value="true"
              ></v-radio>
              <v-radio
                inline
                label="Non"
                :value="false"
              ></v-radio>
            </v-radio-group>
          </div>

          <!-- --------------------- Validation directe de la déclaration pour les admins --------------------- -->
          <div v-if="type_action == 'CREATION' || type_action == 'MODIFICATION'">
            <div
              v-if="this.$store.getters.droitMax >= 5"
              style="margin-top: 30px"
            >
              <h3>Validation de la déclaration pour les admins</h3>
              <div style="padding-left: 20px">
                <v-radio-group
                  v-model="declaration_data.b_valid"
                  :mandatory="false"
                  inline
                  density="compact"
                  hide-details="auto"
                >
                  <v-radio
                    inline
                    label="Oui"
                    :value="true"
                  ></v-radio>
                  <v-radio
                    inline
                    label="Non"
                    :value="false"
                  ></v-radio>
                </v-radio-group>
              </div>
            </div>
          </div>

          <div v-if="type_action !== 'CLOTURE'">
            <v-btn
              color="primary"
              @click="etape_affichage = 'AFFICHAGE_FORM'"
              style="margin-right: 30px"
              :disabled="processing == true"
            >
              Retourner à la déclaration
            </v-btn>
            <v-btn
              color="success"
              @click="submitDeclaration"
              :disabled="processing == true"
            >
              <span v-if="type_action == 'RENOUVELLEMENT'">Renouveller ma déclaration</span>
              <span v-else>Soumettre la déclaration</span>
            </v-btn>
          </div>

          <div
            v-if="type_action === 'CLOTURE'"
            style="margin-top: 30px; display: flex; justify-content: center"
          >
            <v-btn
              color="red"
              @click="closeDeclaration"
              :disabled="processing"
              style="width: 100%; max-width: 400px; height: 50px"
            >
              Cloturer cette déclaration
            </v-btn>
          </div>
          <v-progress-linear
            v-if="processing"
            active
            indeterminate
          ></v-progress-linear>
        </div>
      </div>
    </div>

    <!-- affiche un encart en bas de page si l'utilisateur valide sa déclaration et qu'il manque des informations -->
    <div
      style="
        position: fixed;
        bottom: 20px;
        left: 0;
        width: 100%;
        display: flex;
        justify-content: center;
        z-index: 9999;
      "
    ></div>

    <v-dialog
      v-model="affichage_fenetre_succes"
      max-width="600"
    >
      <v-card>
        <v-card-title class="headline">
          {{
            type_action == 'CLOTURE'
              ? 'Votre déclaration a bien été clôturée'
              : 'Votre déclaration a bien été enregistrée'
          }}
        </v-card-title>
        <v-card-text>
          <p>Vous pouvez désormais</p>
          <ul>
            <li>
              <a
                href="#"
                @click.prevent="goTo('/declaration/declarer_en_ligne')"
              >
                Déclarer de nouveaux dégâts en forêt
              </a>
            </li>
            <li v-if="type_action != 'CLOTURE'">
              <a
                href="#"
                @click.prevent="goTo('/declaration/liste')"
              >
                Voir la liste des dégâts déclarés
              </a>
            </li>
            <li>
              <a
                href="#"
                @click.prevent="goTo('/')"
              >
                Retourner à l'accueil
              </a>
            </li>
          </ul>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            variant="text"
            @click="affichage_fenetre_succes = false"
          >
            Fermer
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog
      v-model="affichage_fenetre_token_invalide"
      max-width="600"
      persistent
    >
      <v-card>
        <v-card-title class="headline">Lien invalide ou expiré</v-card-title>
        <v-card-text>
          <p>Le lien utilisé n'est plus valide, il a peut-être déjà été utilisé ou a expiré.</p>
          <p>Pour gérer vos déclarations, veuillez vous connecter à votre compte.</p>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            variant="text"
            @click="goTo('/')"
          >
            Retourner à l'accueil
          </v-btn>
          <v-btn
            color="primary"
            variant="flat"
            @click="redirect_to_login"
          >
            Se connecter
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import help from '@/components/form/help_static.vue';
import tableAide from '@/modules/content/table-aide.vue';
import { formFunctions } from '@/components/form/functions/form.js';
import { apiRequest } from '@/core/js/data/api';
import { fetch_forets_from_code } from './utils/api_request.js';
import MapDeclaration from './map/map_declaration.vue';
import degatsForm from '@/components/form/degats_declaration_form.vue';
import resumeDeclaration from '@/modules/declaration/resume_declaration.vue';
import helpContent from '@/modules/declaration/help-content.vue';
import DeclarationFormPeuplement from './declaration-form-peuplement.vue';
import DeclarationFormForet from './declaration-form-foret.vue';
import { snackbarStore } from '@/store/snackbar';

export default {
  name: 'ModifierDeclaration',

  props: [],
  components: {
    help,
    tableAide,
    MapDeclaration,
    degatsForm,
    resumeDeclaration,
    helpContent,
    DeclarationFormPeuplement,
    DeclarationFormForet,
  },

  data() {
    return {
      nomenclature: {}, // Nomenclature des essences et autres données
      title: '',
      declaration_data: {}, // Données de la déclaration
      liste_declarants: [], // Liste des déclarants, à récupérer si l'utilisateur a un droit >= 5
      storeName: 'declaration',
      declarationId: this.$route.query.id, // ID de la déclaration à modifier récupéré depuis l'URL
      token_renouvellement: this.$route.query.token, // Token récupéré depuis l'URL
      action: this.$route.query.action, // Action à effectuer (modifier ou dupliquer) récupérée depuis l'URL
      initialized: false, // Ajouté pour suivre l'état d'initialisation
      processing: false, // les boutons seront désactivés si processing est à true, pour éviter les doubles clics
      error: null, // Ajouté pour stocker les erreurs potentielles
      selected: [], // IDs sélectionnés pour la carte
      rules: formFunctions.rules, // Règles de validation

      // Étape d'affichage du formulaire (
      // AFFICHAGE_FORM => formulaire classique
      // AFFICHAGE_RESUME => résumé de la déclaration avant validation
      etape_affichage: 'AFFICHAGE_FORM',

      // type_action: action de l'utilisateur, qui peut être :
      // CREATION => création d'une nouvelle déclaration,
      // MODIFICATION => modification d'une déclaration existante,
      // RENOUVELLEMENT => Renouvellement d'une déclaration existante
      // CLOTURE => clôture d'une déclaration existante
      type_action: '',
      information_declarant: {}, // Informations sur la personne connectée
      // liste_selection_essences: [], // Liste des essences sélectionnées
      affichage_fenetre_succes: false, // Affichage de la fenêtre de succès après soumission
      affichage_fenetre_token_invalide: false, // Affichage de la fenêtre invitant à se connecter si le token de renouvellement/clôture est invalide
      affichage_peuplement_maturite: false, // Affichage de la maturité du peuplement
      response: null, // Réponse de l'API lors de la récupération des données de la déclaration
      areas_infos: { forets: [], secteurs: [], communes: [] },
    };
  },

  computed: {},
  watch: {
    // si l'utilisateur à selectionné une autre foret, on met à jours les données de propriétaire et le nom et la superficie de la foret
    'declaration_data.code_foret'(newVal, oldVal) {
      if (newVal && newVal !== oldVal && oldVal !== undefined) {
        fetch_forets_from_code(newVal)
          .then((result) => {
            if (result && result.label_foret) {
              this.declaration_data.label_foret = result.label_foret;
              this.declaration_data.surface_renseignee = result.surface_renseignee;
              this.declaration_data.nom_foret = result.nom_foret;
              // Les données propriétaire sont désormais dans t_forets
              this.declaration_data.nom_proprietaire = result.nom_proprietaire;
              this.declaration_data.adresse = result.adresse;
              this.declaration_data.s_commune_proprietaire = result.s_commune_proprietaire;
              this.declaration_data.telephone = result.telephone;
              this.declaration_data.email = result.email;
            }
          })
          .catch((error) => {
            console.error('Erreur lors de la récupération des données de la forêt:', error);
          });
      }
    },
    'declaration_data.areas_localisation_cadastre': {
      handler() {
        this.refresh_areas_infos();
      },
      deep: true,
    },
    'declaration_data.areas_localisation_onf_ug': {
      handler() {
        this.refresh_areas_infos();
      },
      deep: true,
    },
    'declaration_data.b_document'(newVal, oldVal) {
      if (newVal === false && oldVal !== undefined) {
        // Si le document de gestion est activé, on désactive les champs de nom de forêt et superficie
        this.declaration_data.nom_proprietaire = this.information_declarant.nom_complet;
        this.declaration_data.adresse = '';
        this.declaration_data.s_commune_proprietaire = '';
        this.declaration_data.telephone = '';
        this.declaration_data.email = this.information_declarant.email;
        this.declaration_data.label_foret = '';
        this.declaration_data.surface_renseignee = '';
        this.declaration_data.nom_foret = '';
      }
    },
  },

  created() {},

  async mounted() {
    this.define_type_action();

    // si id_droit_max >= 5 on récupère la liste des déclarants
    if (this.$store.getters.droitMax >= 5) {
      this.liste_declarants = await apiRequest('GET', 'api/user/users');
    }

    // si l'utilisateur est connecté
    if (this.$store.getters.isAuth) {
      this.information_declarant = this.$store.getters.user;
      this.response = await apiRequest(
        'GET',
        `api/declaration/declaration?${this.declarationId ? `id=${this.declarationId}` : ''}`
      );
    } else {
      // l'utilisateur n'est pas connecté, on vérifie si c'est un renouvellement avec token
      if (this.type_action === 'RENOUVELLEMENT' || this.type_action === 'CLOTURE') {
        if (this.token_renouvellement && this.declarationId) {
          this.response = await apiRequest(
            'GET',
            `api/declaration/declaration_renouvellement?id=${this.declarationId}&token=${this.token_renouvellement}`
          );
          if (this.response['success'] == false) {
            this.affichage_fenetre_token_invalide = true;
          }
        } else {
          this.affichage_fenetre_token_invalide = true;
        }
      }
    }

    if (this.response && this.response['success'] == true) {
      this.declaration_data = this.response.data;
      this.nomenclature = await apiRequest('GET', `api/oeasc/nomenclatures`);
      if (!this.declaration_data.id_declarant) {
        this.declaration_data.id_declarant = this.$store.getters.user.id_role;
        this.declaration_data.email = this.$store.getters.user.email;
        this.declaration_data.nom_proprietaire = this.$store.getters.user.nom_complet;
      }

      if (!this.declaration_data.b_valid) {
        this.declaration_data.b_valid = false; // Par défaut, la déclaration n'est pas validée
      }
      await this.refresh_areas_infos();
      this.initialized = true;
    }
  },

  methods: {
    async refresh_areas_infos() {
      const parcelles = [
        ...(this.declaration_data.areas_localisation_cadastre || []),
        ...(this.declaration_data.areas_localisation_onf_ug || []),
      ];
      if (!parcelles.length) {
        this.areas_infos = { forets: [], secteurs: [], communes: [] };
        return;
      }
      const params = parcelles.map((id) => `id_parcelle=${id}`).join('&');
      const result = await apiRequest('GET', `api/ref_geo/areas_infos_from_parcelles?${params}`);
      if (result) this.areas_infos = result;
    },

    /**
     * Dernière petites vérifications avant l'envoi de la déclaration.
     * On clean certains champs superflus qui pourraient créer des erreurs
     */
    async submitDeclaration() {
      // Vérification des règles de validation

      if (this.processing) {
        return;
      }

      if (!this.declaration_data.b_autorisation) {
        snackbarStore.show(
          'Veuillez indiquer si vous autorisez la transmission des informations.',
          'info'
        );
        return;
      }

      // Vérifier que la déclaration est bien chargée
      if (!this.declaration_data || Object.keys(this.declaration_data).length === 0) {
        snackbarStore.show(
          'Les données de la déclaration ne sont pas chargées. Veuillez réessayer plus tard.',
          'error'
        );
        return;
      }

      //------------------------------ preparation et envoi des données ------------------------------

      this.processing = true; // Désactiver les boutons pour éviter les doubles clics

      try {
        // Le backend renvoie toujours un HTTP 200 : le succès réel est porté par
        // response.success. On le vérifie systématiquement avant d'afficher la
        // fenêtre de succès, sinon une erreur applicative passe inaperçue
        // (« la requête retourne 200 mais rien ne se passe »).
        const check_success = (response) => {
          if (response && response.success === false) {
            snackbarStore.show(
              response.message ||
                "Une erreur s'est produite lors de la soumission. Veuillez réessayer.",
              'error'
            );
            return false;
          }
          this.affichage_fenetre_succes = true; // Affiche la fenêtre de succès
          return true;
        };

        if (this.type_action === 'RENOUVELLEMENT') {
          const options = { postData: { ...this.declaration_data } };
          const response = await apiRequest(
            'POST',
            `/api/declaration/duplicate_declaration`,
            options
          );
          check_success(response);
        } else if (this.type_action === 'CREATION') {
          if (this.declaration_data.id_declaration) {
            snackbarStore.show(
              'Une erreur est survenue: la déclaration existe déjà. Veuillez réessayer.',
              'error'
            );
            return;
          }
          const options = { postData: { ...this.declaration_data } };
          const response = await apiRequest('POST', `/api/declaration/declaration`, options);
          if (check_success(response)) {
            this.$store.commit('declarations', {});
          }
        } else if (this.type_action === 'MODIFICATION') {
          // Envoi de la déclaration via l'API
          if (!this.declaration_data.id_declaration) {
            snackbarStore.show(
              "Une erreur est survenue: l'ID de déclaration est manquant pour la modification. Veuillez réessayer.",
              'error'
            );
            return;
          }
          this.declaration_data.b_valid = false; // Lors d'une modification, la déclaration doit être à nouveau validée par un admin

          const options = { postData: { ...this.declaration_data } };
          const response = await apiRequest('PATCH', `api/declaration/declaration`, options);
          if (check_success(response)) {
            // on vide les données du store declarations pour recharger les données
            this.$store.commit('declarations', {});
          }
        }
      } catch (error) {
        console.error('Erreur lors de la soumission de la déclaration:', error);
        snackbarStore.show(
          "Une erreur s'est produite lors de la soumission. Veuillez réessayer.",
          'error'
        );
      } finally {
        this.processing = false; // Réactiver les boutons après le traitement
      }
    },

    /**
     * Lorsque l'utilisateur à terminé de remplir, on vérifie si toutes les données sont valides avant
     * d'afficher le résumé de la déclaration.
     */
    async action_terminer_declaration() {
      this.error = null; // Réinitialiser l'erreur

      // Vuetify 3 : form.validate() est désormais asynchrone et renvoie { valid, errors }
      const { valid } = await this.$refs.form.validate();
      if (!valid) {
        snackbarStore.show('Veuillez remplir tous les champs requis.', 'info');
        return;
      }

      if (this.declaration_data.b_document === false) {
        if (this.declaration_data.areas_localisation_cadastre.length === 0) {
          snackbarStore.show(
            'Veuillez sélectionner au moins une aire de localisation cadastrale.',
            'info'
          );
          return;
        }
        // Vérification si l'utilisateur à bien selectionné au moins une area sur la carte
        if (!this.declaration_data.nom_proprietaire) {
          snackbarStore.show(
            "Le nom du propriétaire est requis si il n'y a pas de document de gestion.",
            'info'
          );
          return;
        }
        if (!this.declaration_data.telephone) {
          snackbarStore.show(
            "Le numéro de téléphone du propriétaire est requis si il n'y a pas de document de gestion.",
            'info'
          );
          return;
        }
        if (!this.declaration_data.email) {
          snackbarStore.show(
            "L'email du propriétaire est requis si il n'y a pas de document de gestion.",
            'info'
          );
          return;
        }
        if (!this.declaration_data.surface_renseignee) {
          snackbarStore.show(
            "La superficie renseignée est requise si il n'y a pas de document de gestion.",
            'info'
          );
          return;
        }
      } else {
        // il y a un document de gestion
        if (
          this.declaration_data.b_statut_public == true &&
          this.declaration_data.areas_localisation_onf_ug.length === 0
        ) {
          snackbarStore.show(
            'Veuillez sélectionner au moins une aire de localisation ONF UG.',
            'info'
          );
          return;
        }
        if (
          this.declaration_data.b_statut_public === false &&
          this.declaration_data.areas_localisation_cadastre.length === 0
        ) {
          snackbarStore.show(
            'Veuillez sélectionner au moins une aire de localisation cadastrale.',
            'info'
          );
          return;
        }
      }

      // si l'utilisateur  a bien selectionné les infos sur les dégats mais a oublié de le valider
      if (this.declaration_data.degats.length > 0) {
        this.declaration_data.degats.forEach((degat) => {
          if (degat.degat_essences.length === 0 && degat.id_nomenclature_degat_type !== 480) {
            snackbarStore.show(
              'Veuillez valider le type de dégât pour tous les dégâts renseignés.',
              'info'
            );
            return;
          }
        });
      } else {
        snackbarStore.show('Veuillez ajouter au moins un dégât.', 'info');
        return;
      }

      if (
        this.declaration_data.id_nomenclature_peuplement_type != 525 &&
        this.declaration_data.nomenclatures_peuplement_maturite.length === 0
      ) {
        snackbarStore.show('Veuillez sélectionner au moins une maturité du peuplement.', 'info');
        return;
      }

      if (this.declaration_data.nomenclatures_peuplement_origine2.length === 0) {
        snackbarStore.show('Veuillez sélectionner au moins une origine du peuplement.', 'info');
        return;
      }

      if (
        this.declaration_data.b_peuplement_protection_existence == true &&
        this.declaration_data.nomenclatures_peuplement_protection_type.length === 0
      ) {
        snackbarStore.show('Veuillez sélectionner au moins un type de protection.', 'info');
        return;
      }

      if (this.declaration_data.b_peuplement_paturage_presence == true) {
        if (
          this.declaration_data.nomenclatures_peuplement_paturage_type.length === 0 ||
          this.declaration_data.id_nomenclature_peuplement_paturage_statut === null ||
          this.declaration_data.id_nomenclature_peuplement_paturage_frequence === null
        ) {
          snackbarStore.show('Veuillez remplir tous les champs liés au pâturage.', 'info');
          return;
        }
        if (
          this.declaration_data.id_nomenclature_peuplement_paturage_frequence == 547 &&
          this.declaration_data.nomenclatures_peuplement_paturage_saison.length === 0
        ) {
          snackbarStore.show('Veuillez sélectionner au moins une saison pour le pâturage.', 'info');
          return;
        }
      }

      if ((await this.$refs.form.validate()).valid && this.error === null) {
        this.etape_affichage = 'AFFICHAGE_RESUME';
        return;
      }
    },

    /**
     * Navigation depuis la fenêtre de succès : on ferme d'abord la modale
     * (sinon le scrim Vuetify reste au-dessus de la page cible et « rien ne se
     * passe » visuellement), puis on route via vue-router.
     */
    goTo(path) {
      this.affichage_fenetre_succes = false;
      this.affichage_fenetre_token_invalide = false;
      if (this.$route.path !== path) {
        this.$router.push(path);
      }
    },

    handleLayerSelect(layerId) {
      const index = this.selected.indexOf(layerId);
      if (index === -1) {
        this.selected.push(layerId);
      } else {
        this.selected.splice(index, 1);
      }
    },

    define_type_action() {
      if (this.$route.name === 'modifier_declaration') {
        this.type_action = 'MODIFICATION';
        this.title = `Modification de la déclaration: ${this.declarationId}`;
      } else if (this.$route.name === 'nouvelle_declaration') {
        this.type_action = 'CREATION';
        this.title = "Création d'une nouvelle déclaration";
      } else if (this.$route.name === 'actualisation_declaration') {
        if (this.action === 'oui') {
          this.type_action = 'RENOUVELLEMENT';
          this.title = `Renouvellement de la déclaration: ${this.declarationId}`;
        } else {
          this.type_action = 'CLOTURE';
          this.title = `Clôture de la déclaration: ${this.declarationId}`;
          this.etape_affichage = 'AFFICHAGE_RESUME';
        }
      }
    },

    redirect_to_login() {
      this.$router.push({
        name: 'user.login',
        query: { redirect: this.$route.fullPath },
      });
    },

    closeDeclaration() {
      if (this.processing) {
        return;
      }

      if (!this.declaration_data.id_declaration) {
        snackbarStore.show(
          "Une erreur est survenue: l'ID de déclaration est manquant pour la clôture. Veuillez réessayer.",
          'error'
        );
        return;
      }

      this.processing = true; // Désactiver le bouton pour éviter les doubles clics
      apiRequest('POST', `api/declaration/cloture_declaration`, {
        postData: {
          id_declaration: this.declaration_data.id_declaration,
          token_renouvellement: this.declaration_data.token_renouvellement,
        },
      })
        .then(() => {
          this.affichage_fenetre_succes = true; // Affiche la fenêtre de succès
        })
        .catch(() => {
          snackbarStore.show(
            "Une erreur s'est produite lors de la clôture. Veuillez réessayer.",
            'error'
          );
        })
        .finally(() => {
          this.processing = false; // Réactiver le bouton après le traitement
        });
    },
  },
};
</script>

<style>
@import url('../../components/form/form.css');

pre {
  background-color: #f4f4f4;
  padding: 10px;
  border: 1px solid #ddd;
  white-space: pre-wrap; /* Pour que le texte long s'enroule */
  word-wrap: break-word; /* Pour que les mots longs se cassent */
}

.encadrer {
  border: 1px solid #ccc;
  padding: 20px;
  border-radius: 5px;
}
</style>

<style scoped></style>
