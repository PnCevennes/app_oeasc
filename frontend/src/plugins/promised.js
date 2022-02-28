import Vue from 'vue'
import { Promised, usePromise } from 'vue-promised'

Vue.component('Promised', Promised)
export default {
  setup() {
    const usersPromise = ref(fetchUsers())
    const promised = usePromise(usersPromise)

    return {
      ...promised,
    }
  },
}