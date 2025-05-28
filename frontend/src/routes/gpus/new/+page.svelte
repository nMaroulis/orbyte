<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { user } from '$lib/stores/auth';
  import Button from '$lib/components/ui/Button.svelte';
  import Card from '$lib/components/ui/Card.svelte';
  import { api } from '$lib/api/client';
  import { API_ENDPOINTS } from '$lib/api/config';
  import type { AxiosResponse } from 'axios';
  
  interface GpuSpecs {
    description?: string;
    [key: string]: any;
  }
  
  interface Gpu {
    uuid: string;
    name: string;
    memory_total_gb: number;
    [key: string]: any;
  }
  
  // Form state
  let loading = false;
  let error: string | null = null;
  let success = false;
  let availableGpus: Gpu[] = [];
  
  // Form fields
  let selectedGpuId = '';
  let name = '';
  let pricePerHour = 0.5;
  let description = '';
  
  // Fetch available system GPUs
  async function fetchSystemGpus() {
    try {
      loading = true;
      error = null;
      
      const response: AxiosResponse<{ data: Gpu[] }> = await api.get(`${API_ENDPOINTS.GPUS.LIST}?system=true`);
      availableGpus = response.data?.data || [];
      
      // Auto-select the first GPU if available
      if (availableGpus.length > 0) {
        selectedGpuId = availableGpus[0].uuid;
        name = availableGpus[0].name || '';
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      console.error('Error fetching system GPUs:', errorMessage);
      error = 'Failed to load available GPUs. Please try again.';
    } finally {
      loading = false;
    }
  }
  
  // Handle form submission
  async function handleSubmit() {
    if (!selectedGpuId) {
      error = 'Please select a GPU';
      return;
    }
    
    try {
      loading = true;
      error = null;
      
      const selectedGpu = availableGpus.find((gpu) => gpu.uuid === selectedGpuId);
      
      if (!selectedGpu) {
        throw new Error('Selected GPU not found');
      }
      
      const gpuData = {
        name: name || selectedGpu.name,
        model: selectedGpu.name,
        vram_gb: selectedGpu.memory_total_gb,
        price_per_hour: pricePerHour,
        specs: {
          description,
          ...selectedGpu
        }
      };
      
      await api.post(API_ENDPOINTS.GPUS.LIST, gpuData);
      
      // Show success message and redirect
      success = true;
      setTimeout(() => {
        goto('/dashboard');
      }, 1500);
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      console.error('Error deploying GPU:', errorMessage);
      error = 'Failed to deploy GPU. Please try again.';
      
      if (err && typeof err === 'object' && 'response' in err) {
        const response = (err as { response: any }).response;
        if (response?.data?.detail) {
          error = response.data.detail;
        }
      }
    } finally {
      loading = false;
    }
  }
  
  onMount(() => {
    fetchSystemGpus();
  });
</script>

<div class="min-h-screen bg-white py-12 px-4 sm:px-6 lg:px-8">
  <div class="max-w-3xl mx-auto">
    <div class="text-center mb-8">
      <div class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-indigo-100 mb-4">
        <svg class="h-8 w-8 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
        </svg>
      </div>
      <h1 class="text-3xl font-extrabold text-gray-900">Deploy New GPU</h1>
      <p class="mt-2 text-gray-600 max-w-2xl mx-auto">Make your GPU available for rent and start earning passive income. Fill in the details below to get started.</p>
    </div>
    
    <Card padding="lg" className="bg-white shadow-sm rounded-lg">
      {#if loading && availableGpus.length === 0}
        <div class="text-center py-12">
          <svg class="mx-auto h-12 w-12 animate-spin text-indigo-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <h3 class="mt-4 text-lg font-medium text-gray-900">Scanning for GPUs</h3>
          <p class="mt-2 text-sm text-gray-500">We're checking your system for available GPUs. This may take a moment...</p>
        </div>
      {:else if availableGpus.length === 0}
        <div class="text-center py-12">
          <div class="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-red-100">
            <svg class="h-8 w-8 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <h3 class="mt-4 text-lg font-medium text-gray-900">No GPUs Detected</h3>
          <p class="mt-2 text-sm text-gray-500">We couldn't find any NVIDIA GPUs in your system. Make sure your GPU is properly installed and drivers are up to date.</p>
          <div class="mt-6">
            <a href="https://www.nvidia.com/download/index.aspx" target="_blank" rel="noopener noreferrer" class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
              Download NVIDIA Drivers
              <svg class="ml-2 -mr-1 h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10.293 5.293a1 1 0 011.414 0l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414-1.414L12.586 11H5a1 1 0 110-2h7.586l-2.293-2.293a1 1 0 010-1.414z" clip-rule="evenodd" />
              </svg>
            </a>
          </div>
        </div>
      {:else if error}
        <div class="bg-red-50 border-l-4 border-red-400 p-4 mb-6">
          <div class="flex">
            <div class="flex-shrink-0">
              <svg class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
              </svg>
            </div>
            <div class="ml-3">
              <p class="text-sm text-red-700">
                {error}
              </p>
            </div>
          </div>
        </div>
      {:else if success}
        <div class="rounded-md bg-green-50 p-4 mb-6">
          <div class="flex">
            <div class="flex-shrink-0">
              <svg class="h-5 w-5 text-green-400" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
              </svg>
            </div>
            <div class="ml-3">
              <p class="text-sm font-medium text-green-800">
                GPU deployed successfully! Redirecting to dashboard...
              </p>
            </div>
          </div>
        </div>
      {:else}
        <form class="space-y-6" on:submit|preventDefault={handleSubmit}>
          <div class="space-y-2">
            <label for="gpu" class="block text-sm font-medium text-gray-700">Select GPU</label>
            <div class="relative">
              <select
                id="gpu"
                bind:value={selectedGpuId}
                class="block w-full pl-3 pr-10 py-3 text-base border border-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-lg transition-all duration-150"
                disabled={loading}
              >
                {#each availableGpus as gpu}
                  <option value={gpu.uuid}>
                    {gpu.name} - {gpu.memory_total_gb}GB VRAM
                  </option>
                {/each}
              </select>
              <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-700">
                <svg class="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
              </div>
            </div>
          </div>
          
          <div class="space-y-2">
            <label for="name" class="block text-sm font-medium text-gray-700">Display Name</label>
            <div class="relative rounded-md shadow-sm">
              <input
                type="text"
                id="name"
                bind:value={name}
                class="block w-full border border-gray-300 rounded-md py-3 px-4 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm transition-all duration-150"
                placeholder="e.g., My RTX 3090"
                disabled={loading}
              />
            </div>
          </div>
          
          <div class="space-y-2">
            <label for="price" class="block text-sm font-medium text-gray-700">
              Price per hour (USD)
            </label>
            <div class="relative rounded-md shadow-sm">
              <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <span class="text-gray-500">$</span>
              </div>
              <input
                type="number"
                id="price"
                bind:value={pricePerHour}
                min="0.1"
                step="0.1"
                class="block w-full pl-7 pr-16 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm transition-all duration-150"
                placeholder="0.50"
                disabled={loading}
              />
              <div class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                <span class="text-gray-500 text-sm">/ hour</span>
              </div>
            </div>
            <p class="mt-1 text-xs text-gray-500">
              Suggested: $0.50 - $2.00 per hour based on GPU performance
            </p>
          </div>
          
          <div class="space-y-2">
            <label for="description" class="block text-sm font-medium text-gray-700">
              Description (optional)
            </label>
            <div class="rounded-md shadow-sm">
              <textarea
                id="description"
                bind:value={description}
                rows={4}
                class="block w-full border border-gray-300 rounded-md py-3 px-4 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm transition-all duration-150"
                placeholder="Example: This GPU is available 24/7 and is optimized for machine learning tasks. It's water-cooled and maintained in a temperature-controlled environment."
                disabled={loading}
              ></textarea>
            </div>
            <p class="mt-1 text-xs text-gray-500">
              Include any special features, availability, or requirements
            </p>
          </div>
          
          <div class="pt-2">
            <Button
              type="submit"
              variant="primary"
              class="w-full justify-center py-3 px-6 text-base font-medium rounded-lg shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 transition-all duration-150"
              disabled={loading || availableGpus.length === 0}
            >
              {#if loading}
                <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              {/if}
              {loading ? 'Deploying...' : availableGpus.length > 0 ? 'Deploy GPU' : 'No GPUs Available'}
            </Button>
            <p class="mt-3 text-center text-sm text-gray-500">
              By deploying your GPU, you agree to our{' '}
              <a href="/terms" class="font-medium text-indigo-600 hover:text-indigo-500">Terms of Service</a>
            </p>
          </div>
        </form>
      {/if}
    </Card>
    
    <div class="mt-6 text-center">
      <button
        type="button"
        on:click={() => goto('/dashboard')}
        class="text-sm font-medium text-indigo-600 hover:text-indigo-500 focus:outline-none"
        disabled={loading}
      >
        &larr; Back to Dashboard
      </button>
    </div>
  </div>
</div>
