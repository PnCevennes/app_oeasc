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

  color.OEASC_ONF_FRT = color.p1;
  color.OEASC_ONF_PRF = color.p2;
  color.OEASC_ONF_UG = color.p3;
  color.OEASC_DGD = color.p1;
  color.OEASC_COMMUNE = color.p1;
  color.OEASC_CADASTRE = color.p3;
  color.LOCALISATION_SELECTION = color.selected;

  color.foret = color.p1
  color.localisation = color.p3


  var stripes = new L.StripePattern({
    weight: 2,
    opacity: 0.5,
    angle: 45,
    color: color.oeasc
  });

  var style={};

  style.oeasc = {
    weight: 2,
    opacity: 0.5,
    fillOpacity: 0.5,
    color: color.black,
    fillPattern: stripes,
    // fillColor : color.oeasc,
  };

  style.zc = {
    weight: 1,
    opacity: 0.5,
    fillOpacity: 0.5,
    color : color.black,
    fillColor: color.zc,
  };

  style.aa = {
    weight: 1,
    opacity: 0.5,
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
    url: "/api/ref_geo/areas/",
    label: "ONF : Forêt",
    keys: [ "area_code", "area_name" ],
    color: color.OEASC_ONF_FRT,
    pane: 1,
  };

  d_ls.OEASC_ONF_PRF = {
    name: "OEASC_ONF_PRF",
    url: "/api/ref_geo/areas/",
    label: "ONF : Parcelle",
    keys: [ "area_code", "area_name" ],
    color: color.OEASC_ONF_PRF,
    pane: 2,
    select_multi: true,
  };

  d_ls.OEASC_ONF_UG = {
    name: "OEASC_ONF_UG",
    url: "/api/ref_geo/areas/",
    label: "ONF : Unité de gestion",
    keys: [ "area_code", "area_name" ],
    color: color.OEASC_ONF_UG,
    pane: 3,
    select_multi: true,
  };

  d_ls.OEASC_DGD = {
    name: "OEASC_DGD",
    url: "/api/ref_geo/areas/",
    label: "Document de gestion durable",
    keys: [ "area_code", "area_name" ],
    color: color.OEASC_DGD,
    pane: 1,
  };

  d_ls.OEASC_COMMUNE = {
    name: "OEASC_COMMUNE",
    url: "/api/ref_geo/areas/",
    label: "Commune",
    keys: [ "area_name" ],
    color: color.OEASC_COMMUNE,
    pane: 1,
    select_multi: true,
  };

  d_ls.OEASC_CADASTRE = {
    name: "OEASC_CADASTRE",
    url: "/api/ref_geo/areas/",
    label: "Cadastre",
    keys: [ "area_code", "area_name" ],
    color: color.OEASC_CADASTRE,
    pane: 2,
    select_multi: true,
  };

// formulaire

var list = {};

list.data=[
"OEASC_ONF_FRT",
"OEASC_ONF_PRF",
"OEASC_ONF_UG",
"OEASC_DGD",
"OEASC_COMMUNE",
"OEASC_CADASTRE",
];

M.select = {};
list.data.forEach(function(e){
  M.select[e] = $("#" + e.toLowerCase());
});


M.style = style;
M.color = color;
M.stripes = stripes;

M.list = list;

M.d_ls = d_ls;


});
