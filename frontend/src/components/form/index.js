function waitForElm(selector) {
    return new Promise(resolve => {
        if (document.querySelector(selector)) {
            return resolve(document.querySelector(selector));
        }
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

const STORE = {
    actions: {
        focus: ({state}, id) => {
            state;
            waitForElm(id).then(elem => setTimeout(() => {
                elem.focus();
            }, 100));
        },
        setClearableTabIndex: ({state}, selector) => {
            state;
            setTimeout(() => {
                const elem = selector
                    ? document.querySelector(selector)
                    : document
                if (!elem) {
                    console.error(`Selector ${selector} no match`)
                    return;
                }
                // mdi-close
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