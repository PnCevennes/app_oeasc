// /**
//  * fonction concernant l'ancien formulaire de declararation
//  * permet de selectionner des zones sur une carte. Sera a supprimer lorsque le dynamic form sera supprimé
//  */

// import { copy } from "@/core/js/util/util.js";
// import { config } from "@/config/config.js";
// import { formFunctions } from "./functions/form.js";

// const configBaseSelect = config.map.configBaseSelect;

// const selectMapMethods = {

//   /**
//    * Initialise la configuration de la carte selon le mode (container ou normal).
//    * Cette fonction gère la configuration des couches, les règles de validation,
//    * les légendes, les URLs et les noms des couches à afficher sur la carte.
//    */
//     initMapConfig: function() {
//       // Récupère la référence du composant select pour la carte
//       const selectRef = this.$refs[`select_map_${this.config.name}`];
//       if (selectRef) {
//         // Réinitialise la validation du select si la référence existe
//         this.$refs[`select_map_${this.config.name}`].resetValidation();
//       }

//       // Initialise la liste des couches de la carte
//       const layerList = {
//         po: {} // couche par défaut, peut être modifiée selon le contexte
//       };

//       let legend = "",
//         url = "";

//       // Mode container : permet de sélectionner une zone "container" avant la sélection normale
//       if (this.selectContainer) {
//         legend = this.config.containerLegend; // Légende spécifique au container
//         this.description = this.config.containerDescription; // Description du container

//         // Règle de validation personnalisée pour le container
//         const ruleContainer = v =>
//           !(!v || (Array.isArray(v) && v.length != 0)) ||
//           `Veuillez ${
//             this.config.multiple ? "ajouter un élément suplémentaire et / ou" : ""
//           } et appuyer sur "VALIDER LA SELECTION" pour passer à la selection des ${this.config.legend.toLowerCase()}`;

//         // Définition des règles de validation selon si le champ est requis et multiple
//         this.rules = this.config.required
//           ? this.config.multiple
//             ? [formFunctions.rules.requiredListMultiple, ruleContainer]
//             : [formFunctions.rules.requiredListSimple, ruleContainer]
//           : [];

//         // Détermination de l'URL pour récupérer les données du container
//         url =
//           typeof this.config.containerUrl === "function"
//             ? this.config.containerUrl(this.baseModel)
//             : this.config.containerUrl;

//         // Nom du champ utilisé pour le container
//         this.name = this.config.containerName;

//       } else {
//         // Mode normal : sélection classique d'une zone
//         legend = this.config.legend; // Légende classique
//         this.description = this.config.description; // Description classique
//         this.rules = this.config.rules; // Règles de validation classiques

//         // Détermination de l'URL pour récupérer les données de la couche
//         url =
//           typeof this.config.url === "function"
//             ? this.config.url({
//                 baseModel: this.baseModel,
//                 areasContainer: this.baseModel[this.config.containerName]
//               })
//             : this.config.url;

//         // Nom du champ utilisé pour la sélection normale
//         this.name = this.config.name;
//       }

//       // Affecte la légende à la propriété de l'objet
//       this.legend = legend;

//       // Prépare la configuration de la couche à afficher sur la carte
//       const selectLayerConfig = {
//         ...configBaseSelect, // Configuration de base
//         ...{
//           legend,
//           url
//         }
//       };

//       // Ajoute la configuration de la couche à la liste des couches
//       layerList[this.config.name] = selectLayerConfig;

//       // Met à jour la configuration de la carte avec la nouvelle liste de couches
//       this.mapConfig = {
//         layerList
//       };

//       // Met à jour la légende de la couche dans le service de la carte si disponible
//       if (this.mapService) {
//         this.mapService._config.layers[this.config.name].legend = this.legend;
//       }
//       },

//     /**
//      * Fonction appelée lors de l'initialisation de la sélection.
//      * Elle est déclenchée par un événement personnalisé et
//      * initialise les données de sélection à partir des couches de la carte.
//      * @param {*} event
//      */
//     initSelect: function(event) {
//       if (event.detail.key === this.config.name) {
//         this.dataSelect = this.mapService
//           .findLayers("key", this.config.name)
//           .map(layer => {
//             const properties = layer.feature.properties;
//             const elem = {};
//             for (const [key, fieldName] of Object.entries(
//               this.config.dataFieldNames
//             )) {
//               elem[key] = properties[fieldName];
//             }
//             return elem;
//           });
//       }
//       this.updateLayers(false);
//     },

//     /**
//      * Fonction appelée lors de l'initialisation de la sélection.
//      * Elle est déclenchée par un événement personnalisé et
//      * initialise les données de sélection à partir des couches de la carte.
//      * @param {*} event
//      */
//     selectChange: function(event) {
//       this.updateLayers();
//     },

//     /**
//      * Fonction appelée lors d'un clic sur une couche.
//      * Elle met à jour le modèle de base en fonction de la sélection
//      * et gère l'ajout ou la suppression de valeurs dans le modèle.
//      * Si le mode de sélection est multiple, elle ajoute ou supprime la valeur sélectionnée
//      * de la liste des valeurs sélectionnées. Sinon, elle remplace la valeur actuelle.
//      * @param {*} event
//      */
//     clickOnLayer: function(event) {
//       const value = event.detail.id_area;

//       if (!this.config.multiple) {
//         this.baseModel[this.name] = value;
//       } else {
//         const index = this.baseModel[this.name].indexOf(value);
//         if (index > -1) {
//           this.baseModel[this.name].splice(index, 1);
//         } else {
//           this.baseModel[this.name].push(value);
//         }
//       }

//       this.updateLayers();
//     },

//     /**
//      * Fonction appelée lors de l'initialisation de la sélection.
//      * Elle est déclenchée par un événement personnalisé et
//      * met à jour les couches de la carte en fonction de la sélection.
//      * @param {*} bChange
//      */
//     updateLayers: function(bChange = true) {
//       // bChange pour ne pas executer la function change à l'initialisation du composant
//       bChange &&
//         this.config.change &&
//         this.config.change({
//           baseModel: this.baseModel,
//           config: this.config,
//           $store: this.$store
//         });

//       const layerConfig = this.mapConfig.layerList[this.config.name];

//       const styles = {
//         normal: layerConfig.style,
//         select: layerConfig.select.style
//       };

//       // selected => normal
//       const layers = this.mapService.findLayers("selected", true);
//       for (const layer of layers) {
//         layer.feature.properties.selected = false;
//         layer.curStyle = styles.normal;
//         layer.setStyle(layer.curStyle);
//       }

//       // model => selected
//       let model = copy(this.baseModel[this.name]) || [];
//       if (!Array.isArray(model)) {
//         model = [model];
//       }

//       for (const id_area of model) {
//         const layer = this.mapService.findLayer("id_area", id_area);
//         if (!layer) {
//           continue;
//         }
//         layer.feature.properties.selected = true;
//         layer.curStyle = styles.select;
//         layer.setStyle(layer.curStyle);
//       }
//     },

//     /**
//      * Réinitialise le conteneur de sélection.
//      * Cette fonction remet à zéro le modèle de base pour le conteneur,
//      * réinitialise la sélection et les couches associées,
//      * et recharge la configuration de la carte.
//      * Elle est utilisée pour permettre à l'utilisateur de recommencer la sélection
//      * d'une zone de conteneur sans avoir à recharger la page.
//      * @returns {void}
//      */
//     reinitContainer: function() {
//       this.selectContainer = true;
//       this.baseModel[this.config.name] = this.config.multiple ? [] : null;

//       let layers = null;

//       layers = this.mapService.findLayers("key", this.config.name);
//       this.mapService.removeLayers(layers);

//       // load new layer + select
//       this.initMapConfig();

//       this.mapService.addLayer({
//         ...this.mapConfig.layerList[this.config.name],
//         key: this.config.name
//       });
//     },

//     /**
//      * Valide le conteneur de sélection.
//      * Cette fonction est appelée lorsque l'utilisateur a terminé de sélectionner une zone de conteneur
//      * et souhaite valider sa sélection. Elle met à jour la carte en zoomant sur les couches sélectionnées,
//      * supprime les couches de conteneur existantes, recharge la configuration de la carte
//      * et ajoute la nouvelle couche sélectionnée.
//      * @returns {void}
//      */
//     validerContainer: function() {
//       this.selectContainer = false;
//       let layers = null;
//       // zoom on layer selected
//       layers = this.mapService.findLayers("selected", true);
//       this.mapService.zoomOnLayers(layers);

//       // remove layer container
//       layers = this.mapService.findLayers("key", this.config.name);
//       this.mapService.removeLayers(layers);

//       // load new layer + select
//       this.initMapConfig();

//       this.mapService.addLayer({
//         ...this.mapConfig.layerList[this.config.name],
//         key: this.config.name
//       });
//     }

// };

// export { selectMapMethods };
