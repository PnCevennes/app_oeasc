<!-- Page de visualisation d'une déclaration. Est appelé dans form-chained
Comprend le résumé de la déclaration, les cartes et le bouton d'export PDF. -->
<template>
  <div style="min-width: 900px; max-width: 1000px; margin: auto">
    <v-progress-linear
      v-if="isExporting"
      active
      indeterminate
    ></v-progress-linear>

    <v-snackbar
      v-model="showExportError"
      color="error"
      :timeout="6000"
    >
      L'export PDF a échoué : {{ exportErrorMsg }}
    </v-snackbar>

    <div>
      <span>
        <v-btn
          color="red"
          :disabled="!declaration_data"
          @click="exportToPdf"
          title="Exporter la déclaration au format pdf"
        >
          <v-icon left>mdi-file-pdf</v-icon>
          Exporter en PDF
        </v-btn>
      </span>

      <span v-if="show_buttom_relance_mail">
        <v-btn
          style="margin-left: 16px"
          color="orange lighten-2"
          title="Envoyer un mail de relance pour cette déclaration"
          @click="show_popup_relance = true"
        >
          <v-icon left>mdi-email-send</v-icon>
          Envoyer un mail de relance
        </v-btn>
      </span>
    </div>

    <confirmRelanceMail
      v-if="declaration_data"
      :declaration_data="declaration_data"
      :show_popup_relance="show_popup_relance"
      @close-relance-popup="show_popup_relance = false"
    />

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
              <v-table
                density="compact"
                style="margin-bottom: 16px; width: 100%; max-width: 100%; margin: auto"
              >
                <thead>
                  <tr>
                    <th colspan="2">Résumé de la déclaration</th>
                  </tr>
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
                  <tr v-if="this.$store.getters.droitMax >= 4">
                    <td class="gauche">Validité</td>
                    <td class="droite">{{ declaration_data.valide }}</td>
                  </tr>

                  <tr>
                    <td class="gauche">Partage d'information</td>
                    <td class="droite">
                      {{ declaration_data.autorisation }}
                    </td>
                  </tr>
                  <tr v-if="this.$store.getters.droitMax >= 2">
                    <td class="gauche">Statut</td>
                    <td class="droite">
                      {{ declaration_data.statut_label }}
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
              </v-table>
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
          :liste_layers="create_liste_layers_from_config('loin')"
          :zoom_on="['SECTEUR']"
        ></MapDeclarationSimple>
      </div>

      <div style="margin-top: 1em">
        <MapDeclarationSimple
          v-if="declaration_data"
          ref="map2"
          :declaration_data="declaration_data"
          mapID="map2"
          :liste_layers="create_liste_layers_from_config('moyen')"
          :zoom_on="['FORETS_ONF', 'FORETS_DGD', 'COMMUNES']"
        ></MapDeclarationSimple>
      </div>

      <div style="margin-top: 1em">
        <MapDeclarationSimple
          v-if="declaration_data"
          ref="map3"
          :declaration_data="declaration_data"
          mapID="map3"
          :liste_layers="create_liste_layers_from_config('proche')"
          :zoom_on="['UG_ONF', 'CADASTRES']"
        ></MapDeclarationSimple>
      </div>
    </div>
  </div>
</template>

<script>
import { apiRequest } from '@/core/js/data/api';
import './declaration.css';
import resumeDeclaration from './resume_declaration.vue';
import MapDeclarationSimple from './map/map_declaration_simple.vue';
import confirmRelanceMail from './confirm_relance_mail.vue';
import config_variables from '@/../../config/variables/declaration.json';

// jsPDF et html2canvas sont volumineux et uniquement utiles pour l'export PDF :
// on les charge à la demande (voir exportToPdf) pour alléger le bundle initial.
let jsPDFLib = null;
let html2canvasLib = null;

export default {
  name: 'voir_declaration',
  data: () => ({
    pdfProcessing: false,
    declaration_data: null,
    b_init: false,
    mapList: ['secteur', 'foret', 'parcelles'],
    isExporting: false,
    show_popup_relance: false,
    show_buttom_relance_mail: false,
    showExportError: false,
    exportErrorMsg: '',
  }),

  components: {
    resumeDeclaration,
    MapDeclarationSimple,
    confirmRelanceMail,
  },
  methods: {
    // Rend brièvement la main au navigateur : anime la barre de progression et évite
    // que l'onglet soit tué pour "script non responsive" sur les PC lents.
    _yield(ms = 40) {
      return new Promise((resolve) => setTimeout(resolve, ms));
    },

    // Machines peu puissantes -> on réduit la résolution de capture pour éviter les
    // dépassements mémoire (crash d'onglet). deviceMemory / hardwareConcurrency ne sont
    // pas dispo sur tous les navigateurs : valeurs par défaut prudentes.
    _isLowPowerDevice() {
      const mem = navigator.deviceMemory || 8;
      const cores = navigator.hardwareConcurrency || 8;
      return mem <= 4 || cores <= 4;
    },

    // Attend que la carte soit prête, AVEC un timeout pour ne jamais bloquer l'export.
    waitForMapReady(mapRef, timeout = 8000) {
      return new Promise((resolve) => {
        const map = mapRef && mapRef.getMapInstance ? mapRef.getMapInstance() : null;
        if (!map) {
          resolve();
          return;
        }

        let settled = false;
        const finish = () => {
          if (settled) return;
          settled = true;
          clearTimeout(timer);
          // laisse le temps aux dernières tuiles de se peindre
          setTimeout(resolve, 350);
        };

        const timer = setTimeout(finish, timeout);

        // whenReady() se déclenche immédiatement si la carte a déjà un centre/zoom,
        // sinon au premier "load" (contrairement à once('load') qui, si "load" a déjà
        // été émis, ne se redéclenche jamais et bloque l'export indéfiniment).
        try {
          map.whenReady(finish);
        } catch (e) {
          finish();
        }
      });
    },

    // Capture un élément DOM en image.
    // PNG (net) pour le texte du tableau, JPEG (léger) pour les cartes.
    // Le canvas est libéré immédiatement (crucial sur les PC à faible RAM).
    async captureElement(el, { scale = 1.5, format = 'png', quality = 0.85 } = {}) {
      const canvas = await html2canvasLib(el, {
        useCORS: true,
        backgroundColor: '#ffffff',
        scale,
        logging: false,
        imageTimeout: 15000,
      });
      const mime = format === 'jpeg' ? 'image/jpeg' : 'image/png';
      const data = canvas.toDataURL(mime, quality);
      const width = canvas.width;
      const height = canvas.height;
      canvas.width = 0;
      canvas.height = 0;
      return { data, width, height, format: format === 'jpeg' ? 'JPEG' : 'PNG' };
    },

    async exportToPdf() {
      if (this.isExporting || !this.declaration_data) return;
      this.isExporting = true;

      // laisse la barre de progression s'afficher avant les traitements lourds
      await this.$nextTick();
      await this._yield(60);

      try {
        // chargement à la demande des librairies d'export
        if (!jsPDFLib) jsPDFLib = (await import('jspdf')).default;
        if (!html2canvasLib) html2canvasLib = (await import('html2canvas')).default;

        const lowPower = this._isLowPowerDevice();
        const tableScale = lowPower ? 1.2 : 1.6;
        const mapScale = lowPower ? 1 : 1.5;

        const pdf = new jsPDFLib('p', 'mm', 'a4');
        const pageWidth = pdf.internal.pageSize.getWidth();
        const pageHeight = pdf.internal.pageSize.getHeight();
        const margin = 10;
        const contentWidth = pageWidth - margin * 2;
        let currentY = margin;
        const dateStr = new Date().toLocaleString();

        pdf.setFontSize(14);
        pdf.text(`Déclaration no : ${this.declaration_data.id_declaration}`, margin, currentY);
        currentY += 10;
        pdf.setFontSize(12);
        pdf.setTextColor(40, 40, 40);
        pdf.text(`Exporté le : ${dateStr}`, margin, currentY);
        currentY += 10;

        // ---- TABLEAU RÉCAPITULATIF ----
        const tableEl = document.getElementById('resume_declaration');
        if (tableEl) {
          await this.$nextTick();
          await this._yield(150);
          try {
            const table = await this.captureElement(tableEl, { scale: tableScale, format: 'png' });
            const tableHeight = (contentWidth * table.height) / table.width;
            if (currentY + tableHeight > pageHeight - margin) {
              pdf.addPage();
              currentY = margin;
            }
            pdf.addImage(
              table.data,
              'PNG',
              margin,
              currentY,
              contentWidth,
              tableHeight,
              undefined,
              'FAST'
            );
          } catch (e) {
            console.error('Tableau non capturé pour le PDF :', e);
          }
        }
        await this._yield(50);

        // ---- CARTES ----
        pdf.addPage();
        pdf.setFontSize(12);
        pdf.setTextColor(40, 40, 40);
        pdf.text('Cartes de localisation', margin, margin);

        const maps = [
          { ref: this.$refs.map1, y: 16 },
          { ref: this.$refs.map2, y: 107 },
          { ref: this.$refs.map3, y: 198 },
        ];

        // Capture SÉQUENTIELLE : une seule carte en mémoire à la fois.
        // Une carte en échec n'empêche pas la génération du reste du PDF.
        for (const item of maps) {
          let corsEnabled = false;
          try {
            await this.waitForMapReady(item.ref);
            const map = item.ref && item.ref.getMapInstance ? item.ref.getMapInstance() : null;
            if (!map) continue;
            // recharge le fond de carte avec crossOrigin pour permettre la capture canvas
            if (item.ref.enableCorsTiles) {
              await item.ref.enableCorsTiles();
              corsEnabled = true;
            }
            try {
              map.invalidateSize({ animate: false });
            } catch (e) {
              /* ignore */
            }
            await this._yield(150);
            const img = await this.captureElement(map.getContainer(), {
              scale: mapScale,
              format: 'jpeg',
              quality: 0.82,
            });
            pdf.addImage(img.data, 'JPEG', margin, item.y, 190, 90, undefined, 'FAST');
          } catch (e) {
            console.error('Carte non capturée pour le PDF :', e);
          } finally {
            // rétablit le fond de carte normal (sans crossOrigin)
            if (corsEnabled && item.ref && item.ref.disableCorsTiles) {
              try {
                item.ref.disableCorsTiles();
              } catch (e) {
                /* ignore */
              }
            }
          }
          // rend la main entre chaque carte
          await this._yield(60);
        }

        pdf.save(`declaration_${this.declaration_data.id_declaration}.pdf`);
      } catch (error) {
        console.error('Erreur lors de la génération du PDF :', error);
        this.exportErrorMsg = error && error.message ? error.message : 'erreur inconnue';
        this.showExportError = true;
        this.$emit('export-error', this.exportErrorMsg);
      } finally {
        this.isExporting = false;
      }
    },

    define_show_buttom_relance_mail() {
      // le bouton de relance mail n'est affiché que pour les admins et si la déclaration est dans un statut qui autorise la relance
      if (this.$store.getters.droitMax >= 4 && this.declaration_data) {
        const statut = this.declaration_data.statut;
        const config_statut = config_variables['STATUT_DECLARATION'];
        if (statut >= config_statut['Relance']) {
          this.show_buttom_relance_mail = true;
        }
        const [day, month, year] = this.declaration_data.date_fin.split('/');
        const dateFin = new Date(year, month - 1, day);

        if (statut === config_statut['Active'] && dateFin && dateFin < new Date()) {
          this.show_buttom_relance_mail = true;
          // console.log('Active show_buttom_relance_mail:', this.show_buttom_relance_mail);
        }
      }
    },

    create_liste_layers_from_config(types) {
      // méthode pour créer une liste de couches à afficher en fonction du type de forêt (qui dépend de document_foret et statut_public_foret dans declaration_data)
      // type est le type de vue que l'on veut ("loin", "moyen" ou "proche" )

      if (!this.declaration_data) {
        return [];
      }
      const liste = [];
      if (types == 'loin') {
        liste.push('OEASC');
        liste.push('SECTEUR');
        if (this.declaration_data.document_foret == false) {
          liste.push('COMMUNES');
          liste.push('CADASTRES');
        } else {
          if (this.declaration_data.statut_public_foret == true) {
            liste.push('FORETS_ONF');
            liste.push('PARCELLES_ONF');
          } else {
            liste.push('FORETS_DGD');
            liste.push('COMMUNES');
            liste.push('CADASTRES');
          }
        }
      } else if (types == 'moyen') {
        liste.push('SECTEUR');
        if (this.declaration_data.document_foret == false) {
          liste.push('COMMUNES');
          liste.push('CADASTRES');
        } else {
          if (this.declaration_data.statut_public_foret == true) {
            liste.push('FORETS_ONF');
            // liste.push('PARCELLES_ONF');
            liste.push('UG_ONF');
          } else {
            liste.push('FORETS_DGD');
            liste.push('CADASTRES');
          }
        }
      } else if (types == 'proche') {
        liste.push('SECTEUR');
        if (this.declaration_data.document_foret == false) {
          liste.push('SECTIONS');
          liste.push('CADASTRES');
        } else {
          if (this.declaration_data.statut_public_foret == true) {
            liste.push('FORETS_ONF');
            // liste.push('PARCELLES_ONF');
            liste.push('UG_ONF');
          } else {
            liste.push('FORETS_DGD');
            liste.push('CADASTRES');
          }
        }
      }

      return liste;
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
    this.define_show_buttom_relance_mail();
  },
  async mounted() {
    // si il y a une query param relance=true, on affiche directement le popup de relance
    if (this.$route.query.relance === 'true') {
      this.show_popup_relance = true;
    }
  },
  watch: {},
};
</script>
<style scoped></style>
