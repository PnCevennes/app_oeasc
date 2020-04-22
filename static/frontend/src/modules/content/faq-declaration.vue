<template>
  <div>
    <v-row justify="center">
      <v-expansion-panels>
        <v-expansion-panel v-for="(item, index) in faq" :key="index">
          <v-expansion-panel-header>
            <span style="line-height:23px" v-html="item.question">{{ item.question }}</span>
          </v-expansion-panel-header>
          <v-expansion-panel-content>
            <div v-html="item.response"></div>
          </v-expansion-panel-content>
        </v-expansion-panel>
      </v-expansion-panels>
    </v-row>
  </div>
</template>

<script>
export default {
  name: "faqDeclaration",
  data: () => ({
    faq: [
      {
        question: "<b>Quels types de dégâts puis-je puis signaler ?</b>",
        response:
          'Vous pouvez signaler des dégâts d’abroutissement, de frottis et d’écorçage, ou signaler une absence de régénération qui vous semble anormale et pourrait être liée à la présence de cervidés. Vous pouvez également signaler des dégâts sur les pistes ou les clôtures de votre forêt. Les différents types de dégâts sont décrits et présentés <a href="#/declaration/degat_grand_gibier">ici</a>).'
      },
{
  question: "<b>Comment signaler des dégâts ?</b>",
        response:
          'Rien de plus simple ! Connectez à votre compte « utilisateur » (si vous ne l’avez pas encore fait, vous pouvez le créer en cliquant <a href="#/user/create">ici</a>), et suivez les étapes du formulaire en ligne.'
      },
      {
        question: "<b>Combien de temps cela va-t-il me prendre ?</b>",
        response:
          "Le renseignement du formulaire d’alerte en ligne se veut relativement rapide et ne vous prendra en moyenne qu'entre 10 et 20 minutes."
      },
      {
        question: "<b>Ma forêt est-elle incluse dans le périmètre de l'Observatoire ?</b>",
        response: "Le périmètre de l'Observatoire est constitué de l'ensemble des communes en partie incluses ou frontalières au coeur du Parc national des Cévennes. Pour vérifier si votre forêt est située dans ce périmètre, nous vous invitons à consulter la carte présentée <a href='#/presentation/perimetre'>ici</a>."
      },
      {
        question: "<b>Ai-je besoin d'aller collecter des informations en forêt pour déclarer des dégâts ?</b>",
        response: "Pas nécessairement, si vous connaissez suffisamment votre forêt et le peuplement touché par les dégâts. Le formulaire est constitué de questions simples. Il ne nécessite aucune collecte de données sur le terrain, et a été conçu afin de pouvoir être renseigné sur la base des connaissances élémentaires que vous avez de votre forêt. À partir des simples observations que vous aurez pu faire lorsque vous avez constaté les dégâts, vous devriez donc pouvoir remplir le formulaire directement depuis chez vous, devant votre ordinateur."
      },
      {
        question: "<b>Quel est mon intérêt à déclarer des dégâts ?</b>",
        response: `En renseignant un formulaire d’alerte, vous :
<ul>
  <li>
      attirez l’attention des décideurs sur votre propriété et un potentiel problème d’équilibre sylvo-cynégétique ;
  </li>
  <li>
      contribuez à fournir des informations qui seront utilisées pour définir des mesures de gestion justes et adaptées (les alertes pourront notamment influencer des décisions telles que les attributions des plans de chasse) ;
  </li>
  <li>
      vous inscrivez dans une démarche de gestion durable du territoire dont fait partie votre forêt ;
  </li>
  <li>
      rendez possible la programmation d’actions de chasse localement ciblées, afin d’accentuer la pression de chasse et de limiter la pression du grand gibier sur la végétation, si nécessaire ;
  </li>
  <li>
      ouvrez la possibilité à votre forêt de bénéficier d’un diagnostic sylvicole qui permettra d’évaluer précisément et objectivement les dégâts subis au regard de vos objectifs sylvicoles.
  </li>
</ul>
`
      },
      {
        question: "<b>Les informations fournies resteront-elles confidentielles ?</b>",
        response: "<b>Oui !</b> Soyez rassuré(e), toutes les informations fournies restent strictement confidentielles et ne seront pas utilisées à des fins commerciales ou publicitaires. Les données issues du système d’alerte seront traitées de façon globale, et non nominative."
      },
      {
        question: "<b>J’ai déjà déclaré des dégâts, à l’époque, par l’intermédiaire du syndicat de propriétaires forestiers, et rien n’a été fait : quelle différence cette fois-ci ?</b>",
        response: `
<p>
Vous avez déjà, par le passé, pris la peine de renseigner une déclaration de dégâts de gibier, et vous avez peut-être été déçu de voir que rien n’avait été fait ensuite, ou vous avez l’impression que cela n’a servi à rien ?
</p>

<p>
Souvent, et malheureusement, les informations que vous aviez fournies jusqu'à présent n’ont pas pu être réellement utilisées ou valorisées. C’est justement pour remédier à cela que le système d’alerte de l’Observatoire a été créé. Grace à leur centralisation sur un vaste périmètre, les données collectées contribueront directement à la définition de mesures de gestion. Les informations que vous avez pris la peine de fournir ne seront pas archivées puis oubliées, mais analysées finement, et les résultats seront partagés avec les partenaires de l’Observatoire afin de les valoriser au mieux.
</p>

<p>
Ce système d’alerte permettra également de suivre l’évolution de la situation dans le temps.
</p>

<p>
Enfin, certains peuplements feront l’objet d’un diagnostic approfondi qui évaluera précisément et objectivement les dégâts subis au regard de vos objectifs sylvicoles.
</p>
        `
      },
    ]
  }),
};
</script>

