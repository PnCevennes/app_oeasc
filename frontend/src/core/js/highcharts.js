// Point d'entrée unique de Highcharts : initialise une seule fois les modules (export, highcharts-more)
// et les libellés français. À importer par les composants graphiques (jamais depuis main.js :
// Highcharts doit rester chargé à la demande, pas dans le chunk d'entrée).
import Highcharts from 'highcharts';
// Depuis Highcharts 12+, les modules s'enregistrent eux-mêmes à l'import (plus d'appel de fonction).
import 'highcharts/highcharts-more'; // séries 'errorbar' (ICE) et autres types avancés
import 'highcharts/modules/exporting'; // menu d'export (PNG, PDF...)
import 'highcharts/modules/offline-exporting'; // export côté client
import { Chart } from 'highcharts-vue';

// Les modules ES ne sont évalués qu'une fois, mais on se protège d'une double initialisation
// (HMR, instances multiples) avec un drapeau sur l'instance Highcharts.
if (!Highcharts.__oeascInit) {
  Highcharts.setOptions({
    // Highcharts 13 suit par défaut le thème sombre du système ('light dark') : on force le thème clair.
    palette: {
      colorScheme: 'light',
      // Palette par défaut de Highcharts 9 (celle de Highcharts 13 est différente : la 2e couleur y est violette
      // alors qu'elle était gris foncé, ce qui changeait les graphiques existants).
      colors: ['#7cb5ec', '#434348', '#90ed7d', '#f7a35c', '#8085e9', '#f15c80', '#e4d354', '#2b908f', '#f45b5b', '#91e8e1'],
    },
    lang: {
      months: [
        'janvier',
        'février',
        'mars',
        'avril',
        'mai',
        'juin',
        'juillet',
        'août',
        'septembre',
        'octobre',
        'novembre',
        'décembre',
      ],
      shortMonths: [
        'janv.',
        'févr.',
        'mars',
        'avr.',
        'mai',
        'juin',
        'juil.',
        'août',
        'sept.',
        'oct.',
        'nov.',
        'déc.',
      ],
      weekdays: ['dimanche', 'lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi'],
      shortWeekdays: ['dim.', 'lun.', 'mar.', 'mer.', 'jeu.', 'ven.', 'sam.'],
      contextButtonTitle: 'Menu du graphique',
      downloadPNG: 'Télécharger en PNG',
      downloadJPEG: 'Télécharger en JPEG',
      downloadPDF: 'Télécharger en PDF',
      downloadSVG: 'Télécharger en SVG',
      printChart: 'Imprimer le graphique',
      viewFullscreen: 'Plein écran',
      exitFullscreen: 'Quitter le plein écran',
      resetZoom: 'Réinitialiser le zoom',
      loading: 'Chargement…',
      noData: 'Aucune donnée à afficher',
    },
  });
  Highcharts.__oeascInit = true;
}

export default Highcharts;
export { Chart };
