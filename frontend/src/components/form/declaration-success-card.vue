
<!-- ----------------------------------------------------------------------------------------------------
Fenetre s'ouvrant lorsqu'on valide la création ou la modification d'une déclaration de dégâts en forêt.
----------------------------------------------------------------------------------------------------- -->


<template>
<div slot="success">
         <v-dialog value=true persistent max-width="600">
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
      </div>

</template>
<script>
export default {
  name: "declaration-success-card",
  props: ["config"],
  data: () => ({}),
  computed: {},
  methods: {},
};
</script>