<!-- Tableau récapitulatif d'une déclaration déjà enregistrée (données de l'API voir_declaration :
valeurs déjà mises en libellés). Extrait de voir_declaration.vue ; à ne pas confondre avec
resume_declaration.vue, qui affiche une déclaration en cours de saisie. -->
<template>
    <div>
      <v-table
        density="compact"
        :class="{ 'declaration-table-compact': compact }"
        style="margin-bottom: 16px; width: 100%; max-width: 100%; margin: auto"
      >
        <thead v-if="!compact">
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

<script>
export default {
  name: 'VoirDeclarationTable',
  props: {
    declaration_data: { type: Object, required: true },
    // mode dense (export PDF) : lignes plus basses, sans l'en-tête « Résumé de la déclaration »
    compact: { type: Boolean, default: false },
  },
};
</script>

<style>
/* styles partagés avec resume_declaration.vue (qui les déclare aussi) : ne pas dépendre de
   l'import de ce composant pour que le tableau soit correctement mis en forme */
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

/* mode dense pour l'export PDF : le tableau doit tenir sur une page A4 avec son titre */
.declaration-table-compact .v-table__wrapper > table > tbody > tr > td,
.declaration-table-compact .v-table__wrapper > table > tbody > tr > th {
  height: auto !important;
  padding: 0 6px !important;
  line-height: 1.1 !important;
}
</style>
