<!--
  Composant Vue.js affichant deux boîtes de dialogue (modales) pour la gestion d'une déclaration :
  - La première boîte de dialogue (bModalPost) affiche une animation de chargement (cercle de progression) pendant le traitement de la déclaration.
    - Le titre et le texte de cette boîte sont personnalisables via des slots nommés "title" et "text".
    - La propriété "persistent" empêche la fermeture de la boîte par clic en dehors.
    - La largeur maximale est fixée à 500px.
  - La seconde boîte de dialogue (bModalSuccess) s'affiche lorsque la déclaration a été enregistrée avec succès.
    - Elle affiche un message de confirmation et propose trois actions à l'utilisateur :
      1. Déclarer de nouveaux dégâts en forêt.
      2. Voir la liste des dégâts déjà déclarés.
      3. Retourner à l'accueil.
    - La propriété "persistent" empêche la fermeture de la boîte par clic en dehors.
    - La largeur maximale est fixée à 600px.
  - Les deux boîtes de dialogue sont intégrées dans une ligne (v-row) pour la mise en page.
-->
<!-- <template>
          <v-row>
        <v-dialog v-model="bModalPost" persistent max-width="500">
          <v-card>
            <v-card-title class="headline"
              >
              <slot name="title"></slot>
              </v-card-title
            >
            <v-card-text class="text-center">
              <v-progress-circular
                indeterminate
                color="primary"
              ></v-progress-circular>
            </v-card-text>
            <v-card-text
              >
              <slot name="text"></slot>
            </v-card-text>
          </v-card>
        </v-dialog>

        <v-dialog v-model="bModalSuccess" persistent max-width="600">
          <v-card>
            <v-card-title class="headline"
              >Votre déclaration à bien été enregistrée</v-card-title
            >
            <v-card-text>
              <p>Vous pouvez désormais</p>
              <ul>
                <li>
                  <a href="#/declaration/declarer_en_ligne"
                    >Déclarer de nouveaux dégâts en forêt</a
                  >
                </li>
                <li>
                  <a Voir href="#/declaration/liste"
                    >Voir la liste des dégâts déclarés</a
                  >
                </li>
                <li><a href="#/">Retourner à l'accueil</a></li>
              </ul>
            </v-card-text>
          </v-card>
        </v-dialog>
      </v-row>
</template> -->

<script>
// export default {
//     name='wait',

// }
</script>
