import {writable} from "svelte/store";

export function localStore (key, initial) {

    if (localStorage.getItem(key) === null) {
        localStorage.setItem(key, JSON.stringify(initial));
    }

    const saved = JSON.parse(localStorage.getItem(key));

    const { subscribe, set, update } = writable(saved);

    return {
        subscribe,
        set: (value) => {
            localStorage.setItem(key, JSON.stringify(value));
            return set(value);
        },
        update,
        delete: (key) =>{
            localStorage.removeItem(key);
        }
    };

}

export function sessionStore (key, initial) {

    if (sessionStorage.getItem(key) === null) {
        sessionStorage.setItem(key, JSON.stringify(initial));
    }

    const saved = JSON.parse(sessionStorage.getItem(key));

    const { subscribe, set, update } = writable(saved);

    return {
        subscribe,
        set: (value) => {
            sessionStorage.setItem(key, JSON.stringify(value));
            return set(value);
        },
        update,
        delete: (key) =>{
            sessionStorage.removeItem(key);
        }
    };

}
