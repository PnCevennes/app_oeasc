<template>
<genericForm :config="configFormTest"></genericForm> 
</template>

<script>
import genericForm from '@/components/form/generic-form'
import configFormTest from './config/form-test.js'
export default {
    name: 'test-form',
    components: { genericForm },
    data: () => ({
        configFormTest
    })
}
</script>
