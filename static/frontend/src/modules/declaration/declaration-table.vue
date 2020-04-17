<template>
  <div v-if='bInit'>
    <table class="table-declaration">
      <tbody>
        <tr>
          <th colspan="3">Informations</th>
        </tr>
        <tr v-if="this.$store.getters.droitMax >= 5">
          <th>Validité</th>
          <td>{{ declarationDisplay.valide }}</td>
        </tr>
        <tr>
          <th>Partage d'information</th>
          <td v-if="declarationDisplay.b_autorisation">
            Autorisé
          </td>
          <td v-else>
            Non autorisé
          </td>
        </tr>
        <tr>
          <th>Date</th>
          <td>{{ declarationDisplay.declaration_date }}</td>
        </tr>
        <tr>
          <th>Accessibilité</th>
          <td>{{ declarationDisplay.peuplement_acces_label }}</td>
        </tr>
        <tr>
          <th>Espèces présentes</th>
          <td>{{ declarationDisplay.espece_label }}</td>
        </tr>
      </tbody>

      <tbody v-if="declarationDisplay.declarant">
        <tr>
          <th colspan="3">Déclarant</th>
        </tr>
        <tr>
          <th>NOM prénom</th>
          <td>{{ declarationDisplay.declarant }}</td>
        </tr>
        <tr>
          <th>Organisme</th>
          <td>{{ declarationDisplay.organisme }}</td>
        </tr>
      </tbody>

      <tbody>
        <tr>
          <th colspan="3">Forêt</th>
        </tr>
        <tr>
          <th>Nom</th>
          <td v-if="declarationDisplay.label_foret != ''">
            {{ declarationDisplay.label_foret }}
          </td>
          <td v-else>nom inconnu</td>
        </tr>
        <tr>
          <th>Statut</th>
          <td>{{ declarationDisplay.statut_public }}</td>
        </tr>
        <tr>
          <th>Documentée</th>
          <td
            v-if="
              declarationDisplay.b_document &&
                declarationDisplay.b_statut_public
            "
          >
            oui <i>(régime forestier)</i>
          </td>
          <td
            v-else-if="
              declarationDisplay.b_document &&
                !declarationDisplay.b_statut_public
            "
          >
            oui <i>(document de gestion durable)</i>
          </td>
          <td v-else>
            non
          </td>
        </tr>
        <tr>
          <th>Type</th>
          <td>{{ foretType(declarationDisplay.foret_type_label) }}</td>
        </tr>
      </tbody>

      <tbody>
        <tr>
          <th colspan="3">Peuplement - <i>localisation</i></th>
        </tr>
        <tr v-if="declarationDisplay.secteur">
          <th>Secteur</th>
          <td>{{ declarationDisplay.secteur }}</td>
        </tr>
        <tr v-if="declarationDisplay.communes">
          <th>Commune(s)</th>
          <td>{{ declarationDisplay.communes }}</td>
        </tr>

        <tr>
          <th>Parcelle(s)</th>
          <td>{{ declarationDisplay.parcelles }}</td>
        </tr>
      </tbody>

      <tbody>
        <tr>
          <th colspan="3">Peuplement - <i>essence(s)</i></th>
        </tr>
        <tr>
          <th>Principale</th>
          <td>{{ declarationDisplay.peuplement_ess_1_label }}</td>
        </tr>
        <tr v-if="declarationDisplay.peuplement_ess_2_label">
          <th>Secondaire(s)</th>
          <td>{{ declarationDisplay.peuplement_ess_2_label }}</td>
        </tr>
        <tr v-if="declarationDisplay.peuplement_ess_3_label">
          <th>Complémentaire(s)</th>
          <td>{{ declarationDisplay.peuplement_ess_3_label }}</td>
        </tr>
      </tbody>

      <tbody>
        <tr>
          <th colspan="3">Peuplement - <i>description</i></th>
        </tr>
        <tr>
          <th>Superficie (ha)</th>
          <td>
            {{ declarationDisplay.peuplement_surface || "Non renseignée" }}
          </td>
        </tr>
        <tr>
          <th>Origine</th>
          <td>{{ declarationDisplay.peuplement_origine_label }}</td>
        </tr>
        <tr>
          <th>Origine 2</th>
          <td>{{ declarationDisplay.peuplement_origine2_label }}</td>
        </tr>
        <tr>
          <th>Type</th>
          <td>{{ declarationDisplay.peuplement_type_label }}</td>
        </tr>

        <tr v-if="declarationDisplay.peuplement_maturite_label">
          <th>Maturité</th>
          <td>{{ declarationDisplay.peuplement_maturite_label }}</td>
        </tr>
      </tbody>

      <tbody>
        <tr>
          <th colspan="3">Peuplement - <i>protection</i></th>
        </tr>
        <tr>
          <th>Existence</th>
          <td v-if="declarationDisplay.b_peuplement_protection_existence">
            oui
          </td>
          <td v-else>non</td>
        </tr>
        <template v-if="declarationDisplay.b_peuplement_protection_existence">
          <tr>
            <th>Type</th>
            <td>
              {{ declarationDisplay.peuplement_protection_type_label }}
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
          <td v-if="declarationDisplay.b_peuplement_paturage_presence">
            oui
          </td>
          <td v-else>non</td>
        </tr>
        <template v-if="declarationDisplay.b_peuplement_paturage_presence">
          <tr>
            <th>Type</th>
            <td>{{ declarationDisplay.peuplement_paturage_type_label }}</td>
          </tr>

          <tr>
            <th>Statut</th>
            <td>{{ declarationDisplay.peuplement_paturage_statut_label }}</td>
          </tr>

          <tr>
            <th>Fréquence</th>
            <td>{{ declarationDisplay.peuplement_paturage_frequence_label }}</td>
          </tr>

          <tr v-if="declarationDisplay.peuplement_paturage_saison_label">
            <th>Saison</th>
            <td>{{ declarationDisplay.peuplement_paturage_saison_label }}</td>
          </tr>
        </template>
      </tbody>

      <tbody>
        <tr>
          <th colspan="3">Dégâts</th>
        </tr>
        <template v-for="(degat, indexDegat) in declarationDisplay.degats">
          <template v-if="degat.degat_essences && degat.degat_essences.length">
            <tr
              v-for="(degatEssence, indexDegatEssence) in degat.degat_essences"
              :key="degatEssence.id_degat_essence"
            >
              <th
                v-if="indexDegatEssence == 0"
                :rowspan="degat.degat_essences.length"
              >
                {{ degat.degat_type_label }}
                {{ degat.degat_type_mnemo }}
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
        <tr v-if="declarationDisplay.precision_localisation">
          <th>Précisions sur la localisation</th>
          <td>{{ declarationDisplay.precision_localisation }}</td>
        </tr>
      </tbody>

      <tbody v-if="declarationDisplay.commentaire">
        <tr>
          <th colspan="3">Commentaires</th>
        </tr>
        <tr>
          <th></th>
          <td>
            {{ declarationDisplay.commentaire }}
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import { rawToDisplay, getDeclarationData } from "./declaration.js";
export default {
  name: "declarationTable",
  props: ["declaration", 'type'],
  data: () => ({
    bInit: false
  }),
  methods: {
    foretType(s) {
      const foretTypes = {
        État: "Domaniale",
        "Centre hospitalier": "Autre forêt publique",
        "EP PNC": "Autre forêt publique",
        Commune: "Communale",
        "Groupement forestier": "Groupement forestier",
        "Section / hameau": "Sectionale",
        Privé: "Privée"
      };
      return foretTypes[s];
    }
  },
  computed: {
    declarationDisplay() {
      if (this.type === "raw") {
        return rawToDisplay(this);
        }
        return this.declaration;
    }
  },
  mounted() {
    if (this.type ==='raw') {
      getDeclarationData(this).then(()=>{
        this.bInit = true
      })
    } else {
      this.bInit = true;
    }
  }
};
</script>
