<!--#############################################################################
// Affichage d'un tableau récapitulatif d'une déclaration. Est utilisé à la fin de la
// creation d'une déclaration et sera à mettre dans la nouvelle page de visualisation
// d'une déclaration.
##############################################################################-->

<template v-if="bInit == true">
  <div>
    <v-table
      density="compact"
      style="margin-bottom: 16px; width: 70%; max-width: 100%; margin: auto"
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
        <tr v-if="this.$store.getters.droitMax >= 5">
          <td class="gauche">Validité</td>
          <td class="droite">{{ declaration_data.b_valid ? 'Validé' : 'Non validé' }}</td>
        </tr>

        <tr>
          <td class="gauche">Partage d'information</td>
          <td class="droite">
            {{ declaration_data.b_autorisation_transmission ? 'Autorisé' : 'Non autorisé' }}
          </td>
        </tr>

        <tr>
          <td class="gauche">Date</td>
          <td class="droite">
            {{ new Date(declaration_data.meta_create_date).toLocaleDateString('fr-FR') }}
          </td>
        </tr>
      </tbody>

      <!-- ------------------------------- DECLARANT -------------------------------- -->
      <tbody v-if="declaration_data.id_declarant">
        <tr>
          <th
            colspan="2"
            class="sous_titre"
          >
            Déclarant
          </th>
        </tr>

        <tr v-if="declaration_data.nom_proprietaire">
          <td class="gauche">Nom du propriétaire</td>
          <td class="droite">{{ declaration_data.nom_proprietaire }}</td>
        </tr>
        <tr v-if="declaration_data.org_mnemo">
          <td class="gauche">Organisme</td>
          <td class="droite">{{ declaration_data.organisme }}</td>
          <!-- <td class="droite">{{declaration_data.org_mnemo || "Non renseigné"}}</td> -->
        </tr>
        <tr v-if="declaration_data.email">
          <td class="gauche">Email</td>
          <td class="droite">{{ declaration_data.email || 'Non renseigné' }}</td>
        </tr>
        <tr v-if="declaration_data.telephone">
          <td class="gauche">Téléphone</td>
          <td class="droite">{{ declaration_data.telephone || 'Non renseigné' }}</td>
        </tr>
        <!-- <tr v-if="declaration_data.adresse">
          <td class="gauche">Adresse</td>
          <td class="droite">{{declaration_data.adresse || "Non renseigné"}}</td>
        </tr>
        <tr v-if="declaration_data.s_code_postal">
          <td class="gauche">Code postal</td>
          <td class="droite">{{declaration_data.s_code_postal || "Non renseigné"}}</td>
        </tr>
        <tr v-if="declaration_data.s_commune_proprietaire">
          <td class="gauche">Commune</td>
          <td class="droite">{{declaration_data.s_commune_proprietaire || "Non renseigné"}}</td>
        </tr> -->
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

        <tr v-if="declaration_data.label_foret">
          <td class="gauche">Nom</td>
          <td class="droite">{{ declaration_data.label_foret || 'Non connu' }}</td>
        </tr>

        <tr>
          <td class="gauche">Statut</td>
          <td class="droite">
            {{ declaration_data.b_statut_public ? 'Public' : 'Privé' }}
          </td>
        </tr>

        <tr>
          <td class="gauche">Document de gestion durable</td>
          <td class="droite">
            {{ declaration_data.b_document ? 'Oui' : 'Non' }}
            <span v-if="declaration_data.b_document && declaration_data.b_statut_public">
              <i>(régime forestier)</i>
            </span>
            <span v-else-if="declaration_data.b_document && !declaration_data.b_statut_public">
              <i>(document de gestion durable)</i>
            </span>
          </td>
        </tr>

        <tr v-if="declaration_data.surface_renseignee">
          <td class="gauche">Superficie (ha)</td>
          <td class="droite">
            {{ declaration_data.surface_renseignee }}
          </td>
        </tr>

        <tr v-if="declaration_data.id_nomenclature_proprietaire_type">
          <td class="gauche">Type</td>
          <td class="droite">
            <!-- ici le type de foret affiché a été renommé par foretType, voir dans les script -->
            {{
              foretType(
                get_nomenclature_to_string(
                  'OEASC_PROPRIETAIRE_TYPE',
                  declaration_data.id_nomenclature_proprietaire_type
                )
              )
            }}
          </td>
        </tr>

        <tr
          v-if="
            declaration_data.nomenclatures_peuplement_espece &&
            declaration_data.nomenclatures_peuplement_espece.length > 0
          "
        >
          <td class="gauche">Espèces présentes</td>
          <td class="droite">
            {{
              get_nomenclature_to_string(
                'OEASC_PEUPLEMENT_ESPECE',
                declaration_data.nomenclatures_peuplement_espece
              )
            }}
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
        <tr v-if="areas_commune_computed.length > 0">
          <td class="gauche">Commune(s)</td>
          <td class="droite">
            <v-chip
              v-for="area_commune in areas_commune_computed"
              :key="area_commune.id_area"
              small
              class="ma-1"
            >
              {{ area_commune }}
            </v-chip>
          </td>
        </tr>
        <tr v-if="areas_section_computed.length > 0">
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
        </tr>

        <tr v-if="areas_cadastre_computed.length > 0">
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
        </tr>

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

        <tr v-if="areas_ug_computed.length > 0">
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
        </tr>

        <tr v-if="declaration_data.id_nomenclature_peuplement_acces">
          <td class="gauche">Accessibilité</td>
          <td class="droite">
            {{
              get_nomenclature_to_string(
                'OEASC_PEUPLEMENT_ACCES',
                declaration_data.id_nomenclature_peuplement_acces
              )
            }}
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
        <tr v-if="declaration_data.id_nomenclature_peuplement_essence_principale">
          <td class="gauche">Principale</td>
          <td class="droite">
            {{
              get_nomenclature_to_string(
                'OEASC_PEUPLEMENT_ESSENCE',
                declaration_data.id_nomenclature_peuplement_essence_principale
              )
            }}
          </td>
        </tr>
        <tr v-if="declaration_data.nomenclatures_peuplement_essence_secondaire.length > 0">
          <td class="gauche">Secondaire(s)</td>
          <td class="droite">
            {{
              get_nomenclature_to_string(
                'OEASC_PEUPLEMENT_ESSENCE',
                declaration_data.nomenclatures_peuplement_essence_secondaire
              )
            }}
          </td>
        </tr>
        <tr v-if="declaration_data.nomenclatures_peuplement_essence_complementaire.length > 0">
          <td class="gauche">Complémentaire(s)</td>
          <td class="droite">
            {{
              get_nomenclature_to_string(
                'OEASC_PEUPLEMENT_ESSENCE',
                declaration_data.nomenclatures_peuplement_essence_complementaire
              )
            }}
          </td>
        </tr>
        <tr v-if="declaration_data.peuplement_surface">
          <td class="gauche">Superficie du peuplement (ha)</td>
          <td class="droite">
            {{ declaration_data.peuplement_surface }}
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
        <tr v-if="declaration_data.id_nomenclature_peuplement_origine">
          <td class="gauche">Origine</td>
          <td class="droite">
            {{
              get_nomenclature_to_string(
                'OEASC_PEUPLEMENT_ORIGINE',
                declaration_data.id_nomenclature_peuplement_origine
              )
            }}
          </td>
        </tr>
        <tr v-if="declaration_data.nomenclatures_peuplement_origine2.length > 0">
          <td class="gauche">Origine des plants touchés</td>
          <td class="droite">
            {{
              get_nomenclature_to_string(
                'OEASC_PEUPLEMENT_ORIGINE2',
                declaration_data.nomenclatures_peuplement_origine2
              )
            }}
          </td>
        </tr>
        <tr v-if="declaration_data.id_nomenclature_peuplement_type">
          <td class="gauche">Type</td>
          <td class="droite">
            {{
              get_nomenclature_to_string(
                'OEASC_PEUPLEMENT_TYPE',
                declaration_data.id_nomenclature_peuplement_type
              )
            }}
          </td>
        </tr>
        <tr v-if="declaration_data.nomenclatures_peuplement_maturite.length > 0">
          <td class="gauche">Maturité</td>
          <td class="droite">
            {{
              get_nomenclature_to_string(
                'OEASC_PEUPLEMENT_MATURITE',
                declaration_data.nomenclatures_peuplement_maturite
              )
            }}
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
        <tr v-if="declaration_data.b_peuplement_protection_existence !== undefined">
          <td class="gauche">Existence</td>
          <td class="droite">
            {{ declaration_data.b_peuplement_protection_existence ? 'Oui' : 'Non' }}
          </td>
        </tr>
        <tr v-if="declaration_data.nomenclatures_peuplement_protection_type.length > 0">
          <td class="gauche">Type</td>
          <td class="droite">
            {{
              get_nomenclature_to_string(
                'OEASC_PEUPLEMENT_PROTECTION_TYPE',
                declaration_data.nomenclatures_peuplement_protection_type
              )
            }}
          </td>
        </tr>
      </tbody>

      <!-- --------------------------- PEUPLEMENT - PATURAGE --------------------------- -->
      <tbody>
        <tr>
          <th
            colspan="2"
            class="sous_titre"
          >
            Peuplement - pâturage
          </th>
        </tr>
        <tr v-if="declaration_data.b_peuplement_paturage_presence !== undefined">
          <td class="gauche">Présence</td>
          <td class="droite">
            {{ declaration_data.b_peuplement_paturage_presence ? 'Oui' : 'Non' }}
          </td>
        </tr>
        <!-- Si il y a présence de pâturage, on affiche les détails -->
        <template v-if="declaration_data.b_peuplement_paturage_presence == true">
          <tr
            v-if="
              declaration_data.nomenclatures_peuplement_paturage_type &&
              declaration_data.nomenclatures_peuplement_paturage_type.length > 0
            "
          >
            <td class="gauche">Type</td>
            <td class="droite">
              {{
                get_nomenclature_to_string(
                  'OEASC_PEUPLEMENT_PATURAGE_TYPE',
                  declaration_data.nomenclatures_peuplement_paturage_type
                )
              }}
            </td>
          </tr>
          <tr v-if="declaration_data.id_nomenclature_peuplement_paturage_statut">
            <td class="gauche">Statut</td>
            <td class="droite">
              {{
                get_nomenclature_to_string(
                  'OEASC_PEUPLEMENT_PATURAGE_STATUT',
                  declaration_data.id_nomenclature_peuplement_paturage_statut
                )
              }}
            </td>
          </tr>
          <tr v-if="declaration_data.id_nomenclature_peuplement_paturage_frequence">
            <td class="gauche">Fréquence</td>
            <td class="droite">
              {{
                get_nomenclature_to_string(
                  'OEASC_PEUPLEMENT_PATURAGE_FREQUENCE',
                  declaration_data.id_nomenclature_peuplement_paturage_frequence
                )
              }}
            </td>
          </tr>
          <tr
            v-if="
              declaration_data.nomenclatures_peuplement_paturage_saison &&
              declaration_data.nomenclatures_peuplement_paturage_saison.length > 0
            "
          >
            <td class="gauche">Saison</td>
            <td class="droite">
              {{
                get_nomenclature_to_string(
                  'OEASC_PEUPLEMENT_PATURAGE_SAISON',
                  declaration_data.nomenclatures_peuplement_paturage_saison
                )
              }}
            </td>
          </tr>
        </template>
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
          <td class="gauche">
            {{
              get_nomenclature_to_string('OEASC_DEGAT_TYPE', item_degat.id_nomenclature_degat_type)
            }}
          </td>
          <td class="droite">
            <!-- si le type de degat n'est pas un degat sur cloture-->
            <template v-if="item_degat.id_nomenclature_degat_type != 480">
              <template>
                <div
                  v-for="(item_degat_essence, index_essence) in item_degat.degat_essences"
                  :key="index_essence"
                >
                  <strong>
                    {{
                      get_nomenclature_to_string(
                        'OEASC_PEUPLEMENT_ESSENCE',
                        item_degat_essence.id_nomenclature_degat_essence
                      )
                    }}
                  </strong>
                  <!-- si le degat n'est pas un defaut de regeneration, on affiche les détails -->
                  <span v-if="item_degat.id_nomenclature_degat_type != 479">
                    :
                    {{
                      get_nomenclature_to_string(
                        'OEASC_DEGAT_ETENDUE',
                        item_degat_essence.id_nomenclature_degat_etendue
                      )
                    }},
                    {{
                      get_nomenclature_to_string(
                        'OEASC_DEGAT_GRAVITE',
                        item_degat_essence.id_nomenclature_degat_gravite
                      )
                    }},
                    {{
                      get_nomenclature_to_string(
                        'OEASC_DEGAT_ANTERIORITE',
                        item_degat_essence.id_nomenclature_degat_anteriorite
                      )
                    }}
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
          <td class="droite">{{ declaration_data.precision_localisation || 'Non renseigné' }}</td>
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

    <!-- ---------------------------------------------------------------- -->
  </div>
</template>

<script>
export default {
  name: 'resumeDeclaration',
  props: ['declaration_data', 'nomenclature'],
  data: () => ({
    bInit: false,
  }),
  methods: {
    /**
     * Affiche le ou les labels d'une nomenclature en fonction de son type et d'un id ou d'une liste d'id
     * @param type_nomenclature nom de la nomenclature (ex: "OEASC_PEUPLEMENT_ESSENCE", "OEASC_PEUPLEMENT_MATURITE", etc.)
     * @param id_nomenclature int ou liste de int representant les id de la nomenclature
     * @returns string
     */
    get_nomenclature_to_string(type_nomenclature, id_nomenclature) {
      // si id_nomenclature est un int on en fait un tableau
      if (typeof id_nomenclature === 'number') {
        id_nomenclature = [id_nomenclature];
      } else if (!Array.isArray(id_nomenclature)) {
        return 'Non renseigné';
      }
      let string_nomenclature = '';

      // parcours la liste des id fournis et on cherche leurs labels dans le tableau des nomenclatures
      for (const id of id_nomenclature) {
        const item = this.nomenclature[type_nomenclature].values.find(
          (n) => n.id_nomenclature === id
        );
        if (item) {
          string_nomenclature += item.label_fr + ', ';
        }
      }

      return string_nomenclature.length > 0
        ? string_nomenclature.slice(0, -2) // retrait de la virgule et de l'espace à la fin
        : 'Non renseigné';
    },

    /**
     * sert juste à remplacer les labels d'un type de foret par des labels plus explicites
     * @param s le label de la nomenclature du type de foret
     */
    foretType(s) {
      const foretTypes = {
        État: 'Domaniale',
        'Centre hospitalier': 'Autre forêt publique',
        'EP PNC': 'Autre forêt publique',
        Commune: 'Communale',
        'Groupement forestier': 'Groupement forestier',
        'Section / hameau': 'Sectionale',
        Privé: 'Privée',
      };
      return foretTypes[s];
    },
  },

  computed: {
    areas_cadastre_computed() {
      if (!this.declaration_data.areas_localisation_cadastre) {
        return [];
      }
      return this.declaration_data.areas_localisation_cadastre
        .map((area) => {
          const found = this.declaration_data.areas_localisation.find((a) => a.id_area === area);
          return found ? found.label : null;
        })
        .filter((label) => label !== null && label !== undefined);
    },
    areas_section_computed() {
      if (!this.declaration_data.areas_foret_sections) {
        return [];
      }
      return this.declaration_data.areas_foret_sections
        .map((area) => {
          const found = this.declaration_data.areas_localisation.find((a) => a.id_area === area);
          return found ? found.label : null;
        })
        .filter((label) => label !== null && label !== undefined);
    },
    areas_commune_computed() {
      if (!this.declaration_data.areas_foret_communes) {
        return [];
      }
      return this.declaration_data.areas_foret_communes
        .map((area) => {
          const found = this.declaration_data.areas_localisation.find((a) => a.id_area === area);
          return found ? found.label : undefined;
        })
        .filter((label) => label !== null && label !== undefined);
    },
    areas_ug_computed() {
      if (!this.declaration_data.areas_localisation_onf_ug) {
        return [];
      }
      return this.declaration_data.areas_localisation_onf_ug
        .map((area) => {
          const found = this.declaration_data.areas_localisation.find((a) => a.id_area === area);
          return found ? found.area_code : null;
        })
        .filter((area_code) => area_code !== null && area_code !== undefined);
    },
  },

  created() {},
  mounted() {
    if (this.declaration_data && this.nomenclature) {
      this.bInit = true;
    }
    console.log('areas_commune_computed', this.areas_commune_computed);
  },
};
</script>

<style>
.sous_titre {
  background-color: #e6e6e6;
  pointer-events: none;
}

.gauche {
  font-size: smaller !important;
  text-align: left;
  width: 30%;
  font-weight: bold;
}

.droite {
  font-size: smaller !important;
  text-align: left;
  width: 70%;
}
</style>
