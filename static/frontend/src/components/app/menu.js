import menus from '@/config/menu.js'

const processRouteName = function(routeName, { $store, $router }) {
  const route = $router.options.routes.find(route => route.name == routeName);

  const processRoute = {};

  for (const key of Object.keys(route)) {
    if (key == "component") {
      continue;
    }
    processRoute[key] =
      typeof route[key] == "function" ? route[key]({ $store }) : route[key];

    if (key == 'path') {
      const paths = route[key].split('/');
      if (paths[paths.length -1 ][0]==':') {
        paths[paths.length -1 ] = "";

      }
      route[key] = paths.join('/');
    }
  }



  return processRoute;
};

const processMenu = function(menu, { $store, $router }) {
  let menuOut = {...menu};
  if (menu.name) {
    menuOut = { ...menu, ...processRouteName(menu.name, { $store, $router }) };
  }
  for (const key of Object.keys(menuOut)) {
    menuOut[key] =
      typeof menuOut[key] === "function" ? menuOut[key]({ $store }) : menuOut[key];
  }
  return menuOut;
};

const configMenu = function(menuName, { $store, $router }) {
  const menu = processMenu(menus[menuName], { $store, $router });

  return {
    ...menu,
    menus: (menu.names || [])
      .map(name => processRouteName(name, { $store, $router }))
      .filter(menu => !menu.hidden)
  };
};

export { configMenu, menus };
