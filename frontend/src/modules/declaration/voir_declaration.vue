<!-- Page de visualisation d'une déclaration. Est appelé dans form-chained
Comprend le résumé de la déclaration, les cartes et le bouton d'export PDF. -->
<template>
  <div style="min-width: 900px; max-width: 1000px; margin: auto">
    <v-progress-linear
      v-if="pdfProcessing"
      active
      indeterminate
    ></v-progress-linear>

    <div
      style="width: 100%"
      id="declaration"
    >
      <div v-if="declaration_data">
        <h1>Déclaration {{ declaration_data.id_declaration }}</h1>
        <v-btn
          class="ignorepdf"
          icon
          color="red"
          @click="exportDeclaration()"
          title="Exporter la déclaration au format pdf"
        >
          <v-icon>mdi-file-pdf</v-icon>
        </v-btn>

        <div
          id="resume_declaration"
          style=""
        >
          <template v-if="bInit == true">
            <div>
              <v-simple-table
                dense
                style="margin-bottom: 16px; width: 100%; max-width: 100%; margin: auto"
              >
                <thead>
                  <th colspan="2">Résumé de la déclaration</th>
                </thead>

                <!-- ------------------------------- INFORMATIONS -------------------------------- -->
                <tbody>
                  <tr>
                    <th
                      colspan="2"
                      class="sous_titre"
                    >
                      Informations
                    </th>
                  </tr>
                  <!-- seulement visible par les admins -->
                  <tr v-if="this.$store.getters.droitMax >= 5">
                    <td class="gauche">Validité</td>
                    <td class="droite">{{ declaration_data.valide }}</td>
                  </tr>

                  <tr>
                    <td class="gauche">Partage d'information</td>
                    <td class="droite">
                      {{ declaration_data.autorisation }}
                    </td>
                  </tr>

                  <tr>
                    <td class="gauche">Date de création</td>
                    <td class="droite">
                      {{ declaration_data.declaration_date }}
                    </td>
                  </tr>
                  <tr>
                    <td class="gauche">Date de fin</td>
                    <td class="droite">
                      {{ declaration_data.date_fin }}
                    </td>
                  </tr>
                </tbody>

                <!-- ------------------------------- DECLARANT -------------------------------- -->
                <tbody v-if="declaration_data.declarant || declaration_data.organisme">
                  <tr>
                    <th
                      colspan="2"
                      class="sous_titre"
                    >
                      Déclarant
                    </th>
                  </tr>

                  <tr v-if="declaration_data.declarant">
                    <td class="gauche">Nom du propriétaire</td>
                    <td class="droite">{{ declaration_data.declarant }}</td>
                  </tr>
                  <tr v-if="declaration_data.organisme">
                    <td class="gauche">Organisme</td>
                    <td class="droite">{{ declaration_data.organisme }}</td>
                    <!-- <td class="droite">{{declaration_data.org_mnemo || "Non renseigné"}}</td> -->
                  </tr>
                </tbody>

                <!-- ------------------------------- FORET -------------------------------- -->
                <tbody>
                  <tr>
                    <th
                      colspan="2"
                      class="sous_titre"
                    >
                      Forêt
                    </th>
                  </tr>

                  <tr v-if="declaration_data.nom_foret">
                    <td class="gauche">Nom</td>
                    <td class="droite">{{ declaration_data.nom_foret }}</td>
                  </tr>

                  <tr v-if="declaration_data.statut_public">
                    <td class="gauche">Statut</td>
                    <td class="droite">
                      {{ declaration_data.statut_public }}
                    </td>
                  </tr>

                  <tr v-if="declaration_data.document">
                    <td class="gauche">Document de gestion durable</td>
                    <td class="droite">
                      {{ declaration_data.document }}
                      <span v-if="declaration_data.b_document && declaration_data.b_statut_public">
                        <i>(régime forestier)</i>
                      </span>
                      <span
                        v-else-if="declaration_data.b_document && !declaration_data.b_statut_public"
                      >
                        <i>(document de gestion durable)</i>
                      </span>
                    </td>
                  </tr>

                  <tr v-if="declaration_data.type_foret">
                    <td class="gauche">Type</td>
                    <td class="droite">
                      <!-- ici le type de foret affiché a été renommé par foretType, voir dans les script -->
                      {{ declaration_data.type_foret }}
                    </td>
                  </tr>

                  <tr v-if="declaration_data.espece_label">
                    <td class="gauche">Espèces présentes</td>
                    <td class="droite">
                      {{ declaration_data.espece_label }}
                    </td>
                  </tr>
                </tbody>

                <!-- ------------------------------- PEUPLEMENT LOCALISATION -------------------------------- -->
                <tbody>
                  <tr>
                    <th
                      colspan="2"
                      class="sous_titre"
                    >
                      Peuplement - localisation
                    </th>
                  </tr>
                  <tr v-if="declaration_data.secteur">
                    <td class="gauche">Secteur</td>
                    <td class="droite">{{ declaration_data.secteur }}</td>
                  </tr>

                  <tr v-if="declaration_data.communes">
                    <td class="gauche">Commune(s)</td>
                    <td class="droite">{{ declaration_data.communes }}</td>
                  </tr>

                  <tr v-if="declaration_data.parcelles">
                    <td class="gauche">Parcelle(s)</td>
                    <td class="droite">{{ declaration_data.parcelles }}</td>
                  </tr>

                  <tr v-if="declaration_data.accessibilite">
                    <td class="gauche">Accessibilité</td>
                    <td class="droite">
                      {{ declaration_data.accessibilite }}
                    </td>
                  </tr>
                  <tr v-if="declaration_data.precision_localisation">
                    <td class="gauche">Précisions sur la localisation</td>
                    <td class="droite">
                      {{ declaration_data.precision_localisation || 'Non renseigné' }}
                    </td>
                  </tr>
                </tbody>

                <!-- ---------------------------PEUPLEMENT - ESSENCES --------------------------- -->
                <tbody>
                  <tr>
                    <th
                      colspan="2"
                      class="sous_titre"
                    >
                      Peuplement - essences
                    </th>
                  </tr>
                  <tr v-if="declaration_data.peuplement_ess_1">
                    <td class="gauche">Principale</td>
                    <td class="droite">
                      {{ declaration_data.peuplement_ess_1 }}
                    </td>
                  </tr>
                  <tr v-if="declaration_data.peuplement_ess_2">
                    <td class="gauche">Secondaire(s)</td>
                    <td class="droite">
                      {{ declaration_data.peuplement_ess_2 }}
                    </td>
                  </tr>

                  <tr v-if="declaration_data.peuplement_ess_3">
                    <td class="gauche">Complémentaire(s)</td>
                    <td class="droite">
                      {{ declaration_data.peuplement_ess_3 }}
                    </td>
                  </tr>
                </tbody>

                <!-- --------------------------- PEUPLEMENT - DESCRIPTION --------------------------- -->
                <tbody>
                  <tr>
                    <th
                      colspan="2"
                      class="sous_titre"
                    >
                      Peuplement - description
                    </th>
                  </tr>
                  <tr v-if="declaration_data.surface_renseignee">
                    <td class="gauche">Superficie du peuplement (ha)</td>
                    <td class="droite">
                      {{
                        declaration_data.surface_renseignee
                          ? declaration_data.surface_renseignee
                          : 'Non renseignée'
                      }}
                    </td>
                  </tr>
                  <tr v-if="declaration_data.origine_peuplement">
                    <td class="gauche">Origine</td>
                    <td class="droite">
                      {{ declaration_data.origine_peuplement }}
                    </td>
                  </tr>
                  <tr v-if="declaration_data.origine_plants_touches">
                    <td class="gauche">Origine des plants touchés</td>
                    <td class="droite">
                      {{ declaration_data.origine_plants_touches }}
                    </td>
                  </tr>
                  <tr v-if="declaration_data.peuplement_type">
                    <td class="gauche">Type</td>
                    <td class="droite">
                      {{ declaration_data.peuplement_type }}
                    </td>
                  </tr>
                  <tr v-if="declaration_data.peuplement_maturite">
                    <td class="gauche">Maturité</td>
                    <td class="droite">
                      {{ declaration_data.peuplement_maturite }}
                    </td>
                  </tr>
                </tbody>

                <!-- --------------------------- PEUPLEMENT - PROTECTION --------------------------- -->
                <tbody>
                  <tr>
                    <th
                      colspan="2"
                      class="sous_titre"
                    >
                      Peuplement - protection
                    </th>
                  </tr>
                  <tr>
                    <td class="gauche">Existence</td>
                    <td class="droite">
                      {{ declaration_data.peuplement_protection_type ? 'Oui' : 'Non' }}
                    </td>
                  </tr>
                  <tr v-if="declaration_data.peuplement_protection_type">
                    <td class="gauche">Type</td>
                    <td class="droite">
                      {{ declaration_data.peuplement_protection_type }}
                    </td>
                  </tr>
                </tbody>

                <!-- --------------------------- PEUPLEMENT - PATURAGE --------------------------- -->
                <tbody v-if="declaration_data.peuplement_paturage_type">
                  <tr>
                    <th
                      colspan="2"
                      class="sous_titre"
                    >
                      Peuplement - pâturage
                    </th>
                  </tr>

                  <tr v-if="declaration_data.peuplement_paturage_type">
                    <td class="gauche">Type</td>
                    <td class="droite">
                      {{ declaration_data.peuplement_paturage_type }}
                    </td>
                  </tr>
                  <tr v-if="declaration_data.paturage_statut">
                    <td class="gauche">Statut</td>
                    <td class="droite">
                      {{ declaration_data.paturage_statut }}
                    </td>
                  </tr>
                  <tr v-if="declaration_data.paturage_frequence">
                    <td class="gauche">Fréquence</td>
                    <td class="droite">
                      {{ declaration_data.paturage_frequence }}
                    </td>
                  </tr>
                  <tr v-if="declaration_data.peuplement_paturage_saison">
                    <td class="gauche">Saison</td>
                    <td class="droite">
                      {{ declaration_data.peuplement_paturage_saison }}
                    </td>
                  </tr>
                </tbody>

                <!-- --------------------------- DEGATS --------------------------- -->
                <tbody>
                  <tr>
                    <th
                      colspan="2"
                      class="sous_titre"
                    >
                      Dégâts
                    </th>
                  </tr>

                  <tr
                    v-for="(item_degat, index) in declaration_data.degats"
                    :key="index"
                  >
                    <td class="gauche">{{ item_degat.degat_type_label }}</td>
                    <td class="droite">
                      <!-- si le type de degat n'est pas un degat sur cloture-->
                      <template v-if="item_degat.degat_type_code != 'P/C'">
                        <template>
                          <div
                            v-for="(item_degat_essence, index_essence) in item_degat.essences"
                            :key="index_essence"
                          >
                            <strong>
                              {{ item_degat_essence.degat_essence_label }}
                            </strong>
                            <!-- si le degat n'est pas un defaut de regeneration, on affiche les détails -->
                            <span v-if="item_degat.degat_type_code != 'ABS'">
                              :
                              {{ item_degat_essence.degat_etendue_label }},
                              {{ item_degat_essence.degat_gravite_label }},
                              {{ item_degat_essence.degat_anteriorite_label }}
                            </span>
                          </div>
                        </template>
                      </template>
                      <template v-if="item_degat.id_nomenclature_degat_type == 480">
                        <!-- si le type de degat est un degat sur cloture  on met juste oui-->
                        Oui
                      </template>
                    </td>
                  </tr>
                </tbody>

                <!-- --------------------------- COMMENTAIRES --------------------------- -->
                <tbody v-if="declaration_data.commentaire">
                  <tr>
                    <th
                      colspan="2"
                      class="sous_titre"
                    >
                      Commentaires
                    </th>
                  </tr>
                  <tr>
                    <!-- <td class="gauche"></td> -->
                    <td
                      class="droite"
                      colspan="2"
                      style="padding: 10px"
                    >
                      {{ declaration_data.commentaire }}
                    </td>
                  </tr>
                </tbody>
              </v-simple-table>
            </div>
          </template>
        </div>
      </div>

      <div class="html2pdf__page-break"></div>

      <h2 style="margin-top: 2em">Cartes</h2>

      <div style="margin-top: 1em">
        <MapDeclarationSimple
          v-if="declaration_data"
          :declaration_data="declaration_data"
          :liste_layers="[
            'OEASC',
            'SECTEUR',
            'COMMUNES',
            'FORETS_DGD',
            'FORETS_ONF',
            'PARCELLES_ONF',
            'CADASTRES',
          ]"
          :zoom_on="['SECTEUR']"
        ></MapDeclarationSimple>
      </div>

      <div style="margin-top: 1em">
        <MapDeclarationSimple
          v-if="declaration_data"
          :declaration_data="declaration_data"
          :liste_layers="[
            'OEASC',
            'FORETS_ONF',
            'UG_ONF',
            'FORETS_DGD',
            'PARCELLES_ONF',
            'CADASTRES',
            'SECTIONS',
          ]"
          :zoom_on="['FORETS_ONF', 'FORETS_DGD', 'COMMUNES']"
        ></MapDeclarationSimple>
      </div>

      <div style="margin-top: 1em">
        <MapDeclarationSimple
          v-if="declaration_data"
          :declaration_data="declaration_data"
          :liste_layers="['OEASC', 'FORETS_ONF', 'UG_ONF', 'FORETS_DGD', 'CADASTRES', 'SECTIONS']"
          :zoom_on="['PARCELLES_ONF', 'CADASTRES']"
        ></MapDeclarationSimple>
      </div>

      <!-- <div style="margin-top: 3em">
          <div v-for="type in mapList">
            <div
              v-if="configMaps[type]"
              :key="type"
            >
              <div small>{{ configMaps[type].title }}</div>
              <base-map
                :mapId="`map_${type}`"
                :config="configMaps[type]"
                height="315px"
              ></base-map>
            </div>
          </div>
        </div> -->
    </div>
    <!-- <pre>{{ declaration_data }}</pre> -->
  </div>
</template>

<script>
// import baseMap from '@/components/map/base-map';
// import { exportPDF } from "@/modules/export";
import { apiRequest } from '@/core/js/data/api';
import './declaration.css';
import html2pdf from 'html2pdf.js';
import html2canvas from 'html2canvas';
import resumeDeclaration from './resume_declaration.vue';
import MapDeclarationSimple from './map/map_declaration_simple.vue';

const styles = {
  foret: {
    color: 'purple',
    fillColor: 'purple',
    weight: 2,
    opacity: 1,
    fillOpacity: 0.5,
  },
  parcelles: {
    color: 'black',
    fillColor: 'green',
    weight: 2,
    opacity: 1,
    fillOpacity: 0.5,
  },
};

export default {
  name: 'voir_declaration',
  data: () => ({
    pdfProcessing: false,
    declaration_data: null,
    b_init: false,
    mapList: ['secteur', 'foret', 'parcelles'],
  }),
  components: {
    resumeDeclaration,
    // baseMap,
    MapDeclarationSimple,
  },
  methods: {
    exportDeclaration() {
      this.pdfProcessing = true;
      this.$nextTick(() => {
        // Attendre que toutes les cartes soient entièrement chargées
        setTimeout(() => {
          const element = document.getElementById('declaration');

          // Masquer les éléments avec la classe ignorepdf
          const elementsToHide = element.querySelectorAll('.ignorepdf');
          elementsToHide.forEach((el) => (el.style.display = 'none'));

          const opt = {
            margin: 0.5,
            filename: `declaration_${this.declaration_data.id_declaration}.pdf`,
            image: { type: 'jpeg', quality: 0.98 },
            html2canvas: {
              scale: 1.5,
              useCORS: true,
              logging: false,
              width: element.scrollWidth,
              height: element.scrollHeight,
              scrollX: 0,
              scrollY: 0,
              windowWidth: element.scrollWidth,
              windowHeight: element.scrollHeight,
              allowTaint: true,
              foreignObjectRendering: false,
              backgroundColor: '#ffffff',
            },
            jsPDF: {
              unit: 'mm',
              format: 'a4',
              orientation: 'portrait',
              compress: true,
            },
            pagebreak: { mode: ['avoid-all', 'css', 'legacy'] },
          };

          html2pdf()
            .set(opt)
            .from(element)
            .save()
            .then(() => {
              // Remettre les éléments cachés
              elementsToHide.forEach((el) => (el.style.display = ''));
              this.pdfProcessing = false;
            })
            .catch((error) => {
              console.error('Erreur lors de la génération du PDF:', error);
              // Remettre les éléments cachés même en cas d'erreur
              elementsToHide.forEach((el) => (el.style.display = ''));
              this.pdfProcessing = false;
            });
        }, 2000); // Délai plus long pour s'assurer que les cartes sont chargées
      });
    },

    // configMap(type) {
    //   if (!this.declaration_data) {
    //     return;
    //   }
    //   const markers = [
    //     {
    //       coords: this.declaration_data.centroid,
    //       type: 'marker',
    //       style: {
    //         color: 'blue',
    //         icon: 'map-marker',
    //       },
    //     },
    //   ];
    //   const markerLegendGroups = [
    //     {
    //       legends: [
    //         {
    //           icon: 'map-marker',
    //           text: 'Localisation des alertes',
    //           color: '#3689CE',
    //         },
    //       ],
    //     },
    //   ];
    //   const titles = {
    //     secteur: "Localisation de l'alerte dans le périmètre de l'observatoire",
    //     foret: 'Localisation des parcelles',
    //     parcelles: 'Carte des parcelles',
    //   };
    //   const layerList = {
    //     secteur: {},
    //     foret: {
    //       url: `api/ref_geo/areas_from_type/l?id_area=${this.declaration_data.areas_foret.join(
    //         '&id_area='
    //       )}`,
    //       legend: "Forêt concernée par l'alerte",
    //       style: styles.foret,
    //       pane: 'PANE_LAYER_1',
    //     },
    //     parcelles: {
    //       url: `api/ref_geo/areas_from_type/l?id_area=${this.declaration_data.areas_localisation.join(
    //         '&id_area='
    //       )}`,

    //       legend: "Parcelle(s) concernée(s) par l'alerte",
    //       style: styles.parcelles,
    //       pane: 'PANE_LAYER_2',
    //     },
    //   };

    //   layerList[type] = {
    //     ...layerList[type],
    //     tooltip: {
    //       permanent: true,
    //       className: 'tooltip-label',
    //       label: 'label',
    //     },
    //     zoom: true,
    //   };
    //   if (type != '') {
    //     delete layerList.secteur;
    //   }
    //   return { layerList, title: titles[type], markers, markerLegendGroups };
    // },
  },
  computed: {
    id() {
      return this.$route.params.id;
    },
    // configMaps() {
    //   const configMaps = {};
    //   for (const type of this.mapList) {
    //     configMaps[type] = this.configMap(type);
    //   }
    //   return configMaps;
    // },
  },
  async created() {
    // this.initDeclaration();
    this.id_declaration = this.$route.params.id;
    this.bInit = true;
    this.nomenclature = await apiRequest('GET', `api/oeasc/nomenclatures`);
    this.declaration_data = await apiRequest(
      'GET',
      `api/declaration/voir_declaration/${this.id_declaration}`
    );

    console.log('declaration_data', this.declaration_data);
  },
  async mounted() {},
  watch: {},
};
</script>
<style scoped></style>
