<script>
    import UploadGroupContainer from "./UploadGroupContainer.svelte";
    import {has_uploaded, xml_generated, file_paths} from "../../stores/stores.js";
    import PDFLabelUIContainer from "./PDFLabelUIContainer.svelte";
    import apiClient from "../../../baseurl.js";


    async function handleDelete(){
        try {
          await apiClient.delete("/rmfiles")
            $has_uploaded = false;
            $xml_generated = false;
            $file_paths = {};
            console.log("Files deleted", $has_uploaded, $xml_generated, $file_paths)
        }
        catch (error) {
          console.log(error.message)
        }
    }

</script>

<div id="main-container">
    <div id="delButton">
        <button id="delfiles" on:click={handleDelete}>
            DELETE FILES
        </button>
    </div>
    {#if (!$has_uploaded || !$xml_generated) && Object.keys($file_paths).length === 0}
        <UploadGroupContainer/>
    {:else }
        <PDFLabelUIContainer/>
    {/if}

</div>

<style>
    #main-container {
        display: flex;
        flex-direction: column;
        max-height: 100%;
        overflow: auto; /* Prevent scrollbars */
        padding: 0;
        margin: 0; /* Remove any default margins */
        flex-grow: 1;
        flex-shrink: 0;
    }
    #delButton {
        flex-shrink: 1;
        padding: 0;
        margin: 0;
    }

</style>
