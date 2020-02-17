/** Functions utiles */

var copy = (obj) => JSON.parse(JSON.stringify(obj));

var htmlToElement = (html) => {
    var template = document.createElement('template');
    template.innerHTML = html.trim();

    return template.content.firstChild;
}

var removeDoublons = (array) => [...new Set(array)];

export { copy, htmlToElement, removeDoublons };
