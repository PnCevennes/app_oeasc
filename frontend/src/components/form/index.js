const STORE = {
    actions: {
        focus: ({state}, d) => {
            state
            setTimeout(() => {
                const elem = document.getElementById(d.id);
                if(!elem) {
                    return
                }
                elem.focus();

            }, d.t || 100)
        },
        setClearableTabIndex: ({state}) => {
            state
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