<script>
  export let onFileSelected;

  let selectedFile = null;

  function handleFileChange(event) {
    const files = event.target.files;
    if (files.length > 0) {
      selectedFile = files[0];
      onFileSelected(selectedFile);
    }
  }

  function handleDrop(event) {
    event.preventDefault();
    const files = event.dataTransfer.files;
    if (files.length > 0) {
      selectedFile = files[0];
      onFileSelected(selectedFile);
    }
  }

  function handleDragOver(event) {
    event.preventDefault();
  }
</script>

<div
  class="upload-container"
  on:drop="{handleDrop}"
  on:dragover="{handleDragOver}"
>
  <h3>Drag & Drop a ZIP File to Upload</h3>
  <input type="file" accept=".zip" on:change="{handleFileChange}" id="fileInput" />
  <label for="fileInput" style="cursor: pointer;">...or click here to select a file 👅</label>
</div>

<style>
  .upload-container {
    padding: 1rem;
    border: 2px solid #667a91;
    border-radius: 5px;
    text-align: center;
    max-width: 400px;
    margin: auto;
  }

  .upload-container input {
    display: none;
  }

  .upload-container.drag-over {
    background-color: #b6cfdc;
  }
</style>
