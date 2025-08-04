
// si NODE_ENV est en production, on retourne le chemin /front/ sinon on retourne le chemin /
// NODE_ENV est une variable d'environnement qui est définie à production lorsqu'on fait un npm run build
// NODE_ENV est à development par défaut lorsqu'on fait un npm run serve
// Pour définir une variable d'environnement, on peut utiliser la commande export NODE_ENV=production
// Pour vérifier la valeur de NODE_ENV, on peut utiliser la commande echo $NODE_ENV

module.exports = {
    runtimeCompiler: true,
    publicPath: process.env.NODE_ENV === 'production'? '/' : '/',

    
  };
  