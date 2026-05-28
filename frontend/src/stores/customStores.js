import {writable} from "svelte/store";


export function setStore(initial) {
    let initialSet = null;
    if (initial instanceof Set) {
        initialSet = initial
    } else {
        initialSet = new Set(initial)
    }
    const { subscribe, set, update } = writable(initialSet);
    return {
        subscribe,
        set: (value) => {
            if (value instanceof Set) {
                initialSet = value;
            } else {
                initialSet = new Set(value);
            }
            return set(initialSet);
        },
        add: (item) => {
            initialSet.add(item);
            set(initialSet);
        },
        delete: (item) => {
            initialSet.delete(item);
            set(initialSet);
        },
        has: (item) => {
            return initialSet.has(item);
        },
        clear: () => {
            initialSet.clear();
            set(initialSet);
        },
        values: () => {
            return Array.from(initialSet.values());
        },
        update,
    }
}