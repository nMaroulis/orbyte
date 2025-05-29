<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { api } from '$lib/api/client';
  import { API_ENDPOINTS } from '$lib/api/config';

  interface GPU {
    id: number;
    name: string;
    model: string;
    vram_gb: number;
    price_per_hour: number;
    status: string;
    specs: {
      supported_models?: string[];
      [key: string]: any;
    };
    supported_workflows?: string[];
  }

  let gpus: GPU[] = [];
  let isLoading = true;
  let error = '';

  async function fetchGPUs() {
    try {
      isLoading = true;
      error = '';
      
      const response = await api.get<{ data: GPU[] }>(
        `${API_ENDPOINTS.GPUS.LIST}?status=available&limit=100`
      );
      
      gpus = response.data || [];
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch GPUs';
      error = 'Failed to load GPUs. Please try again later.';
      console.error('Error fetching GPUs:', errorMessage);
    } finally {
      isLoading = false;
    }
  }

  function formatWorkflows(workflows: string[] = []) {
    if (!workflows || workflows.length === 0) return [];
    return workflows.map(type => 
      type
        .split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ')
    );
  }

  function formatModels(models: string[] = []) {
    return models || [];
  }

  onMount(() => {
    fetchGPUs();
  });
</script>

<div class="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
  <div class="max-w-7xl mx-auto">
    <div class="sm:flex sm:items-center">
      <div class="sm:flex-auto">
        <h1 class="text-3xl font-bold text-gray-900">Available GPUs</h1>
        <p class="mt-2 text-sm text-gray-700">
          Browse and manage available GPUs in the network
        </p>
      </div>
      <div class="mt-4 sm:mt-0 sm:ml-16 sm:flex-none">
        <button
          type="button"
          on:click={() => goto('/gpus/new')}
          class="inline-flex items-center justify-center rounded-md border border-transparent bg-blue-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 sm:w-auto"
        >
          Add GPU
        </button>
      </div>
    </div>

    {#if error}
      <div class="mt-8 bg-red-50 border-l-4 border-red-400 p-4">
        <div class="flex">
          <div class="flex-shrink-0">
            <svg class="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.28 7.22a.75.75 0 00-1.06 1.06L8.94 10l-1.72 1.72a.75.75 0 101.06 1.06L10 11.06l1.72 1.72a.75.75 0 101.06-1.06L11.06 10l1.72-1.72a.75.75 0 00-1.06-1.06L10 8.94 8.28 7.22z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="ml-3">
            <p class="text-sm text-red-700">{error}</p>
          </div>
        </div>
      </div>
    {/if}

    {#if isLoading}
      <div class="mt-8 flex justify-center">
        <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    {:else}
      <div class="mt-8 flex flex-col">
        <div class="-my-2 -mx-4 overflow-x-auto sm:-mx-6 lg:-mx-8">
          <div class="inline-block min-w-full py-2 align-middle md:px-6 lg:px-8">
            <div class="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
              <table class="min-w-full divide-y divide-gray-300">
                <thead class="bg-gray-50">
                  <tr>
                    <th scope="col" class="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900 sm:pl-6">Name</th>
                    <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Model</th>
                    <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">VRAM</th>
                    <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Price/Hour</th>
                    <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Status</th>
                    <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Workflows</th>
                    <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Models</th>
                    <th scope="col" class="relative py-3.5 pl-3 pr-4 sm:pr-6">
                      <span class="sr-only">Actions</span>
                    </th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-gray-200 bg-white">
                  {#each gpus as gpu}
                    <tr>
                      <td class="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-blue-600 hover:text-blue-900 sm:pl-6">
                        <button on:click={() => goto(`/gpus/${gpu.id}`)} class="text-left hover:underline">
                          {gpu.name}
                        </button>
                      </td>
                      <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{gpu.model}</td>
                      <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{gpu.vram_gb} GB</td>
                      <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">${gpu.price_per_hour.toFixed(2)}</td>
                      <td class="whitespace-nowrap px-3 py-4 text-sm">
                        <span class="inline-flex rounded-full bg-green-100 px-2 text-xs font-semibold leading-5 text-green-800">
                          {gpu.status}
                        </span>
                      </td>
                      <td class="px-3 py-4 text-sm text-gray-500" title={formatWorkflows(gpu.supported_workflows).join(', ')}>
                        <div class="flex items-center">
                          <span class="inline-flex items-center justify-center h-6 w-6 rounded-full bg-indigo-100 text-indigo-800 text-xs font-medium mr-2">
                            {gpu.supported_workflows?.length || 0}
                          </span>
                        </div>
                      </td>
                      <td class="px-3 py-4 text-sm text-gray-500" title={formatModels(gpu.specs.supported_models).join(', ')}>
                        <div class="flex items-center">
                          <span class="inline-flex items-center justify-center h-6 w-6 rounded-full bg-blue-100 text-blue-800 text-xs font-medium mr-2">
                            {gpu.specs.supported_models?.length || 0}
                          </span>
                        </div>
                      </td>
                      <td class="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-6">
                        <!-- Configuration moved to New GPU page -->
                      </td>
                    </tr>
                  {/each}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    {/if}
  </div>
</div>
