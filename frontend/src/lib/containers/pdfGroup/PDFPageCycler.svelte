<script>
  import {currentPage, selectedBlock, file_paths, currentPDF} from "../../../stores/stores.js";
  import {onMount, onDestroy} from "svelte";

  let showPrev = false;
  let showNext = false;


  function nextPage() {
    if ($currentPage < $file_paths[$currentPDF]["num_pages"]) {
      currentPage.update((page) => page + 1);
      selectedBlock.set(-1);
    }
  }

  function prevPage() {
    if ($currentPage > 1){
      currentPage.update((page) => Math.max(1, page - 1));
      selectedBlock.set(-1);
    }
  }

  function handleKeyPress(event) {
    if (!event.shiftKey && event.key === "ArrowLeft") {
      prevPage();
    } else if (!event.shiftKey && event.key === "ArrowRight") {
      nextPage();
    }
  }

  onMount(() => {
    window.addEventListener("keydown", handleKeyPress);
  });

  onDestroy(() => {
    window.removeEventListener("keydown", handleKeyPress);
  });
</script>

<div class="page-cycler-overlay">
  <div
          class="prev-column"
          on:mouseenter={() => (showPrev = true)}
          on:mouseleave={() => (showPrev = false)}
          on:click={prevPage}
  >
    {#if showPrev}
      <span class="page-cycler-text">&lt;</span>
    {/if}
  </div>

  <div
          class="next-column"
          on:mouseenter={() => (showNext = true)}
          on:mouseleave={() => (showNext = false)}
          on:click={nextPage}
  >
    {#if showNext}
      <span class="page-cycler-text">&gt;</span>
    {/if}
  </div>
</div>

<style>
  .page-cycler-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    display: flex;
    justify-content: space-between;
    pointer-events: none;
  }

  .prev-column,
  .next-column {
    width: 4%; /* Thin hover area */
    height: 100%;
    pointer-events: auto; /* Enable hover interaction */
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0;
    padding: 0;
  }


  .prev-column:hover,
  .next-column:hover {
    cursor: pointer;
     background-color: rgba(119, 119, 119, 0.5);
  }

  .prev-column:hover .page-cycler-text,
  .next-column:hover .page-cycler-text {
    opacity: 1;
  }

  .page-cycler-text {
    color: white;
    background-color: rgba(0, 0, 0, 0.5);
    padding-left: 0.2rem;
    padding-right: 0.2rem;
    border-radius: 5px;
    font-size: 1rem;
    opacity: 0;
    transition: opacity 0.3s;
  }
</style>
