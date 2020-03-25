import { MapService } from './map-service.js'

const STORE = {
    state: {
        _mapServices: {}
    },
    getters: {
        mapService: (state) => (key) => {
            return state._mapServices[key]
        }
    },
    mutations: {
        setMapService: (state, mapService) => {
            state._mapServices[mapService._id] = mapService
        }
    },
    actions: {},
}

export { STORE, MapService }