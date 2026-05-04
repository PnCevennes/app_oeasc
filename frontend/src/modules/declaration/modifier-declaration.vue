<template>
  <div style="margin: 40px; width: 100%">
    <h1>{{ title }}</h1>

    <div>
      <div v-if="etape_affichage === 'AFFICHAGE_FORM'">
        <div v-if="initialized">
          <p>
            Besoin d'aide
            <help style="margin-left: 30px">
              Personnes à contacter
              <tableAide></tableAide>
            </help>
          </p>

          <v-form ref="form">
            <!-- premier encart -->
            <div>
              <h2>Informations sur la forêt</h2>
              <h4>Status</h4>
              <div
                style="margin-top: 10px; border: 1px solid #ccc; padding: 20px; border-radius: 5px"
              >
                <div style="display: flex; align-items: center">
                  <span>Status de la forêt</span>
                  <span class="required">*</span>

                  <v-radio-group
                    v-model="declaration_data.b_statut_public"
                    :rules="[rules.required]"
                    row
                  >
                    <v-radio
                      label="Public"
                      :value="true"
                    ></v-radio>
                    <v-radio
                      label="Privée"
                      :value="false"
                    ></v-radio>
                  </v-radio-group>

                  <help style="margin-left: 20px">
                    <helpContent helpID="form_statut_foret"></helpContent>
                  </help>
                </div>

                <div style="display: flex; align-items: center">
                  <span v-if="declaration_data.b_statut_public">
                    La forêt relève-t-elle du régime forestier ?
                  </span>
                  <span v-else>
                    La forêt est-elle dotée d'un document de gestion durable (plan simple de gestion
                    ou code de bonnes pratiques sylvicoles) ?
                  </span>
                  <span class="required">*</span>

                  <v-radio-group
                    v-model="declaration_data.b_document"
                    :rules="[rules.required]"
                    row
                  >
                    <v-radio
                      label="Oui"
                      :value="true"
                    ></v-radio>
                    <v-radio
                      label="Non"
                      :value="false"
                    ></v-radio>
                  </v-radio-group>
                </div>
              </div>
            </div>

            <v-fade-transition
              v-if="
                declaration_data &&
                'b_statut_public' in declaration_data &&
                'b_document' in declaration_data
              "
            >
              <div>
                <!-- ------------------  La carte  ---------------------  -->

                <div>
                  <div><h3>Localisation</h3></div>

                  <div style="width: 100%; position: relative">
                    <MapDeclaration
                      :b_statut_public="declaration_data.b_statut_public"
                      :b_document="declaration_data.b_document"
                      :declaration_data="declaration_data"
                      @layer-selected="handleLayerSelect"
                    />
                  </div>
                </div>

                <!-- -------------  informations sur la foret ---------------- -->

                <div
                  style="margin-top: 30px"
                  v-if="declaration_data.b_document === false"
                >
                  <h3>Informations sur la forêt</h3>
                  <div>
                    <p>
                      Le nom de la forêt et sa superficie sont issues des données transmises par
                      l’ONF. Ces informations ne peuvent être modifiées. Si vous constatez une
                      erreur, merci de l’indiquer dans le cadre dédié aux commentaires libres en fin
                      de formulaire ou de contacter l’animateur de l’Observatoire.
                    </p>
                    Veuillez cliquer sur « Suivant ».

                    <div
                      style="
                        margin-top: 10px;
                        border: 1px solid #ccc;
                        padding: 20px;
                        border-radius: 5px;
                      "
                    >
                      <v-text-field
                        v-model="declaration_data.label_foret"
                        label="Nom de la forêt"
                        :disabled="declaration_data.b_document === true"
                      >
                        <template v-slot:append-outer>
                          <help><helpContent helpID="form_nom_foret"></helpContent></help>
                        </template>
                      </v-text-field>
                      <v-text-field
                        v-model="declaration_data.surface_renseignee"
                        :rules="[rules.required]"
                        label="Total de la surface (en ha)"
                        :disabled="declaration_data.b_document === true"
                      >
                        <template v-slot:append-outer>
                          <help><helpContent helpID="form_superficie_foret"></helpContent></help>
                        </template>
                      </v-text-field>
                    </div>
                  </div>
                </div>

                <!-- ------------- informations sur le propriétaire, modifiable unique si document de gestion à false ---------------- -->

                <div
                  style="margin-top: 30px"
                  v-if="declaration_data.b_document === false"
                >
                  <h3>Informations sur le propriétaire</h3>
                  <p>
                    Le nom de la forêt et sa superficie sont issues des données transmises par
                    l’ONF. Ces informations ne peuvent être modifiées. Si vous constatez une erreur,
                    merci de l’indiquer dans le cadre dédié aux commentaires libres en fin de
                    formulaire ou de contacter l’animateur de l’Observatoire. Veuillez cliquer sur «
                    Suivant ».
                  </p>

                  <div
                    style="
                      margin-top: 10px;
                      border: 1px solid #ccc;
                      padding: 20px;
                      border-radius: 5px;
                      display: flex;
                    "
                  >
                    <div style="width: 100%; padding-right: 20px">
                      <v-text-field
                        v-model="declaration_data.nom_proprietaire"
                        label="Nom du propriétaire"
                        :disabled="declaration_data.b_document === true"
                      ></v-text-field>
                      <v-text-field
                        v-model="declaration_data.telephone"
                        :rules="[rules.required, rules.telephone]"
                        :disabled="declaration_data.b_document === true"
                        label="Teléphone"
                      ></v-text-field>
                      <v-text-field
                        v-model="declaration_data.email"
                        :rules="[rules.required, rules.email]"
                        :disabled="declaration_data.b_document === true"
                        label="Email"
                      ></v-text-field>
                    </div>
                  </div>
                </div>

                <!-- ---------- Informations sur le peuplement ------------------- -->

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
                      item-text="label_fr"
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
                      item-text="label_fr"
                      label="Essence secondaire (plusieurs possibles)"
                      multiple
                    ></v-select>

                    <!-- -------- Essences complémentaires: liste select, plusieurs choix possibles -------- -->
                    <v-select
                      v-model="declaration_data.nomenclatures_peuplement_essence_complementaire"
                      :items="nomenclature.OEASC_PEUPLEMENT_ESSENCE.values"
                      title="Sélectionnez l'essence complémentaire (plusieurs possibles)"
                      item-value="id_nomenclature"
                      item-text="label_fr"
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
                            $refs.form &&
                            !$refs.form.valid
                          "
                        ></v-checkbox>
                        <div
                          v-if="
                            Array.isArray(declaration_data.nomenclatures_peuplement_origine2) &&
                            declaration_data.nomenclatures_peuplement_origine2.length === 0 &&
                            $refs.form &&
                            !$refs.form.valid
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
                          row
                          style="margin-left: 20px"
                        >
                          <v-radio
                            label="Oui"
                            :value="true"
                          ></v-radio>
                          <v-radio
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
                          row
                          style="margin-left: 20px"
                        >
                          <v-radio
                            label="Oui"
                            :value="true"
                          ></v-radio>
                          <v-radio
                            label="Non"
                            :value="false"
                          ></v-radio>
                        </v-radio-group>
                      </div>

                      <div
                        v-if="declaration_data.b_peuplement_paturage_presence == true"
                        style="padding-left: 20px"
                      >
                        <div style="display: flex; flex-direction: row">
                          <div>
                            <v-select
                              v-model="declaration_data.nomenclatures_peuplement_paturage_type"
                              :items="nomenclature.OEASC_PEUPLEMENT_PATURAGE_TYPE.values"
                              title="Sélectionnez le type de pâturage, plusieurs possibles"
                              item-value="id_nomenclature"
                              item-text="label_fr"
                              label="Type de pâturage, plusieurs possibles"
                              multiple
                            ></v-select>
                          </div>
                          <div style="margin-left: 20px">
                            <v-select
                              v-model="declaration_data.id_nomenclature_peuplement_paturage_statut"
                              :items="nomenclature.OEASC_PEUPLEMENT_PATURAGE_STATUT.values"
                              title="Sélectionnez le statut du pâturage"
                              item-value="id_nomenclature"
                              item-text="label_fr"
                              label="Statut du pâturage"
                            ></v-select>
                          </div>
                          <div style="margin-left: 20px">
                            <v-select
                              v-model="
                                declaration_data.id_nomenclature_peuplement_paturage_frequence
                              "
                              :items="nomenclature.OEASC_PEUPLEMENT_PATURAGE_FREQUENCE.values"
                              title="Sélectionnez la fréquence du pâturage"
                              item-value="id_nomenclature"
                              item-text="label_fr"
                              label="Fréquence du pâturage"
                            ></v-select>
                          </div>
                          <div
                            v-if="
                              declaration_data.id_nomenclature_peuplement_paturage_frequence == 547
                            "
                            style="margin-left: 20px"
                          >
                            <v-select
                              v-model="declaration_data.nomenclatures_peuplement_paturage_saison"
                              :items="nomenclature.OEASC_PEUPLEMENT_PATURAGE_SAISON.values"
                              title="Sélectionnez la saison du pâturage, plusieurs possibles"
                              item-value="id_nomenclature"
                              item-text="label_fr"
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
                          row
                        >
                          <v-radio
                            v-for="(item, index) in nomenclature.OEASC_PEUPLEMENT_ACCES.values"
                            :key="index"
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
                          item-text="label_fr"
                          :rules="[rules.requiredListMultiple]"
                          label="Espèces présentes (plusieurs possibles)"
                          multiple
                        ></v-select>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- ---------- Informations sur les dégats ------------------- -->

                <div style="margin-top: 30px">
                  <h3>Informations sur les dégats</h3>
                  <div
                    class="encadrer"
                    style="padding-left: 20px"
                  >
                    <degatsForm
                      :declaration_data="declaration_data"
                      :nomenclature="nomenclature"
                    ></degatsForm>
                  </div>
                </div>

                <div style="margin-top: 30px">
                  <h3>Précisions sur la localisation des degats</h3>
                  <div
                    class="encadrer"
                    style="padding-left: 20px"
                  >
                    <v-textarea
                      v-model="declaration_data.precision_localisation"
                      label="Précisions sur la localisation des dégâts"
                      rows="2"
                      auto-grow
                    ></v-textarea>
                  </div>
                </div>

                <div style="margin-top: 30px">
                  <h3>Commentaires</h3>
                  <div
                    class="encadrer"
                    style="padding-left: 20px"
                  >
                    <p>
                      Vous pouvez indiquer ici des informations complémentaires sur la déclaration,
                      par exemple des précisions sur les dégâts constatés, les conditions de la
                      forêt, etc.
                    </p>
                    <v-textarea
                      v-model="declaration_data.commentaire"
                      label="Commentaires"
                      rows="4"
                      auto-grow
                    ></v-textarea>
                  </div>
                </div>

                <!-- --------------------- Bouton de validation --------------------- -->

                <div style="margin-top: 30px; display: flex">
                  <v-btn
                    color="primary"
                    @click="action_terminer_declaration"
                  >
                    Terminer la déclaration
                  </v-btn>
                </div>
              </div>
            </v-fade-transition>
          </v-form>
        </div>

        <div v-else>
          Chargement en cours
          <v-progress-linear
            active
            indeterminate
          ></v-progress-linear>
        </div>
      </div>

      <!-- Lorsque l'utilisateur valide une première fois son formulaire un résumé et un bouton de validation
       apparait -->
      <div v-else-if="initialized && etape_affichage === 'AFFICHAGE_RESUME'">
        <h2>Résumé de la déclaration</h2>
        <div>
          <p>Veuillez vérifier les informations saisies avant de soumettre la déclaration.</p>
          <div style="margin-top: 30px">
            <h3>Résumé et validation</h3>
            <div
              class="encadrer"
              style="padding-left: 20px"
            >
              <!-- --------------------- Résumé de la déclaration --------------------- -->
              <div>
                <resumeDeclaration
                  :declaration_data="declaration_data"
                  :nomenclature="nomenclature"
                ></resumeDeclaration>
              </div>
            </div>
          </div>

          <!-- --------------------- Autorisation de transmission d'informations --------------------- -->
          <div v-if="type_action !== 'CLOTURE'">
            <p>
              J’autorise la transmission des informations fournies aux responsables cynégétiques
              locaux, pour pouvoir adapter la pression de chasse
            </p>
            <v-radio-group
              v-model="declaration_data.b_autorisation"
              :rules="[rules.required]"
              row
            >
              <v-radio
                label="Oui"
                :value="true"
              ></v-radio>
              <v-radio
                label="Non"
                :value="false"
              ></v-radio>
            </v-radio-group>
          </div>

          <!-- --------------------- Validation directe de la déclaration pour les admins --------------------- -->
          <div v-if="(type_action == 'CREATION') | (type_action == 'MODIFICATION')">
            <div
              v-if="this.$store.getters.droitMax >= 5"
              style="margin-top: 30px"
            >
              <h3>Validation de la déclaration pour les admins</h3>
              <div style="padding-left: 20px">
                <v-radio-group
                  v-model="declaration_data.b_valid"
                  :mandatory="false"
                  row
                >
                  <v-radio
                    label="Oui"
                    :value="true"
                  ></v-radio>
                  <v-radio
                    label="Non"
                    :value="false"
                  ></v-radio>
                </v-radio-group>
              </div>
            </div>
          </div>

          <div v-if="type_action !== 'CLOTURE'">
            <v-btn
              color="primary"
              @click="etape_affichage = 'AFFICHAGE_FORM'"
              style="margin-right: 30px"
              :disabled="processing"
            >
              Modifier la déclaration
            </v-btn>
            <v-btn
              color="success"
              @click="submitDeclaration"
              :disabled="processing"
            >
              <span v-if="type_action == 'RENOUVELLEMENT'">Renouveller ma déclaration</span>
              <span v-else>Soumettre la déclaration</span>
            </v-btn>
          </div>
          <div
            v-if="type_action === 'CLOTURE'"
            style="margin-top: 30px; display: flex; justify-content: center"
          >
            <v-btn
              color="red"
              @click="closeDeclaration"
              :disabled="processing"
              style="width: 100%; max-width: 400px; height: 50px"
            >
              Cloturer cette déclaration
            </v-btn>
          </div>
          <v-progress-linear
            v-if="processing"
            active
            indeterminate
          ></v-progress-linear>
        </div>
      </div>
    </div>

    <!-- affiche un encart en bas de page si l'utilisateur valide sa déclaration et qu'il manque des informations -->
    <div
      style="
        position: fixed;
        bottom: 20px;
        left: 0;
        width: 100%;
        display: flex;
        justify-content: center;
        z-index: 9999;
      "
    ></div>

    <!-- <div style="width: 70%;">
      <br><br>
      <pre> declaration_data: {{ JSON.stringify(declaration_data, null, 2)}}</pre>
    </div> -->

    <div
      v-if="affichage_fenetre_succes"
      slot="success"
    >
      <v-dialog
        value="true"
        persistent
        max-width="600"
      >
        <v-card v-if="type_action != 'CLOTURE'">
          <v-card-title class="headline">Votre déclaration à bien été enregistrée</v-card-title>
          <v-card-text>
            <p>Vous pouvez désormais</p>
            <ul>
              <li>
                <a href="#/declaration/declarer_en_ligne">Déclarer de nouveaux dégâts en forêt</a>
              </li>
              <li>
                <a
                  Voir
                  href="#/declaration/liste"
                >
                  Voir la liste des dégâts déclarés
                </a>
              </li>
              <li><a href="#/">Retourner à l'accueil</a></li>
            </ul>
          </v-card-text>
        </v-card>
        <v-card v-else>
          <v-card-title class="headline">Votre déclaration à bien été clôturée</v-card-title>
          <v-card-text>
            <p>Vous pouvez désormais</p>
            <ul>
              <li>
                <a href="#/declaration/declarer_en_ligne">Déclarer de nouveaux dégâts en forêt</a>
              </li>
              <li><a href="#/">Retourner à l'accueil</a></li>
            </ul>
          </v-card-text>
        </v-card>
      </v-dialog>
    </div>
  </div>
</template>

<script>
// import { mapState } from 'vuex';
import help from '@/components/form/help_static.vue';
import tableAide from '@/modules/content/table-aide.vue';
import { formFunctions } from '@/components/form/functions/form.js';
import { apiRequest } from '@/core/js/data/api';
import { fetch_forets_from_code, fetch_proprietaires_from_id } from './utils/api_request.js'; // Importez les fonctions nécessaires si elles existent
import MapDeclaration from './map/map_declaration.vue';
import degatsForm from '@/components/form/degats_declaration_form.vue';
import resumeDeclaration from '@/modules/declaration/resume_declaration.vue';
import helpContent from '@/modules/declaration/help-content.vue';
import { snackbarStore } from '@/store/snackbar';

export default {
  name: 'ModifierDeclaration',

  props: [],
  components: {
    help,
    tableAide,
    MapDeclaration,
    degatsForm,
    resumeDeclaration,
    helpContent,
  },

  data() {
    return {
      nomenclature: {}, // Nomenclature des essences et autres données
      title: '',
      declaration_data: {}, // Données de la déclaration
      storeName: 'declaration',
      declarationId: this.$route.query.id, // ID de la déclaration à modifier récupéré depuis l'URL
      token_renouvellement: this.$route.query.token, // Token récupéré depuis l'URL
      action: this.$route.query.action, // Action à effectuer (modifier ou dupliquer) récupérée depuis l'URL
      initialized: false, // Ajouté pour suivre l'état d'initialisation
      processing: false, // les boutons seront désactivés si processing est à true, pour éviter les doubles clics
      error: null, // Ajouté pour stocker les erreurs potentielles
      selected: [], // IDs sélectionnés pour la carte
      rules: formFunctions.rules, // Règles de validation

      // Étape d'affichage du formulaire (
      // AFFICHAGE_FORM => formulaire classique
      // AFFICHAGE_RESUME => résumé de la déclaration avant validation
      etape_affichage: 'AFFICHAGE_FORM',

      // type_action: action de l'utilisateur, qui peut être :
      // CREATION => création d'une nouvelle déclaration,
      // MODIFICATION => modification d'une déclaration existante,
      // RENOUVELLEMENT => Renouvellement d'une déclaration existante
      // CLOTURE => clôture d'une déclaration existante
      type_action: '',
      information_declarant: {}, // Informations sur la personne connectée
      // liste_selection_essences: [], // Liste des essences sélectionnées
      affichage_fenetre_succes: false, // Affichage de la fenêtre de succès après soumission
      affichage_peuplement_maturite: false, // Affichage de la maturité du peuplement
      response: null, // Réponse de l'API lors de la récupération des données de la déclaration
    };
  },

  computed: {},
  watch: {
    // si l'utilisateur à selectionné une autre foret, on met à jours les données de propriétaire et le nom et la superficie de la foret
    'declaration_data.code_foret'(newVal, oldVal) {
      if (newVal && newVal !== oldVal && oldVal !== undefined) {
        fetch_forets_from_code(newVal)
          .then((result) => {
            if (result && result.label_foret) {
              this.declaration_data.label_foret = result.label_foret;
              this.declaration_data.surface_renseignee = result.surface_renseignee;
              this.declaration_data.nom_foret = result.nom_foret;
              // id_proprietaire = result.id_proprietaire;
              fetch_proprietaires_from_id(result.id_proprietaire)
                .then((proprietaire) => {
                  if (proprietaire) {
                    this.declaration_data.nom_proprietaire = proprietaire.nom_proprietaire;
                    this.declaration_data.adresse = proprietaire.adresse;
                    this.declaration_data.s_commune_proprietaire =
                      proprietaire.s_commune_proprietaire;
                    this.declaration_data.telephone = proprietaire.telephone;
                    this.declaration_data.email = proprietaire.email;
                  } else {
                    console.error("Propriétaire non trouvé pour l'ID:", result.id_proprietaire);
                  }
                })
                .catch((error) => {
                  console.error(
                    'Erreur lors de la récupération des données du propriétaire:',
                    error
                  );
                });
            }
          })
          .catch((error) => {
            console.error('Erreur lors de la récupération des données de la forêt:', error);
          });
      }
    },
    'declaration_data.b_document'(newVal, oldVal) {
      if (newVal === false && oldVal !== undefined) {
        // Si le document de gestion est activé, on désactive les champs de nom de forêt et superficie
        this.declaration_data.nom_proprietaire = this.information_declarant.nom_complet;
        this.declaration_data.adresse = '';
        this.declaration_data.s_commune_proprietaire = '';
        this.declaration_data.telephone = '';
        this.declaration_data.email = this.information_declarant.email;
        this.declaration_data.label_foret = '';
        this.declaration_data.surface_renseignee = '';
        this.declaration_data.nom_foret = '';
      }
    },
  },

  created() {},

  async mounted() {
    this.define_type_action();

    // si l'utilisateur est connecté
    if (this.$store.getters.isAuth) {
      this.information_declarant = this.$store.getters.user;
      this.response = await apiRequest(
        'GET',
        `api/declaration/declaration?${this.declarationId ? `id=${this.declarationId}` : ''}`
      );
      // console.log("Response de l'API pour la déclaration:", this.response);
    } else {
      // l'utilisateur n'est pas connecté, on vérifie si c'est un renouvellement avec token
      if (this.type_action === 'RENOUVELLEMENT' || this.type_action === 'CLOTURE') {
        if (this.token_renouvellement && this.declarationId) {
          this.response = await apiRequest(
            'GET',
            `api/declaration/declaration_renouvellement?id=${this.declarationId}&token=${this.token_renouvellement}`
          );
          if (this.response['success'] == false) {
            snackbarStore.show(
              'Token invalide pour le renouvellement de la déclaration. ',
              'error'
            );
            // this.redirect_to_login();
          }
        } else {
          snackbarStore.show(
            'Token de renouvellement manquant ou ID de déclaration manquant. ',
            'error'
          );
          // this.redirect_to_login();
        }
      }
    }

    if (this.response['success'] == true) {
      this.declaration_data = this.response.data;
      this.nomenclature = await apiRequest('GET', `api/oeasc/nomenclatures`);
      if (!this.declaration_data.id_declarant) {
        this.declaration_data.id_declarant = this.$store.getters.user.id_role;
        this.declaration_data.email = this.$store.getters.user.email;
        this.declaration_data.nom_proprietaire = this.$store.getters.user.nom_complet;
        // this.declaration_data.b_document = null; // On laisse le choix à l'utilisateur de renseigner ou non le document de gestion
        // this.declaration_data.b_statut_public = null;
      }

      if (!this.declaration_data.b_valid) {
        this.declaration_data.b_valid = false; // Par défaut, la déclaration n'est pas validée
      }
      // console.log("Données de la déclaration après traitement du renouvellement:", this.declaration_data);
      this.initialized = true;
    }
  },

  methods: {
    /**
     * Dernière petites vérifications avant l'envoi de la déclaration.
     * On clean certains champs superflus qui pourraient créer des erreurs
     */
    async submitDeclaration() {
      // Vérification des règles de validation
      // const isValid = this.$refs.form.validate();

      this.processing = true; // Désactiver les boutons pour éviter les doubles clics

      if (!this.declaration_data.b_autorisation) {
        snackbarStore.show(
          'Veuillez indiquer si vous autorisez la transmission des informations.',
          'info'
        );
        return;
      }

      // Vérifier que la déclaration est bien chargée
      if (!this.declaration_data || Object.keys(this.declaration_data).length === 0) {
        snackbarStore.show(
          'Les données de la déclaration ne sont pas chargées. Veuillez réessayer plus tard.',
          'error'
        );
        return;
      }

      //------------------------------ preparation et envoi des données ------------------------------

      let options = { postData: { ...this.declaration_data } };
      console.log('Données à soumettre:', options.postData);

      if (this.type_action === 'RENOUVELLEMENT') {
        apiRequest('POST', `/api/declaration/duplicate_declaration`, options)
          .then((response) => {
            // console.log("Déclaration renouvelée avec succès:", response);
            this.affichage_fenetre_succes = true; // Affiche la fenêtre de succès
          })
          .catch((error) => {
            console.error('Erreur lors du renouvellement de la déclaration:', error);
            snackbarStore.show(
              "Une erreur s'est produite lors de la soumission. Veuillez réessayer.",
              'error'
            );
          });
      } else if (this.type_action === 'CREATION') {
        if (this.declaration_data.id_declaration) {
          snackbarStore.show(
            'Une erreur est survenue: la déclaration existe déjà. Veuillez réessayer.',
            'error'
          );
          return;
        }
        apiRequest('POST', `/api/declaration/declaration`, options)
          .then((response) => {
            // console.log("Déclaration créée avec succès:", response);
            this.affichage_fenetre_succes = true; // Affiche la fenêtre de succès
          })
          .catch((error) => {
            console.error('Erreur lors de la création de la déclaration:', error);
            snackbarStore.show(
              "Une erreur s'est produite lors de la soumission. Veuillez réessayer.",
              'error'
            );
          });
      } else if (this.type_action === 'MODIFICATION') {
        // Envoi de la déclaration via l'API
        if (!this.declaration_data.id_declaration) {
          snackbarStore.show(
            "Une erreur est survenue: l'ID de déclaration est manquant pour la modification. Veuillez réessayer.",
            'error'
          );
          return;
        }
        this.declaration_data.b_valid = false; // Lors d'une modification, la déclaration doit être à nouveau validée par un admin

        await apiRequest('PATCH', `api/declaration/declaration`, options)
          .then((response) => {
            // console.log("Déclaration mise à jour avec succès:", response);
            this.affichage_fenetre_succes = true; // Affiche la fenêtre de succès
          })
          .catch((error) => {
            console.error('Erreur lors de la mise à jour de la déclaration:', error);
            snackbarStore.show(
              "Une erreur s'est produite lors de la soumission. Veuillez réessayer.",
              'error'
            );
          });
      }
      this.processing = false; // Réactiver les boutons après le traitement
    },

    /**
     * Lorsque l'utilisateur à terminé de remplir, on vérifie si toutes les données sont valides avant
     * d'afficher le résumé de la déclaration.
     */
    action_terminer_declaration() {
      this.error = null; // Réinitialiser l'erreur

      if (!this.$refs.form.validate()) {
        snackbarStore.show('Veuillez remplir tous les champs requis.', 'info');
        return;
      }

      if (this.declaration_data.b_document === false) {
        if (this.declaration_data.areas_localisation_cadastre.length === 0) {
          snackbarStore.show(
            'Veuillez sélectionner au moins une aire de localisation cadastrale.',
            'info'
          );
          return;
        }
        // Vérification si l'utilisateur à bien selectionné au moins une area sur la carte
        if (!this.declaration_data.nom_proprietaire) {
          snackbarStore.show(
            "Le nom du propriétaire est requis si il n'y a pas de document de gestion.",
            'info'
          );
          return;
        }
        if (!this.declaration_data.telephone) {
          snackbarStore.show(
            "Le numéro de téléphone du propriétaire est requis si il n'y a pas de document de gestion.",
            'info'
          );
          return;
        }
        if (!this.declaration_data.email) {
          snackbarStore.show(
            "L'email du propriétaire est requis si il n'y a pas de document de gestion.",
            'info'
          );
          return;
        }
        if (!this.declaration_data.surface_renseignee) {
          snackbarStore.show(
            "La superficie renseignée est requise si il n'y a pas de document de gestion.",
            'info'
          );
          return;
        }
      } else {
        // il y a un document de gestion
        if (
          this.declaration_data.b_statut_public == true &&
          this.declaration_data.areas_localisation_onf_ug.length === 0
        ) {
          snackbarStore.show(
            'Veuillez sélectionner au moins une aire de localisation ONF UG.',
            'info'
          );
          return;
        }
        if (
          this.declaration_data.b_statut_public === false &&
          this.declaration_data.areas_localisation_cadastre.length === 0
        ) {
          snackbarStore.show(
            'Veuillez sélectionner au moins une aire de localisation cadastrale.',
            'info'
          );
          return;
        }
      }

      // si l'utilisateur  a bien selectionné les infos sur les dégats mais a oublié de le valider
      if (this.declaration_data.degats.length > 0) {
        this.declaration_data.degats.forEach((degat) => {
          if (degat.degat_essences.length === 0 && degat.id_nomenclature_degat_type !== 480) {
            snackbarStore.show(
              'Veuillez valider le type de dégât pour tous les dégâts renseignés.',
              'info'
            );
            return;
          }
        });
      } else {
        snackbarStore.show('Veuillez ajouter au moins un dégât.', 'info');
        return;
      }

      if (
        this.declaration_data.id_nomenclature_peuplement_type != 525 &&
        this.declaration_data.nomenclatures_peuplement_maturite.length === 0
      ) {
        snackbarStore.show('Veuillez sélectionner au moins une maturité du peuplement.', 'info');
        return;
      }

      if (this.declaration_data.nomenclatures_peuplement_origine2.length === 0) {
        snackbarStore.show('Veuillez sélectionner au moins une origine du peuplement.', 'info');
        return;
      }

      if (
        this.declaration_data.b_peuplement_protection_existence == true &&
        this.declaration_data.nomenclatures_peuplement_protection_type.length === 0
      ) {
        snackbarStore.show('Veuillez sélectionner au moins un type de protection.', 'info');
        return;
      }

      if (this.declaration_data.b_peuplement_paturage_presence == true) {
        if (
          this.declaration_data.nomenclatures_peuplement_paturage_type.length === 0 ||
          this.declaration_data.id_nomenclature_peuplement_paturage_statut === null ||
          this.declaration_data.id_nomenclature_peuplement_paturage_frequence === null
        ) {
          snackbarStore.show('Veuillez remplir tous les champs liés au pâturage.', 'info');
          return;
        }
        if (
          this.declaration_data.id_nomenclature_peuplement_paturage_frequence == 547 &&
          this.declaration_data.nomenclatures_peuplement_paturage_saison.length === 0
        ) {
          snackbarStore.show('Veuillez sélectionner au moins une saison pour le pâturage.', 'info');
          return;
        }
      }

      if (this.$refs.form.validate() && this.error === null) {
        this.etape_affichage = 'AFFICHAGE_RESUME';
        return;
      }
    },

    /**
     * Concatène les listes d'aires sélectionnées de la déclaration pour "afficher les zonnes selectionnées" (le bouton à droite de la carte) sur la carte.
     * @returns {Array} Un tableau contenant toutes les aires de localisation sélectionnées.
     */
    concateneAreasSelected() {
      return [
        this.declaration_data.areas_localisation_cadastre,
        this.declaration_data.areas_localisation_onf_prf,
        this.declaration_data.areas_localisation_onf_ug,
      ]
        .filter(Boolean)
        .flat();
    },

    handleLayerSelect(layerId) {
      const index = this.selectedLayers.indexOf(layerId);
      if (index === -1) {
        this.selectedLayers.push(layerId);
      } else {
        this.selectedLayers.splice(index, 1);
      }
    },

    define_type_action() {
      if (this.$route.name === 'modifier_declaration') {
        this.type_action = 'MODIFICATION';
        this.title = `Modification de la déclaration: ${this.declarationId}`;
      } else if (this.$route.name === 'nouvelle_declaration') {
        this.type_action = 'CREATION';
        this.title = "Création d'une nouvelle déclaration";
      } else if (this.$route.name === 'actualisation_declaration') {
        if (this.action === 'oui') {
          this.type_action = 'RENOUVELLEMENT';
          this.title = `Renouvellement de la déclaration: ${this.declarationId}`;
        } else {
          this.type_action = 'CLOTURE';
          this.title = `Clôture de la déclaration: ${this.declarationId}`;
          this.etape_affichage = 'AFFICHAGE_RESUME';
        }
      }
    },

    redirect_to_login() {
      this.$router.push({
        name: 'user.login',
        query: { redirect: this.$route.fullPath },
      });
    },

    closeDeclaration() {
      if (!this.declaration_data.id_declaration) {
        snackbarStore.show(
          "Une erreur est survenue: l'ID de déclaration est manquant pour la clôture. Veuillez réessayer.",
          'error'
        );
        return;
      }
      apiRequest('POST', `api/declaration/cloture_declaration`, {
        postData: {
          id_declaration: this.declaration_data.id_declaration,
          token_renouvellement: this.declaration_data.token_renouvellement,
        },
      })
        .then((response) => {
          // console.log("Déclaration clôturée avec succès:", response);
          // snackbarStore.show("Déclaration clôturée avec succès.", 'success');
          this.affichage_fenetre_succes = true; // Affiche la fenêtre de succès
        })
        .catch((error) => {
          snackbarStore.show(
            "Une erreur s'est produite lors de la clôture. Veuillez réessayer.",
            'error'
          );
        });
    },
  },
};
</script>

<style>
@import url('../../components/form/form.css');

pre {
  background-color: #f4f4f4;
  padding: 10px;
  border: 1px solid #ddd;
  white-space: pre-wrap; /* Pour que le texte long s'enroule */
  word-wrap: break-word; /* Pour que les mots longs se cassent */
}

.encadrer {
  border: 1px solid #ccc;
  padding: 20px;
  border-radius: 5px;
}
</style>

<style scoped></style>
