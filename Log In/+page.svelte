<script>
  import { supaClient } from '$lib/supabase';

  let signupEmail = '';
  let signupPassword = '';
  let loginEmail = '';
  let loginPassword = '';
  let loggedIn = false;
  let userId = null;
  let apiKeys = [];

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

<main>
  {#if !loggedIn}
    <h2>Sign Up</h2>
    <input type="email" bind:value={signupEmail} placeholder="Email" />
    <input type="password" bind:value={signupPassword} placeholder="Password" />
    <button on:click={signUp}>Sign Up</button>

    <h2>Login</h2>
    <input type="email" bind:value={loginEmail} placeholder="Email" />
    <input type="password" bind:value={loginPassword} placeholder="Password" />
    <button on:click={login}>Login</button>
  {:else}
    <h2>Your API Keys</h2>
    <button on:click={generateKey}>Generate New Key</button>
    {#if apiKeys.length > 0}
      <ul>
        {#each apiKeys as api}
          <li>
            <strong>Key:</strong> {api.key} <br />
            <strong>Uses:</strong> {api.uses}
            <br />
            <button on:click={() => deleteKey(api.key)}>Delete</button>
          </li>
        {/each}
      </ul>
    {:else}
      <p>No API keys found.</p>
    {/if}
    <button on:click={signOut}>Sign Out</button>
  {/if}
</main>

