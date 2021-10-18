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
            waitForElm(id).then(elem => setTimeout(() => elem.focus(), 100));
        },
        setClearableTabIndex: ({state}) => {
            state;
            setTimeout(() => {
                document.getElementsByClassName('v-input__icon--clear')
                    .forEach(elem =>
                        elem.getElementsByTagName('button').
                            forEach(b => {
                                b.tabIndex = -1;
                            })
                    )
            }, 600);
        }
    }
}

export { STORE }