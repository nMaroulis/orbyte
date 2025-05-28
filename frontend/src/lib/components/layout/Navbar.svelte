<script lang="ts">
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import { user } from '$lib/stores/auth';
  
  // Track mobile menu and user menu states
  let isMobileMenuOpen = $state(false);
  let showUserMenu = $state(false);
  
  // Compute current path
  let currentPath = $derived($page.url.pathname);
  
  const isActive = (path: string): boolean => currentPath === path;
  
  // Navigation items
  const mainNavItems = [
    { name: 'Dashboard', path: '/dashboard', icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6' },
    { name: 'Orbyte Chat', path: '/chat', icon: 'M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.308-3.076C3.88 15.611 3 13.9 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z' },
  ];
  
  const secondaryNavItems = [
    { name: 'About', path: '/about', icon: 'M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z' },
  ];
  
  // Combine all nav items for mobile menu
  const allNavItems = [...mainNavItems, ...secondaryNavItems];
  
  function toggleMenu() {
    isMobileMenuOpen = !isMobileMenuOpen;
  }
  
  function toggleUserMenu() {
    showUserMenu = !showUserMenu;
  }
  
  function closeUserMenu() {
    showUserMenu = false;
  }
  
  async function handleLogout() {
    try {
      // Close the user menu
      showUserMenu = false;
      
      // Clear user data from the store
      user.set(null);
      
      // Clear any stored authentication data
      if (typeof window !== 'undefined') {
        localStorage.removeItem('user');
        sessionStorage.removeItem('user');
      }
      
      // Call the logout API
      await fetch('/api/auth/logout', { method: 'POST' });
      
      // Redirect to the auth login page
      await goto('/auth/login');
    } catch (error) {
      console.error('Logout failed:', error);
      // Still redirect to login even if there was an error
      await goto('/auth/login');
    }
  }
  
  // Close user menu when clicking outside
  $effect(() => {
    if (showUserMenu) {
      const handleClickOutside = (event: MouseEvent) => {
        const target = event.target as HTMLElement;
        if (!target.closest('.user-menu')) {
          closeUserMenu();
        }
      };
      
      document.addEventListener('click', handleClickOutside);
      return () => document.removeEventListener('click', handleClickOutside);
    }
  });
  
  // Component props
  let { className = '' } = $props<{ className?: string }>();
  
  // Close menu when route changes
  $effect(() => {
    currentPath; // Track path changes
    closeUserMenu();
  });
</script>

<header class="bg-white shadow-sm">
  <nav class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8" aria-label="Top">
    <div class="flex justify-between h-16">
      <div class="flex items-center">
        <a href="/" class="flex items-center">
          <span class="text-xl font-bold text-blue-600">Orbyte</span>
        </a>
      </div>
      
      <!-- Desktop Navigation -->
      <div class="hidden md:ml-10 md:flex md:space-x-8">
        <!-- Main Navigation -->
        {#each mainNavItems as item}
          <a 
            href={item.path}
            class="inline-flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors {isActive(item.path) 
              ? 'bg-blue-50 text-blue-700' 
              : 'text-gray-700 hover:bg-gray-100 hover:text-gray-900'}"
          >
            <svg class="mr-2 h-5 w-5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d={item.icon} />
            </svg>
            {item.name}
          </a>
        {/each}
        
        <!-- Divider -->
        <div class="border-t border-gray-200 my-2"></div>
        
        <!-- Secondary Navigation -->
        {#each secondaryNavItems as item}
          <a 
            href={item.path}
            class="inline-flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors {isActive(item.path) 
              ? 'bg-blue-50 text-blue-700' 
              : 'text-gray-700 hover:bg-gray-100 hover:text-gray-900'}"
          >
            <svg class="mr-2 h-5 w-5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d={item.icon} />
            </svg>
            {item.name}
          </a>
        {/each}
      </div>
      
      <div class="hidden md:flex items-center space-x-4">
        {#if $user?.email}
          <div class="relative ml-4 user-menu">
            <button 
              type="button" 
              class="flex items-center max-w-xs rounded-full focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              id="user-menu-button"
              aria-expanded="false"
              aria-haspopup="true"
              onclick={toggleUserMenu}
            >
              <span class="sr-only">Open user menu</span>
              <div class="h-8 w-8 rounded-full bg-blue-500 flex items-center justify-center text-white font-medium">
                {$user?.email?.charAt(0).toUpperCase() || 'U'}
              </div>
              <span class="ml-2 text-sm font-medium text-gray-700 hidden md:inline-block">
                {$user?.email || 'User'}
              </span>
              <svg 
                class={`ml-1 h-5 w-5 text-gray-400 transition-transform duration-200 ${showUserMenu ? 'transform rotate-180' : ''}`} 
                fill="currentColor" 
                viewBox="0 0 20 20"
                aria-hidden="true"
              >
                <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
              </svg>
            </button>
            
            {#if showUserMenu}
              <div 
                class="origin-top-right absolute right-0 mt-2 w-56 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 focus:outline-none z-10" 
                role="menu" 
                aria-orientation="vertical"
                tabindex="0"
                onclick={(e) => {
                  e.stopPropagation();
                }}
                onkeydown={(e) => {
                  if (e.key === 'Escape') {
                    e.preventDefault();
                    showUserMenu = false;
                    const menuButton = (e.currentTarget as HTMLElement).previousElementSibling as HTMLElement | null;
                    if (menuButton) menuButton.focus();
                  }
                }}
              >
                <div class="py-1">
                  <div class="px-4 py-2 text-sm text-gray-700 border-b border-gray-100">
                    <p class="font-medium">{$user?.email || 'User'}</p>
                    <p class="text-xs text-gray-500">Free Plan</p>
                  </div>
                  <a 
                    href="/account" 
                    class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    role="menuitem"
                  >
                    Account Settings
                  </a>
                  <a 
                    href="/billing" 
                    class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    role="menuitem"
                  >
                    Billing
                  </a>
                  <div class="border-t border-gray-100 my-1"></div>
                  <button
                    type="button"
                    onclick={handleLogout}
                    class="w-full text-left block px-4 py-2 text-sm text-red-600 hover:bg-red-50 hover:text-red-700"
                    role="menuitem"
                  >
                    Sign out
                  </button>
                </div>
              </div>
            {/if}
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
          onclick={toggleMenu}
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
  {#if isMobileMenuOpen}
    <div class="md:hidden">
      <div class="pt-2 pb-3 space-y-1">
        {#each allNavItems as item}
          <a 
            href={item.path}
            class="flex items-center px-4 py-2 text-base font-medium {isActive(item.path) 
              ? 'bg-blue-50 text-blue-700' 
              : 'text-gray-600 hover:bg-gray-50 hover:text-gray-800'}"
          >
            <svg class="mr-3 h-5 w-5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d={item.icon} />
            </svg>
            {item.name}
          </a>
        {/each}
        
        {#if $user?.email}
          <div class="border-t border-gray-200 pt-4 pb-3">
            <div class="px-4">
              <div class="text-sm font-medium text-gray-800">{$user.email}</div>
              <div class="text-xs text-gray-500">Free Plan</div>
            </div>
            <div class="mt-3 space-y-1">
              <a 
                href="/account" 
                class="block px-4 py-2 text-base font-medium text-gray-500 hover:bg-gray-100 hover:text-gray-800"
              >
                Account Settings
              </a>
              <a 
                href="/billing" 
                class="block px-4 py-2 text-base font-medium text-gray-500 hover:bg-gray-100 hover:text-gray-800"
              >
                Billing
              </a>
              <button
                type="button"
                onclick={handleLogout}
                class="w-full text-left block px-4 py-2 text-base font-medium text-gray-500 hover:bg-gray-100 hover:text-gray-800"
              >
                Sign out
              </button>
            </div>
          </div>
        {/if}
      </div>
    </div>
  {/if}
</header>
