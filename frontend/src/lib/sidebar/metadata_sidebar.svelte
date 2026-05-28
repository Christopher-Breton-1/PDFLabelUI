<script>
  import { metadata } from "../stores";
</script>

<div class="metadata-sidebar">
  <h2>Metadata</h2>
  {#if $metadata}
    <ul>
      {#each Object.entries($metadata) as [key, value]}
        <li><strong>{key}</strong>: {value}</li>
      {/each}
    </ul>
  {/if}
</div>

<style>
  .metadata-sidebar {
    width: 20%;
    padding: 1rem;
    border-right: 1px solid #ddd;
  }
</style>
