<script>
  import { onMount, onDestroy } from "svelte";
  import { blocks, selectedBlock } from "../../stores/stores.js";
  import Select from "../utilComponents/Select.svelte";
  import {setStore} from "../../stores/customStores.js";

  export let pageImage; // Base64 or URL of the PDF page image
  export let pdfDimensions; // Dimensions of the original PDF (from XML)

  let scaleX = 1; // Scaling factor for horizontal coordinates
  let scaleY = 1; // Scaling factor for vertical coordinates

  let imgElement; // Reference to the image element
  let observer; // Resize observer for dynamic scaling

  let allowMultipleSelect = false;

  // Calculate scaling factors based on rendered dimensions
  function calculateScalingFactors() {
    if (imgElement && pdfDimensions) {
      const displayedWidth = imgElement.clientWidth; // Rendered width in the browser
      const displayedHeight = imgElement.clientHeight; // Rendered height in the browser

      // Calculate scale factors between the rendered size and the original PDF dimensions
      scaleX = pdfDimensions.width / displayedWidth;
      scaleY = pdfDimensions.height / displayedHeight;
    } else {
      console.error("Missing imgElement or pdfDimensions for scaling calculation.");
    }
  }

  // function handleBlockClick(block, e) {
  //   console.log("Block clicked:", block);
  //   selectedBlock.set(block.id)
  // }
  //
  function highlightBlock(e) {
    const el = e.currentTarget;
    el.classList.add("highlight");
    for (const child of el.children) {
      child.classList.add('highlight')
    }
  }

  function removeHighlightBlock(e) {
    const el = e.currentTarget;
    el.classList.remove("highlight");
    for (const child of el.children) {
      child.classList.remove('highlight')
    }
  }

  let selectedBlocks = setStore(new Set());
  let selectedBlockIds = new Set();

  $:{
      selectedBlockIds = new Set(
          $selectedBlocks.values().map((e)=> {
              if (e.classList.contains("block-id")) {
                  // return e.parentElement.id;
                  console.log(e.innerText);
              } else {
                  return e.id;
              }
          }));
  } //TODO: need to link parent with child somehow. Should add as an option to Select component


  function getAllBlockElms(withChildren=false) {
    let output = [];
    for (const block of $blocks) {
      const divElm = document.getElementById(`block-bbox-${block.id}`)
      if (divElm !== null) {
        output.push(divElm)
          if (withChildren && divElm.children.length > 0){
              console.log(withChildren);
              [...divElm.children].forEach((childElm)=>output.push(childElm));
          }
      }
    }
    return output;
  }

  let blockElements = [];

  let pdfDiv = null;


  onMount(() => {

    blockElements = getAllBlockElms(false);
    // Calculate initial scaling factors after the image loads
    if (imgElement) {

      imgElement.onload = calculateScalingFactors;
      // Set up ResizeObserver to recalculate scaling factors dynamically
      observer = new ResizeObserver(() => {
        calculateScalingFactors();
      });
      observer.observe(imgElement);

    }

  });

  onDestroy(() => {
    if (observer) {
      observer.disconnect(); // Cleanup observer on component destruction
    }

  });
  let pdfScrollContainer;
  $: {
      if (pdfDiv){
          pdfScrollContainer = pdfDiv.parentElement.parentElement.parentElement;
      }
  }
</script>

<div bind:this={pdfDiv} class="pdf-viewer" tabindex="0">
  <Select
          containerDiv={pdfDiv}
          bind:selectedElms={selectedBlocks}
          bind:selectableElements={blockElements}
          scrollContainer={pdfScrollContainer}
          throttle={15}
          syncDepth={1}
          scrollOnSelect={true}
  />
  {#each $blocks as block}
<!--        {`block-bbox-${block.id}` === selectedBlockId?'highlightSelected':''}-->
<!--        {$selectedBlockIds.has('block-bbox-'.concat(block.id)) ? 'highlightInSelBox' : ''}-->
    <div class="
          block-outline
          {selectedBlockIds.has('block-bbox-'.concat(block.id)) ? 'highlightSelected' : ''}
        "
         id="block-bbox-{block.id}"
         on:mouseenter={(e)=>highlightBlock(e)}
         on:mouseleave={(e)=>removeHighlightBlock(e)}
    style="
        left: {block.bbox[0] / scaleX}px;
        top: {block.bbox[1] / scaleY}px;
        width: {(block.bbox[2] - block.bbox[0]) / scaleX}px;
        height: {(block.bbox[3] - block.bbox[1]) / scaleY}px;
      "
    >
    <!--      on:click={() => handleBlockClick(block)}-->
      <p class="block-id {selectedBlockIds.has('block-bbox-'.concat(block.id)) ? 'highlightSelected' : ''}">{block.id}</p>
<!--      <p class="block-id {block.id === $selectedBlock?'highlightSelected':''}">{block.id}</p>-->
    </div>
  {/each}
  <img
    bind:this={imgElement}
    class="PAGE"
    src={pageImage}
    alt="PDF Page"
    style="max-height: {pdfDimensions.height*1.5}px"
  />
</div>

<style>
  .pdf-viewer {
    /*display: flex;*/
    align-content: center;
    align-items: center;
    justify-content: center;
    position: relative;
    width: fit-content;
    height: auto;
    margin: 0 auto;
  }

  :global(.block-outline.highlight) {
    border: 1px solid red !important;
    background-color: rgba(195, 255, 0, 0.05) !important;
    z-index: 90;
  }

  :global(.block-outline.highlightSelected) {
    border-color: #ff00d5 !important; /* Highlight block border */
    background-color: rgba(94, 255, 0, 0.25) !important;
    z-index: 99;
  }

  :global(.block-id.highlight) {
    border: 1px solid #ff0000 !important;
    background-color: rgb(194, 205, 187) !important;
    z-index: 90;
  }

  :global(.block-id.highlightSelected) {
    border: 2px solid #ff00d5 !important; /* Highlight block border */
    background-color: rgb(94, 255, 0) !important;
    z-index: 99;
  }

  :global(.block-outline.highlightInSelBox) {
    border: 2px solid #22ff00 !important; /* Highlight block border */
    background-color: rgba(184, 0, 255, 0.25) !important;
    z-index: 99;
  }

  .block-outline {
    position: absolute;
    pointer-events: auto;
    cursor: pointer;
    border: 2px solid blue;
  }


  .PAGE {
    min-width: 0;
    width: fit-content;
    max-width: 100%; /* Scale the image to fit the container */
    height: auto; /* Maintain aspect ratio */
    display: block; /* Prevent inline gaps below the image */
  }

  .block-id {
      background-color: lightblue;
      border: 1px black;
      width: fit-content;
      height: fit-content;
      position: absolute;
      top: 0;
      left: -1.3rem; /* Shift the label to the left of the block */
      color: blue;
      background-color: rgba(102,122,145,0.44);
      margin: 0;
      font-size: 0.5rem;
      padding: 0.1rem 0.2rem;
      white-space: nowrap;
  }

</style>
