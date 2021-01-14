export default {
    displayDateFr(date) {
        return date.split(' ')[0].split('-').reverse().join('/');
    }
}
