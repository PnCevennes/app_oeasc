<template>
    <chained-form :config="configFormChainedDeclaration" :meta="{idDeclaration}">
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

  computed: {
    idDeclaration() {
      return this.$route.params.idDeclaration || null;
    }
  }
};
</script>
<style></style>
