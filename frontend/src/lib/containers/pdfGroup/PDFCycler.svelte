<script>
  import {
    currentPDF,
    currentPage,
    file_paths,
    selectedBlock,
    changingPDF
  } from "../../../stores/stores.js";
  import {onDestroy, onMount} from "svelte";

  let pdfNames = Object.keys($file_paths);

  $: if (!$currentPDF && pdfNames.length > 0) {
    currentPDF.set(pdfNames[0]); // set the first pdf as the current one
  }

  $: if (!$currentPage) {
    currentPage.set(1); // default to the first page
  }

  function nextPDF() {
    const currentIndex = pdfNames.indexOf($currentPDF);
    if (currentIndex !== -1 && currentIndex < pdfNames.length - 1) {
      changingPDF.set(true);
      currentPDF.set(pdfNames[currentIndex + 1]);
      currentPage.set(1);
      selectedBlock.set(-1);
    }
  }

  function previousPDF() {
    const currentIndex = pdfNames.indexOf($currentPDF);
    if (currentIndex > 0) {
      changingPDF.set(true);
      currentPDF.set(pdfNames[currentIndex - 1]);
      currentPage.set(1);
      selectedBlock.set(-1);
    }
  }

  function handleKeyPress(event) {
    if (event.shiftKey && event.key === "ArrowLeft") {
      previousPDF();
    } else if (event.shiftKey && event.key === "ArrowRight") {
      nextPDF();
    }
  }


  onMount(() => {
    window.addEventListener("keydown", handleKeyPress);
  });

  onDestroy(() => {
    window.removeEventListener("keydown", handleKeyPress);
  });
</script>

<div class="pdf-cycler">
  <button on:click="{previousPDF}" disabled="{pdfNames.indexOf($currentPDF) === 0}">
    Previous PDF
  </button>
  <button on:click="{nextPDF}" disabled="{pdfNames.indexOf($currentPDF) === pdfNames.length - 1}">
    Next PDF
  </button>
</div>

<style>
  .pdf-cycler {
    display: flex;
    justify-content: space-between;
    margin-bottom: 1rem;
    max-width: 98dvw;
  }

  button {
    padding: 0.5rem 1rem;
    border: none;
    background-color: #007bff;
    color: white;
    cursor: pointer;
    border-radius: 5px;
  }

  button:disabled {
    background-color: #cccccc;
    cursor: not-allowed;
  }
</style>
