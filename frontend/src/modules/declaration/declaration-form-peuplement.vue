<!-- Section « Informations sur le peuplement » du formulaire de déclaration (essences, origine,
type, maturité, protection, pâturage, accessibilité, espèces présentes). Extraite de
modifier-declaration.vue. Comme degats_declaration_form.vue, elle modifie directement les champs de
l'objet `declaration_data` fourni par le parent (v-model sur ses propriétés). -->
<template>
    <div style="margin-top: 30px">
      <h3>Informations sur le peuplement</h3>

      <div
        style="
          margin-top: 10px;
          border: 1px solid #ccc;
          padding: 20px;
          border-radius: 5px;
        "
      >
        <h4>
          Essences
          <help style="margin-left: 2em">
            <helpContent helpID="group_form_essences"></helpContent>
          </help>
        </h4>

        <!-- -------- Essences principales: liste select, un seul choix possible -------- -->
        <v-select
          v-model="declaration_data.id_nomenclature_peuplement_essence_principale"
          :items="nomenclature.OEASC_PEUPLEMENT_ESSENCE.values"
          title="Sélectionnez l'essence principale"
          item-value="id_nomenclature"
          item-title="label_fr"
          label="Essence principale"
          :rules="[rules.requiredListSimple]"
          solo
          place-holder="Sélectionnez l'essence principale"
        ></v-select>

        <!-- -------- Essences secondaire: liste select, plusieurs choix possibles -------- -->
        <v-select
          v-model="declaration_data.nomenclatures_peuplement_essence_secondaire"
          :items="nomenclature.OEASC_PEUPLEMENT_ESSENCE.values"
          title="Sélectionnez l'essence secondaire (plusieurs possibles)"
          item-value="id_nomenclature"
          item-title="label_fr"
          label="Essence secondaire (plusieurs possibles)"
          multiple
        ></v-select>

        <!-- -------- Essences complémentaires: liste select, plusieurs choix possibles -------- -->
        <v-select
          v-model="declaration_data.nomenclatures_peuplement_essence_complementaire"
          :items="nomenclature.OEASC_PEUPLEMENT_ESSENCE.values"
          title="Sélectionnez l'essence complémentaire (plusieurs possibles)"
          item-value="id_nomenclature"
          item-title="label_fr"
          label="Essence complementaire (plusieurs possibles)"
          multiple
        ></v-select>

        <!-- --------------- Superficie, uniquement un float    -------------- -->
        <h4>Superficie</h4>
        <v-text-field
          v-model="declaration_data.peuplement_surface"
          :rules="[rules.number]"
          label="Superficie du peuplement (en ha)"
        ></v-text-field>

        <div><h4>Origine et structure</h4></div>
        <div
          style="
            display: flex;
            flex-direction: row;
            padding-left: 20px;
            margin-top: 10px;
            width: 100%;
          "
        >
          <!-- ---- Origine des arbres: checkbox choix multiples (Rejet de souche, Régéneration naturelle, Plantation) ---- -->
          <div style="display: flex; flex-direction: column; width: 30%">
            <h5>
              Origine des arbres / plants / semis touchés
              <br />
              par les dégâts de grand gibier
            </h5>
            <v-checkbox
              v-for="item in nomenclature.OEASC_PEUPLEMENT_ORIGINE2.values"
              :key="item.id_nomenclature"
              :label="item.label_fr"
              :value="item.id_nomenclature"
              v-model="declaration_data.nomenclatures_peuplement_origine2"
              :rules="[rules.required]"
              hide-details
              dense
              style="margin-bottom: 0"
              :error="
                Array.isArray(declaration_data.nomenclatures_peuplement_origine2) &&
                declaration_data.nomenclatures_peuplement_origine2.length === 0 &&
                formInvalid
              "
            ></v-checkbox>
            <div
              v-if="
                Array.isArray(declaration_data.nomenclatures_peuplement_origine2) &&
                declaration_data.nomenclatures_peuplement_origine2.length === 0 &&
                formInvalid
              "
              style="color: red; font-size: 0.9em"
            >
              Veuillez cocher au moins une origine.
            </div>
          </div>

          <!-- ---- Type de peuplement: radio (taillis, futaie, futaie irrégulière etc) ---- -->
          <div
            style="display: flex; flex-direction: column; margin-left: 20px; width: 30%"
          >
            <h5>
              Type de peuplement
              <help style="margin-left: 2em">
                <helpContent helpID="form_type_peuplement"></helpContent>
              </help>
            </h5>
            <div>
              <v-radio-group
                v-model="declaration_data.id_nomenclature_peuplement_type"
                :rules="[rules.required]"
              >
                <div
                  v-for="item in nomenclature.OEASC_PEUPLEMENT_TYPE.values"
                  :key="item.id_nomenclature"
                  style="display: flex; align-items: center"
                >
                  <v-radio
                    inline
                    :label="item.label_fr"
                    :value="item.id_nomenclature"
                  ></v-radio>
                  <help
                    v-if="item.id_nomenclature === 525"
                    style="margin-left: 2em"
                  >
                    <helpContent helpID="form_futaie_irreguliere"></helpContent>
                  </help>
                  <help
                    v-if="item.id_nomenclature === 526"
                    style="margin-left: 2em"
                  >
                    <helpContent helpID="form_taillis"></helpContent>
                  </help>
                  <help
                    v-if="item.id_nomenclature === 524"
                    style="margin-left: 2em"
                  >
                    <helpContent helpID="form_futaie_reguliere"></helpContent>
                  </help>
                  <help
                    v-if="item.id_nomenclature === 527"
                    style="margin-left: 2em"
                  >
                    <helpContent helpID="form_futaie_melangee"></helpContent>
                  </help>
                </div>
              </v-radio-group>
            </div>
          </div>

          <!-- ---- Maturité du peuplement: checkbox choix multiples (diametre 20cm, hauteur >2m etc) ---- -->
          <!-- s'affiche uniquement si le type de peuplement n'est pas "futaie irrégulière" (id 525) -->
          <div
            v-if="declaration_data.id_nomenclature_peuplement_type != 525"
            style="display: flex; flex-direction: column; margin-left: 20px; width: 30%"
          >
            <h5>Maturité du peuplement</h5>
            <div>
              <v-checkbox
                v-for="item in nomenclature.OEASC_PEUPLEMENT_MATURITE.values"
                :key="item.id_nomenclature"
                :label="item.label_fr"
                :value="item.id_nomenclature"
                v-model="declaration_data.nomenclatures_peuplement_maturite"
                :rules="[rules.required]"
                hide-details
                dense
              ></v-checkbox>
            </div>
          </div>
        </div>
        <!-- fin de la ligne contenant les 3 formulaires "origine et structure"-->

        <!-- ---- protection: bool radio oui/non ---- -->
        <div>
          <h4>Protection</h4>
          <div
            style="
              display: flex;
              flex-direction: row;
              width: 100%;
              align-items: center;
              padding-left: 20px;
            "
          >
            <p>Existence de dispositifs de protection contre le grand gibier?</p>
            <v-radio-group
              v-model="declaration_data.b_peuplement_protection_existence"
              :rules="[rules.required]"
              inline
              density="compact"
              hide-details="auto"
              style="margin-left: 20px"
            >
              <v-radio
                inline
                label="Oui"
                :value="true"
              ></v-radio>
              <v-radio
                inline
                label="Non"
                :value="false"
              ></v-radio>
            </v-radio-group>
          </div>
          <div
            v-if="declaration_data.b_peuplement_protection_existence"
            style="padding-left: 40px; margin-top: -10px; margin-bottom: 20px"
          >
            <div
              v-for="item in nomenclature.OEASC_PEUPLEMENT_PROTECTION_TYPE.values"
              :key="item.id_nomenclature"
            >
              <v-checkbox
                v-model="declaration_data.nomenclatures_peuplement_protection_type"
                :label="item.label_fr"
                :value="item.id_nomenclature"
                hide-details
                dense
              ></v-checkbox>
            </div>
          </div>
        </div>

        <!-- ---- paturage: domestisque  oui/non---- -->
        <div>
          <h4>
            Paturage domestique
            <help style="margin-left: 2em">
              <helpContent helpID="form_paturage_domestique"></helpContent>
            </help>
          </h4>
          <div
            style="
              display: flex;
              flex-direction: row;
              width: 100%;
              align-items: center;
              padding-left: 20px;
            "
          >
            <p>Présence de pâturage domestique ?</p>
            <v-radio-group
              v-model="declaration_data.b_peuplement_paturage_presence"
              :rules="[rules.required]"
              inline
              density="compact"
              hide-details="auto"
              style="margin-left: 20px"
            >
              <v-radio
                inline
                label="Oui"
                :value="true"
              ></v-radio>
              <v-radio
                inline
                label="Non"
                :value="false"
              ></v-radio>
            </v-radio-group>
          </div>

          <div
            v-if="declaration_data.b_peuplement_paturage_presence == true"
            style="padding-left: 20px"
          >
            <div style="display: flex; flex-direction: row; flex-wrap: wrap; gap: 20px">
              <div style="flex: 1 1 240px; min-width: 240px">
                <v-select
                  v-model="declaration_data.nomenclatures_peuplement_paturage_type"
                  :items="nomenclature.OEASC_PEUPLEMENT_PATURAGE_TYPE.values"
                  title="Sélectionnez le type de pâturage, plusieurs possibles"
                  item-value="id_nomenclature"
                  item-title="label_fr"
                  label="Type de pâturage, plusieurs possibles"
                  multiple
                ></v-select>
              </div>
              <div style="flex: 1 1 240px; min-width: 240px">
                <v-select
                  v-model="declaration_data.id_nomenclature_peuplement_paturage_statut"
                  :items="nomenclature.OEASC_PEUPLEMENT_PATURAGE_STATUT.values"
                  title="Sélectionnez le statut du pâturage"
                  item-value="id_nomenclature"
                  item-title="label_fr"
                  label="Statut du pâturage"
                ></v-select>
              </div>
              <div style="flex: 1 1 240px; min-width: 240px">
                <v-select
                  v-model="
                    declaration_data.id_nomenclature_peuplement_paturage_frequence
                  "
                  :items="nomenclature.OEASC_PEUPLEMENT_PATURAGE_FREQUENCE.values"
                  title="Sélectionnez la fréquence du pâturage"
                  item-value="id_nomenclature"
                  item-title="label_fr"
                  label="Fréquence du pâturage"
                ></v-select>
              </div>
              <div
                v-if="
                  declaration_data.id_nomenclature_peuplement_paturage_frequence == 547
                "
                style="flex: 1 1 240px; min-width: 240px"
              >
                <v-select
                  v-model="declaration_data.nomenclatures_peuplement_paturage_saison"
                  :items="nomenclature.OEASC_PEUPLEMENT_PATURAGE_SAISON.values"
                  title="Sélectionnez la saison du pâturage, plusieurs possibles"
                  item-value="id_nomenclature"
                  item-title="label_fr"
                  label="Saison du pâturage, plusieurs possibles"
                  multiple
                ></v-select>
              </div>
            </div>
          </div>
        </div>

        <!-- ---- Accessibilité: Aisée/uniquement 4x4/ Uniquement à pied ---- -->
        <div>
          <h4>
            Accessibilité du peuplement
            <help style="margin-left: 2em">
              <helpContent helpID="form_accessiblite_peuplement"></helpContent>
            </help>
          </h4>
          <!-- 3 choix : aisée, uniquement 4x4 ou uniquement à pied -->
          <div style="width: 100%; padding-left: 20px">
            <v-radio-group
              v-model="declaration_data.id_nomenclature_peuplement_acces"
              :rules="[rules.required]"
              inline
              density="compact"
              hide-details="auto"
            >
              <v-radio
                v-for="(item, index) in nomenclature.OEASC_PEUPLEMENT_ACCES.values"
                :key="index"
                inline
                :label="item.label_fr"
                :value="item.id_nomenclature"
              ></v-radio>
            </v-radio-group>
          </div>
        </div>

        <!-- ---- Espèces présentes: liste à choix multiples (cerfs, chamois, etc)---- -->
        <div>
          <h4>Espèces présentes</h4>
          <div style="width: 100%; padding-left: 20px">
            <h5>
              Espèces de grand gibier dont la présence est avérée (observations directes
              ou indices de présence)
              <span class="required">*</span>
            </h5>
            <v-select
              v-model="declaration_data.nomenclatures_peuplement_espece"
              :items="nomenclature.OEASC_PEUPLEMENT_ESPECE.values"
              title="Sélectionnez les espèces présentes (plusieurs possibles)"
              item-value="id_nomenclature"
              item-title="label_fr"
              :rules="[rules.requiredListMultiple]"
              label="Espèces présentes (plusieurs possibles)"
              multiple
            ></v-select>
          </div>
        </div>
      </div>
    </div>
</template>

<script>
import help from '@/components/form/help_static.vue';
import helpContent from '@/modules/declaration/help-content.vue';
import { formFunctions } from '@/components/form/functions/form.js';

export default {
  name: 'DeclarationFormPeuplement',
  components: { help, helpContent },
  props: {
    declaration_data: { type: Object, required: true },
    // nomenclatures (api/oeasc/nomenclatures)
    nomenclature: { type: Object, required: true },
    // vrai quand le v-form parent a été validé et est invalide : affiche les erreurs des cases à cocher
    formInvalid: { type: Boolean, default: false },
  },
  data: () => ({
    rules: formFunctions.rules,
  }),
};
</script>
