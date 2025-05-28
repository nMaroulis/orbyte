<script lang="ts">
  import { page } from '$app/stores';
  import { user } from '$lib/stores/auth';
  import { onMount } from 'svelte';
  import { AuthService } from '$lib/services/auth.service';
  import Button from '$lib/components/ui/Button.svelte';
  
  let currentPath = '';
  let isMenuOpen = false;
  
  $: isActive = (path: string) => currentPath === path;
  
  const navItems = [
    { name: 'Dashboard', path: '/dashboard' },
    { name: 'GPUs', path: '/gpus' },
    { name: 'Tasks', path: '/tasks' },
    { name: 'Payments', path: '/payments' },
  ];
  
  function toggleMenu() {
    isMenuOpen = !isMenuOpen;
  }
  
  function handleLogout() {
    AuthService.logout();
  }
  
  $: {
    if (typeof window !== 'undefined') {
      currentPath = window.location.pathname;
    }
  }
</script>

<header class="bg-white shadow-sm">
  <nav class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8" aria-label="Top">
    <div class="flex justify-between h-16">
      <div class="flex items-center
        <a href="/" class="flex items-center">
          <span class="text-xl font-bold text-blue-600">Orbyte</span>
        </a>
        
        <!-- Desktop Navigation -->
        <div class="hidden md:ml-10 md:flex md:space-x-8">
          {#each navItems as item}
            <a 
              href={item.path}
              class="inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium {isActive(item.path) 
                ? 'border-blue-500 text-gray-900' 
                : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'}"
            >
              {item.name}
            </a>
          {/each}
        </div>
      </div>
      
      <div class="hidden md:flex items-center space-x-4">
        {#if $user}
          <div class="flex items-center
            <span class="text-sm text-gray-700 mr-4">
              {#if $user.email}
                {($user.email.match(/^[^@]+/) || [''])[0]}
              {/if}
            </span>
            <Button variant="outline" size="sm" on:click={handleLogout}>
              Sign out
            </Button>
          </div>
        {:else}
          <a href="/login" class="text-sm font-medium text-gray-500 hover:text-gray-900">
            Sign in
          </a>
          <a 
            href="/register" 
            class="ml-8 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            Sign up
          </a>
        {/if}
      </div>
      
      <!-- Mobile menu button -->
      <div class="-mr-2 flex items-center md:hidden">
        <button 
          type="button" 
          class="bg-white rounded-md p-2 inline-flex items-center justify-center text-gray-400 hover:text-gray-500 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-blue-500"
          on:click={toggleMenu}
          aria-expanded="false"
        >
          <span class="sr-only">Open main menu</span>
          <svg 
            class="h-6 w-6" 
            xmlns="http://www.w3.org/2000/svg" 
            fill="none" 
            viewBox="0 0 24 24" 
            stroke="currentColor" 
            aria-hidden="true"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
      </div>
    </div>
  </nav>
  
  <!-- Mobile menu, show/hide based on menu state. -->
  {#if isMenuOpen}
    <div class="md:hidden">
      <div class="pt-2 pb-3 space-y-1">
        {#each navItems as item}
          <a 
            href={item.path}
            class="block pl-3 pr-4 py-2 border-l-4 text-base font-medium {isActive(item.path) 
              ? 'bg-blue-50 border-blue-500 text-blue-700' 
              : 'border-transparent text-gray-600 hover:bg-gray-50 hover:border-gray-300 hover:text-gray-800'}"
          >
            {item.name}
          </a>
        {/each}
        
        {#if $user}
          <div class="pt-4 pb-3 border-t border-gray-200">
            <div class="flex items-center px-4">
              <div class="text-sm font-medium text-gray-500">
                {#if $user.email}
                  {$user.email}
                {/if}
              </div>
            </div>
            <div class="mt-3 space-y-1">
              <button 
                on:click={handleLogout}
                class="block w-full text-left px-4 py-2 text-base font-medium text-gray-500 hover:text-gray-800 hover:bg-gray-100"
              >
                Sign out
              </button>
            </div>
          </div>
        {:else}
          <div class="pt-4 pb-3 border-t border-gray-200">
            <div class="space-y-1">
              <a 
                href="/login" 
                class="block px-4 py-2 text-base font-medium text-gray-500 hover:text-gray-800 hover:bg-gray-100"
              >
                Sign in
              </a>
              <a 
                href="/register" 
                class="block px-4 py-2 text-base font-medium text-gray-500 hover:text-gray-800 hover:bg-gray-100"
              >
                Sign up
              </a>
            </div>
          </div>
        {/if}
      </div>
    </div>
  {/if}
</header>
