<script>

  import apiClient from "../../../../baseurl.js";
  import {file_paths, currentPDF, metadata_rdy} from "../../../stores/stores.js";

  let metadata = null;

  $: {
    if ($currentPDF) {
      fetchPageData($currentPDF);
    }
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
// TODO: I now realise that the pdf has to be processed for metadata to come out of it.
//           This means that it is probably useless to get it separately from the main pdf.
  async function fetchPageData(pdfName) {
  try {
    const tmpDir = $file_paths[pdfName]["tmp_dir"].split("/")[1];
    const filename = $file_paths[pdfName]["filename"];
    const response = await apiClient.get(`pdf/metadata/${tmpDir}/${filename}`);
    // console.log("API Response:", response.data);

    const { status, task_id, metadata: fetchedMetadata } = response.data;

    if (status === "processing" || status === "started") {
      // console.log("Task started/processing. Polling status...");
      const taskComplete = await pollTaskStatus(task_id);
      if (taskComplete) {
        await fetchPageData(pdfName); // Retry fetching data after completion
      }
    } else if (fetchedMetadata) {
      metadata = fetchedMetadata; // Update metadata
      // isVisible = true; // Show sidebar
        metadata_rdy.set(true);
      // console.log("Metadata updated:", metadata);
    }
  } catch (error) {
    console.error("Failed to fetch page data:", error);
  }
}

  export let isVisible;

  let visTimer = false;

  $:{
    isVisible?
            setTimeout(()=> {
      visTimer = true
    }, 400)
            : visTimer = false;
  }

</script>

<div class="sb-group">
  {#if metadata !== null}
    <div class="metadata-container {isVisible&&visTimer?'':'no-overflow'}">
      {#each Object.keys(metadata) as key}
        <div class="metadata-item">
          <p class="metadata-key">{key}:</p>
          <p class="metadata-value">{metadata[key]}</p>
        </div>
      {/each}
    </div>
  {/if}
</div>

<style>
    .sb-group {
        display: flex;
        flex-direction: row;
        flex-grow: 1;
        padding: 1rem; /* Add padding for better spacing */
        height: 100%;
        position: relative;
        background-color: inherit;
        /*z-index: 998;*/
        color: inherit;
        font-family: Arial, sans-serif; /* Cleaner font */
        font-size: 0.9rem;
        text-wrap: normal;
      /*overflow: hidden;*/
    }

    .metadata-container {
        flex: 40;
        margin: 0;
        padding-top: 1rem;
        display: flex;
        flex-direction: column;
        gap: 1.5rem; /* Add space between metadata items */
        text-align: left; /* Ensure text is left-aligned */
        height: 100%;
      width: inherit;
        overflow-y: auto;
        padding-right: 0.3rem;
    }

    .no-overflow {
      overflow: hidden !important;
    }

    .metadata-item {
        margin: 0;
        display: flex;
        /*gap: 0.1rem; !* Space between key and value *!*/
        gap: 0;
        word-wrap: break-word; /* Prevent long text from breaking layout */
        flex-direction: column;
    }

    .metadata-key {
        margin:0;
        font-weight: bold; /* Make the key bold */
        color: #8a8a8a; /* Slightly darker text color for contrast */
    }

    .metadata-value {
        margin: 0;
        /*color: #666; !* Lighter text color for values *!*/
        font-size: 0.8rem;
    }


    .transition-sb-cont {
        height: 100%;
        width: auto;
        overflow: hidden; /* Prevent scrollbars during transition */
    }
</style>