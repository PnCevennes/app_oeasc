import declarationForm from './declaration-form'

const ROUTE = [
    {
        path: '/declaration/declarer_en_ligne',
        redirect: '/declaration/declarer_en_ligne/foret_statut'
    },
    {
        path: '/declaration/declarer_en_ligne/:keySession',
        label: 'declarer_en_ligne',
        access: [],
        name: 'declarer_en_ligne',
        component: declarationForm
    },
];

const STORE = {
    state: {
        _configDeclaration: {}
    },
    getters: {
        configDeclaration: (state) => {
            return state._configDeclaration
        }
    },
    mutations: {
        configDeclaration: (state, configDeclaration) => {
            state._configDeclaration = configDeclaration
        }
    },
    actions: {},
}

export { ROUTE, STORE };
