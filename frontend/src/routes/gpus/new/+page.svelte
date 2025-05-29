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
  
  // Workflow and model configuration
  const workflowOptions = [
    { value: 'pytorch_inference', label: 'PyTorch Inference' },
    { value: 'fine_tuning', label: 'Fine Tuning' },
    { value: 'orbyte_chatbot', label: 'Orbyte Chatbot' },
    { value: 'training', label: 'Training' },
    { value: 'inference', label: 'Generic Inference' },
    { value: 'embedding', label: 'Embedding Generation' },
    { value: 'model_serving', label: 'Model Serving' },
  ];
  
  let supportedWorkflows: string[] = [];
  let installedModels: string[] = [];
  let newModel = '';
  
  // Toggle workflow selection
  function toggleWorkflow(workflow: string) {
    if (supportedWorkflows.includes(workflow)) {
      supportedWorkflows = supportedWorkflows.filter((w) => w !== workflow);
    } else {
      supportedWorkflows = [...supportedWorkflows, workflow];
    }
  }
  
  // Add a new model
  function addModel() {
    if (newModel.trim() && !installedModels.includes(newModel.trim())) {
      installedModels = [...installedModels, newModel.trim()];
      newModel = '';
    }
  }
  
  // Remove a model
  function removeModel(model: string) {
    installedModels = installedModels.filter((m) => m !== model);
  }
  
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
        },
        supported_workflows: supportedWorkflows,
        installed_models: installedModels
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
        <!-- GPU Selection Card -->
        <Card padding="lg" className="bg-white shadow-sm rounded-lg mb-6">
          <h2 class="text-xl font-semibold mb-6">GPU Configuration</h2>
          <div class="space-y-6">
            <div class="space-y-2">
              <label for="gpu" class="block text-sm font-medium text-gray-700">Select GPU</label>
              <div class="relative">
                <select
                  id="gpu"
                  bind:value={selectedGpuId}
                  class="block w-full pl-3 pr-10 py-3 text-base border border-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-lg transition-all duration-150"
                  disabled={loading || availableGpus.length === 0}
                >
                  {#each availableGpus as gpu}
                    <option value={gpu.uuid}>
                      {gpu.name} - {gpu.memory_total_gb}GB VRAM
                    </option>
                  {:else}
                    <option disabled>No GPUs available</option>
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
              <label for="name" class="block text-sm font-medium text-gray-700">GPU Name</label>
              <input
                type="text"
                id="name"
                bind:value={name}
                disabled={loading || availableGpus.length === 0}
                class="block w-full border border-gray-300 rounded-md py-2 px-3 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm transition-all duration-150"
                class:bg-gray-100={availableGpus.length === 0}
                placeholder="e.g., My RTX 4090"
              />
            </div>
            
            <div class="space-y-2">
              <label for="price" class="block text-sm font-medium text-gray-700">Price per hour ($)</label>
              <input
                type="number"
                id="price"
                bind:value={pricePerHour}
                min="0.01"
                step="0.01"
                disabled={loading || availableGpus.length === 0}
                class="block w-full border border-gray-300 rounded-md py-2 px-3 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm transition-all duration-150"
                class:bg-gray-100={availableGpus.length === 0}
              />
            </div>
            
            <div class="space-y-2">
              <label for="description" class="block text-sm font-medium text-gray-700">Description (Optional)</label>
              <textarea
                id="description"
                bind:value={description}
                rows={3}
                disabled={loading || availableGpus.length === 0}
                class="block w-full border border-gray-300 rounded-md py-2 px-3 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm transition-all duration-150"
                class:bg-gray-100={availableGpus.length === 0}
                placeholder="Add any additional details about this GPU..."
              ></textarea>
            </div>
          </div>
        </Card>
        
      {/if}
    </Card>
    <!-- Workflow and Model Configuration Card -->
    <Card padding="lg" className="bg-white shadow-sm rounded-lg">
      <h2 class="text-xl font-semibold mb-6">Workflow & Model Configuration</h2>
      <div class="space-y-6">
        <!-- Supported Workflows Section -->
        <div class="space-y-4">
          <h3 class="text-lg font-medium text-gray-900">Supported Workflows</h3>
          <p class="text-sm text-gray-500">Select the types of workloads this GPU can handle:</p>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            {#each workflowOptions as option}
              <label class="flex items-center space-x-3">
                <input
                  type="checkbox"
                  class="form-checkbox h-5 w-5 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
                  checked={supportedWorkflows.includes(option.value)}
                  on:change={() => toggleWorkflow(option.value)}
                  disabled={loading || availableGpus.length === 0}
                />
                <span class="text-gray-700">{option.label}</span>
              </label>
            {/each}
          </div>
        </div>
        
        <!-- Installed Models Section -->
        <div class="space-y-4">
          <h3 class="text-lg font-medium text-gray-900">Installed Models</h3>
          <p class="text-sm text-gray-500">Add models that are pre-installed on this GPU:</p>
          
          <div class="flex space-x-2">
            <input
              type="text"
              bind:value={newModel}
              class="flex-1 min-w-0 block w-full px-3 py-2 rounded-md border border-gray-300 shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              placeholder="e.g., llama3-7b"
              on:keydown={(e) => e.key === 'Enter' && (e.preventDefault(), addModel())}
              disabled={loading || availableGpus.length === 0}
            />
            <button
              type="button"
              on:click={addModel}
              class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-gray-400 disabled:cursor-not-allowed"
              disabled={loading || availableGpus.length === 0 || !newModel.trim()}
            >
              Add Model
            </button>
          </div>
          
          {#if installedModels.length > 0}
            <div class="flex flex-wrap gap-2 mt-2">
              {#each installedModels as model}
                <span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
                  {model}
                  <button
                    type="button"
                    on:click={() => removeModel(model)}
                    class="ml-2 text-blue-500 hover:text-blue-700"
                    disabled={loading || availableGpus.length === 0}
                    aria-label="Remove model"
                  >
                    <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </span>
              {/each}
            </div>
          {/if}
        </div>
        
        <!-- Submit Button -->
        <div class="pt-4">
          <button
            type="button"
            on:click={handleSubmit}
            class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:bg-gray-400 disabled:cursor-not-allowed"
            disabled={loading || availableGpus.length === 0}
          >
            {loading ? 'Deploying...' : 'Deploy GPU'}
          </button>
        </div>
      </div>
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
