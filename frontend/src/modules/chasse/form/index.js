 

// attendre que l'element soit créé pour l'action focus
function waitForElm(selector) {
    return new Promise(resolve => {
        // si l'element existe deja, on le retourne tout simplement
        if (document.querySelector(selector)) {
            return resolve(document.querySelector(selector));
        }
        // sinon on attend qu'il soit créé
        const observer = new MutationObserver(mutations => {
            mutations
            if (document.querySelector(selector)) {
                resolve(document.querySelector(selector));
                observer.disconnect();
            }
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    });
}


// ajoute une fonction de temporisation sur les formulaire dynamique pour éviter 
// surtout pour améliorier l'accessibilité
const STORE = {
    actions: {
        // focus sur un élément du formulaire après son chargement
        focus: ({state}, id) => {
            state;
            waitForElm(id).then(elem => setTimeout(() => {
                elem.focus();
            }, 100));
        },
        setClearableTabIndex: ({state}, selector) => {
            state;
            // on attend que le formulaire soit chargé pour ajouter le tabindex
            setTimeout(() => {
                const elem = selector
                    ? document.querySelector(selector)
                    : document

                // si le selecteur n'existe pas, on affiche un message d'erreur
                if (!elem) {
                    console.error(`Selector ${selector} no match`)
                    return;
                }
                // on ajoute un tabindex de -1 sur les boutons de suppression des champs
                elem.querySelectorAll('.v-input__icon--clear, .mdi-close')
                    .forEach(elem =>  {
                        elem.getElementsByTagName('button').
                            forEach(b => {
                                b.tabIndex = -1;
                            })
                        }   )
            }, 600);
        }
    }
}

export { STORE }