<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { user } from '$lib/stores/auth';
  import { onDestroy } from 'svelte';
  import { invalidateAll } from '$app/navigation';
  import { AuthService } from '$lib/services/auth.service';
  
  // State for user menu dropdown
  let showUserMenu = false;
  
  // Close menu when clicking outside
  function handleClickOutside(event: MouseEvent) {
    const target = event.target as HTMLElement;
    if (!target.closest('.relative')) {
      showUserMenu = false;
    }
  }
  
  // Add click outside listener
  onMount(() => {
    document.addEventListener('click', handleClickOutside);
    return () => {
      document.removeEventListener('click', handleClickOutside);
    };
  });
  
  // Handle logout
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
      
      // Invalidate all data
      await invalidateAll();
      
      // Redirect to the auth login page
      await goto('/auth/login');
    } catch (error) {
      console.error('Logout failed:', error);
      // Still redirect to login even if there was an error
      await goto('/auth/login');
    }
  }
  import Card from '$lib/components/ui/Card.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import { API_ENDPOINTS } from '$lib/api/config';
  import { api } from '$lib/api/client';
  import type { GPU, Task, Payment } from '$lib/types';
  
  // Stats
  let stats = [
    { name: 'Total GPUs', value: '0', change: '+0%', changeType: 'increase' },
    { name: 'Active Tasks', value: '0', change: '+0%', changeType: 'decrease' },
    { name: 'Total Earnings', value: '$0', change: '+0%', changeType: 'increase' },
    { name: 'Tasks Completed', value: '0', change: '+0%', changeType: 'increase' },
  ];
  
  // Recent tasks
  let recentTasks: Task[] = [];
  let isLoadingTasks = true;
  
  // Recent payments
  let recentPayments: Payment[] = [];
  let isLoadingPayments = true;
  
  // Available GPUs
  let availableGpus: GPU[] = [];
  let isLoadingGpus = true;
  
  // My GPUs
  let myGpus: GPU[] = [];
  let isLoadingMyGpus = true;
  let myGpusError: string | null = null;
  
  // Fetch data
  async function fetchDashboardData() {
    try {
      // Fetch user's recent tasks
      const [tasksRes, paymentsRes, gpusRes, myGpusRes] = await Promise.all([
        api.get<{data: Task[]}>(`${API_ENDPOINTS.TASKS.LIST}?limit=5`).catch(() => ({data: []})),
        api.get<{data: Payment[]}>(`${API_ENDPOINTS.PAYMENTS.RECEIVED}?limit=5`).catch(() => ({data: []})),
        api.get<{data: GPU[]}>(`${API_ENDPOINTS.GPUS.LIST}?status=available&limit=5`).catch(() => ({data: []})),
        api.get<{data: GPU[]}>(`${API_ENDPOINTS.GPUS.MY_GPUS}`).catch((error) => {
          console.error('Error fetching my GPUs:', error);
          myGpusError = error.message || 'Failed to load your GPUs';
          return { data: [] };
        })
      ]);
      
      recentTasks = tasksRes?.data || [];
      recentPayments = paymentsRes?.data || [];
      availableGpus = gpusRes?.data || [];
      myGpus = myGpusRes?.data || [];
      myGpusError = null;
      
      // Update stats (in a real app, these would come from the API)
      stats = [
        { name: 'Total GPUs', value: availableGpus.length.toString(), change: '+0%', changeType: 'increase' },
        { 
          name: 'Active Tasks', 
          value: recentTasks.filter(t => ['pending', 'running'].includes(t.status)).length.toString(), 
          change: '+0%', 
          changeType: 'decrease' 
        },
        { 
          name: 'Total Earnings', 
          value: `$${recentPayments.reduce((sum, p) => sum + p.amount, 0).toFixed(2)}`, 
          change: '+0%', 
          changeType: 'increase' 
        },
        { 
          name: 'Tasks Completed', 
          value: recentTasks.filter(t => t.status === 'completed').length.toString(), 
          change: '+0%', 
          changeType: 'increase' 
        },
      ];
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      isLoadingTasks = false;
      isLoadingPayments = false;
      isLoadingGpus = false;
      isLoadingMyGpus = false;
    }
  }
  
  // Format date
  function formatDate(dateString: string): string {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }
  
  // Format currency
  function formatCurrency(amount: number): string {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  }
  
  // Get status color
  function getStatusColor(status: string): string {
    const statusColors: Record<string, string> = {
      pending: 'bg-yellow-100 text-yellow-800',
      running: 'bg-blue-100 text-blue-800',
      completed: 'bg-green-100 text-green-800',
      failed: 'bg-red-100 text-red-800',
      cancelled: 'bg-gray-100 text-gray-800',
    };
    return statusColors[status] || 'bg-gray-100 text-gray-800';
  }
  
  // Subscribe to user store
  let unsubscribe: () => void;
  
  onMount(() => {
    unsubscribe = user.subscribe(($user) => {
      if (!$user) {
        goto('/auth/login');
      } else {
        fetchDashboardData();
      }
    });
    
    // Refresh data every 30 seconds
    const interval = setInterval(fetchDashboardData, 30000);
    
    return () => {
      clearInterval(interval);
      if (unsubscribe) unsubscribe();
    };
  });
</script>

<div class="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
  <!-- Top Navigation -->
  <header class="bg-white shadow-sm">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between h-16 items-center">
        <div class="flex items-center">
          <span class="text-xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">Orbyte</span>
        </div>
        <div class="flex items-center space-x-4">
          <button class="p-2 rounded-full hover:bg-gray-100" aria-label="Notifications">
            <svg class="h-5 w-5 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
            </svg>
          </button>
          <div class="relative">
            <button 
              class="flex items-center space-x-2 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 rounded-full p-1" 
              aria-label="User menu" 
              aria-haspopup="true"
              aria-expanded={showUserMenu}
              on:click={() => showUserMenu = !showUserMenu}
              on:keydown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault();
                  showUserMenu = !showUserMenu;
                } else if (e.key === 'Escape') {
                  showUserMenu = false;
                }
              }}
            >
              <div class="h-8 w-8 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-600 font-medium">
                {$user?.email?.charAt(0).toUpperCase() || 'U'}
              </div>
              <span class="hidden md:inline-block text-sm font-medium text-gray-700">{$user?.email || 'User'}</span>
              <svg 
                class={`h-5 w-5 text-gray-400 transition-transform duration-200 ${showUserMenu ? 'transform rotate-180' : ''}`} 
                fill="currentColor" 
                viewBox="0 0 20 20"
                aria-hidden="true"
              >
                <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
              </svg>
            </button>
            
            {#if showUserMenu}
              <div 
                class="absolute right-0 mt-2 w-56 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 focus:outline-none z-10" 
                role="menu" 
                aria-orientation="vertical"
                tabindex="0"
                on:click|stopPropagation
                on:keydown={(e) => {
                  if (e.key === 'Escape') {
                    e.preventDefault();
                    showUserMenu = false;
                    // Focus the menu button when closing with Escape
                    const menuButton = e.currentTarget.previousElementSibling as HTMLElement | null;
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
                    on:click={handleLogout}
                    class="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-gray-100"
                    role="menuitem"
                  >
                    Sign out
                  </button>
                </div>
              </div>
            {/if}
          </div>
        </div>
      </div>
    </div>
  </header>

  <main class="py-8">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between items-center mb-8">
        <div>
          <h1 class="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p class="mt-1 text-sm text-gray-500">Welcome back, {$user?.email || 'User'}! Here's what's happening with your account.</p>
        </div>
        <div class="flex space-x-4">
          <Button 
            on:click={() => goto('api/tasks/new')} 
            variant="outline" 
            size="lg"
            class="group hidden sm:inline-flex items-center px-6 py-3 border border-gray-300 shadow-sm text-base font-medium rounded-lg text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-all duration-200"
          >
            <svg class="-ml-1 mr-3 h-5 w-5 text-gray-500 group-hover:text-gray-600 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
            New Task
          </Button>
          <Button 
            on:click={() => goto('api/gpus/new')} 
            variant="primary" 
            size="lg"
            class="group inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-lg shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-all duration-200"
          >
            <svg class="-ml-1 mr-3 h-5 w-5 text-indigo-200 group-hover:text-white transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            Deploy GPU
          </Button>
        </div>
      </div>

      <!-- Stats Grid -->
      <div class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4 mb-8">
        {#each stats as stat}
          <div class="bg-white overflow-hidden shadow rounded-xl transition-all duration-200 hover:shadow-lg">
            <div class="p-5">
              <div class="flex items-center">
                <div class="flex-shrink-0 rounded-md p-3" class:bg-indigo-100={stat.name === 'Total GPUs'}
                  class:bg-green-100={stat.name === 'Tasks Completed'}
                  class:bg-blue-100={stat.name === 'Active Tasks'}
                  class:bg-purple-100={stat.name === 'Total Earnings'}>
                  {#if stat.name === 'Total GPUs'}
                    <svg class="h-6 w-6 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
                    </svg>
                  {:else if stat.name === 'Active Tasks'}
                    <svg class="h-6 w-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                    </svg>
                  {:else if stat.name === 'Total Earnings'}
                    <svg class="h-6 w-6 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  {:else}
                    <svg class="h-6 w-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  {/if}
                </div>
                <div class="ml-5 w-0 flex-1">
                  <dt class="text-sm font-medium text-gray-500 truncate">
                    {stat.name}
                  </dt>
                  <dd class="flex items-baseline">
                    <div class="text-2xl font-semibold text-gray-900">
                      {stat.value}
                    </div>
                    <div class="ml-2 flex items-baseline text-sm font-semibold" 
                      class:!text-green-600={stat.changeType === 'increase'}
                      class:!text-red-600={stat.changeType === 'decrease'}>
                      {#if stat.changeType === 'increase'}
                        <svg class="self-center flex-shrink-0 h-4 w-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                          <path fill-rule="evenodd" d="M12 7a1 1 0 01.707.293l4 4a1 1 0 01-1.414 1.414L12 9.414 8.707 12.707a1 1 0 01-1.414-1.414l4-4A1 1 0 0112 7z" clip-rule="evenodd" />
                        </svg>
                      {:else}
                        <svg class="self-center flex-shrink-0 h-4 w-4 text-red-500" fill="currentColor" viewBox="0 0 20 20">
                          <path fill-rule="evenodd" d="M12 13a1 1 0 01-.707-.293l-4-4a1 1 0 011.414-1.414L12 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4A1 1 0 0112 13z" clip-rule="evenodd" />
                        </svg>
                      {/if}
                      <span class="sr-only">
                        {stat.changeType === 'increase' ? 'Increased' : 'Decreased'} by
                      </span>
                      {stat.change}
                    </div>
                  </dd>
                </div>
              </div>
            </div>
            <div class="px-5 py-3 bg-gray-50 text-right text-sm">
              <Button variant="ghost" size="sm" on:click={() => goto('/tasks')}>
                View all
              </Button>
            </div>
          </div>
        {/each}
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Recent Tasks -->
        <div class="lg:col-span-2">
          <div class="bg-white shadow overflow-hidden rounded-xl">
            <div class="px-6 py-5 border-b border-gray-200 flex items-center justify-between">
              <h2 class="text-lg font-medium text-gray-900 flex items-center">
                <svg class="h-5 w-5 text-gray-500 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                </svg>
                Recent Tasks
              </h2>
              <Button variant="ghost" size="sm" on:click={() => goto('/tasks')}>
                View all
              </Button>
            </div>
            <div class="divide-y divide-gray-200">
              {#if isLoadingTasks}
                <div class="p-6 text-center text-gray-500">
                  <svg class="mx-auto h-8 w-8 animate-spin text-gray-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <p class="mt-2">Loading tasks...</p>
                </div>
              {:else if recentTasks.length === 0}
                <div class="p-6 text-center">
                  <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
                  </svg>
                  <h3 class="mt-2 text-sm font-medium text-gray-900">No tasks</h3>
                  <p class="mt-1 text-sm text-gray-500">Get started by creating a new task.</p>
                  <div class="mt-6">
                    <button type="button" class="-my-1.5 flex flex-none items-center justify-center p-1.5 text-gray-400 hover:text-gray-500" aria-label="Previous month">
                      <span class="sr-only">Previous</span>
                      <svg class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                        <path fill-rule="evenodd" d="M12.79 5.23a.75.75 0 01-.02 1.06L8.832 10l3.938 3.71a.75.75 0 11-1.04 1.08l-4.5-4.25a.75.75 0 010-1.08l4.5-4.25a.75.75 0 011.06.02z" clip-rule="evenodd" />
                      </svg>
                    </button>
                    <Button variant="primary" on:click={() => goto('/tasks/new')} aria-label="Create a new task">
                      <svg class="-ml-1 mr-2 h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M10 5a1 1 0 011 1v3h3a1 1 0 110 2h-3v3a1 1 0 01-1 1h-3a1 1 0 110-2h3V9a1 1 0 011-1V6a1 1 0 110-2z" clip-rule="evenodd" />
                      </svg>
                      New Task
                    </Button>
                  </div>
                </div>
              {:else}
                <ul class="divide-y divide-gray-200">
                  {#each recentTasks as task}
                    <li class="px-6 py-4 hover:bg-gray-50 transition-colors duration-150">
                      <div class="flex items-center">
                        <div class="min-w-0 flex-1">
                          <div class="flex items-center">
                            <p class="text-sm font-medium text-gray-900 truncate">
                              {task.title}
                            </p>
                          </div>
                          <p class="text-sm text-gray-500 truncate">
                            {task.description || 'No description'}
                          </p>
                        </div>
                        <div class="ml-4 flex-shrink-0">
                          <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium" 
                            class:bg-green-100={task.status === 'completed'}
                            class:text-green-800={task.status === 'completed'}
                            class:bg-yellow-100={task.status === 'pending'}
                            class:text-yellow-800={task.status === 'pending'}
                            class:bg-blue-100={task.status === 'running'}
                            class:text-blue-800={task.status === 'running'}
                            class:bg-red-100={task.status === 'failed'}
                            class:text-red-800={task.status === 'failed'}>
                            {task.status}
                          </span>
                        </div>
                      </div>
                      <div class="mt-2 sm:flex sm:justify-between">
                        <div class="sm:flex">
                          <p class="flex items-center text-sm text-gray-500">
                            <svg class="flex-shrink-0 mr-1.5 h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" stroke="currentColor">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                            </svg>
                            {formatDate(task.created_at)}
                          </p>
                        </div>
                        <div class="mt-2 flex items-center text-sm text-gray-500 sm:mt-0">
                          <svg class="flex-shrink-0 mr-1.5 h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M10 9l3 3m-3 3l-3 3m-3-3h12a9 9 0 110-18 9 9 0 010 18z" />
                          </svg>
                          <p>
                            {task.cost ? formatCurrency(task.cost) : '--:--'}
                          </p>
                        </div>
                      </div>
                    </li>
                  {/each}
                </ul>
              {/if}
            </div>
          </div>
        </div>

        <!-- Recent Payments -->
        <div>
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-lg font-medium text-gray-900">Recent Payments</h2>
            <Button variant="ghost" size="sm" on:click={() => goto('/payments')}>
              View all
            </Button>
          </div>
          <div class="bg-white shadow overflow-hidden rounded-xl">
            {#if isLoadingPayments}
              <div class="p-6 text-center text-gray-500">
                <svg class="mx-auto h-8 w-8 animate-spin text-gray-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <p class="mt-2">Loading payments...</p>
              </div>
            {:else if recentPayments.length === 0}
              <div class="p-6 text-center text-gray-500">
                <p>No payments found</p>
              </div>
            {:else}
              <ul class="divide-y divide-gray-200">
                {#each recentPayments as payment}
                  <li class="px-6 py-4 hover:bg-gray-50">
                    <div class="flex items-center justify-between">
                      <div class="flex-1 min-w-0">
                        <p class="text-sm font-medium text-gray-900">
                          {payment.task?.title || 'Payment'}
                        </p>
                        <p class="text-sm text-gray-500">
                          {payment.sender?.email || 'Unknown sender'}
                        </p>
                      </div>
                      <div class="ml-4 flex-shrink-0">
                        <p class="text-sm font-medium text-green-600">
                          +${payment.amount?.toFixed(2) || '0.00'}
                        </p>
                      </div>
                    </div>
                    <div class="mt-1 text-sm text-gray-500">
                      {formatDate(payment.created_at)}
                    </div>
                  </li>
                {/each}
              </ul>
            {/if}
          </div>
        </div>
      </div>

      <!-- My GPUs Section -->
      <div class="mt-8">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-medium text-gray-900">My GPUs</h2>
          <a href="/gpus/my-gpus" class="text-sm font-medium text-indigo-600 hover:text-indigo-500">View all my GPUs</a>
        </div>
        {#if isLoadingMyGpus}
          <div class="bg-white shadow overflow-hidden rounded-lg p-6 text-center">
            <svg class="mx-auto h-8 w-8 animate-spin text-gray-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <p class="mt-2 text-sm text-gray-500">Loading your GPUs...</p>
          </div>
        {:else if myGpusError}
          <div class="bg-red-50 border-l-4 border-red-400 p-4">
            <div class="flex">
              <div class="flex-shrink-0">
                <svg class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                </svg>
              </div>
              <div class="ml-3">
                <p class="text-sm text-red-700">
                  Failed to load your GPUs. Please try again.
                </p>
              </div>
            </div>
          </div>
        {:else if myGpus.length === 0}
          <div class="bg-white shadow overflow-hidden rounded-lg p-6 text-center">
            <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
            <h3 class="mt-2 text-sm font-medium text-gray-900">No GPUs found</h3>
            <p class="mt-1 text-sm text-gray-500">You haven't deployed any GPUs yet.</p>
            <div class="mt-6">
              <button
                type="button"
                on:click={() => goto('/gpus/new')}
                class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                <svg class="-ml-1 mr-2 h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                  <path fill-rule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 01-1 1h-3a1 1 0 110-2h3V9a1 1 0 011-1V6a1 1 0 110-2z" clip-rule="evenodd" />
                </svg>
                Deploy New GPU
              </button>
            </div>
          </div>
        {:else}
          <div class="bg-white shadow overflow-hidden rounded-lg">
            <ul role="list" class="divide-y divide-gray-200">
              {#each myGpus.slice(0, 3) as gpu}
                <li class="px-6 py-4 hover:bg-gray-50 transition-colors duration-150">
                  <div class="flex items-center justify-between">
                    <div class="flex items-center">
                      <div class="flex-shrink-0 h-10 w-10 rounded-md bg-indigo-100 flex items-center justify-center">
                        <svg class="h-6 w-6 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                        </svg>
                      </div>
                      <div class="ml-4">
                        <div class="text-sm font-medium text-gray-900">{gpu.name || 'Unnamed GPU'}</div>
                        <div class="text-sm text-gray-500">
                          {gpu.model} • {gpu.vram_gb}GB VRAM • ${gpu.price_per_hour?.toFixed(2)}/hr
                        </div>
                      </div>
                    </div>
                    <div class="flex items-center">
                      <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium capitalize" 
                        class:bg-green-100={gpu.status === 'available'} 
                        class:text-green-800={gpu.status === 'available'}
                        class:bg-yellow-100={gpu.status === 'in_use'}
                        class:text-yellow-800={gpu.status === 'in_use'}
                        class:bg-red-100={gpu.status === 'offline'}
                        class:text-red-800={gpu.status === 'offline'}
                        class:bg-gray-100={!['available', 'in_use', 'offline'].includes(gpu.status)}
                        class:text-gray-800={!['available', 'in_use', 'offline'].includes(gpu.status)}>
                        {gpu.status?.replace('_', ' ')}
                      </span>
                    </div>
                  </div>
                </li>
              {/each}
            </ul>
            {#if myGpus.length > 3}
              <div class="bg-gray-50 px-6 py-4 text-right text-sm">
                <a href="/gpus/my-gpus" class="font-medium text-indigo-600 hover:text-indigo-500">View all my GPUs</a>
              </div>
            {/if}
          </div>
        {/if}
      </div>

      <!-- Available GPUs -->
      <div class="mt-8">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-medium text-gray-900">Available GPUs</h2>
          <a href="/gpus" class="text-sm font-medium text-indigo-600 hover:text-indigo-500">View all</a>
        </div>
        <div class="bg-white shadow overflow-hidden rounded-xl">
          {#if isLoadingGpus}
            <div class="p-6 text-center text-gray-500">
              <svg class="mx-auto h-8 w-8 animate-spin text-gray-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <p class="mt-2">Loading GPUs...</p>
            </div>
          {:else if availableGpus.length === 0}
            <div class="p-6 text-center">
              <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
              </svg>
              <h3 class="mt-2 text-sm font-medium text-gray-900">No GPUs available</h3>
              <p class="mt-1 text-sm text-gray-500">Check back later for available GPUs.</p>
            </div>
          {:else}
            <ul class="divide-y divide-gray-200">
              {#each availableGpus as gpu}
                <li class="px-6 py-4 hover:bg-gray-50 transition-colors duration-150">
                  <div class="flex items-center justify-between">
                    <div class="flex items-center">
                      <div class="flex-shrink-0 h-10 w-10 rounded-md bg-indigo-100 flex items-center justify-center">
                        <svg class="h-6 w-6 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
                        </svg>
                      </div>
                      <div class="ml-4">
                        <p class="text-sm font-medium text-gray-900">
                          {gpu.name}
                        </p>
                        <p class="text-sm text-gray-500">
                          {gpu.vram_gb}GB VRAM • {gpu.model}
                        </p>
                      </div>
                    </div>
                    <div class="ml-4 flex-shrink-0">
                      <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                        ${gpu.price_per_hour}/hr
                      </span>
                    </div>
                  </div>
                </li>
              {/each}
            </ul>
          {/if}
        </div>
      </div>
    </div>
  </main>
</div>
