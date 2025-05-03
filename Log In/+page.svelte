<script>
  import { supaClient } from '$lib/supabase';

  let signupEmail = '';
  let signupPassword = '';
  let loginEmail = '';
  let loginPassword = '';
  let loggedIn = false;
  let userId = null;
  let apiKeys = [];
  let allowed = 0;
  let uses = 0;
  async function signUp() {
    const { data: existing, error: checkError } = await supaClient
      .from('users')
      .select('*')
      .eq('email', signupEmail);

    if (checkError) return alert(`Error: ${checkError.message}`);
    if (existing.length > 0) return alert('Email already registered.');

    const { data, error } = await supaClient
      .from('users')
      .insert([{ email: signupEmail, password: signupPassword }])
      .select()
      .single();

    if (error) return alert(`Signup failed: ${error.message}`);

    userId = data.id;
    loggedIn = true;
    uses = data.current_requests;
    allowed = data.allowed_requests;
    await fetchApiKeys();
  }

  async function login() {
    const { data, error } = await supaClient
      .from('users')
      .select('*')
      .eq('email', loginEmail)
      .eq('password', loginPassword)
      .single();

    if (error) return alert(`Error: ${error.message}`);
    if (!data) return alert('Invalid email or password.');

    userId = data.id;
    uses = data.current_requests;
    allowed = data.allowed_requests;
    loggedIn = true;
    await fetchApiKeys();
  }

  async function fetchApiKeys() {
    const { data, error } = await supaClient
      .from('keys')
      .select('id, key, uses')
      .eq('id', userId);

    if (error) return alert(`Error fetching keys: ${error.message}`);
    apiKeys = data;
  }

  async function deleteKey(key) {
    const { error } = await supaClient
      .from('keys')
      .delete()
      .eq('key', key);

    if (error) return alert(`Failed to delete key: ${error.message}`);
    await fetchApiKeys();
  }

  async function generateKey() {
    const { error } = await supaClient
      .from('keys')
      .insert([{uses: 0, id: userId }]);

    if (error) return alert(`Failed to generate key: ${error.message}`);
    await fetchApiKeys();
  }

  function signOut() {
    loggedIn = false;
    userId = null;
    apiKeys = [];
    signupEmail = signupPassword = loginEmail = loginPassword = '';
  }
</script>

<style>
  :global(body) {
    background-color: #1a1a1a;
    font-family: 'Inter', sans-serif;
    margin: 0;
    padding: 2rem;
  }

  main {
    max-width: 800px;
    margin: 0 auto;
  }

  h2 {
    color: white;
    margin: 2rem 0 1rem;
    border-bottom: 2px solid #2a2a2a;
    padding-bottom: 0.5rem;
  }

  .auth-section {
    background: #2a2a2a;
    padding: 2rem;
    border-radius: 8px;
    margin-bottom: 2rem;
  }

  .auth-container {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 2rem;
  }

  input {
    display: block;
    width: 100%;
    padding: 0.8rem;
    margin: 0.5rem 0 1.5rem;
    background: #333;
    border: 1px solid #404040;
    border-radius: 4px;
    color: white;
  }

  input:focus {
    outline: none;
    border-color: #646cff;
    box-shadow: 0 0 0 2px rgba(100, 108, 255, 0.2);
  }

  button {
    background: #646cff;
    color: white;
    border: none;
    padding: 0.8rem 1.5rem;
    border-radius: 4px;
    cursor: pointer;
    transition: background 0.2s ease;
  }

  button:hover {
    background: #747bff;
  }

  .danger {
    background: #dc2626;
  }

  .danger:hover {
    background: #ef4444;
  }

  .key-list {
    background: #2a2a2a;
    border-radius: 8px;
    padding: 1rem;
    margin: 1rem 0;
  }

  ul {
    list-style: none;
    padding: 0;
    margin: 0;
  }

  li {
    background: #333;
    padding: 1rem;
    margin: 0.5rem 0;
    border-radius: 4px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .key-info {
    flex-grow: 1;
    margin-right: 1rem;
  }

  .key-actions {
    flex-shrink: 0;
  }
</style>

<main>
  {#if !loggedIn}
    <div class="auth-container">
      <div class="auth-section">
        <h2>Sign Up</h2>
        <input type="email" bind:value={signupEmail} placeholder="Email" />
        <input type="password" bind:value={signupPassword} placeholder="Password" />
        <button on:click={signUp}>Sign Up</button>
      </div>

      <div class="auth-section">
        <h2>Login</h2>
        <input type="email" bind:value={loginEmail} placeholder="Email" />
        <input type="password" bind:value={loginPassword} placeholder="Password" />
        <button on:click={login}>Login</button>
      </div>
    </div>
  {:else}
    <div class="auth-section">
      <h2>Your API Keys</h2>
      <h3>used {uses}/{allowed} requests</h3>
      <button on:click={generateKey}>Generate New Key</button>
      {#if apiKeys.length > 0}
        <div class="key-list">
          <ul>
            {#each apiKeys as api}
              <li>
                <div class="key-info">
                  <div><strong>Key:</strong> {api.key}</div>
                  <div><strong>Uses:</strong> {api.uses}</div>
                </div>
                <div class="key-actions">
                  <button class="danger" on:click={() => deleteKey(api.key)}>Delete</button>
                </div>
              </li>
            {/each}
          </ul>
        </div>
      {:else}
        <p style="color: #888; margin: 1rem 0;">No API keys found.</p>
      {/if}
      
      <button style="margin-top: 1rem;" on:click={signOut}>Sign Out</button>
    </div>
  {/if}
</main>

<!-- Add Inter font -->
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
