/**
 * Read a data attribute the way jQuery `.data()` used to: JSON when the value
 * parses, the raw string otherwise.
 *
 * @param {HTMLElement} el
 * @param {string} key camelCase key (`data-ajax-onchange` -> `ajaxOnchange`)
 * @param {*} [fallback]
 */
export function readData(el, key, fallback = undefined) {
    const raw = el.dataset[key];
    if (raw === undefined) {
        return fallback;
    }
    try {
        return JSON.parse(raw);
    } catch {
        return raw;
    }
}
