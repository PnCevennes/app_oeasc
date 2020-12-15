<template>
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
</v-card-text
            >
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
</template>

<script>
export default {
    name='wait',

}
</script>
