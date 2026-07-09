<!-- ################################################################################################
Mini formulaire de declaration de dégats en fonction des essences. Ce formulaire 
est seulement utilisé dans modifier-declaration.vue.  Ce formulaire à besoin de la liste des essences
selectionnées dans le peuplement pour fonctionner. Les essences primaires, secondaires et complémentaires
sont concaténées pour être proposées dans une liste de type select.

TODO: eventuellement récupérer les nomencaltures dans le store si elles existent déjà
################################################################################################ -->

<template>
  <div>
    <div
      v-if="liste_selection_essences.length > 0"
      style="display: flex; flex-direction: column; width: 30%"
    >
      <div
        v-for="(item_type_degat, index_type_degat) of nomenclature.OEASC_DEGAT_TYPE.values"
        :key="item_type_degat.id_nomenclature"
      >
        <!-- ---- Les checkbox correspondants aux types de dégats (Abroutissement, frottis, écorcage etc..) 
           avec les pastilles d'aide --------- -->
        <div style="position: relative; display: inline-block">
          <v-checkbox
            v-model="SelecteddegatTypesComputed"
            :hide-details="
              index_type_degat < nomenclature.OEASC_DEGAT_TYPE.values.length - 1 ? true : false
            "
            :value="item_type_degat.id_nomenclature"
            :label="item_type_degat.label_fr"
            dense
            :rules="[
              (v) =>
                SelecteddegatTypesComputed.length > 0 ||
                'Veuillez sélectionner au moins un type de dégât',
            ]"
          >
            <template v-slot:label>
              {{ item_type_degat.label_fr }}
              <help
                v-if="item_type_degat.cd_nomenclature === 'ABR'"
                style="margin-left: 2em"
              >
                <helpContent helpID="degat_abroutissement"></helpContent>
              </help>
              <help
                v-if="item_type_degat.cd_nomenclature === 'FRO'"
                style="margin-left: 2em"
              >
                <helpContent helpID="degat_frottis"></helpContent>
              </help>
              <help
                v-if="item_type_degat.cd_nomenclature === 'SANG'"
                style="margin-left: 2em"
              >
                <helpContent helpID="degat_sanglier"></helpContent>
              </help>
              <help
                v-if="item_type_degat.cd_nomenclature === 'ÉCO'"
                style="margin-left: 2em"
              >
                <helpContent helpID="degat_ecorcage"></helpContent>
              </help>
              <help
                v-if="item_type_degat.cd_nomenclature === 'ABS'"
                style="margin-left: 2em"
              >
                <helpContent helpID="degat_deficit_regeneration"></helpContent>
              </help>
            </template>
          </v-checkbox>

          <!-- -----------------  affichage des degats déja enregisté ------------------------ -->

          <!-- si ce type de dégat est selectionné ou si il existe déja dans declaration_data -->
          <div
            v-if="SelecteddegatTypesComputed.includes(item_type_degat.id_nomenclature)"
            style="margin-left: 50px"
          >
            <v-table style="width: 900px">
              <!-- le type de dégat en cours n'est pas un dégat de piste et cloture ni un déficit de régénération -->
              <thead
                v-if="
                  item_type_degat.cd_nomenclature !== 'P/C' &&
                  item_type_degat.cd_nomenclature !== 'ABS'
                "
              >
                <tr>
                  <th>Essence</th>
                  <th>Gravité</th>
                  <th>Étendue</th>
                  <th>Antériorité</th>
                  <th>Actions</th>
                </tr>
              </thead>

              <!-- le type de dégat en cours est un dégat de deficite de régénération-->
              <thead v-else-if="item_type_degat.cd_nomenclature === 'ABS'">
                <tr>
                  <th>Essence</th>
                  <th>Actions</th>
                </tr>
              </thead>

              <!-- le type de dégat en cours est un dégat de piste et cloture. -->
              <thead v-else-if="item_type_degat.cd_nomenclature === 'P/C'"></thead>

              <tbody>
                <!-- --------------------- affichage des degats enregistrés --------------------- -->

                <!-- boucle sur les essences de ce type de dégat -->
                <tr
                  v-for="(
                    item_degat_essence, index_degat_essence
                  ) of get_degat_declaration_from_id_nomenclature(item_type_degat.id_nomenclature)
                    .degat_essences"
                  :key="index_degat_essence"
                >
                  <th v-if="item_type_degat.cd_nomenclature !== 'P/C'">
                    <!-- si l'essence est selectionnée dans la liste des essences du peuplement -->
                    <span
                      v-if="
                        liste_selection_essences.includes(
                          item_degat_essence.id_nomenclature_degat_essence
                        ) && item_type_degat.cd_nomenclature !== 'P/C'
                      "
                    >
                      {{
                        get_nomenclature_degat_of_declaration(
                          item_type_degat.id_nomenclature,
                          index_degat_essence,
                          'id_nomenclature_degat_essence',
                          'OEASC_PEUPLEMENT_ESSENCE'
                        ).label_fr
                      }}
                    </span>
                    <!-- sinon on affiche l'essence selectionnée dans le dégat -->
                    <!-- <span v-else>
                          {{ get_essence_of_degat_from_declaration(item_type_degat.id_nomenclature, item_degat_essence.id_nomenclature_degat_essence).label_fr }}
                        </span> -->
                  </th>

                  <th
                    v-if="
                      item_type_degat.cd_nomenclature !== 'P/C' &&
                      item_type_degat.cd_nomenclature !== 'ABS'
                    "
                  >
                    {{
                      get_nomenclature_degat_of_declaration(
                        item_type_degat.id_nomenclature,
                        index_degat_essence,
                        'id_nomenclature_degat_gravite',
                        'OEASC_DEGAT_GRAVITE'
                      ).label_fr
                    }}
                  </th>
                  <th
                    v-if="
                      item_type_degat.cd_nomenclature !== 'P/C' &&
                      item_type_degat.cd_nomenclature !== 'ABS'
                    "
                  >
                    {{
                      get_nomenclature_degat_of_declaration(
                        item_type_degat.id_nomenclature,
                        index_degat_essence,
                        'id_nomenclature_degat_etendue',
                        'OEASC_DEGAT_ETENDUE'
                      ).label_fr
                    }}
                  </th>
                  <th
                    v-if="
                      item_type_degat.cd_nomenclature !== 'P/C' &&
                      item_type_degat.cd_nomenclature !== 'ABS'
                    "
                  >
                    {{
                      get_nomenclature_degat_of_declaration(
                        item_type_degat.id_nomenclature,
                        index_degat_essence,
                        'id_nomenclature_degat_anteriorite',
                        'OEASC_DEGAT_ANTERIORITE'
                      ).label_fr
                    }}
                  </th>

                  <!-- actions sur le dégat -->
                  <th v-if="item_type_degat.cd_nomenclature !== 'P/C'">
                    <v-btn
                      icon
                      @click="
                        removeDegatEssence(
                          item_type_degat.id_nomenclature,
                          item_degat_essence.id_nomenclature_degat_essence
                        )
                      "
                    >
                      <v-icon>mdi-delete</v-icon>
                    </v-btn>
                  </th>
                </tr>

                <!-- ------------- affichage du  mini formulaire d'ajout de degat ----------- -->

                <tr v-if="condition_affichage_mini_formulaire_degat(item_type_degat)">
                  <th v-if="item_type_degat.cd_nomenclature !== 'P/C'">
                    <!-- ne propose dans le select que les essences déclarées dans le peuplement et que les essences qui ne sont
                            pas déjà dans ce type dégat -->
                    <v-select
                      v-model="degatEssence.essence"
                      :items="
                        nomenclature.OEASC_PEUPLEMENT_ESSENCE.values.filter(
                          (e) =>
                            liste_selection_essences.includes(e.id_nomenclature) &&
                            !get_degat_declaration_from_id_nomenclature(
                              item_type_degat.id_nomenclature
                            ).degat_essences.some(
                              (de) => de.id_nomenclature_degat_essence === e.id_nomenclature
                            )
                        )
                      "
                      title="Sélectionnez l'essence"
                      item-value="id_nomenclature"
                      item-title="label_fr"
                      label="Essence"
                      :rules="[rules.requiredListSimple]"
                      solo
                      dense
                      placeholder="Essence"
                      class="select-list-label"
                    ></v-select>
                  </th>

                  <th
                    v-if="
                      item_type_degat.cd_nomenclature !== 'P/C' &&
                      item_type_degat.cd_nomenclature !== 'ABS'
                    "
                  >
                    <v-select
                      v-model="degatEssence.gravite"
                      :items="nomenclature.OEASC_DEGAT_GRAVITE.values"
                      item-value="id_nomenclature"
                      item-title="label_fr"
                      label="Gravité"
                      :rules="[rules.requiredListSimple]"
                      solo
                      dense
                      placeholder="Gravité"
                      class="select-list-label"
                    ></v-select>
                  </th>

                  <th
                    v-if="
                      item_type_degat.cd_nomenclature !== 'P/C' &&
                      item_type_degat.cd_nomenclature !== 'ABS'
                    "
                  >
                    <v-select
                      v-model="degatEssence.etendue"
                      :items="nomenclature.OEASC_DEGAT_ETENDUE.values"
                      item-value="id_nomenclature"
                      item-title="label_fr"
                      label="Étendue"
                      :rules="[rules.requiredListSimple]"
                      solo
                      dense
                      placeholder="Étendue"
                      class="select-list-label"
                    ></v-select>
                  </th>

                  <th
                    v-if="
                      item_type_degat.cd_nomenclature !== 'P/C' &&
                      item_type_degat.cd_nomenclature !== 'ABS'
                    "
                  >
                    <v-select
                      v-model="degatEssence.anteriorite"
                      :items="nomenclature.OEASC_DEGAT_ANTERIORITE.values"
                      item-value="id_nomenclature"
                      item-title="label_fr"
                      label="Antériorité"
                      :rules="[rules.requiredListSimple]"
                      solo
                      dense
                      placeholder="Antériorité"
                      class="select-list-label"
                    ></v-select>
                  </th>

                  <!-- ----------------------- Bouton de validation ou d'annulation du mini formulaire ----------------------- -->
                  <!-- uniquement pour les degats qui ne sont pas de type cloture et piste -->

                  <th v-if="item_type_degat.cd_nomenclature !== 'P/C'">
                    <div>
                      <v-btn
                        small
                        color="success"
                        :disabled="
                          !degatEssence.essence ||
                          (item_type_degat.cd_nomenclature !== 'ABS' &&
                            (!degatEssence.gravite ||
                              !degatEssence.etendue ||
                              !degatEssence.anteriorite))
                        "
                        @click="addDegatEssence(item_type_degat.id_nomenclature)"
                      >
                        <v-icon>mdi-check</v-icon>
                      </v-btn>
                      <v-btn
                        small
                        color="error"
                        @click="cancelDegatEssence(item_type_degat.id_nomenclature)"
                      >
                        <v-icon>mdi-close</v-icon>
                      </v-btn>
                    </div>
                    <div
                      v-if="
                        !(
                          !degatEssence.essence ||
                          (item_type_degat.cd_nomenclature !== 'ABS' &&
                            (!degatEssence.gravite ||
                              !degatEssence.etendue ||
                              !degatEssence.anteriorite))
                        )
                      "
                    >
                      <span style="color: red">Veuillez valider avant de continuer</span>
                    </div>
                  </th>
                </tr>
              </tbody>

              <!-- ------------------- Bouton d'ajout d'essence dans un degat ------------------ -->
              <tfoot
                v-if="
                  item_type_degat.cd_nomenclature !== 'P/C' &&
                  condition_affichage_btn_add_degat_essence(item_type_degat)
                "
              >
                <tr>
                  <td colspan="5">
                    <v-btn
                      color="light-green lighten-3"
                      small
                      style="text-transform: none"
                      @click="displayDegatEssenceForm(item_type_degat.id_nomenclature)"
                    >
                      Ajouter d'une nouvelle ligne dans ce type de dégat
                    </v-btn>
                  </td>
                </tr>
              </tfoot>
            </v-table>
          </div>
        </div>
        <!-- fin de div des checkbox -->
      </div>
      <!-- fin de la boucle des types de dégâts -->
    </div>
    <div v-else>
      <p>
        Pour déclarer des dégâts, veuillez d'abord sélectionner des essences dans l'encart précédent
      </p>
    </div>

    <!-- <pre> Liste des degats: {{ this.declaration_data.degats}}</pre> -->
    <!-- <pre> Liste des essences secondaire: {{ declaration_data.nomenclatures_peuplement_essence_secondaire}}</pre>  -->
    <!-- <pre> {{ this.$store.state }}</pre> -->
  </div>
</template>

<script>
import { copy } from '@/core/js/util/util.js';
import { formFunctions } from '@/components/form/functions/form.js';
import help from '@/components/form/help_static.vue';
import helpContent from '@/modules/declaration/help-content.vue';

export default {
  compatConfig: { MODE: 3 }, // verrouille les acquis Phase 4 (composant testé sans warning au 2026-07-10)
  name: 'degatsForm',
  components: {
    help,
    helpContent,
  },
  data() {
    return {
      rules: formFunctions.rules, // Règles de validation pour les champs du formulaire (utilisées dans les v-select)
      items: null, // Variable inutilisée, peut servir à stocker des listes d'items pour des selects
      degatTypes: [], // Tableau des types de dégâts sélectionnés (synchronisé avec le formulaire)
      liste_selection_essences: this.concateneEssencesPeuplement(), // Liste des essences sélectionnées dans le peuplement, utilisée pour filtrer les essences proposées dans le formulaire de dégâts
      degatEssence: {
        // Objet temporaire pour stocker les valeurs du mini-formulaire d'ajout d'une essence à un dégât
        essence: null, // ID de l'essence sélectionnée
        gravite: null, // ID de la gravité sélectionnée
        etendue: null, // ID de l'étendue sélectionnée
        anteriorite: null, // ID de l'antériorité sélectionnée
      },

      displayMsgErrorValider: false, // Booléen pour afficher un message d'erreur lors de la validation du formulaire
      showDegatEssenceForm: null, // ID du type de dégât pour lequel le mini-formulaire d'ajout d'essence est affiché (null si aucun formulaire n'est affiché)
    };
  },

  watch: {
    'declaration_data.id_nomenclature_peuplement_essence_principale': function () {
      this.liste_selection_essences = this.concateneEssencesPeuplement();
    },
    // deep:true nécessaire en Vue 3 pour ces deux tableaux : les mutations (push/splice) ne
    // déclenchent plus un watcher par défaut comme en Vue 2 (voir compat WATCH_ARRAY)
    'declaration_data.nomenclatures_peuplement_essence_secondaire': {
      handler() {
        this.liste_selection_essences = this.concateneEssencesPeuplement();
      },
      deep: true,
    },
    'declaration_data.nomenclatures_peuplement_essence_complementaire': {
      handler() {
        this.liste_selection_essences = this.concateneEssencesPeuplement();
      },
      deep: true,
    },
  },

  props: {
    // Le json contenant toutes les données du formulaire de déclaration en cours.
    declaration_data: {
      type: Object,
      required: true,
      watch: {
        handler(newVal) {
          this.degatTypes = this.SelecteddegatTypesComputed; // Met à jour degatTypes lorsque declaration_data change
          this.liste_selection_essences = this.concateneEssencesPeuplement(); // Met à jour la liste des essences sélectionnées
        },
        deep: true, // Permet de surveiller les changements profonds dans declaration_data
      },
    },
    nomenclature: {
      type: Object,
      required: true,
    },
  },
  computed: {
    /**
     * Propriété calculée pour obtenir la liste des types de dégâts depuis declaration_data.degats
     * et permettre la liaison bidirectionnelle avec v-model. Nécessaire car declaration_data est récupéré de
     * manière asynchrone et donc declaration_data.degats peut ne pas exister
     */

    SelecteddegatTypesComputed: {
      get() {
        if (!this.declaration_data || !this.declaration_data['degats']) {
          return []; // evite une erreur si declaration_data n'est pas encore initialisé et que degats n'existe pas
        }
        // return this.declaration_data.degats;
        return this.declaration_data.degats.map((d) => d.id_nomenclature_degat_type);
      },

      set(newVal) {
        // Met à jour degatTypes et synchronise declaration_data.degats en conséquence
        this.degatTypes = newVal;
        // Remove degats not in newVal
        this.declaration_data.degats = this.declaration_data.degats.filter((d) =>
          newVal.includes(d.id_nomenclature_degat_type)
        );
        // Add new degats for any new values
        newVal.forEach((type) => {
          if (!this.declaration_data.degats.find((d) => d.id_nomenclature_degat_type === type)) {
            this.declaration_data.degats.push({
              id_nomenclature_degat_type: type,
              degat_essences: [],
              id_declaration: this.declaration_data.id_declaration, // Ajout de id_declaration
            });
          }
        });
      },
    },
  },
  methods: {
    /**
     * créé une liste sans doublons avec toutes les essences selectionnées dans les informations sur le peuplement
     *  pour les afficher dans la liste des essences dans les dégats. Cette fonction se lance à chaque modif de
     * declaration_data
     * @returns {Array} tableau des essences sélectionnées
     */
    concateneEssencesPeuplement() {
      const essences = [
        this.declaration_data.id_nomenclature_peuplement_essence_principale,
        ...(this.declaration_data.nomenclatures_peuplement_essence_secondaire || []),
        ...(this.declaration_data.nomenclatures_peuplement_essence_complementaire || []),
      ]
        .filter(Boolean)
        .flat();
      return Array.from(new Set(essences));
    },

    /**
     * Vérifie si le mini formulaire d'ajout d'essence dans un dégat doit être affiché.
     * @param {Object} item_type_degat - L'objet de nomenclature du type de dégat. (nomenclature.OEASC_DEGAT_TYPE)
     * @returns {boolean} - Retourne true si le mini formulaire doit être affiché, sinon false.
     */
    condition_affichage_mini_formulaire_degat(item_type_degat) {
      const degat = this.declaration_data.degats.find(
        (d) =>
          d.id_nomenclature_degat_type === item_type_degat.id_nomenclature && // c'est le type de dégat en cours
          item_type_degat.cd_nomenclature !== 'P/C' && // le degat n'est pas de type piste et cloture
          ((d.degat_essences || []).length === 0 || // il n'y a pas encore d'essence dans ce type de dégat
            this.showDegatEssenceForm === d.id_nomenclature_degat_type) // showDegatEssenceForm correspond au type de dégat en cours
      );
      return !!degat;
    },

    /**
     * return True si on peut afficher le bouton d'ajout d'une essence dans le type de dégat en cours.
     * @param item_type_degat - L'objet de nomenclature du type de dégat. (nomenclature.OEASC_DEGAT_TYPE)
     * @returns {boolean} - Retourne true si le bouton d'ajout de dé
     */
    condition_affichage_btn_add_degat_essence(item_type_degat) {
      const degat = this.declaration_data.degats.find(
        (d) => d.id_nomenclature_degat_type === item_type_degat.id_nomenclature
      );
      return (
        degat &&
        degat.degat_essences &&
        degat.degat_essences.length < 3 && // si il y a moins de 3 essences dans ce type de dégat
        degat.degat_essences.length < this.liste_selection_essences.length && // si il reste des essences à ajouter
        this.showDegatEssenceForm !== item_type_degat.id_nomenclature // si le mini formulaire n'est pas déjà affiché pour ce type de dégat
      );
    },

    /**
     * Récupère l'objet nomenclature correspondant à l'id_degat_type de la declaration. Utilisé pour récupérer
     * les informations sur le type de dégât, comme le nom (label_fr) ou d'autres propriétés à afficher dans le formulaire.
     * @param {number} id_degat_type - L'ID du type de dégât.
     * @param {number} index_essence - L'index de l'essence dans le tableau des essences du dégât.
     * @param {string} key_nomenclature - La clé de la nomenclature à récupérer. (ex: "id_nomenclature_degat_gravite")
     * @param {string} type_nomenclature - Le type de nomenclature (ex: 'OEASC_DEGAT_TYPE').
     * @returns {Object|null} - Retourne l'objet de nomenclature ou null si non trouvé.
     */
    get_nomenclature_degat_of_declaration(
      id_degat_type,
      index_essence,
      key_nomenclature,
      type_nomenclature
    ) {
      const degat = this.declaration_data.degats.find(
        (d) => d.id_nomenclature_degat_type === id_degat_type
      );

      if (degat) {
        return this.nomenclature[type_nomenclature].values.find(
          (n) => n.id_nomenclature === degat.degat_essences[index_essence][key_nomenclature]
        );
      }
      return null;
    },

    /**
     * affiche le formulaire d'ajout d'une essence dans un type de dégat.
     * @param id_nomenclature_degat_type id du type de dégat
     */
    displayDegatEssenceForm(id_nomenclature_degat_type) {
      this.declaration_data.freeze = true;
      this.showDegatEssenceForm = id_nomenclature_degat_type;
    },

    /**
     * est lancé lorsque l'on valide le formulaire d'ajout d'une essence dans un type de dégat.
     * @param id_nomenclature_degat_type id du type de dégat dans lequel on ajoute une essence
     */
    addDegatEssence(id_nomenclature_degat_type) {
      const degat = this.declaration_data.degats.find(
        (d) => d.id_nomenclature_degat_type === id_nomenclature_degat_type
      );
      degat.degat_essences = degat.degat_essences || [];
      const degat_essence = {
        id_nomenclature_degat_essence: this.degatEssence.essence,
        id_nomenclature_degat_gravite: this.degatEssence.gravite,
        id_nomenclature_degat_etendue: this.degatEssence.etendue,
        id_nomenclature_degat_anteriorite: this.degatEssence.anteriorite,
      };
      degat.degat_essences.push(degat_essence);
      this.declaration_data.degats = copy(this.declaration_data.degats);
      this.clearDegatEssenceForm();
      this.declaration_data.freeze = false;
      this.showDegatEssenceForm = null;
    },

    /**
     * Réinitialise le formulaire d'ajout d'essence dans un type de dégat.
     * Utilisé pour vider les champs du formulaire après l'ajout ou l'annulation.
     */
    clearDegatEssenceForm() {
      this.degatEssence.essence = null;
      this.degatEssence.gravite = null;
      this.degatEssence.etendue = null;
      this.degatEssence.anteriorite = null;
    },

    /**
     * Annule l'ajout d'une essence dans un type de dégat lorsque l'on clique sur le bouton d'annulation (croix rouge).
     * Si le type de dégat n'a pas d'essence, il est supprimé de la déclaration.
     * @param id_nomenclature_degat_type id du type de dégat
     */
    cancelDegatEssence(id_nomenclature_degat_type) {
      const degat = this.declaration_data.degats.find(
        (d) => d.id_nomenclature_degat_type === id_nomenclature_degat_type
      );
      if (degat.degat_essences.length === 0) {
        const index = this.declaration_data.degats.indexOf(degat);
        this.declaration_data.degats.splice(index, 1);
      } else {
        this.showDegatEssenceForm = null;
      }
      this.degatTypes = this.declaration_data.degats.map((d) => d.id_nomenclature_degat_type);
      this.declaration_data.freeze = false;
    },

    /**
     * Supprime une essence d'un type de dégat. lorsque l'on clique sur la poubelle a droite de chaque ligne d'essence.
     * @param {number} id_nomenclature_degat_type - L'ID du type de dégat.
     * @param {number} id_nomenclature_degat_essence - L'ID de l'essence à supprimer.
     */
    removeDegatEssence(id_nomenclature_degat_type, id_nomenclature_degat_essence) {
      const degat = this.declaration_data.degats.find(
        (d) => d.id_nomenclature_degat_type === id_nomenclature_degat_type
      );
      const degat_essence = degat.degat_essences.find(
        (de) => de.id_nomenclature_degat_essence === id_nomenclature_degat_essence
      );
      const index = degat.degat_essences.indexOf(degat_essence);
      degat.degat_essences.splice(index, 1);

      if (degat.degat_essences.length == 0) {
        this.declaration_data.freeze = true;
      }
    },

    /**
     * Récupère les dégât de la declaration à partir de l'ID de la nomenclature du type de dégât.
     * @param {number} id_nomenclature_degat_type - L'ID de la nomenclature du type de dégât.
     * @returns {Object|null} - Retourne l'objet de déclaration de dégât ou null si non trouvé.
     */
    get_degat_declaration_from_id_nomenclature(id_nomenclature_degat_type) {
      return this.declaration_data.degats.find(
        (d) => d.id_nomenclature_degat_type === id_nomenclature_degat_type
      );
    },

    // peut être pas utilisé fair tous les test
    get_essence_of_degat_from_declaration(
      id_nomenclature_degat_type,
      id_nomenclature_degat_essence
    ) {
      const degat = this.get_degat_declaration_from_id_nomenclature(id_nomenclature_degat_type);
      if (degat) {
        return degat.degat_essences.find(
          (de) => de.id_nomenclature_degat_essence === id_nomenclature_degat_essence
        );
      }
      return null;
    },

    // pas utilisé
    getEssencesSelected: function (declaration_data) {
      const essencesSelected = {};

      essencesSelected['all'] = [
        ...declaration_data.nomenclatures_peuplement_essence_secondaire,
        ...declaration_data.nomenclatures_peuplement_essence_complementaire,
      ];
      if (declaration_data.id_nomenclature_peuplement_essence_principale) {
        essencesSelected['all'].push(
          declaration_data.id_nomenclature_peuplement_essence_principale
        );
      }
      essencesSelected['degats'] = [
        ...declaration_data.nomenclatures_peuplement_essence_secondaire,
      ];
      if (declaration_data.id_nomenclature_peuplement_essence_principale) {
        essencesSelected['degats'].push(
          declaration_data.id_nomenclature_peuplement_essence_principale
        );
      }

      for (const degat of declaration_data.degats || []) {
        const nomenclature = this.get_nomenclature_degat_of_declaration(
          degat.id_nomenclature_degat_type,
          'id_nomenclature_degat_type',
          'OEASC_DEGAT_TYPE'
        );

        const cd = nomenclature.cd_nomenclature;
        if (cd !== 'P/C') {
          essencesSelected[cd] = [];
          for (const degat_essence of degat.degat_essences || []) {
            essencesSelected[cd].push(degat_essence.id_nomenclature_degat_essence);
          }
        }
      }
      return essencesSelected;
    },

    // pas utilisé
    updateDegats: function () {
      for (const degatType of this.degatTypes) {
        const degat = this.declaration_data.degats.find(
          (d) => degatType === d.id_nomenclature_degat_type
        );
        if (!degat) {
          this.declaration_data.degats.push({
            id_nomenclature_degat_type: degatType,
            degat_essences: [],
          });

          if (this.$store.getters.nomenclature(degatType).cd_nomenclature != 'P/C') {
            this.declaration_data.freeze = true;
          }
        }
      }

      for (const [index, degat] of this.declaration_data.degats.entries()) {
        if (!this.degatTypes.find((d) => d === degat.id_nomenclature_degat_type)) {
          this.declaration_data.degats.splice(index, 1);
        }
      }
    },

    //pas utilisé
    configDegatEssence: function (degatType) {
      return {
        essence: {
          name: 'essence',
          required: true,
          type: 'essence',
          label: 'Choisir une essence',
          declaration: this.declaration_data,
          essenceType: degatType,
          rules: [formFunctions.rules.requiredListSimple],
        },
        gravite: {
          name: 'gravite',
          type: 'nomenclature',
          required: true,
          nomenclatureType: 'OEASC_DEGAT_GRAVITE',
          rules: [formFunctions.rules.requiredListSimple],
        },
        etendue: {
          name: 'etendue',
          type: 'nomenclature',
          required: true,
          nomenclatureType: 'OEASC_DEGAT_ETENDUE',
          rules: [formFunctions.rules.requiredListSimple],
        },
        anteriorite: {
          name: 'anteriorite',
          type: 'nomenclature',
          required: true,
          nomenclatureType: 'OEASC_DEGAT_ANTERIORITE',
          rules: [formFunctions.rules.requiredListSimple],
        },
      };
    },
  },

  created: function () {
    this.degatTypes = this.SelecteddegatTypesComputed;
  },
};
</script>

<style scoped>
.degat {
  display: inline-block;
}

.flex-5 > div {
  width: 20%;
  margin: 1px;
}

.select-list-label-container {
  margin-bottom: 10px;
}

.select-list-label {
  font-weight: normal;
}

.flex-container {
  display: flex;
  flex-direction: column;
}

.flex-row {
  flex-direction: row;
}
</style>
