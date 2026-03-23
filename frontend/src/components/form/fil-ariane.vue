<!-- Uniquement utilisé dans chained-form. 
 Il faudra le supprimer lors de la modification l'affichage des declarations
 mais verifier avant si ce n'est pas appelé dans le content de la base de donnée -->

<template>
  <div v-if="keySession != 'all'">
    <v-row
      dense
      class="fil-arianne-container"
    >
      <v-col
        v-for="([keySessionGroup, sessionGroup], indexGroup) in Object.entries(
          config.sessionGroups
        )"
        :key="keySessionGroup"
        @click="condValidSessionGroup(keySessionGroup) && onSessionGroupClick(keySessionGroup)"
        :class="{
          'current-group': condCurrentGroup(keySessionGroup),
          'valid-group': condValidSessionGroup(keySessionGroup),
        }"
      >
        {{ indexGroup + 1 }}. {{ sessionGroup.title }}
      </v-col>
    </v-row>
    <v-row
      dense
      v-for="([keySessionGroup, sessionGroup], indexGroup) in Object.entries(config.sessionGroups)"
      :key="keySessionGroup"
      class="fil-arianne-container"
    >
      <template v-if="condSessions(keySessionGroup)">
        <v-col
          v-for="(keySession, indexSession) in sessionGroup.sessions"
          :key="keySession"
          @click="condValidSession(keySession) && onSessionClick(keySession)"
          :class="{
            'current-session': condCurrentSession(keySession),
            'valid-session': condValidSession(keySession),
          }"
        >
          {{ indexGroup + 1 }}.{{ indexSession + 1 }} -
          {{ config.sessionDefs[keySession].title }}
        </v-col>
      </template>
    </v-row>
  </div>
</template>
<script>
import { sessionFunctions } from '@/components/form/functions/session.js';
// import "./declaration.css";
export default {
  name: 'fil-arianne',
  props: ['config', 'keySession', 'baseModel'],
  data: () => ({}),
  watch: {
    baseModel: {
      handler() {},
    },
    deep: true,
  },
  computed: {
    freeze() {
      return this.baseModel.freeze;
    },
  },
  methods: {
    /**
     * Gère le clic sur un groupe de sessions dans le fil d'Ariane.
     *
     * Cette méthode est appelée lorsqu'un utilisateur clique sur un groupe de sessions.
     * Elle utilise la fonction utilitaire `sessionFunctions.firstSession` pour récupérer
     * la première session associée au groupe sélectionné (`keySessionGroup`). Ensuite,
     * elle déclenche la navigation vers cette session en appelant la méthode `onSessionClick`.
     *
     * @param {string} keySessionGroup - La clé identifiant le groupe de sessions cliqué.
     *
     * Étapes :
     * 1. Récupère la première session du groupe via la fonction utilitaire.
     * 2. Appelle la méthode de navigation vers la session correspondante.
     *
     * Cette logique permet à l'utilisateur de naviguer directement vers la première session
     * d'un groupe en cliquant sur le groupe dans le fil d'Ariane.
     */
    onSessionGroupClick(keySessionGroup) {
      const keySession = sessionFunctions.firstSession(this.config, keySessionGroup);
      this.onSessionClick(keySession);
    },

    /**
     * Gère le clic sur une session dans le fil d'Ariane.
     *
     * Cette méthode est appelée lorsqu'un utilisateur clique sur une session spécifique.
     * Elle utilise le routeur Vue pour naviguer vers la session sélectionnée en mettant à jour
     * le paramètre de requête `keySession` dans l'URL. Cela permet d'afficher la session correspondante
     * dans le formulaire en chaîne.
     *
     * @param {string} keySession - La clé identifiant la session cliquée.
     *
     * Étapes :
     * 1. Met à jour l'URL via le routeur Vue en ajoutant/modifiant le paramètre `keySession`.
     * 2. Déclenche la navigation vers la session sélectionnée.
     *
     * Cette logique permet une navigation fluide entre les différentes sessions du formulaire,
     * tout en gardant l'état dans l'URL pour une meilleure gestion et partage du lien.
     */
    onSessionClick(keySession) {
      this.$router.push({ query: { keySession } });
    },

    /**
     * Vérifie si le groupe de sessions courant doit afficher ses sessions.
     *
     * Cette méthode détermine si les sessions d'un groupe donné doivent être affichées
     * dans le fil d'Ariane. Elle compare la clé du groupe passé en paramètre avec le groupe
     * auquel appartient la session courante (déterminé par la fonction utilitaire `sessionFunctions.group`).
     *
     * @param {string} keySessionGroup - La clé identifiant le groupe de sessions à vérifier.
     * @returns {boolean} Retourne vrai si le groupe correspond à celui de la session courante, sinon faux.
     *
     * Étapes :
     * 1. Utilise la fonction utilitaire `sessionFunctions.group` pour obtenir le groupe de la session courante.
     * 2. Compare ce groupe avec le groupe passé en paramètre.
     * 3. Retourne le résultat de la comparaison.
     *
     * Cette logique permet d'afficher uniquement les sessions du groupe actuellement sélectionné,
     * améliorant ainsi la lisibilité et la navigation dans le fil d'Ariane.
     */
    condSessions(keySessionGroup) {
      return keySessionGroup == sessionFunctions.group(this.config, this.keySession);
    },

    /**
     * Vérifie si une session est valide.
     *
     * Cette méthode utilise la fonction utilitaire `sessionFunctions.condValidSession`
     * pour déterminer si la session identifiée par `keySession` est valide.
     * Elle lui transmet un objet contenant la configuration (`config`), le store Vuex (`$store`)
     * et le modèle de base (`baseModel`). Ensuite, elle s'assure que le modèle n'est pas figé
     * (`freeze` doit être faux) pour autoriser la validation.
     *
     * @param {string} keySession - La clé identifiant la session à valider.
     * @returns {boolean} Retourne vrai si la session est valide et que le modèle n'est pas figé, sinon faux.
     *
     * Étapes :
     * 1. Appelle la fonction utilitaire de validation de session avec les paramètres nécessaires.
     * 2. Vérifie que le modèle n'est pas figé.
     * 3. Retourne le résultat combiné des deux conditions.
     */
    condValidSession(keySession) {
      return (
        sessionFunctions.condValidSession(
          {
            config: this.config,
            $store: this.$store,
            baseModel: this.baseModel,
          },
          keySession
        ) && !this.baseModel.freeze
      );
    },

    /**
     * Vérifie si un groupe de sessions est valide.
     *
     * Cette méthode prend en paramètre la clé d'un groupe de sessions,
     * récupère la première session associée à ce groupe via la fonction
     * `sessionFunctions.firstSession`, puis vérifie si cette session est valide
     * en appelant `condValidSession`. Elle s'assure également que le modèle
     * de base n'est pas figé (`freeze` doit être faux).
     *
     * @param {string} keySessionGroup - La clé identifiant le groupe de sessions à valider.
     * @returns {boolean} Retourne vrai si la première session du groupe est valide et que le modèle n'est pas figé, sinon faux.
     */
    condValidSessionGroup(keySessionGroup) {
      const keySession = sessionFunctions.firstSession(this.config, keySessionGroup);
      return this.condValidSession(keySession) && !this.baseModel.freeze;
    },

    /**
     * Vérifie si la session courante satisfait une condition spécifique.
     *
     * @param {string} keySession - La clé identifiant la session à vérifier.
     * @returns {boolean} - Retourne le résultat de la condition sur la session courante.
     *
     * Étapes :
     * 1. Compare la clé de la session courante avec la clé fournie.
     * 2. Retourne le résultat de cette comparaison.
     */
    condCurrentSession(keySession) {
      return this.keySession == keySession;
    },

    /**
     * Vérifie si le groupe de session courant satisfait une condition spécifique.
     *
     * @param {string} keySessionGroup - La clé identifiant le groupe de sessions à vérifier.
     * @returns {boolean} - Retourne le résultat de la condition sur la session courante du groupe.
     *
     * Étapes :
     * 1. Récupère la première session du groupe via la fonction utilitaire 'firstSession'.
     * 2. Passe la clé de cette session à la méthode 'condCurrentSession' pour vérifier la condition.
     * 3. Retourne le résultat de cette vérification.
     *
     * Remarque : Cette méthode permet d'abstraire la logique de vérification sur un groupe de sessions,
     * en se basant sur la première session du groupe.
     */
    condCurrentGroup(keySessionGroup) {
      const keySession = sessionFunctions.firstSession(this.config, keySessionGroup);
      return this.condCurrentSession(keySession);
    },
  },
};
</script>

<style scoped>
.fil-arianne-container > div {
  /* flex-grow: 1; */
  text-align: center;
  margin: 1px;
  background-color: lightgrey;
}

.fil-arianne-container > div.current-group,
.fil-arianne-container > div.current-session {
  font-weight: bold;
}

.fil-arianne-container > div.valid-session,
.fil-arianne-container > div.valid-group {
  background-color: lightgoldenrodyellow;
  cursor: pointer;
}
</style>
