<!-- Contient tous les textes d'aide du formulaire de déclaration.  -->

<template>
  <div>
    <div v-if="helpID === 'form_statut_foret'">
      <h4>
        Statut de la forêt
        <v-icon>help</v-icon>
      </h4>
      <ul>
        <li>
          <strong>Public</strong>
          = forêt
          <strong>domaniale</strong>
          ,
          <strong>communale</strong>
          ,
          <strong>sectionale</strong>
          ou
          <strong>appartenant à un établissement public</strong>
          (même au titre de son domaine privé).
        </li>
        <li>
          <strong>Privé</strong>
          = forêt appartenant à une
          <strong>personne physique</strong>
          ou
          <strong>morale de droit privé</strong>
          (groupement forestier ou foncier, entreprise, SCI, association, etc.)
        </li>
      </ul>
    </div>

    <div v-if="helpID === 'form_dgestion_durable'">
      <h4>
        Forêts dotées d'un document de gestion durable
        <v-icon>help</v-icon>
      </h4>
      <p>
        Chaque forêt est identifiée par son nom (enregistré dans la base de données du CRPF, quand
        il est disponible), le type de document de gestion et son numéro (référence enregistrée dans
        la base de données du CRPF).
      </p>
    </div>

    <div v-if="helpID === 'form_nom_foret'">
      <h4>
        Nom de la forêt
        <v-icon>help</v-icon>
      </h4>
      <p>
        Nom
        <strong>officiel</strong>
        ou
        <strong>usuel</strong>
        de la forêt concernée par l'alerte (si elle en possède un). Le cas échéant, utiliser le nom
        figurant sur le document de gestion durable (PSG, CBPS, aménagement forestier).
      </p>
    </div>

    <div v-if="helpID === 'form_superficie_foret'">
      <h4>
        Superficie totale de la forêt (ha)
        <v-icon>help</v-icon>
      </h4>
      <p>
        Superficie totale (arrondie à l'hectare près) de l’ensemble de la forêt concernée par
        l’alerte.
      </p>
    </div>

    <div v-if="helpID === 'form_selection_carte'">
      <h4>
        Utilisation de la carte interactive
        <v-icon>help</v-icon>
      </h4>

      <p>
        Cliquez sur un élément pour le sélectionner ou le désélectionner (les éléments sélectionnés
        apparaissent en orange), ou utilisez la liste déroulante située à droite de la carte.
      </p>

      <p>
        Pour les
        <strong>forêts relevant du régime forestier</strong>
        ou
        <strong>dotées d'un document de gestion durable</strong>
        vous ne pouvez sélectionner qu'
        <strong>une seule forêt</strong>
        .
      </p>

      <p>
        Dans les
        <strong>autres cas</strong>
        (sélection des communes, des sections cadastrales, des parcelles forestières ou cadastrales
        ou des unités de gestion), vous pouvez sélectionner
        <strong>plusieurs entités</strong>
      </p>

      <p>
        Vous pouvez zoomer à l'aide de la molette de votre souris ou des icônes +/- situées en haut
        à gauche de la carte, et choisir le fond de carte
        <strong>via</strong>
        l'icône située en haut à droite de la carte, parmi les choix suivants :
      </p>
      <ul>
        <li>OpenTopoMap: permet la visualisation des courbes de niveau</li>
        <li>Mapbox : choix par défaut (fond OpenStreetMap)</li>
        <li>
          IGN (cartes) : fond de carte IGN, jusqu'au 1 : 25 000
          <sup>e</sup>
          (SCAN1000®, SCAN Régional®, SCAN100® et SCAN25®)
        </li>
        <li>IGN (ortho.) : photographies aériennes de l'IGN (BD ORTHO®)</li>
      </ul>
    </div>

    <div v-if="helpID === 'foret_non_visible'">
      <h3>
        Je ne retrouve pas ma forêt
        <v-icon>help</v-icon>
      </h3>

      <p>
        Il est possible que votre forêt ne figure pas sur la carte ci-contre et dans la liste
        ci-dessous, notamment si votre document de gestion a été déposé ou agréé récemment.
      </p>
      <p>
        Dans ce cas, nous vous invitons à cliquer sur ce bouton, qui vous redirigera vers une carte
        vous permettant de localiser votre forêt à partir des communes et du cadastre. Votre alerte
        sera alors renseignée comme si votre forêt n'était pas dotée d'un document de gestion
        durable. Cependant,
        <strong>
          nous vous invitons à indiquer dans le cadre de libre expression, en fin de formulaire, que
          votre forêt est bien dotée d'un document de gestion durable mais ne figurait pas dans la
          liste proposée.
        </strong>
      </p>
    </div>

    <div v-if="helpID === 'group_form_essences'">
      <h4>Essence(s)</h4>
      <v-icon>help</v-icon>
      <ul>
        <li>
          <strong>Essence objectif principale</strong>
          = essence constituant
          <strong>l'essentiel de l'intérêt économique</strong>
          (actuel ou à venir) du peuplement
        </li>
        <li>
          <strong>Essences objectif secondaire</strong>
          = autres essences
          <strong>contribuant à l'intérêt économique</strong>
          du peuplement (3 essences maximum)
        </li>
        <li>
          <strong>Essences complémentaires</strong>
          = essences présentes (significativement) mais
          <strong>ne constituant pas un enjeu économique</strong>
          (3 essences maximum)
        </li>
      </ul>
    </div>

    <div v-if="helpID === 'form_type_peuplement'">
      <h4>Type de peuplement</h4>
      <v-icon>help</v-icon>
      Décrire ici la
      <strong>structure actuelle</strong>
      du peuplement (et non son
      <strong>mode de traitement</strong>
      ) Ainsi, pour un peuplement régulier en cours d'irrégularisation, par exemple, cochez
      <strong>"futaie régulière"</strong>
      , et précisez en réponse à la question suivante les catégories de hauteur/diamètre présentes.
    </div>

    <div v-if="helpID === 'form_futaie_reguliere'">
      <h4>Type de peuplement</h4>
      <v-icon>help</v-icon>
      <strong>Futaie régulière</strong>
      = peuplement issu de graines ou de plants dont la majorité des arbres ont approximativement le
      même âge, et présentent des dimensions (hauteur, diamètre) similaires
      <content-img
        center
        src="tooltips_futaie_reg.jpg"
        title="Futaie régulière (à différents stades de développement)"
      />
    </div>

    <div v-if="helpID === 'form_futaie_irreguliere'">
      <h4>Type de peuplement</h4>
      <v-icon>help</v-icon>
      <strong>Futaie irrégulière</strong>
      = peuplement dont les arbres sont répartis dans toutes les classes d’âge et toutes les
      dimensions (mélange de régénération et de petits, moyens et gros arbres)
      <content-img
        center
        src="tooltips_futaie_irr.jpg"
        title="Futaie irrégulière"
      />
    </div>

    <div v-if="helpID === 'form_futaie_melangee'">
      <h4>Type de peuplement</h4>
      <v-icon>help</v-icon>
      <strong>Mélange taillis-futaie</strong>
      = peuplement composé à la fois d’arbres issus de graines ou de plants (futaie), et d’un
      taillis issu de rejets de souche
      <content-img
        center
        src="tooltips_melange_futaie_taillis.jpg"
        title="Mélange taillis-futaie."
      />
    </div>

    <div v-if="helpID === 'form_taillis'">
      <h4>Type de peuplement</h4>
      <v-icon>help</v-icon>
      <strong>Taillis</strong>
      peuplement issu du développement des rejets de souche qui, après abattage de certains arbres
      (feuillus le plus souvent), forment des
      <q>bouquets</q>
      (ou cépées)
      <content-img
        center
        src="tooltips_taillis.jpg"
        title="Taillis (à différents stades de développement)."
      />
    </div>

    <div v-if="helpID === 'form_maturite_peuplement'">
      <h4>Maturité du peuplement</h4>
      <v-icon>help</v-icon>
      Stade(s) de développement
      <u><strong>majoritaire(s)</strong></u>
      du peuplement, selon la hauteur et le diamètre des arbres (plusieurs réponses sont possibles,
      si plusieurs stades de maturité sont présents de façon significative).
    </div>

    <div v-if="helpID === 'form_paturage_domestique'">
      <h4>Pâturage domestique</h4>
      <v-icon>help</v-icon>
      Pâturage par des animaux domestiques (moutons, chèvres, vaches, chevaux, ânes), par opposition
      aux animaux sauvages (cerfs, chevreuils, mouflons, chamois, etc.)
    </div>

    <div v-if="helpID === 'form_accessiblite_peuplement'">
      <h4>Accessibilité du peuplement</h4>
      <v-icon>help</v-icon>
      Indiquez ici si le peuplement est accessible ou non aux engins forestiers (tracteurs,
      débardeurs, etc.) et aux piétons.
      <ul>
        <li>
          <strong>Aisée</strong>
          = une piste carrossable par des véhicules standards mène à proximité du peuplement
        </li>
        <li>
          <strong>Uniquement en 4x4</strong>
          = une piste praticable uniquement par des véhicules tout-terrain mène à proximité du
          peuplement
        </li>
        <li>
          <strong>Uniquement à pied</strong>
          aucune piste carrossable ne mène à proximité du peuplement
        </li>
      </ul>
    </div>

    <div v-if="helpID === 'degat_abroutissement'">
      <h3>Type de dégâts</h3>
      <v-icon>help</v-icon>
      <p>
        <strong>Abroutissement</strong>
        = prélèvement des bourgeons, des feuilles ou des pousses dans un but alimentaire
      </p>

      <strong>Taillis</strong>
      peuplement issu du développement des rejets de souche qui, après abattage de certains arbres
      (feuillus le plus souvent), forment des
      <q>bouquets</q>
      (ou cépées)
      <content-img
        center
        src="tooltips_abroutissement_cervide.jpg"
        title="Abroutissement d'un semis de sapin."
      />
    </div>

    <div v-if="helpID === 'degat_frottis'">
      <h3>Type de dégâts</h3>
      <v-icon>help</v-icon>
      <p>
        <strong>Frottis</strong>
        = blessure infligée par les cervidés mâles frottant leurs bois sur les tiges de jeunes
        arbres (écorce arrachée, tige dénudée, voire cassée)
      </p>
      <content-img
        center
        src="tooltips_frottis.jpg"
        title="Frottis sur jeune douglas"
      />
    </div>

    <div v-if="helpID === 'degat_ecorcage'">
      <h3>Type de dégâts</h3>
      <v-icon>help</v-icon>
      <p>
        <strong>Écorçage</strong>
        = prélèvement de l’écorce d’un arbre dans un but alimentaire (cerf uniquement).
        Généralement, le bord de la blessure est net et aucun lambeau d’écorce ne persiste
        (contrairement au frottis).
      </p>
      <content-img
        center
        src="tooltips_ecorcage.jpg"
        title="Écorçage récent sur un épicéa"
      />
    </div>

    <div v-if="helpID === 'degat_sanglier'">
      <h3>Type de dégâts</h3>
      <v-icon>help</v-icon>
      <p>
        <strong>Dégâts de sanglier</strong>
        = déterrage ou endommagement de plants ou de semis dans un objectif de consommation de la
        racine (le plus souvent, mais d’autres types dégâts peuvent également être constatés :
        fouissement, piétinement, gîte, etc.)
      </p>
    </div>

    <div v-if="helpID === 'degat_deficit_regeneration'">
      <h3>Type de dégâts</h3>
      <v-icon>help</v-icon>
      <p>
        <strong>Absence ou déficit de régénération inexpliquée</strong>
        au regard des conditions locales (lumière au sol, notamment), potentiellement liée à la
        pression des cervidés sur les jeunes semis
      </p>
    </div>

    <div v-if="helpID === 'parcelle_cadastrale'">
      <h4>Choix d'une parcelle cadastrale</h4>
      <v-icon>help</v-icon>
      Les parcelles cadastrales sont listées selon un identifiant construit ainsi :
      <strong>n° Insee de la commune - N° de section - N° de parcelle</strong>
    </div>
  </div>
</template>

<script>
import contentImg from '@/modules/content/content-img.vue';
export default {
  compatConfig: { MODE: 3 }, // verrouille les acquis Phase 4 (composant testé sans warning au 2026-07-10)
  name: 'helpContent',
  components: {
    contentImg,
  },
  props: {
    helpID: {
      type: String,
      required: true,
    },
  },
};
</script>
