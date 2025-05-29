<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { user } from '$lib/stores/auth';
  import Card from '$lib/components/ui/Card.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import { API_ENDPOINTS } from '$lib/api/config';
  
  // Navigation functions
  function navigateTo(path: string) {
    goto(path);
  }
  
  // Handle card clicks
  function handleCardClick(path: string) {
    navigateTo(path);
  }
  import { api } from '$lib/api/client';
  import type { GPU, Task, Payment } from '$lib/types';
  
  // Types for stats
  type StatColor = 'indigo' | 'blue' | 'green' | 'purple' | 'emerald';
  
  interface StatItem {
    name: string;
    value: string;
    icon: string;
    color: StatColor;
  }
  
  interface ColorMapItem {
    bg: string;
    icon: string;
    iconBg: string;
  }
  
  // Stats with distinct colors
  let stats: StatItem[] = [
    { 
      name: 'Total GPUs', 
      value: '0',
      icon: 'M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z',
      color: 'blue'  // Blue for GPUs
    },
    { 
      name: 'Active Tasks', 
      value: '0',
      icon: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4',
      color: 'indigo'  // Indigo for tasks
    },
    { 
      name: 'Tasks Completed', 
      value: '0',
      icon: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z',
      color: 'green'  // Green for completed tasks
    },
    { 
      name: 'Total Earnings', 
      value: '$0',
      icon: 'M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z',
      color: 'purple'  // Purple for earnings
    },
    { 
      name: 'Balance', 
      value: '$0.00',
      icon: 'M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z',
      color: 'emerald'  // Amber for balance (changed from emerald to amber for better distinction)
    }
  ];
  
  // Color map for stats cards with more distinct colors
  const colorMap: Record<StatColor, ColorMapItem> = {
    indigo: { bg: 'from-indigo-50 to-indigo-100', icon: 'text-indigo-600', iconBg: 'bg-indigo-100' },
    blue: { bg: 'from-blue-50 to-blue-100', icon: 'text-blue-600', iconBg: 'bg-blue-100' },
    green: { bg: 'from-green-50 to-green-100', icon: 'text-green-600', iconBg: 'bg-green-100' },
    purple: { bg: 'from-purple-50 to-purple-100', icon: 'text-purple-600', iconBg: 'bg-purple-100' },
    emerald: { bg: 'from-amber-50 to-amber-100', icon: 'text-amber-600', iconBg: 'bg-amber-100' }
  };
  
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
      
      // Update stats with actual data
      stats = stats.map((stat: StatItem) => {
        switch(stat.name) {
          case 'Total GPUs':
            return { ...stat, value: availableGpus.length.toString() };
          case 'Active Tasks':
            return { ...stat, value: recentTasks.filter(t => ['pending', 'running'].includes(t.status)).length.toString() };
          case 'Total Earnings':
            return { ...stat, value: `$${recentPayments.reduce((sum, p) => sum + p.amount, 0).toFixed(2)}` };
          case 'Tasks Completed':
            return { ...stat, value: recentTasks.filter(t => t.status === 'completed').length.toString() };
          case 'Balance':
            // In a real app, this would come from the user's account balance
            return { ...stat, value: `$${(100 + Math.random() * 500).toFixed(2)}` };
          default:
            return stat;
        }
      });
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
  <main class="py-8">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between items-center mb-8">
        <div>
          <h1 class="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p class="mt-1 text-sm text-gray-500">Welcome back, {$user?.email || 'User'}! Here's what's happening with your account.</p>
        </div>
        <div class="flex space-x-4">
          <Button 
            onclick={() => navigateTo('/tasks/new')} 
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
            onclick={() => navigateTo('/gpus/new')} 
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
      <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3 mb-8">
        {#each stats as stat}
          <div 
            class="relative overflow-hidden rounded-xl p-4 transition-all duration-200 hover:shadow-md bg-gradient-to-br {colorMap[stat.color].bg}"
          >
            <div class="relative z-10">
              <div class="flex items-center justify-between">
                <div class={`flex-shrink-0 rounded-lg p-2 ${colorMap[stat.color].iconBg}`}>
                  <svg class={`h-5 w-5 ${colorMap[stat.color].icon}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="{stat.icon}" />
                  </svg>
                </div>
              </div>
              <div class="mt-3">
                <dt class="text-xs font-medium text-gray-600 truncate">
                  {stat.name}
                </dt>
                <dd class="mt-1 text-xl font-semibold text-gray-900">
                  {stat.value}
                </dd>
              </div>
            </div>
            <!-- Decorative element -->
            <div class="absolute -bottom-4 -right-4 opacity-20">
              <svg class="h-16 w-16" viewBox="0 0 24 24" fill="currentColor">
                <path d="{stat.icon}" />
              </svg>
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
                <li class="group relative px-6 py-5 hover:bg-gray-50 transition-colors duration-150 border-b border-gray-100 last:border-b-0">
                  <div class="flex items-start justify-between">
                    <div class="flex items-start space-x-4">
                      <div class="flex-shrink-0 h-12 w-12 rounded-lg bg-indigo-50 flex items-center justify-center">
                        <svg class="h-6 w-6 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
                        </svg>
                      </div>
                      <div class="min-w-0 flex-1">
                        <div class="flex items-center space-x-3">
                          <h3 class="text-sm font-semibold text-gray-900">
                            {gpu.name}
                          </h3>
                          <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-indigo-50 text-indigo-700">
                            <svg class="-ml-0.5 mr-1 h-3 w-3 text-indigo-400" fill="currentColor" viewBox="0 0 20 20">
                              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd" />
                            </svg>
                            ${gpu.price_per_hour.toFixed(2)}/hr
                          </span>
                        </div>
                        <p class="text-sm text-gray-500 mt-1">
                          {gpu.model} • {gpu.vram_gb}GB VRAM • {gpu.cpu_model || 'NVIDIA GPU'}
                        </p>
                        
                        <!-- System Information -->
                        <div class="mt-2 grid grid-cols-2 gap-x-4 gap-y-1 text-xs text-gray-500">
                          {#if gpu.os}
                            <div class="flex items-start">
                              <span class="font-medium text-gray-700 w-24">OS:</span>
                              <span class="truncate">{gpu.os}</span>
                            </div>
                          {/if}
                          {#if gpu.cpu_model || gpu.cpu_cores}
                            <div class="flex items-start">
                              <span class="font-medium text-gray-700 w-24">CPU:</span>
                              <span class="truncate">
                                {gpu.cpu_model || ''}{gpu.cpu_cores ? ' (' + gpu.cpu_cores + ' cores)' : ''}
                              </span>
                            </div>
                          {/if}
                          {#if gpu.ram_gb}
                            <div class="flex items-start">
                              <span class="font-medium text-gray-700 w-24">RAM:</span>
                              <span>{gpu.ram_gb} GB</span>
                            </div>
                          {/if}
                          {#if gpu.storage_gb}
                            <div class="flex items-start">
                              <span class="font-medium text-gray-700 w-24">Storage:</span>
                              <span>{gpu.storage_gb} GB</span>
                            </div>
                          {/if}
                          {#if gpu.network_speed_mbps}
                            <div class="flex items-start">
                              <span class="font-medium text-gray-700 w-24">Network:</span>
                              <span>{gpu.network_speed_mbps} Mbps</span>
                            </div>
                          {/if}
                        </div>
                      </div>
                    </div>
                    <div class="ml-4 flex-shrink-0">
                      <button
                        type="button"
                        class="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                        on:click|preventDefault={() => navigateTo(`/gpus/${gpu.id}`)}
                      >
                        View Details
                      </button>
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
