// Point d'entrée unique de Highcharts : initialise une seule fois les modules (export, highcharts-more)
// et les libellés français. À importer par les composants graphiques (jamais depuis main.js :
// Highcharts doit rester chargé à la demande, pas dans le chunk d'entrée).
import Highcharts from 'highcharts';
import More from 'highcharts/highcharts-more'; // séries 'errorbar' (ICE) et autres types avancés
import exportingInit from 'highcharts/modules/exporting'; // menu d'export (PNG, PDF...)
import offlineExporting from 'highcharts/modules/offline-exporting'; // export côté client
import { Chart } from 'highcharts-vue';

// Les modules ES ne sont évalués qu'une fois, mais on se protège d'une double initialisation
// (HMR, instances multiples) avec un drapeau sur l'instance Highcharts.
if (!Highcharts.__oeascInit) {
  More(Highcharts);
  exportingInit(Highcharts);
  offlineExporting(Highcharts);

  Highcharts.setOptions({
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
