<!-- ######################################################################################
// N'est plus utilisé que pour voir les déclarations. Le formulaire de déclaration est maintenant
// dans le composant modifier-declaration.vue
// Il faudra la supprimer quand un component de vision de carte simple sera créé. Le résumé est déja fait
###########################################################$$##########################  -->


<template>
    <chained-form :config="configFormChainedDeclaration">
      <!-- ce div apparait seulement après la validation d'un formulaire -->
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
    </chained-form>
</template>

<script>
import configFormChainedDeclaration from "./config/form-chained-declaration";
import chainedForm from "@/components/form/chained-form"

export default {
  name: "declarationForm",
  components: {chainedForm},
  data: () => ({
    configFormChainedDeclaration
  }),
};
</script>
<style></style>
