<script lang="ts">
  import '../app.css';
  import Navbar from '$lib/components/layout/Navbar.svelte';
  import { page } from '$app/stores';
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  
  let { children } = $props();
  
  // Check if user is authenticated (you might want to replace this with your actual auth check)
  let isAuthenticated = $state(true); // Using Svelte 5 state
  
  // Check if current route is an auth route
  const isAuthRoute = $derived($page.url.pathname.startsWith('/auth'));
  
  // Effect to handle authentication redirect
  $effect(() => {
    if (typeof window !== 'undefined' && !isAuthenticated && !isAuthRoute) {
      goto('/auth/login');
    }
  });
</script>

<div class="min-h-screen bg-gray-50 flex flex-col">
  {#if isAuthenticated && !isAuthRoute}
    <Navbar />
  {/if}
  <main class="flex-1">
    {@render children()}
  </main>
</div>
