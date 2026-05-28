<script>
  import {
          currentPDF,
          currentPage,
          blocks,
          file_paths,
          pageImage,
          pdfIsProcessed,
          metadata_rdy,
          changingPDF,
          selectedBlock
  } from "../../../stores/stores.js";
  import apiClient from "../../../../baseurl.js";
  import StatusMessage from "../../common/StatusMessage.svelte";
  import PDFViewer from "../../pdfView/PDFViewer.svelte";
  import PDFPageCycler from "./PDFPageCycler.svelte";

  let xmlPageDimensions = {width: 0, height: 0};

  $: pdfNames = Object.keys($file_paths);

  $: if (!$currentPDF && pdfNames.length > 0) {
    currentPDF.set(pdfNames[0]); // set the first pdf as the current one
  }

  $: if (!$currentPage) {
    currentPage.set(1); // default to the first page
  }

  $: if ($currentPDF && $currentPage) {
    pageImage.set(null);
    fetchPageData($currentPDF, $currentPage);
  }

  async function pollTaskStatus(taskId, maxAttempts = 10, interval = 2000) {
    let attempts = 0;
    while (attempts < maxAttempts) {
      try {
        const response = await apiClient.get(`/celery/task-status/${taskId}`);
        const {status} = response.data;

        if (status === "success") {
          return true; // Task completed
        } else if (status === "failure") {
          console.error("Task failed.");
          return false;
        }

        // Wait before polling again
        await new Promise((resolve) => setTimeout(resolve, interval));
      } catch (error) {
        console.error("Error polling task status:", error);
        return false;
      }
      attempts++;
    }
  }

  async function fetchPageData(pdfName, pageNumber) {
    try {
      const tmpDir = $file_paths[pdfName]["tmp_dir"].split("/")[1];
      const filename = $file_paths[pdfName]["filename"];
      const response = await apiClient.get(`pdf/${tmpDir}/${filename}/page/${pageNumber}`);
      const {status, task_id, page_image, blocks: pageBlocks, xml_page_dimensions} = response.data;

      metadata_rdy.set(false);

      if (status === "processing" || status === "started") {
        console.log("Task started/processing. Polling status...");
        if ($pdfIsProcessed) {
          pdfIsProcessed.set(false);
        }
        const taskComplete = await pollTaskStatus(task_id);
        if (taskComplete) {
          await fetchPageData(pdfName, pageNumber); // Retry fetching data after completion
        }
      } else {
        if (!$pdfIsProcessed) {
          pdfIsProcessed.set(true);
        }
        // if ($pdfIsProcessed) {
        //   setTimeout(()=>pageImage.set(`data:image/png;base64,${page_image}`), 200);
        // } else {
        //   pageImage.set(`data:image/png;base64,${page_image}`);
        // }
        pageImage.set(`data:image/png;base64,${page_image}`);
        xmlPageDimensions = xml_page_dimensions;
        blocks.set(pageBlocks);
        selectedBlock.set(pageBlocks[0].id)
        changingPDF.set(false);
      }
    } catch (error) {
      console.error("Failed to fetch page data:", error);
    }
  }

</script>

<div class="pdf-container">
  {#if $pageImage && $pageImage.length > 0}
    <div class="viewer-wrapper">
      <div class="prev-cycler"></div>
      <PDFViewer pageImage={$pageImage} pdfDimensions={xmlPageDimensions}/>
      <div class="next-cycler"></div>
    </div>
    <PDFPageCycler/>
  {:else}
      <div id="pdfStatus">
        {#if !$pdfIsProcessed}
          <StatusMessage isLoading="true" message="Processing PDF, please wait..." color="grey"/>
        {:else }
          <StatusMessage isLoading="true" message="Fetching Page" color="grey"/>
        {/if}
      </div>
  {/if}
</div>

<style>
    .pdf-container {
        position: relative;
        width: auto;
        min-width: 0;
        height: 100%;
        display: flex;
        flex-direction: column;
    }

  .viewer-wrapper {
    position: relative;
    display: flex;
    align-items: stretch;
    /*justify-content: flex-end;*/
    min-width: 0;
    /*width: fit-content;*/
    width: auto;
    height:auto;
  }

  .prev-cycler,
  .next-cycler {
    width: 5%; /* Width for the empty areas for page cycling */
    height: 100%;
    background-color: transparent;
  }

  .prev-cycler {
      pointer-events: none;
  }

  .next-cycler {
      pointer-events: none;
  }

  #pdfStatus {
      position: absolute; /* absolute positioning to center it relative to its parent */
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%); /* offset by 50% to center */
      display: flex;
      justify-content: center;
      align-items: center;
      width: 100%; /* optional, depending on your layout needs */
      height: 100%; /* optional, depending on your layout needs */
  }
  /*.viewer-wrapper > PDFViewer {*/
  /*  flex: 1;*/
  /*  position: relative;*/
  /*  z-index: 1; !* Ensure it stays above other elements *!*/
  /*}*/

  /*.viewer-wrapper > PDFPageCycler {*/
  /*  position: absolute;*/
  /*  top: 0;*/
  /*  left: 0;*/
  /*  width: 100%;*/
  /*  height: 100%;*/
  /*  pointer-events: none;*/
  /*}*/
</style>
