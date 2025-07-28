
/**
 * Fonction utilitaire pour attendre la création d'un élément dans le DOM avant d'effectuer une action dessus.
 * @param {*} selector - Sélecteur CSS de l'élément à attendre.
 * @returns {Promise<Element>} - Promise résolue avec l'élément dès qu'il est disponible dans le DOM.
 */
function waitForElm(selector) {
    return new Promise(resolve => {
        // Si l'élément existe déjà dans le DOM, on le retourne immédiatement.
        if (document.querySelector(selector)) {
            return resolve(document.querySelector(selector));
        }
        // Sinon, on utilise un MutationObserver pour surveiller les changements dans le DOM.
        const observer = new MutationObserver(mutations => {
            // À chaque mutation, on vérifie si l'élément existe.
            if (document.querySelector(selector)) {
                // Si l'élément est trouvé, on résout la promesse et on arrête l'observation.
                resolve(document.querySelector(selector));
                observer.disconnect();
            }
        });

        // On observe le body du document, en surveillant l'ajout d'enfants et les sous-arbres.
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    });
}



const STORE = {
    actions: {
        // Action pour donner le focus à un élément du formulaire après son chargement.
        // Utilise waitForElm pour attendre que l'élément soit présent dans le DOM.
        // id : sélecteur CSS de l'élément à cibler.
        focus: ({state}, id) => {
            state; // non utilisé ici, mais conservé pour la signature
            waitForElm(id).then(elem => setTimeout(() => {
                elem.focus(); // Donne le focus à l'élément après un léger délai.
            }, 100));
        },

        /**
         * Action pour rendre les boutons de suppression des champs non accessibles au clavier (tabindex -1).
         * Utile pour améliorer l'accessibilité du formulaire en évitant que ces boutons soient atteints par tabulation.
         * @param {*} param0 - Objet contenant le state (non utilisé ici).
         * @param {*} selector - Sélecteur CSS de l'élément racine à partir duquel chercher les boutons.
         */
        setClearableTabIndex: ({state}, selector) => {
            state; // non utilisé ici, mais conservé pour la signature
            // On attend que le formulaire soit chargé avant d'ajouter le tabindex.
            setTimeout(() => {
                // On récupère l'élément cible via le sélecteur, ou le document si aucun sélecteur n'est fourni.
                const elem = selector
                    ? document.querySelector(selector)
                    : document

                // Si le sélecteur ne correspond à aucun élément, on affiche une erreur.
                if (!elem) {
                    console.error(`Selector ${selector} no match`)
                    return;
                }
                // On sélectionne tous les éléments correspondant aux icônes de suppression.
                elem.querySelectorAll('.v-input__icon--clear, .mdi-close')
                    .forEach(elem =>  {
                        // Pour chaque icône, on cherche les boutons enfants et on leur attribue tabindex -1.
                        Array.from(elem.getElementsByTagName('button'))
                            .forEach(b => {
                                b.tabIndex = -1;
                            })
                        }   )
            }, 600); // Délai pour s'assurer que le DOM est prêt.
        }
    }
}

export { STORE }