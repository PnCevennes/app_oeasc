<template>
<span>
    <span>{{val}}</span>
</span>
</template>

<script>
export default {
    name: "val",
    props: ["action", "value", "fieldName", "storeName"],
    data: () => ({
        val: null,
    }),
    methods: {
        processVal() {
            if (this.storeName && this.value) {
                const configStore = this.$store.getters.configStore(this.storeName);
                const value = this.value;
                const fieldName = this.fieldName;
                this.$store.dispatch(configStore.get, {value, fieldName}).then((val) => {this.val = val[configStore.displayFieldName]});
            }
            if (this.action && this.value) {
                this.$store.dispatch(this.action, this.value).then((val) => {this.val = val})
            }
        }
    },
    watch: {
        value: {
            handler() { this.processVal() },
            deep: true
        }
    }
    ,
    mounted() {
        this.processVal()
    }
}
</script>