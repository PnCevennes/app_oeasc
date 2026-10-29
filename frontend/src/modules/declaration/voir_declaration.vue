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
          :disabled="!declaration_data || isExporting"
          :loading="isExporting"
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
          color="orange-lighten-2"
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

        <div
          id="resume_declaration"
          ref="ref_resume_declaration"
          :style="{ width: pdfCompact ? '450px' : '100%', margin: 'auto' }"
        >
          <template v-if="bInit == true">
            <voir-declaration-table
              :declaration_data="declaration_data"
              :compact="pdfCompact"
            />
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
          :zoom_offset="-2"
        ></MapDeclarationSimple>
      </div>
    </div>
  </div>
</template>

<script>
import { apiRequest } from '@/core/js/data/api';
import './declaration.css';
import VoirDeclarationTable from './voir-declaration-table.vue';
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
    pdfCompact: false, // tableau en mode dense pendant la capture de l'export PDF
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
    VoirDeclarationTable,
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
        // marges réduites sur la page du tableau pour lui laisser le maximum de place
        const tableMargin = 6;
        const tableMarginX = 15; // marges gauche/droite
        const tableContentWidth = pageWidth - tableMarginX * 2;
        let currentY = tableMargin;
        const dateStr = new Date().toLocaleString();

        // titre et date sur une seule ligne, pour laisser le maximum de place au tableau
        pdf.setFontSize(18);
        pdf.setTextColor(40, 40, 40);
        pdf.text(
          `Déclaration no : ${this.declaration_data.id_declaration}`,
          tableMarginX,
          currentY + 6
        );
        pdf.setFontSize(7);
        pdf.text(`Exporté le : ${dateStr}`, pageWidth - tableMarginX, currentY + 6, {
          align: 'right',
        });
        currentY += 10;

        // ---- TABLEAU RÉCAPITULATIF ----
        const tableEl = document.getElementById('resume_declaration');
        if (tableEl) {
          // tableau en mode dense uniquement le temps de la capture, dans un conteneur étroit (450 px) :
          // l'image est mise à la largeur de la page, donc plus le tableau est étroit, plus sa police
          // est grande dans le PDF (avant : 1000 px de large, le tableau n'occupait que la moitié de la
          // page). Si le tableau devient trop haut, il est réduit pour tenir (voir scaleFit).
          // tableau en mode dense uniquement le temps de la capture
          this.pdfCompact = true;
          await this.$nextTick();
          await this._yield(150);
          try {
            const table = await this.captureElement(tableEl, { scale: tableScale, format: 'png' });
            // le tableau doit tenir sur la 1re page, sous le titre : on le réduit (police
            // comprise, c'est une image) pour qu'il tienne en hauteur, sans l'agrandir au-delà
            // de la largeur utile, et on le centre.
            const maxHeight = pageHeight - tableMargin - currentY;
            const scaleFit = Math.min(
              tableContentWidth / table.width,
              maxHeight / table.height
            );
            const tableWidthMm = table.width * scaleFit;
            const tableHeight = table.height * scaleFit;
            pdf.addImage(
              table.data,
              'PNG',
              tableMarginX + (tableContentWidth - tableWidthMm) / 2,
              currentY,
              tableWidthMm,
              tableHeight,
              undefined,
              'FAST'
            );
          } catch (e) {
            console.error('Tableau non capturé pour le PDF :', e);
          } finally {
            this.pdfCompact = false;
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
