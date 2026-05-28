import { writable } from "svelte/store";
import { localStore } from "./webStores.js";

export const currentPDF = writable(null);  // Current PDF file
export const currentPage = writable(1);   // Current page number
export const changingPDF = writable(false);
export const blocks = writable([]);       // Blocks for the current page
export const labels = writable([]);       // Available labels
export const metadata_rdy = writable(false);     // Metadata for the current PDF
export const metadata_sidebar_info = writable({width: 250});
export const has_uploaded = writable(false);
export const xml_generated = writable(false);
export const file_paths = localStore("filePaths", {});
export const pageImage =  writable(null);
export const pdfIsProcessed =  writable(false);
export const selectedBlock =  writable(-1);
export const savedBlocks = localStore('savedBlocks', {});


