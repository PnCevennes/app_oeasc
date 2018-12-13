$(document).ready(function() {

  M={};

  "use strict";

  // Couleur Styles Carte

  var color={};

  color.oeasc = '#2ca25f';
  color.black = '#000000';
  color.zc = '#feb24c';
  color.aa = '#ffeda0';
  color.p1 = '#88419d';
  color.p2 = '#000099';
  color.p3 = '#006600';
  color.selected = '#fd8d3c';

  color.OEASC_ONF_FRT = color.p2;
  color.OEASC_ONF_PRF = color.p2;
  color.OEASC_ONF_UG = color.p2;
  color.OEASC_DGD = color.p2;
  color.OEASC_COMMUNE = color.p2;
  color.OEASC_CADASTRE = color.p2;
  color.OEASC_SECTION = color.p2;
  color.LOCALISATION_SELECTION = color.selected;

  color.foret = color.p1
  color.localisation = color.p3



  var style={};

  style.oeasc = {
    weight: 2,
    opacity: 0.5,
    fillOpacity: 0.1,
    color: color.black,
    fillColor : color.oeasc,
  };

style.secteur = {
    weight: 1,
    // dashArray: 8,
    opacity: 0.5,
    fillOpacity: 0,
    color: color.black,
    // fillColor : color.oeasc,
  };

  style.zc = {
    weight: 1,
    opacity: 0.2,
    fillOpacity: 0.5,
    color : color.black,
    fillColor: color.zc,
  };

  style.aa = {
    weight: 1,
    opacity: 0.2,
    fillOpacity: 0.5,
    color: color.black,
    fillColor : color.aa,
  };

  style.default = {
    weight: 1,
    fillOpacity: 0.3,
  };

  style.highlight = {
    fillOpacity: 0.5,
    weight: 2,
  };

  style.selected = {
    fillColor: color.selected,
    color: color.selected,
  }

  //map

style.pane = {};
style.pane.tooltips = 5;

  var d_ls = {};

  d_ls.OEASC_ONF_FRT = {
    name: "OEASC_ONF_FRT",
    label: "Forêt relevant du régime forestier",
    keys: [ "area_code", "area_name" ],
    color: color.OEASC_ONF_FRT,
    pane: 1,
  };

  d_ls.OEASC_ONF_PRF = {
    name: "OEASC_ONF_PRF",
    label: "Parcelle forestière",
    keys: [ "area_code", "area_name" ],
    color: color.OEASC_ONF_PRF,
    pane: 2,
  };

  d_ls.OEASC_ONF_UG = {
    name: "OEASC_ONF_UG",
    label: "Unité de gestion",
    keys: [ "area_code", "area_name" ],
    color: color.OEASC_ONF_UG,
    pane: 3,
  };

  d_ls.OEASC_DGD = {
    name: "OEASC_DGD",
    label: "Forêt dotée d'un document de gestion durable",
    keys: [ "area_code", "area_name" ],
    color: color.OEASC_DGD,
    pane: 1,
  };

  d_ls.OEASC_DGD_SIMPLE = {
    name: "OEASC_DGD_SIMPLE",
    label: "Forêt possédent un document de gestion durable",
    keys: [ "area_code", "area_name" ],
    color: color.OEASC_DGD,
    pane: 1,
  };


  d_ls.OEASC_COMMUNE = {
    name: "OEASC_COMMUNE",
    label: "Commune",
    keys: [ "area_name" ],
    color: color.OEASC_COMMUNE,
    pane: 1,
  };

  d_ls.OEASC_COMMUNE_SIMPLE = {
    name: "OEASC_COMMUNE_SIMPLE",
    label: "Commune",
    keys: [ "area_name" ],
    color: color.OEASC_COMMUNE,
    pane: 1,
  };

  d_ls.OEASC_SECTION = {
    name: "OEASC_SECTION",
    label: "Section cadastrale",
    keys: [ "area_name" ],
    color: color.OEASC_SECTION,
    pane: 1,
  };

  d_ls.OEASC_CADASTRE = {
    name: "OEASC_CADASTRE",
    label: "Parcelle cadastrale",
    keys: [ "area_code", "area_name" ],
    color: color.OEASC_CADASTRE,
    pane: 2,
  };

// formulaire

var list = {};

var type_codes_areas_localisation = [

  "OEASC_COMMUNE",
  "OEASC_DGD",
  "OEASC_ONF_FRT",
  "OEASC_SECTION",

];

var type_codes_areas_foret = [

  "OEASC_COMMUNE",
  "OEASC_DGD",
  "OEASC_ONF_FRT",
  "OEASC_SECTION",

];

var type_codes_areas_localisation = [

  "OEASC_CADASTRE",
  "OEASC_ONF_UG",
  "OEASC_ONF_PRF",

]

list.data=[
"OEASC_ONF_FRT",
"OEASC_ONF_PRF",
"OEASC_ONF_UG",
"OEASC_DGD",
"OEASC_COMMUNE",
"OEASC_SECTION",
"OEASC_CADASTRE",
];


M.select = {};
list.data.forEach(function(e){

  M.select[e] = $("#" + e.toLowerCase());

});


M.style = style;
M.color = color;

M.list = list;

M.d_ls = d_ls;

M.type_codes_areas_localisation = type_codes_areas_localisation;
M.type_codes_areas_foret = type_codes_areas_foret;


});
