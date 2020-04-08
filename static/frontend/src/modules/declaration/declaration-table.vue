<template>
  <div>
    <table class="table">
      <tbody>
        <tr>
          <th colspan="3">Informations</th>
        </tr>
        <tr>
          <th>Partage d'information</th>
          <td v-if="declaration.b_autorisation">
            Autorisé
          </td>
          <td v-else>
            Non autorisé
          </td>
        </tr>
        <tr>
          <th>Date</th>
          <td>{{ declaration.declaration_date }}</td>
        </tr>
        <tr>
          <th>Accessibilité</th>
          <td>{{ declaration.peuplement_acces_label }}</td>
        </tr>
        <tr>
          <th>Espèces présentes</th>
          <td>{{ declaration.espece_label }}</td>
        </tr>
      </tbody>

      <tbody v-if="declaration.declarant">
        <tr>
          <th colspan="3">Déclarant</th>
        </tr>
        <tr>
          <th>NOM prénom</th>
          <td>{{ declaration.declarant }}</td>
        </tr>
        <tr>
          <th>Organisme</th>
          <td>{{ declaration.organisme }}</td>
        </tr>
      </tbody>

      <tbody>
        <tr>
          <th colspan="3">Forêt</th>
        </tr>
        <tr>
          <th>Nom</th>
          <td v-if="declaration.label_foret != ''">
            {{ declaration.label_foret }}
          </td>
          <td v-else>nom inconnu</td>
        </tr>
        <tr>
          <th>Statut</th>
          <td>{{ declaration.statut_public }}</td>
        </tr>
        <tr>
          <th>Documentée</th>
          <td v-if="declaration.b_document && declaration.b_statut_public">
            oui <i>(régime forestier)</i>
          </td>
          <td
            v-else-if="declaration.b_document && !declaration.b_statut_public"
          >
            oui <i>(document de gestion durable)</i>
          </td>
          <td v-else>
            non
          </td>
        </tr>
        <tr>
          <th>Type</th>
          <td>TODO!!</td>
        </tr>
      </tbody>

      <tbody>
        <tr>
          <th colspan="3">Peuplement - <i>localisation</i></th>
        </tr>
        <tr>
          <th>Secteur</th>
          <td>{{ declaration.secteur }}</td>
        </tr>
        <tr>
          <th>Commune(s)</th>
          <td>{{ declaration.communes }}</td>
        </tr>

        <tr>
          <th>Parcelle(s)</th>
          <td>{{ declaration.parcelles }}</td>
        </tr>
      </tbody>

      <tbody>
        <tr>
          <th colspan="3">Peuplement - <i>essence(s)</i></th>
        </tr>
        <tr>
          <th>Principale</th>
          <td>{{ declaration.peuplement_ess_1_label }}</td>
        </tr>
        <tr>
          <th>Secondaire(s)</th>
          <td>{{ declaration.peuplement_ess_2_label }}</td>
        </tr>
        <tr>
          <th>Complémentaire(s)</th>
          <td>{{ declaration.peuplement_ess_3_label }}</td>
        </tr>
      </tbody>

      <tbody>
        <tr>
          <th colspan="3">Peuplement - <i>description</i></th>
        </tr>
        <tr>
          <th>Superficie (ha)</th>
          <td>{{ declaration.peuplement_surface || "Non renseignée" }}</td>
        </tr>
        <tr>
          <th>Origine</th>
          <td>{{ declaration.peuplement_origine_label }}</td>
        </tr>
        <tr>
          <th>Type</th>
          <td>{{ declaration.peuplement_type_label }}</td>
        </tr>
        <tr>
          <th>Maturité</th>
          <td>{{ declaration.peuplement_maturite_label }}</td>
        </tr>
      </tbody>

      <tbody>
        <tr>
          <th colspan="3">Peuplement - <i>protection</i></th>
        </tr>
        <tr>
          <th>Existence</th>
          <td v-if="declaration.b_peuplement_protection_existence">
            oui
          </td>
          <td v-else>non</td>
        </tr>
        <template v-if="declaration.b_peuplement_protection_existence">
          <tr>
            <th>Type</th>
            <td>
              {{ declaration.peuplement_protection_type_label }}
            </td>
          </tr>
        </template>
      </tbody>

      <tbody>
        <tr>
          <th colspan="3">Peuplement - <i>pâturage</i></th>
        </tr>
        <tr>
          <th>Présence</th>
          <td v-if="declaration.b_peuplement_paturage_presence">
            oui
          </td>
          <td v-else>non</td>
        </tr>
        <template v-if="declaration.b_peuplement_paturage_presence">
          <tr>
            <th>Type</th>
            <td>{{ declaration_table.peuplement_paturage_type_label }}</td>
          </tr>

          <tr>
            <th>Statut</th>
            <td>{{ declaration_table.peuplement_paturage_statut_label }}</td>
          </tr>

          <tr>
            <th>Fréquence</th>
            <td>{{ declaration_table.peuplement_paturage_frequence_label }}</td>
          </tr>

          <tr>
            <th>Fréquence</th>
            <td>{{ declaration_table.peuplement_paturage_frequence_label }}</td>
          </tr>

          <tr>
            <th>Saison</th>
            <td>{{ declaration_table.peuplement_paturage_saison_label }}</td>
          </tr>
        </template>
      </tbody>

      <tbody>
        <tr>
          <th colspan="3">Dégâts</th>
        </tr>
        <template v-for="(degat, indexDegat) in declaration.degats">
          <template v-if="degat.degat_essences">
            <tr
              v-for="(degatEssence, indexDegatEssence) in degat.degat_essences"
              :key="degatEssence.id_degat_essence"
            >
              <th
                v-if="indexDegatEssence == 0"
                :rowspan="degat.degat_essences.length"
              >
                {{ degat.degat_type_label }}
              </th>
              <td>
                {{ degatEssence.degat_essence_label }}
                <template v-if="degat.degat_type_mnemo != 'ABS'">
                  :
                  {{ degatEssence.degat_etendue_label }},
                  {{ degatEssence.degat_gravite_label }},
                  {{ degatEssence.degat_anteriorite_label }}
                </template>
              </td>
            </tr>
          </template>
          <template v-else>
            <tr :key="indexDegat">
              <th>{{ degat.degat_type_label }}</th>
              <td></td>
            </tr>
          </template>
        </template>
        <tr>
          <th>Précisions sur la localisation</th>
          <td>{{ declaration.precision_localisation }}</td>
        </tr>
      </tbody>

    <tbody>
      <tr>
        <th colspan="3">Commentaires</th>
      </tr>
      <tr>
        <th></th>
        <td>
          {{ declaration.commentaire }}
        </td>
      </tr>
      
    </tbody>


    </table>
  </div>
</template>

<script>
export default {
  name: "declarationTable",
  props: ["declaration"]
};
</script>
