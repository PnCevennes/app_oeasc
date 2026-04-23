<!-- Page de visualisation d'une déclaration. Est appelé dans form-chained
Comprend le résumé de la déclaration, les cartes et le bouton d'export PDF. -->
<template>
  <div style="min-width: 900px; max-width: 1000px; margin: auto">
    <v-progress-linear
      v-if="isExporting"
      active
      indeterminate
    ></v-progress-linear>
    <div>
      <v-btn
        icon
        color="red"
        @click="exportToPdf()"
        title="Exporter la déclaration au format pdf"
      >
        <v-icon>mdi-file-pdf</v-icon>
      </v-btn>
    </div>

    <div
      style="width: 100%; margin: auto; padding: 16px; background-color: white"
      id="declaration"
      ref="ref_declaration"
    >
      <div v-if="declaration_data">
        <h1>Déclaration {{ declaration_data.id_declaration }}</h1>

        <div
          id="resume_declaration"
          ref="ref_resume_declaration"
          style="width: 100%; margin: auto"
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

      <h2 style="margin-top: 2em">Cartes</h2>

      <div style="margin-top: 1em">
        <MapDeclarationSimple
          v-if="declaration_data"
          ref="map1"
          :declaration_data="declaration_data"
          mapID="map1"
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
          ref="map2"
          :declaration_data="declaration_data"
          mapID="map2"
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
          ref="map3"
          :declaration_data="declaration_data"
          mapID="map3"
          :liste_layers="[
            'OEASC',
            'PARCELLES_ONF',
            'UG_ONF',
            'FORETS_DGD',
            'CADASTRES',
            'SECTIONS',
          ]"
          :zoom_on="['UG_ONF', 'CADASTRES']"
        ></MapDeclarationSimple>
      </div>
    </div>
  </div>
</template>

<script>
// import baseMap from '@/components/map/base-map';
// import { exportPDF } from "@/modules/export";
import { apiRequest } from '@/core/js/data/api';
import './declaration.css';
import html2canvas from 'html2canvas';
import jsPDF from 'jspdf';
import resumeDeclaration from './resume_declaration.vue';
import MapDeclarationSimple from './map/map_declaration_simple.vue';

export default {
  name: 'voir_declaration',
  data: () => ({
    pdfProcessing: false,
    declaration_data: null,
    b_init: false,
    mapList: ['secteur', 'foret', 'parcelles'],
    isExporting: false,
  }),
  components: {
    resumeDeclaration,
    MapDeclarationSimple,
  },
  methods: {
    // attend que la carte ait fini de charger ses tiles avant de continuer (important pour éviter les problèmes de tiles manquantes dans le PDF si la capture est faite trop tôt)
    waitForMapReady(mapRef) {
      return new Promise((resolve) => {
        const map = mapRef.getMapInstance();

        if (map._loaded) {
          setTimeout(resolve, 300);
          return;
        }

        map.once('load', () => {
          setTimeout(resolve, 300);
        });
      });
    },

    // Pour l'export pdf, on capture le tableau de résumé
    // Capture du tableau récapitulatif (resume_declaration)
    async captureTable() {
      try {
        const el =
          document.getElementById('resume_declaration') ||
          document.querySelector('#resume_declaration');
        if (!el) {
          const c = document.createElement('canvas');
          c.width = 10;
          c.height = 10;
          return c;
        }

        // ensure layout is stable
        await this.$nextTick();
        await new Promise((r) => setTimeout(r, 200));

        const canvas = await html2canvas(el, { useCORS: true, allowTaint: true, scale: 1.5 });
        return canvas;
      } catch (e) {
        const c = document.createElement('canvas');
        c.width = 10;
        c.height = 10;
        return c;
      }
    },

    async exportToPdf() {
      try {
        this.isExporting = true;
        const pdf = new jsPDF('p', 'mm', 'a4');
        const pageWidth = pdf.internal.pageSize.getWidth();
        const pageHeight = pdf.internal.pageSize.getHeight();
        const margin = 10;
        const contentWidth = pageWidth - margin * 2;
        let currentY = margin;
        const dateStr = new Date().toLocaleString();

        pdf.text(`Déclaration no : ${this.declaration_data.id_declaration}`, margin, currentY);
        currentY += 10;

        pdf.setFontSize(12);
        pdf.text(`Exporté le : ${dateStr}`, margin, currentY);
        currentY += 10;

        // ---- TABLEAU ----
        pdf.setFontSize(12);
        pdf.setTextColor(40, 40, 40);

        const tableCanvas = await this.captureTable();
        const tableImgData = tableCanvas.toDataURL('image/png');
        const tableAspectRatio = tableCanvas.height / tableCanvas.width;
        const tableHeight = contentWidth * tableAspectRatio;

        // Vérifier si on doit passer à une nouvelle page
        if (currentY + tableHeight > pageHeight - margin) {
          pdf.addPage();
          currentY = margin;
        }

        pdf.addImage(tableImgData, 'PNG', margin, currentY, contentWidth, tableHeight);
        currentY += tableHeight + 10;

        // ---- CARTES ----
        pdf.setFontSize(12);
        pdf.setTextColor(40, 40, 40);

        // Nouvelle page pour les cartes
        pdf.addPage();
        currentY = margin;
        pdf.text('Cartes de localisation', margin, currentY);
        currentY += 8;

        // s'assurer que les trois maps ont fini de charger leurs tiles
        await this.waitForMapReady(this.$refs.map1);
        await this.waitForMapReady(this.$refs.map2);
        await this.waitForMapReady(this.$refs.map3);

        // Capturer chaque map via html2canvas sur le conteneur DOM (inclut labels/divIcon et légende)
        const map1 = await this.$refs.map1.getMapInstance();
        const map2 = await this.$refs.map2.getMapInstance();
        const map3 = await this.$refs.map3.getMapInstance();

        const canvas1 = await html2canvas(map1.getContainer(), {
          useCORS: true,
          allowTaint: true,
          scale: 2,
        });
        const canvas2 = await html2canvas(map2.getContainer(), {
          useCORS: true,
          allowTaint: true,
          scale: 2,
        });
        const canvas3 = await html2canvas(map3.getContainer(), {
          useCORS: true,
          allowTaint: true,
          scale: 2,
        });

        const img1 = canvas1.toDataURL('image/png');
        const img2 = canvas2.toDataURL('image/png');
        const img3 = canvas3.toDataURL('image/png');

        // positionnement des images de cartes.
        pdf.addImage(img1, 'PNG', 10, 10, 190, 90);
        pdf.addImage(img2, 'PNG', 10, 105, 190, 90);
        pdf.addImage(img3, 'PNG', 10, 200, 190, 90);

        // // Sauvegarde du PDF
        pdf.save(`declaration_${this.declaration_data.id_declaration}.pdf`);
      } catch (error) {
        console.error('Erreur lors de la génération du PDF:', error);
        // Afficher une notification d'erreur avec Vuetify
        this.$emit('export-error', error.message);
      } finally {
        this.isExporting = false;
      }
    },
  },
  computed: {
    id() {
      return this.$route.params.id;
    },
  },
  async created() {
    this.id_declaration = this.$route.params.id;
    this.bInit = true;
    this.nomenclature = await apiRequest('GET', `api/oeasc/nomenclatures`);
    this.declaration_data = await apiRequest(
      'GET',
      `api/declaration/voir_declaration/${this.id_declaration}`
    );

    // console.log('declaration_data', this.declaration_data);
  },
  async mounted() {},
  watch: {},
};
</script>
<style scoped></style>
