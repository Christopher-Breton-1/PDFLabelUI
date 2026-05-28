<script>
  import PDFContainer from "./pdfGroup/PDFContainer.svelte";
  import PDFCycler from "./pdfGroup/PDFCycler.svelte";
  import LabellingContainer from "./pdfGroup/LabellingContainer.svelte";
  import PDFMetaDataSidebar from "./bars/PDFMetaDataSidebar.svelte";

  import {
      has_uploaded,
      xml_generated,
      metadata_sidebar_info,
      changingPDF,
      selectedBlock,
      blocks, metadata_rdy,
  } from "../../stores/stores.js";
  import { onDestroy, onMount } from "svelte";


  let isSidebarVisible = false;
  let fromToggle = false;
  let sidebarWidth = 0;

  $: sidebarWidth = isSidebarVisible ? $metadata_sidebar_info.width : 0;

  onMount(() => {
    window.addEventListener("keydown", handleKeyPress);
  });

  onDestroy(() => {
    window.removeEventListener("keydown", handleKeyPress);
  });

  function handleKeyPress(e) {
    const key = e.key;
    const shift = e.shiftKey;
    if (key === "Tab") e.preventDefault();
    if (key === "Tab" && shift) {
      if ($blocks.length > 0) {
        const minBId = $blocks[0].id;
        if ($selectedBlock > minBId) {
          selectedBlock.set($selectedBlock - 1);
        } else {
          selectedBlock.set($blocks[$blocks.length - 1].id);
        }
      }
    }
    if (key === "Tab" && !shift) {
      if ($blocks.length > 0) {
        const maxBId = $blocks[$blocks.length - 1].id;
        if ($selectedBlock < maxBId) {
          selectedBlock.set($selectedBlock + 1);
        } else {
          selectedBlock.set($blocks[0].id);
        }
      }
    }
  }

  $: {
      if ($changingPDF) {
          fromToggle = !$changingPDF;
      }
  }

  $: {
    if (!fromToggle) {
        isSidebarVisible = !$changingPDF ;
    }
  }

  function toggleSidebar() {
      isSidebarVisible = !isSidebarVisible;
  }

  $: if (!$has_uploaded || !$xml_generated) {
    console.error("PDF not ready for labeling.");
  }


  //--------

    let sidebarMinWidth = 250;

    $: if (isSidebarVisible) {
        sidebarWidth = $metadata_sidebar_info?.width ?? sidebarMinWidth;
    } else {
        sidebarWidth = 0;
    }

    $: if ($metadata_sidebar_info.width < sidebarMinWidth) {
        metadata_sidebar_info.set({"width": sidebarMinWidth})
    }

    $:{
        if (sidebarWidth > sidebarMinWidth) {
            metadata_sidebar_info.set({"width": sidebarWidth})
        }
    }

    $:{
        if ($metadata_sidebar_info.minWidth === undefined) {
            metadata_sidebar_info.update((sbinfo) => {
                sbinfo.minWidth = sidebarMinWidth
                return sbinfo
            })
        }
    }

    $:$metadata_sidebar_info.width!==undefined
        ?sidebarWidth = $metadata_sidebar_info.width
        :sidebarWidth = sidebarMinWidth

    $: sidebarWidth = isSidebarVisible
        ? ($metadata_sidebar_info?.width ?? sidebarMinWidth)
        : 0;



    const resize = (e) => {
        if (isResizing) {
            sidebarWidth = Math.max(200, Math.min(e.pageX, 500)); // Min 150px, Max 500px
        }
    };

    let isResizing = false;

    const startResize = (e) => {
        e.preventDefault();
        isResizing = true;
        document.body.style.cursor = "ew-resize"; // Set cursor globally
        document.body.style.userSelect = "none"; // Prevent text selection
        document.addEventListener("mousemove", resize);
        document.addEventListener("mouseup", stopResize);
    };

    const stopResize = () => {
        isResizing = false;
        document.body.style.cursor = ""; // Reset cursor
        document.body.style.userSelect = ""; // Restore text selection
        document.removeEventListener("mousemove", resize);
        document.removeEventListener("mouseup", stopResize);
    };

    onMount(() => {
        console.clear();
    });

    // Clean up event listeners
    onDestroy(() => {
        document.removeEventListener("mousemove", resize);
        document.removeEventListener("mouseup", stopResize);
    });



</script>

<div class="label-ui-container">
    <div id="pageCycler">
        <PDFCycler />
    </div>
    <div id="pdfGroup">
        <div
            class="sidebar-wrapper {isResizing?'no-transition':''}"
            style="width: {sidebarWidth}px;"
        >
        <svg
            on:click={toggleSidebar}
            class="sidebar-toggle-btn"
            style="
                right: {isSidebarVisible? 0.2 : -1.5}rem;
                top: 0.2rem;
        ">
            {#if isSidebarVisible}
                <path fill="none" d="M0 0h24v24H0V0z" />
                <path d="M15.41 7.41L14 6l-6 6 6 6 1.41-1.41L10.83 12l4.58-4.59z" />
            {:else}
                <path fill="none" d="M0 0h24v24H0V0z" />
                <path d="M10 6L8.59 7.41 13.17 12l-4.58 4.59L10 18l6-6-6-6z" />
            {/if}
        </svg>
        {#if isSidebarVisible}
            <div class="sidebar-content"
                 style="left: {isSidebarVisible ? '0px' : '-100%'};"
            >
                <PDFMetaDataSidebar isVisible={isSidebarVisible}/>
                <div class="resize-handle" on:mousedown={startResize}></div>
            </div>
        {/if}

    </div>
    <div class="main-content">
        <div id="pdf">
            <PDFContainer />
        </div>
        <div id="labels">
            <LabellingContainer />
        </div>
    </div>
  </div>
</div>

<style>
    .label-ui-container {
        position: relative;
        display: flex;
        flex-direction: column;
        height: 100%;
        margin: 0;
        padding: 1rem;
        max-width: 100dvw;
        width: 100%;
        min-width: 0;
        box-sizing: border-box;
        overflow: auto;
    }

    #pdfGroup {
        display: flex;
        flex-direction: row;
        height: 100%;
        width: 100%;
        gap: 1rem;
        flex-grow: 1;
        min-height: 0;
        min-width: 0;
    }

    .no-transition {
        transition: none !important;
    }

    .sidebar-wrapper {
        display: flex;
        flex-direction: row;
        position: relative;
        height: 100%;
        transition: width 0.4s ease-in-out;
        border-right: 1px solid dimgrey;
        border-top: 1px solid dimgrey;
        border-top-right-radius: 1rem;
        overflow-x: visible;
        /*overflow-y: hidden;*/
    }

    .main-content {
        height: 100%;
        min-height: 0;
        max-width: 80dvw;
        width: fit-content;
        min-width: 0;
        display: flex;
        flex-direction: row;
        flex-grow: 1;
        gap: 1rem;
        margin: 0 auto;
        padding: 0;
        overflow: hidden;
        /*transition: width 0.4s ease-in-out;*/
    }

    #pdf {
        height: 100%;
        min-height: 0;
        min-width: 0;
        flex: 2;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-content: center;
        overflow: auto;
    }

    #labels {
        display: flex;
        /*justify-content: center;*/
        /*align-items: center;*/
        height: 100%;
        min-height: 0;
        /*width: 30%;*/
        flex: 1;
        border: 1px solid #ddd;
        border-radius: 5px;
        background-color: #fff;
        overflow-y: auto;
    }

    .sidebar-toggle-btn {
        position: absolute;
        /*top: 4.5rem;*/
        align-self: start;
        width: 1.5rem;
        height: 1.5rem;
        cursor: pointer;
        z-index: 999;
        fill: #595959;
        border-radius: 0.2rem;
        transition: left 0.4s ease-in-out; /* Smooth movement with the sidebar */
    }

    .sidebar-toggle-btn:hover {
        background-color: #3b3b3f;
        fill: #dcdcdc;
    }

    .resize-handle {
        /*background-color: red;*/
        position: absolute; /* take it out of the normal flow */
        right: 0; /* align it to the right edge of its parent */
        top: 0; /* align it to the top edge */
        width: 0.5rem; /* set a fixed width */
        height: 100%; /* span the full height of the parent */
        cursor: ew-resize; /* make it resizable */
        z-index: 999; /* ensure it overlaps other items */
        pointer-events: all; /* allow it to be interactive */
    }

    .sidebar-content {
        /*position: absolute;*/
        /*top: 0;*/
        /*left: 0; !* Default position when visible *!*/
        overflow: hidden;
        width: 100%;
        height: 100%;
        transition: left 0.4s ease-in-out; /* Smoothly follow the parent container */
    }


</style>

