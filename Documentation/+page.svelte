<script>
let checkboxes = Array.from({ length: 11 }, () => true);
let filterArray = [];
const categoriesArray = ["Bread", "Dairy product", "Dessert", "Egg", "Fried food", "Meat", "Noodles-Pasta", "Rice", "Seafood", "Soup", "Vegetable-Fruit"];
function createFilter() {
    filterArray = checkboxes.map(checked => checked ? 1 : 0);
}
</script>

<main>
  <h1 class="title">Documentation</h1>
  
  <h2>Python</h2>
  <p>For a request to be processed a 64x64 image tensor/3-D array is required as well as a filter array which tells the server what categories to label.</p>
  <h4>Example request</h4>
  <pre><code>response = requests.post(
    'http://localhost:5000/process',
    json=&#123;'image': image_array_3d, "api-key":"YOUR API KEY", "filter":filter&#125;
)</code></pre>

  <h3>Create a Filter</h3>
  <p>Tick the boxes of the categories you want to use</p>
  
  <div class="checkbox-container">
    {#each categoriesArray as category, index}
      <label class="checkbox-label">
        <input 
          type="checkbox" 
          bind:checked={checkboxes[index]}
          class="checkbox-input"
        >
        {category}
      </label>
    {/each}
  </div>

  <button on:click={createFilter} class="create-button">
    Create Filter
  </button>

  {#if filterArray.length > 0}
    <div class="output">
      Result: [{filterArray.join(', ')}]
    </div>
  {/if}
</main>

<!-- Add Fira Code font for code blocks -->
<link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
