<template>
  <div>
    <div v-for="[key, item] of Object.entries(setup)" :key="key">
      <h2>{{ item.titre }}</h2>
      <div class="flex">
        <div v-for="key_organisme of item.liste" :key="key_organisme">
          <a :href="organismes[key_organisme].url">
            <img
              :src="`${$store.getters.distPath}img/logos/${key_organisme}.jpg`"
              height="150px"
            />
          </a>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "liste-partenaire",
  data: () => ({
    organismes: {
      pnc: {
        nom: "Établissement public du Parc national des Cévennes",
        url: "http://www.cevennes-parcnational.fr/"
      },
      onf: {
        nom:
          "Office national des forêts - agences territoriales de la Lozère et Hérault/Gard (ONF)",
        url: "http://www.onf.fr/"
      },
      crpf: {
        nom: "https://occitanie.crpf.fr/",
        url: "Centre régional de la propriété forestière (CRPF) Occitanie"
      },
      syndic30: {
        nom: "https://forestiersdugard.com/",
        url: "Syndicat des forestiers privés du Gard"
      },
      syndic48: {
        nom: "Syndicat lozérien de la forêt privée",
        url: "https://www.fransylva.fr/n/fransylva/n:2646"
      },
      fplg: {
        nom: "Coopérative La Forêt Privée Lozérienne et Gardoise",
        url: "https://www.fplg.fr/"
      },
      fc48: {
        nom: "Fédération départementale des chasseurs de la Lozère",
        url: "http://www.chasseurdelozere.com/"
      },
      fc30: {
        nom: "Fédération départementale des chasseurs du Gard",
        url: "http://www.fdc30.fr/"
      },
      fcocc: {
        nom: "Fédération régionale des chasseurs d'Occitanie",
        url: "http://www.chasse-nature-occitanie.fr/frc/"
      },
      agri30: {
        nom: "Chambre d’agriculture du Gard",
        url: "https://lozere.chambre-agriculture.fr/"
      },
      agri48: {
        nom: "Chambre d’agriculture de la Lozère",
        url: "https://gard.chambre-agriculture.fr/"
      },
      ofb: {
        nom: "Office Français de la Biodiversité",
        url: "http://ofb.gouv.fr/"
      },
      ddt48: {
        nom: "Direction départementale des territoires (DDT) de la Lozère",
        url:
          "http://www.lozere.gouv.fr/Services-de-l-Etat/Agriculture-Environnement-Amenagements-et-Logement/La-Direction-Departementale-des-Territoires/Presentation-des-services-de-la-DDT"
      },
      ddtm30: {
        nom:
          "Direction départementale des territoires et de la mer (DDTM) du Gard",
        url:
          "http://www.gard.gouv.fr/Services-de-l-Etat/Agriculture-environnement-amenagement-et-logement/Direction-Departementale-des-Territoires-et-de-la-Mer-DDTM"
      },
      draafocc: {
        nom:
          "Direction régionale de l'alimentation, de l'agriculture et de la forêt (DRAAF) Occitanie",
        url: "http://draaf.occitanie.agriculture.gouv.fr/"
      }
    },
    setup: {
      pnc: {
        titre: "",
        liste: ["pnc"]
      },

      foret: {
        titre: "Forêt - sylviculture",
        liste: ["onf", "crpf", "syndic30", "syndic48", "fplg"]
      },
      chasse: {
        titre: "Chasse",
        liste: ["fcocc","fc48", "fc30" ]
      },
      agriculture: {
        titre: "Agriculture",
        liste: ["agri30", "agri48"]
      },
      science: {
        titre: "Experts scientifiques",
        liste: ["ofb"]
      },
      etat: {
        titre: "Services de l'État",
        liste: ["ddt48", "ddtm30", "draafocc"]
      }
    }
  })
};
</script>

<style lang="css">
.flex {
  display: flex;
  flex-direction: "row";
  justify-content: center;
  flex-wrap: wrap;
  /* width: 100%; */
}
.flex > div {
  justify-content: center;
/*  */
  flex-grow: 1;
  margin: 10px;
  /* width: 45%; */
}
.flex > div  img {
  opacity: 0.8
}

.flex > div  img:hover {
  opacity: 1

}

</style>
