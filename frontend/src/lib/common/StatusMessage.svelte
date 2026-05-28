<script>
  export let message = "";
  export let color = "grey"; // "grey" | "green" | "red"
  export let isLoading = false;
</script>

<div class="status-container" style="color: {color}">
  {#if isLoading}
    <div class="spinner"></div>
  {/if}
  <span>{message}</span>
</div>

<style>
  .status-container {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 16px;
  }

  .spinner {
    width: 16px;
    height: 16px;
    border: 2px solid #ccc;
    border-top: 2px solid #555;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }

  @keyframes spin {
    0% {
      transform: rotate(0deg);
    }
    100% {
      transform: rotate(360deg);
    }
  }
</style>
