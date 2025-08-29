<!-- Page de visualisation d'une déclaration. Est appelé dans form-chained
Comprend le résumé de la déclaration, les cartes et le bouton d'export PDF. -->
<template>
  <div style="min-width: 1000px;">
    <v-progress-linear
      v-if="pdfProcessing"
      active
      indeterminate
    ></v-progress-linear>


    <div style="width: 100%;" id="declaration">
      <div v-if="declaration_data">
        <h1>Déclaration {{ declaration_data.id_declaration }}</h1>
        <v-btn
          class="ignorepdf"
          icon
          color="red"
          @click="exportDeclaration()"
          title="Exporter la déclaration au format pdf"
          ><v-icon>mdi-file-pdf</v-icon></v-btn
        >
        
        <div id="resume_declaration" style="">
          <template v-if="bInit == true">
          <div>
            <v-simple-table dense style="margin-bottom: 16px; width: 100%; max-width: 100%; margin: auto;">
              
              <thead >
                <th colspan="2">
                  Résumé de la déclaration
                </th>
              </thead>

              <!-- ------------------------------- INFORMATIONS -------------------------------- -->
              <tbody >
                <tr>
                  <th colspan="2" class="sous_titre">
                    Informations
                  </th>
                </tr>
                <!-- seulement visible par les admins -->
                <tr v-if="this.$store.getters.droitMax >= 5">
                  <td class="gauche" >Validité</td>
                  <td class="droite">{{declaration_data.valide}}</td>
                </tr>


                <tr>
                  <td class="gauche">Partage d'information</td>
                  <td class="droite">
                    {{declaration_data.b_autorisation	? "Autorisé" : "Non autorisé"}}
                  </td>
                </tr>

                <tr>
                  <td class="gauche">Date</td>
                  <td class="droite">
                    {{ declaration_data.declaration_date }}
                  </td>
                </tr>
              </tbody>


              <!-- ------------------------------- DECLARANT -------------------------------- -->
              <tbody v-if="declaration_data.id_declarant">
                <tr>
                  <th colspan="2" class="sous_titre">
                    Déclarant
                  </th>
                </tr>

                <tr v-if="declaration_data.declarant	">
                  <td class="gauche">Nom du propriétaire</td>
                  <td class="droite">{{declaration_data.declarant	}}</td>
                </tr>
                <tr v-if="declaration_data.organisme	">
                  <td class="gauche">Organisme</td>
                  <td class="droite">{{declaration_data.organisme	}}</td>
                  <!-- <td class="droite">{{declaration_data.org_mnemo || "Non renseigné"}}</td> -->
                </tr>
                <!-- <tr v-if="declaration_data.email">
                  <td class="gauche">Email</td>
                  <td class="droite">{{declaration_data.email || "Non renseigné"}}</td>
                </tr> -->
                <!-- <tr v-if="declaration_data.telephone">
                  <td class="gauche">Téléphone</td>
                  <td class="droite">{{declaration_data.telephone || "Non renseigné"}}</td>
                </tr> -->
                <!-- <tr v-if="declaration_data.adresse">
                  <td class="gauche">Adresse</td>
                  <td class="droite">{{declaration_data.adresse || "Non renseigné"}}</td>
                </tr>
                <tr v-if="declaration_data.s_code_postal">
                  <td class="gauche">Code postal</td>
                  <td class="droite">{{declaration_data.s_code_postal || "Non renseigné"}}</td>
                </tr>-->
                <tr v-if="declaration_data.communes	">
                  <td class="gauche">Commune</td>
                  <td class="droite">{{declaration_data.communes || "Non renseigné"}}</td>
                </tr>
              </tbody>

              <!-- ------------------------------- FORET -------------------------------- -->
              <tbody>
                
                <tr>
                  <th colspan="2" class="sous_titre">
                    Forêt
                  </th>
                </tr>

                <tr v-if="declaration_data.areas_foret_names">
                  <td class="gauche" >Nom</td>
                  <td class="droite">{{declaration_data.areas_foret_names }}</td>
                </tr>

                <tr>
                  <td class="gauche">Statut</td>
                  <td class="droite">
                    {{declaration_data.statut_public}}
                  </td>
                </tr>

                <tr>
                  <td class="gauche">Document de gestion durable</td>
                  <td class="droite">
                    {{ declaration_data.document }}
                    <span v-if="declaration_data.b_document && declaration_data.b_statut_public">
                      <i>(régime forestier)</i>
                    </span>
                    <span v-else-if="declaration_data.b_document && !declaration_data.b_statut_public">
                      <i>(document de gestion durable)</i>
                    </span>
                  </td>
                </tr>


                <tr v-if="declaration_data.foret_type_label">
                  <td class="gauche">Type</td>
                  <td class="droite">
                    <!-- ici le type de foret affiché a été renommé par foretType, voir dans les script -->
                    {{ declaration_data.foret_type_label}}
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
                    <th colspan="2" class="sous_titre">
                      Peuplement - localisation
                    </th>
                  </tr>
                  <tr v-if="declaration_data.secteur">
                    <td class="gauche">Secteur</td>
                    <td class="droite">{{declaration_data.secteur}}</td>
                  </tr>


                  <tr v-if="declaration_data.communes">
                    <td class="gauche">Commune(s)</td>
                    <td class="droite"> {{ declaration_data.communes }}</td>
                  </tr>

                  <tr v-if="declaration_data.parcelles">
                    <td class="gauche">Parcelle(s)</td>
                    <td class="droite"> {{ declaration_data.parcelles }}</td>
                  </tr>

                  <!-- <tr v-if="areas_section_computed.length > 0">
                    <td class="gauche">Section(s)</td>
                    <td class="droite">
                      <v-chip
                      v-for="area_section in areas_section_computed"
                      :key="area_section.id_area"
                      small
                      class="ma-1" 
                      >
                      {{ area_section }}
                    </v-chip>
                    </td>
                  </tr> -->



                  <!-- <tr v-if="areas_cadastre_computed.length > 0">
                    <td class="gauche">Parcelle(s) cadastrale(s)</td>
                    <td class="droite">
                      <v-chip
                      v-for="area_cadastre in areas_cadastre_computed"
                      :key="area_cadastre.id_area"
                      small
                      class="ma-1" 
                      >
                      {{ area_cadastre }}
                    </v-chip>
                    </td>
                  </tr> -->
                  
                  <!-- <tr v-if="declaration_data.areas_localisation_cadastre.length > 0">

                    <td class="gauche">Parcelle(s) cadastrale(s) (id)</td>
                    <td class="droite">
                      <v-chip
                      v-for="area_cadastre in declaration_data.areas_localisation_cadastre"
                      :key="area_cadastre"
                      small
                      class="ma-1" 
                      >
                      {{ area_cadastre }}
                    </v-chip>
                    </td>
                  </tr> -->

                  <!-- <tr v-if="areas_ug_computed.length > 0">
                    <td class="gauche">Unités de gestion ONF</td>
                    <td class="droite">
                      <v-chip
                      v-for="area_ug in areas_ug_computed"
                      :key="area_ug.id_area"
                      small
                      class="ma-1" 
                      >
                      {{ area_ug }}
                    </v-chip>
                      
                    </td>
                  </tr> -->

                  <tr v-if="declaration_data.peuplement_acces_label">
                    <td class="gauche">Accessibilité</td>
                    <td class="droite">
                      {{ declaration_data.peuplement_acces_label }}
                    </td>
                  </tr> 
              </tbody>

              <!-- ---------------------------PEUPLEMENT - ESSENCES --------------------------- -->
              <tbody>
                <tr>
                  <th colspan="2" class="sous_titre">
                    Peuplement - essences
                  </th>
                </tr>
                <tr v-if="declaration_data.peuplement_ess_1_label	">
                  <td class="gauche">Principale</td>
                  <td class="droite">
                    {{ declaration_data.peuplement_ess_1_label }}

                  </td>
                </tr>
                <tr v-if="declaration_data.peuplement_ess_2_label">
                  <td class="gauche">Secondaire(s)</td>
                  <td class="droite">
                    {{ declaration_data.peuplement_ess_2_label }}
                    </td>
                </tr>
                
                <tr v-if="declaration_data.peuplement_ess_3_label	">
                  <td class="gauche">Complémentaire(s)</td>
                  <td class="droite">
                    {{ declaration_data.peuplement_ess_3_label }}
                  </td>
                </tr>
                <tr v-if="declaration_data.peuplement_surface">
                  <td class="gauche">Superficie du peuplement (ha)
                  </td>
                  <td class="droite">
                    {{ declaration_data.peuplement_surface? declaration_data.peuplement_surface : "Non renseignée" }}
                  </td>
                </tr>

                
              </tbody>

              <!-- --------------------------- PEUPLEMENT - DESCRIPTION --------------------------- -->
              <tbody>
                <tr>
                  <th colspan="2" class="sous_titre">
                    Peuplement - description
                  </th>
                </tr>
                <tr v-if="declaration_data.peuplement_origine_label	">
                  <td class="gauche">Origine</td>
                  <td class="droite">
                    {{ declaration_data.peuplement_origine_label }}
                  </td>
                </tr>
                <tr v-if="declaration_data.peuplement_origine2_label	">
                  <td class="gauche">Origine des plants touchés</td>
                  <td class="droite">
                    {{ declaration_data.peuplement_origine2_label }}
                    </td>
                </tr>
                <tr v-if="declaration_data.peuplement_type_label">
                  <td class="gauche">Type</td>
                  <td class="droite">
                    {{ declaration_data.peuplement_type_label }}
                    </td>
                </tr>
                <tr v-if="declaration_data.peuplement_maturite_label">
                  <td class="gauche">Maturité</td>
                  <td class="droite">
                    {{ declaration_data.peuplement_maturite_label }}
                  </td>
                </tr>

              </tbody>

              <!-- --------------------------- PEUPLEMENT - PROTECTION --------------------------- -->
              <tbody>
                <tr>
                  <th colspan="2" class="sous_titre">
                    Peuplement - protection
                  </th>
                </tr>
                <tr v-if="declaration_data.b_peuplement_protection_existence !== undefined">
                  <td class="gauche">Existence</td>
                  <td class="droite">
                    {{declaration_data.b_peuplement_protection_existence ? "Oui" : "Non"}}
                  </td>
                </tr>
                <tr v-if="declaration_data.peuplement_protection_type_label">
                  <td class="gauche">Type</td>
                  <td class="droite">
                    {{declaration_data.peuplement_protection_type_label}}

                  </td>
                </tr>
              </tbody>

              <!-- --------------------------- PEUPLEMENT - PATURAGE --------------------------- -->
              <tbody>
                <tr>
                  <th colspan="2" class="sous_titre">
                    Peuplement - pâturage
                  </th>
                </tr>
                <tr v-if="declaration_data.b_peuplement_paturage_presence !== undefined">
                  <td class="gauche">Présence</td>
                  <td class="droite">
                    {{declaration_data.b_peuplement_paturage_presence ? "Oui" : "Non"}}
                  </td>
                </tr>
                <!-- Si il y a présence de pâturage, on affiche les détails -->
                <template v-if="declaration_data.b_peuplement_paturage_presence == true">
                  <tr v-if="declaration_data.peuplement_paturage_type_label">
                    <td class="gauche">Type</td>
                    <td class="droite">
                      {{ declaration_data.peuplement_paturage_type_label }}
                    </td>
                  </tr>
                  <tr v-if="declaration_data.peuplement_paturage_statut_label">
                    <td class="gauche">Statut</td>
                    <td class="droite">
                      {{ declaration_data.peuplement_paturage_statut_label }}
                    </td>
                  </tr>
                  <tr v-if="declaration_data.peuplement_paturage_frequence_label">
                    <td class="gauche">Fréquence</td>
                    <td class="droite">
                      {{ declaration_data.peuplement_paturage_frequence_label }}
                    </td>
                  </tr>
                  <tr v-if="declaration_data.peuplement_paturage_saison_label">
                    <td class="gauche">Saison</td>
                    <td class="droite">
                      {{ declaration_data.peuplement_paturage_saison_label }}
                    </td>
                  </tr>
                </template>
              </tbody>

              <!-- --------------------------- DEGATS --------------------------- -->
              <tbody>
                <tr>
                  <th colspan="2" class="sous_titre">
                    Dégâts
                  </th>
                </tr>

                <tr v-for="(item_degat, index) in declaration_data.degats" :key="index">
                  <td class="gauche">{{ item_degat.degat_type_label }}</td>
                  <td class="droite">
                    <!-- si le type de degat n'est pas un degat sur cloture-->
                    <template v-if="item_degat.degat_type_code != 'P/C'">
                      
                      <template>
                        <div v-for="(item_degat_essence, index_essence) in item_degat.degat_essences" :key="index_essence">
                          <strong>
                            {{item_degat_essence.degat_essence_label}}
                          </strong>
                          <!-- si le degat n'est pas un defaut de regeneration, on affiche les détails -->
                          <span v-if="item_degat.degat_type_code != 'ABS'">
                            :
                            {{item_degat_essence.degat_etendue_label}},
                            {{item_degat_essence.degat_gravite_label}},
                            {{item_degat_essence.degat_anteriorite_label}}
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


                <tr v-if="declaration_data.precision_localisation">
                  <td class="gauche">Précisions sur la localisation</td>
                  <td class="droite">{{declaration_data.precision_localisation || "Non renseigné"}}</td>
                </tr>
              </tbody>

              <!-- --------------------------- COMMENTAIRES --------------------------- -->
              <tbody v-if="declaration_data.commentaire">
                <tr>
                  <th colspan="2" class="sous_titre">
                    Commentaires
                  </th>
                </tr>
                <tr>
                  <!-- <td class="gauche"></td> -->
                  <td class="droite" colspan="2" style="padding: 10px;">
                    {{declaration_data.commentaire}}
                  </td>
                </tr>
              </tbody>

            </v-simple-table>
        
          </div>
        </template>

        </div>
      </div>
      <div class="html2pdf__page-break"></div>

      <div style="margin-top: 3em;">
        <div v-for="type in mapList">
          <div v-if="configMaps[type]" :key="type" >
            <div small>{{ configMaps[type].title }}</div>
            <base-map
              :mapId="`map_${type}`"
              :config="configMaps[type]"
              height="315px"
            ></base-map>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script>

import baseMap from "@/components/map/base-map";
// import { exportPDF } from "@/modules/export";
import { apiRequest } from "@/core/js/data/api";
import "./declaration.css";
import html2pdf from "html2pdf.js";
import html2canvas from "html2canvas";

const styles = {
  foret: {
    color: "purple",
    fillColor: "purple",
    weight: 2,
    opacity: 1,
    fillOpacity: 0.5
  },
  parcelles: {
    color: "black",
    fillColor: "green",
    weight: 2,
    opacity: 1,
    fillOpacity: 0.5
  }
};

export default {
  name: "voir_declaration",
  data: () => ({
    pdfProcessing: false,
    declaration_data: null,
    b_init: false,
    mapList: ["secteur", "foret", "parcelles"]
  }),
  components: { 
    // resumeDeclaration,
    baseMap
   },
  methods: {

    exportDeclaration() {
      this.pdfProcessing = true;
      this.$nextTick(() => {
        // Attendre que toutes les cartes soient entièrement chargées
        setTimeout(() => {
          const element = document.getElementById("declaration");
          
          // Masquer les éléments avec la classe ignorepdf
          const elementsToHide = element.querySelectorAll('.ignorepdf');
          elementsToHide.forEach(el => el.style.display = 'none');
          
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
              backgroundColor: '#ffffff'
            },
            jsPDF: { 
              unit: 'mm', 
              format: 'a4', 
              orientation: 'portrait',
              compress: true
            },
            pagebreak: { mode: ['avoid-all', 'css', 'legacy'] }
          };
          
          html2pdf().set(opt).from(element).save().then(() => {
            // Remettre les éléments cachés
            elementsToHide.forEach(el => el.style.display = '');
            this.pdfProcessing = false;
          }).catch((error) => {
            console.error('Erreur lors de la génération du PDF:', error);
            // Remettre les éléments cachés même en cas d'erreur
            elementsToHide.forEach(el => el.style.display = '');
            this.pdfProcessing = false;
          });
        }, 2000); // Délai plus long pour s'assurer que les cartes sont chargées
      });
    },


    configMap(type) {
      if (!this.declaration_data) {
        return;
      }
      const markers = [
        {
          coords: this.declaration_data.centroid,
          type: "marker",
          style: {
            color: "blue",
            icon: "map-marker"
          }
        }
      ];
      const markerLegendGroups = [
        {
          legends: [
            {
              icon: "map-marker",
              text: "Localisation des alertes",
              color: "#3689CE"
            }
          ]
        }
      ];
      const titles = {
        secteur: "Localisation de l'alerte dans le périmètre de l'observatoire",
        foret: "Localisation des parcelles",
        parcelles: "Carte des parcelles"
      };
      const layerList = {
        secteur: {},
        foret: {
          url: `api/ref_geo/areas_from_type/l?id_area=${this.declaration_data.areas_foret.join(
            "&id_area="
          )}`,
          legend: "Forêt concernée par l'alerte",
          style: styles.foret,
          pane: "PANE_LAYER_1"
        },
        parcelles: {
          url: `api/ref_geo/areas_from_type/l?id_area=${this.declaration_data.areas_localisation.join(
            "&id_area="
          )}`,

          legend: "Parcelle(s) concernée(s) par l'alerte",
          style: styles.parcelles,
          pane: "PANE_LAYER_2"
        }
      };

      layerList[type] = {
        ...layerList[type],
        tooltip: {
          permanent: true,
          className: "tooltip-label",
          label: "label"
        },
        zoom: true
      };
      if (type != "") {
        delete layerList.secteur;
      }
      return { layerList, title: titles[type], markers, markerLegendGroups };
    }
  },
  computed: {
    id() {
      return this.$route.params.id;
    },
    configMaps() {
      const configMaps = {};
      for (const type of this.mapList) {
        configMaps[type] = this.configMap(type);
      }
      return configMaps;
    }
  },
  async created() {
    // this.initDeclaration();
    this.id_declaration = this.$route.params.id;
    this.nomenclature = await apiRequest("GET", `api/oeasc/nomenclatures`);
    this.declaration_data =  await apiRequest("GET", `api/declaration/declaration/${this.id_declaration}`);
    this.bInit = true;
    
  },
  async mounted(){

  },
  watch: {
  }
};
</script>
<style scoped></style>
