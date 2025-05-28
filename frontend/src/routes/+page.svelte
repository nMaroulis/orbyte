<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  
  onMount(() => {
    // Redirect to login page
    goto('/auth/login');
  });
</script>

<div class="flex items-center justify-center min-h-screen">
  <div class="text-center">
    <h1 class="text-2xl font-bold mb-4">Redirecting to Login...</h1>
    <p>If you are not redirected, <a href="/auth/login" class="text-blue-600 hover:underline">click here</a>.</p>
  </div>
</div>
