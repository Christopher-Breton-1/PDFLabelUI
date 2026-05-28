<script>
  import Upload from "../upload/Upload.svelte";
  import StatusMessage from "../common/StatusMessage.svelte";
  import { writable } from "svelte/store";
  import apiClient from "../../../baseurl.js";
  import {has_uploaded, xml_generated, file_paths} from "../../stores/stores.js";

  // state for upload and XML generation process
  let uploadState = writable({
    status: "idle", // "idle" | "uploading" | "uploaded" | "generating" | "generated"
    message: "",
    color: "grey", // grey for default, green for success, red for error
    isLoading: false,
  });

  // handle file upload
  async function handleFileUpload(file) {
    uploadState.set({
      status: "uploading",
      message: "Uploading...",
      color: "grey",
      isLoading: true,
    });

    const formData = new FormData();
    formData.append("file", file);

    try {
      // TODO: THIS SHOULD BE CONTAINED IN THE UPLOAD COMPONENT
      const response = await apiClient.post("/upload/", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      uploadState.set({
        status: "uploaded",
        message: "Uploaded successfully",
        color: "green",
        isLoading: false,
      });
      has_uploaded.set(true);

      // generate XML after successful upload
      await generateXML(response.data.pdfs, response.data.temp_dirname);
    } catch (error) {
      console.error("Upload failed:", error);
      uploadState.set({
        status: "error",
        message: "Upload failed. Please try again.",
        color: "red",
        isLoading: false,
      });
    }
  }

  // handle XML generation
  async function generateXML(pdfList, tmpDir) {
    uploadState.set({
      status: "generating",
      message: "Generating XML...",
      color: "grey",
      isLoading: true,
    });

    try {
      const response = await apiClient.post(
              "/xml/generate_batch",
              {
                pdf_files: pdfList,
                tmp_dirname: tmpDir,
              }
      );
      if (response.status === 200) {
        uploadState.set({
          status: "generated",
          message: "XML successfully generated",
          color: "green",
          isLoading: false,
        });
      }
      file_paths.set(response.data)
      setTimeout(xml_generated.set, 1000, true);
    } catch (error) {
      console.error("XML generation failed:", error);
      uploadState.set({
        status: "error",
        message: "XML generation failed. Please try again.",
        color: "red",
        isLoading: false,
      });
    }
  }
</script>

<div class="container">
  {#if $uploadState.status === "idle"}
    <Upload onFileSelected="{handleFileUpload}" />
  {:else}
    <StatusMessage
      message="{$uploadState.message}"
      color="{$uploadState.color}"
      isLoading="{$uploadState.isLoading}"
    />
  {/if}
</div>

<style>
  .container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 16px;
    margin-top: 2rem;
  }
</style>
