<script>
  import {blocks, labels, selectedBlock} from "../../../stores/stores.js";

  // Define available labels
  const availableLabels = ["Pick_label", "Title", "Author", "Abstract", "Discard"];
  // TODO it will be better to request valid labels from the backend.
  labels.set(availableLabels);

  // Find the currently selected block within the filtered blocks
  $: currentBlock = $blocks.find((block) => block.id === $selectedBlock);
  // $: console.log(`Block ${currentBlock.id}: `, currentBlock.text)
  // $: console.log($selectedBlock)

  function updateLabel(label) {
    if (currentBlock) {
      const updatedBlocks = [...$blocks];
      const blockToUpdate = updatedBlocks.find((b) => b.id === currentBlock.id);
      if (blockToUpdate) {
        blockToUpdate.label = label;
        blocks.set(updatedBlocks);
      }
    }
  }

  function nextBlock() {
    const currentIndex = $blocks.findIndex((b) => b.id === $selectedBlock);
    if (currentIndex !== -1 && currentIndex < $blocks.length - 1) {
      selectedBlock.set($selectedBlock + 1);
    } else {
      selectedBlock.set($blocks[0].id)
    }
  }

  function prevBlock() {
    const currentIndex = $blocks.findIndex((b) => b.id === $selectedBlock);
    if (currentIndex > 0) {
      selectedBlock.set($selectedBlock - 1);
    }
  }

</script>

<div class="labelling-container">
  <div id="labelTop">
    {#if $blocks.length > 0}
      <div class="block-label">
      {#if $selectedBlock !== -1 && currentBlock}
          <span>Block {$selectedBlock}: {currentBlock.text.slice(0, 50)}{currentBlock.text.length<=50?"":"..."}</span>
          <select on:change={(e) => updateLabel(e.target.value)}>
            {#each $labels as label}
              <option value={label} selected={currentBlock.label.toLowerCase() === label.toLowerCase()}>
                {label}
              </option>
            {/each}
          </select>
      {/if}
      </div>
      <div class="navigation">
        <button
                on:click={prevBlock}
                disabled={$selectedBlock===-1?true:$blocks.findIndex((b) => b.id === $selectedBlock) === 0}
        >
          Previous
        </button>
        <button
                on:click={nextBlock}
                disabled={$blocks.findIndex((b) => b.id === $selectedBlock) === $blocks.length - 1}
        >
          Next
        </button>
      </div>
    {:else}
      <p>No blocks available for labeling on this page.</p>
    {/if}
  </div>
  <div id="labelGroups">

  </div>
</div>

<style>
  .labelling-container {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    margin: 1rem;
    height: auto;
    width: 100%;
    flex-grow: 1;
    color: black;
  }

  .block-label {
    flex: 2;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
  }

  select {
    padding: 0.5rem;
    border: 1px solid #ddd;
    border-radius: 5px;
  }

  #labelTop {
    flex: 2;
    display: flex;
    flex-direction: column;
    border-bottom: 0.1rem solid rgb(30, 31, 34);
    padding: 1rem;
    position: relative;
    /*flex-grow: 1;*/
  }

  #labelGroups {
    flex: 8;
    display: flex;
  }

  .navigation {
    flex: 1;
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    margin-top: 1rem;
    height: 100%;
  }


  button {
    padding: 0.5rem 1rem;
    border: 1px solid #ddd;
    border-radius: 5px;
    background-color: #f9f9f9;
    cursor: pointer;
    color: black;
    height: 2.5rem;
    justify-content: center;
    align-items: center;
    text-align: center;
  }
  button:disabled {
    background-color: #e0e0e0;
    cursor: not-allowed;
  }
</style>
