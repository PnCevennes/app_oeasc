
<!-- <template>
<div class="page" >


    <h1>Suivi de l'indice nocturne</h1>


    L'indice nocturne permet de <strong>suivre l'évolution de l'abondance des populations</strong> d'ongulés sauvages (pour en savoir plus, consultez le paragraphe dédié aux *indicateurs de changement écologique (ICE)* dans l'onglet [contenu de l'Observatoire](#/observatoire/contenu)). Vous trouverez ci-dessous les résultats des suivis mis en œuvre, sur chaque secteur de l'Observatoire, pour 4 espèces (cerf, chevreuil, renard, lièvre).

    <strong>Les résultats concernant le Chevreuil doivent être interprétés avec la plus grande prudence</strong>, car le suivi de l'indice nocturne <strong>n'a pas été validé scientifiquement pour cette espèce</strong>.

    En raison du contexte sanitaire, les suivis de l'indice nocturne n'ont pu être réalisés lors des printemps 2020 et 2021.

    <h2>Résultats par secteur</h2>

    Par défaut, les résultats sont affichés pour l'espèce Cerf.
    Vous pouvez consulter les résultats pour les autres espèces en cliquant sur les boutons ci-dessous.

    <h3>Mont Aigoual - {{contentValues['espece']}}</h3>

    <div>
        <dynamic-form
        :config="{name:'espece', type:'list_form', list_type:'button', items:['Cerf', 'Chevreuil', 'Lièvre', 'Renard'], default:'Cerf'}"
        :baseModel="contentValues"
        ></dynamic-form>
    </div>

    <br>
    <div><in-graph :nom_espece="contentValues['espece']" ug='Aigoual'></in-graph></div>

    A l'heure actuelle, <strong>aucune tendance significative ne peut être dégagée</strong> (quelque soit l'espèce considérée). Toutefois, la valeur relevée en 2024 est la plus faible enregistrée sur le massif (1,29 cerf par kilomètre) et interroge sur la dynamique de la population. La situation est à suivre de très près. 
    <br>
    Le nombre d'années de suivi reste limité. Les <strong>intervalles de confiance élevés</strong> pour les années 2016 et 2018 (les comptages n'ayant pu être effectués que lors de deux sorties, au lieu des quatre requises) nécessitent d'**être d'autant plus prudents** dans l'interprétation des résultats.<br>
    <br>
    La valeur absolue moyenne est élevée (2,24 cerfs par kilomètre) et témoigne d'une forte abondance de cerfs sur le massif.
    ___
    <h3>Causse Méjean - {{contentValues['espece']}}</h3>

    <div>
    <dynamic-form
    :config="{name:'espece', type:'list_form', list_type:'button', items:['Cerf', 'Chevreuil', 'Lièvre', 'Renard'], default:'Cerf'}"
    :baseModel="contentValues"
    ></dynamic-form>
    </div>
    <div><in-graph displayReg :nom_espece="contentValues['espece']" ug='Causse-Gorges'></in-graph></div>

    Une <strong>hausse significative des populations de Cerf</strong> est constatée, à l'échelle de l'ensemble du Causse Méjean. Néanmoins, les intervalles de confiance élevés et le manque de données pour les années 2016 et 2018 nécessitent de rester prudent dans l'interprétation de cette tendance, qui devra être confirmée au cours des prochaines années.
    <br>
    <br>Pour les <strong>autres espèces</strong>, aucune tendance statistiquement significative n'a pu être mise en évidence, hormis pour le renard dont une hausse quasi-significative est observée. <br>
    <br>

    <h3>Causse Méjean (coeur) - {{contentValues['espece']}}</h3>

    <div>
    <dynamic-form
    :config="{name:'espece', type:'list_form', list_type:'button', items:['Cerf', 'Chevreuil', 'Lièvre', 'Renard'], default:'Cerf'}"
    :baseModel="contentValues"
    ></dynamic-form>
    </div>

    <div><in-graph :nom_espece="contentValues['espece']" ug='Causse-Gorges_coeur'></in-graph></div>

    Sur les 2 circuits du Causse Méjean situés dans le cœur du Parc national des Cévennes, <strong>aucune tendance évolutive significative</strong> n'a pu être mise en évidence (quelle que soit l'espèce concernée). 
    <br>
    <br>
    La tendance à la hausse qui semblait s'amorcer entre 2017 et 2022, ne semble pas avérée. D'ailleurs, entre 2022 et 2024, la tendance inverse à l'air de se dessiner. Néanmoins, il convient de ne pas sur-interpréter les résultats, les intervalles de confiance étant larges du fait d'une forte variabilité du nombre d'animaux comptés lors des soirées.
    <br>
    <br>En ce qui concerne le lièvre, une relative stabilité est constatée ces dernières années, avec la présence d'environ 1 individu par kilomètre parcouru.
    ___
    <h3> Mont Lozère - {{contentValues['espece']}} </h3>
    <div>
    <dynamic-form
    :config="{name:'espece', type:'list_form', list_type:'button', items:['Cerf', 'Chevreuil', 'Lièvre', 'Renard'], default:'Cerf'}"
    :baseModel="contentValues"
    ></dynamic-form>
    </div>

    <div><in-graph :nom_espece="contentValues['espece']" ug='Mont Lozère'></in-graph></div>


    A ce jour, <strong>aucune tendance significative ne peut être dégagée</strong> (quelque soit l'espèce considérée). Le nombre d'années de suivi reste toutefois limité (en raison notamment de l'absence de suivi en 2020 et 2021).
    <br>
    <br>En 2018, les comptages n'ont pu être effectués que lors de deux sorties (et même une seule pour l'un des quatre circuits), ce qui affecte fortement la précision de la valeur (intervalle de confiance large).
    <br> 
    <br> Les valeurs observées en 2024, plus faibles que les années précédentes, peuvent s'expliquer par des conditions météorologiques défavorables lors des soirées de comptages.

   <pre>espece:::{{ liste_especes}}</pre>
</div>
</template> -->




<script>


// import '@/modules/page/page.css';
// import inGraph from "@/modules/in/in-graph.vue";
// // import inTable from "@/modules/in/in-table.vue";
// import { apiRequest } from "@/core/js/data/api.js";


// const CONTENT = {
//     inGraph
//   }
// // const storeName = "in";

// export default {
//   name: "resultat_in",
//   props: ["large"],
//   components: { inGraph  },
//   data() {
//     return {

//       contentValues: {
//         espece: "Cerf"
//       },
//       liste_especes: [],
//       store_test: this.$store.state


//     };
//   },


//   methods: {
//     init_data() {
//       console.log("init_data");
//       // fetch('http://localhost:5005/api/in/results/')
//       //   .then(response => response.text()) // lis comme texte brut
//       //   .then(text => {
//       //     console.log(text); // pour voir ce que Flask renvoie
//       //     const data = JSON.parse(text); // ici tu peux attraper l’erreur
//       //     console.log(data);
//       //   })
//       //   .catch(error => {
//       //     console.error("Erreur de parsing ou fetch :", error);
//       //   });
//       // this.liste_especes = this.$store.dispatch("getAllCommonsEspece")
//       // this.liste_especes =  apiRequest("GET", 'api/generic/commons/especes/',  {})
//       // .then((response) => {
//       //   console.log("response", response);
//       //   this.liste_especes = response.data;
//       //   console.log("liste_especes", this.liste_especes);
//       // })
//       // this.liste_especes = this.$store.dispatch(configStore.getEspeces, {});

//     },


//   },

//   mounted() {
//     this.init_data();
//   }
// };

</script>



