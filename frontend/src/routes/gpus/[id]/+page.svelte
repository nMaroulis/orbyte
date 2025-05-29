<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { toast } from 'svelte-sonner';
  import { API_ENDPOINTS } from '$lib/api/config';
  import { api } from '$lib/api/client';
  
  // Get GPU ID from URL params and ensure it's a number
  export let data: { params: { id: string } };
  const gpuId = parseInt(data.params.id, 10);
  
  if (isNaN(gpuId)) {
    throw new Error('Invalid GPU ID');
  }
  
  // Types
  interface GPUSpecs {
    cuda_cores?: number;
    memory_type?: string;
    memory_bus?: number;
    bandwidth?: number;
    tensor_cores?: number;
    base_clock?: number;
    boost_clock?: number;
  }
  
  interface Workflow {
    id: number;
    workflow_type: string;
    status: string;
    config: Record<string, any>;
    created_at: string;
    updated_at: string | null;
  }
  
  interface Model {
    id: number;
    model_type: string;
    model_name: string;
    model_path: string | null;
    is_active: boolean;
    created_at: string;
    updated_at: string | null;
  }
  
  interface GPU {
    id: number;
    name: string;
    model: string;
    vram_gb: number;
    price_per_hour: number;
    status: string;
    os?: string;
    cpu_model?: string;
    cpu_cores?: number;
    ram_gb?: number;
    storage_gb?: number;
    network_speed_mbps?: number;
    specs: GPUSpecs;
    created_at: string;
    updated_at: string | null;
  }
  
  interface GPUDetails {
    gpu: GPU;
    workflows: Workflow[];
    models: Model[];
  }
  
  // State
  let gpu: GPU | null = null;
  let workflows: Workflow[] = [];
  let models: Model[] = [];
  let isLoading = true;
  let error: string | null = null;
  let activeTab: 'overview' | 'workflows' | 'models' = 'overview';
  
  // Fetch GPU details
  async function fetchGPU() {
    if (!gpuId) {
      error = 'GPU ID is required';
      isLoading = false;
      return;
    }

    try {
      isLoading = true;
      error = null;
      
      // Use the API client which handles authentication automatically
      const response = await api.get<{ data: { gpu: GPU, workflows: Workflow[], models: Model[] } }>(
        `${API_ENDPOINTS.GPUS.DETAIL(gpuId)}/details`
      );
      
      gpu = response.data.gpu;
      workflows = response.data.workflows || [];
      models = response.data.models || [];
      
      // Ensure specs is always an object
      if (gpu) {
        gpu.specs = gpu.specs || {};
      }
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load GPU details';
      error = errorMessage;
      toast.error(errorMessage);
    } finally {
      isLoading = false;
    }
  }
  
  // Format date
  function formatDate(dateString: string | null | undefined): string {
    if (!dateString) return 'N/A';
    try {
      return new Date(dateString).toLocaleString();
    } catch (e) {
      return 'Invalid date';
    }
  }
  
  // Format status
  function formatStatus(status: string): string {
    if (!status) return 'Unknown';
    return status
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
      .join(' ');
  }
  
  // Format workflow type
  function formatWorkflowType(type: string): string {
    if (!type) return 'N/A';
    return type
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
      .join(' ');
  }
  
  // Format model type
  function formatModelType(type: string): string {
    if (!type) return 'Unknown';
    return type
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  }
  
  // Format configuration object
  function formatConfig(config: Record<string, any> | null): string {
    if (!config) return 'No configuration';
    try {
      return JSON.stringify(config, null, 2);
    } catch (e) {
      return 'Invalid configuration';
    }
  }
  
  // Initialize
  onMount(() => {
    fetchGPU();
  });
</script>

<div class="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
  <div class="max-w-4xl mx-auto">
    <!-- Back button -->
    <div class="mb-6">
      <button
        on:click={() => goto('/gpus')}
        class="inline-flex items-center text-indigo-600 hover:text-indigo-800"
      >
        <svg class="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
        </svg>
        Back to GPUs
      </button>
    </div>

    {#if isLoading}
      <div class="text-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
        <p class="mt-4 text-sm text-gray-500">Loading GPU details...</p>
      </div>
    {:else if error}
      <div class="bg-red-50 border-l-4 border-red-400 p-4">
        <div class="flex">
          <div class="flex-shrink-0">
            <svg class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="ml-3">
            <p class="text-sm text-red-700">{error}</p>
          </div>
        </div>
      </div>
    {:else if gpu}
      <div class="bg-white shadow overflow-hidden sm:rounded-lg">
        <!-- Header -->
        <div class="px-4 py-5 sm:px-6 border-b border-gray-200">
          <div class="flex justify-between items-center">
            <div>
              <h1 class="text-2xl font-bold text-gray-900">{gpu.name}</h1>
              <p class="mt-1 text-sm text-gray-500">{gpu.model}</p>
            </div>
            <span class={`px-3 py-1 rounded-full text-sm font-medium ${
              gpu.status === 'available' ? 'bg-green-100 text-green-800' :
              gpu.status === 'in_use' ? 'bg-blue-100 text-blue-800' :
              'bg-gray-100 text-gray-800'
            }`}>
              {formatStatus(gpu.status)}
            </span>
          </div>
        </div>

        <!-- Tabs -->
        <div class="border-b border-gray-200">
          <nav class="-mb-px flex space-x-8 px-4">
            <button
              class={`py-4 px-1 border-b-2 font-medium text-sm ${activeTab === 'overview' ? 'border-indigo-500 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}`}
              on:click={() => activeTab = 'overview'}
            >
              Overview
            </button>
            <button
              class={`py-4 px-1 border-b-2 font-medium text-sm ${activeTab === 'workflows' ? 'border-indigo-500 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}`}
              on:click={() => activeTab = 'workflows'}
            >
              Workflows ({workflows.length})
            </button>
            <button
              class={`py-4 px-1 border-b-2 font-medium text-sm ${activeTab === 'models' ? 'border-indigo-500 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}`}
              on:click={() => activeTab = 'models'}
            >
              Models ({models.length})
            </button>
          </nav>
        </div>

        <!-- Tab Content -->
        <div class="px-4 py-5 sm:p-6">
          {#if activeTab === 'overview'}
            <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
              <!-- GPU Details -->
              <div>
                <h2 class="text-lg font-medium text-gray-900 mb-4">GPU Information</h2>
                <dl class="space-y-4">
                  <div class="sm:grid sm:grid-cols-3 sm:gap-4">
                    <dt class="text-sm font-medium text-gray-500">VRAM</dt>
                    <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{gpu.vram_gb} GB</dd>
                  </div>
                  <div class="sm:grid sm:grid-cols-3 sm:gap-4">
                    <dt class="text-sm font-medium text-gray-500">Price/Hour</dt>
                    <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">${gpu.price_per_hour.toFixed(2)}</dd>
                  </div>
                  {#if gpu.specs?.cuda_cores !== undefined}
                    <div class="sm:grid sm:grid-cols-3 sm:gap-4">
                      <dt class="text-sm font-medium text-gray-500">CUDA Cores</dt>
                      <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{gpu.specs.cuda_cores.toLocaleString()}</dd>
                    </div>
                  {/if}
                  {#if gpu.specs?.tensor_cores !== undefined}
                    <div class="sm:grid sm:grid-cols-3 sm:gap-4">
                      <dt class="text-sm font-medium text-gray-500">Tensor Cores</dt>
                      <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{gpu.specs.tensor_cores.toLocaleString()}</dd>
                    </div>
                  {/if}
                  {#if gpu.specs?.memory_type}
                    <div class="sm:grid sm:grid-cols-3 sm:gap-4">
                      <dt class="text-sm font-medium text-gray-500">Memory Type</dt>
                      <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{gpu.specs.memory_type}</dd>
                    </div>
                  {/if}
                  {#if gpu.specs?.memory_bus !== undefined}
                    <div class="sm:grid sm:grid-cols-3 sm:gap-4">
                      <dt class="text-sm font-medium text-gray-500">Memory Bus</dt>
                      <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{gpu.specs.memory_bus}-bit</dd>
                    </div>
                  {/if}
                  {#if gpu.specs?.bandwidth !== undefined}
                    <div class="sm:grid sm:grid-cols-3 sm:gap-4">
                      <dt class="text-sm font-medium text-gray-500">Bandwidth</dt>
                      <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{gpu.specs.bandwidth} GB/s</dd>
                    </div>
                  {/if}
                  {#if gpu.specs?.base_clock !== undefined}
                    <div class="sm:grid sm:grid-cols-3 sm:gap-4">
                      <dt class="text-sm font-medium text-gray-500">Base Clock</dt>
                      <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{gpu.specs.base_clock} MHz</dd>
                    </div>
                  {/if}
                  {#if gpu.specs?.boost_clock !== undefined}
                    <div class="sm:grid sm:grid-cols-3 sm:gap-4">
                      <dt class="text-sm font-medium text-gray-500">Boost Clock</dt>
                      <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{gpu.specs.boost_clock} MHz</dd>
                    </div>
                  {/if}
                </dl>
              </div>

              <!-- System Information -->
              <div>
                <h2 class="text-lg font-medium text-gray-900 mb-4">System Information</h2>
                <dl class="space-y-4">
                  <div class="sm:grid sm:grid-cols-3 sm:gap-4">
                    <dt class="text-sm font-medium text-gray-500">ID</dt>
                    <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2 font-mono">{gpu.id}</dd>
                  </div>
                  {#if gpu.os}
                    <div class="sm:grid sm:grid-cols-3 sm:gap-4">
                      <dt class="text-sm font-medium text-gray-500">OS</dt>
                      <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{gpu.os}</dd>
                    </div>
                  {/if}
                  {#if gpu.cpu_model}
                    <div class="sm:grid sm:grid-cols-3 sm:gap-4">
                      <dt class="text-sm font-medium text-gray-500">CPU</dt>
                      <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                        {gpu.cpu_model}{gpu.cpu_cores ? ` (${gpu.cpu_cores} cores)` : ''}
                      </dd>
                    </div>
                  {/if}
                  {#if gpu.ram_gb !== undefined}
                    <div class="sm:grid sm:grid-cols-3 sm:gap-4">
                      <dt class="text-sm font-medium text-gray-500">System RAM</dt>
                      <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{gpu.ram_gb} GB</dd>
                    </div>
                  {/if}
                  {#if gpu.storage_gb !== undefined}
                    <div class="sm:grid sm:grid-cols-3 sm:gap-4">
                      <dt class="text-sm font-medium text-gray-500">Storage</dt>
                      <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{gpu.storage_gb} GB</dd>
                    </div>
                  {/if}
                  {#if gpu.network_speed_mbps !== undefined}
                    <div class="sm:grid sm:grid-cols-3 sm:gap-4">
                      <dt class="text-sm font-medium text-gray-500">Network Speed</dt>
                      <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{gpu.network_speed_mbps} Mbps</dd>
                    </div>
                  {/if}
                  <div class="sm:grid sm:grid-cols-3 sm:gap-4">
                    <dt class="text-sm font-medium text-gray-500">Created At</dt>
                    <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{formatDate(gpu.created_at)}</dd>
                  </div>
                  {#if gpu.updated_at}
                    <div class="sm:grid sm:grid-cols-3 sm:gap-4">
                      <dt class="text-sm font-medium text-gray-500">Last Updated</dt>
                      <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{formatDate(gpu.updated_at)}</dd>
                    </div>
                  {/if}
                </dl>
              </div>
            </div>
          {:else if activeTab === 'workflows'}
            <div class="overflow-hidden bg-white shadow sm:rounded-md">
              {#if workflows.length === 0}
                <div class="text-center py-12">
                  <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                  </svg>
                  <h3 class="mt-2 text-sm font-medium text-gray-900">No workflows</h3>
                  <p class="mt-1 text-sm text-gray-500">This GPU doesn't have any workflows yet.</p>
                </div>
              {:else}
                <ul class="divide-y divide-gray-200">
                  {#each workflows as workflow}
                    <li class="px-4 py-4 sm:px-6">
                      <div class="flex items-center justify-between">
                        <div class="flex items-center">
                          <p class="text-sm font-medium text-indigo-600 truncate">{formatWorkflowType(workflow.workflow_type)}</p>
                          <span class={`ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                            workflow.status === 'running' ? 'bg-green-100 text-green-800' :
                            workflow.status === 'failed' ? 'bg-red-100 text-red-800' :
                            'bg-gray-100 text-gray-800'
                          }`}>
                            {formatStatus(workflow.status)}
                          </span>
                        </div>
                        <div class="ml-2 flex-shrink-0 flex">
                          <p class="text-sm text-gray-500">{formatDate(workflow.updated_at || workflow.created_at)}</p>
                        </div>
                      </div>
                      {#if workflow.config}
                        <div class="mt-2">
                          <p class="text-xs text-gray-500">Configuration:</p>
                          <pre class="mt-1 text-xs text-gray-900 bg-gray-50 p-2 rounded overflow-auto max-h-40">
                            {formatConfig(workflow.config)}
                          </pre>
                        </div>
                      {/if}
                    </li>
                  {/each}
                </ul>
              {/if}
            </div>
          {:else if activeTab === 'models'}
            <div class="overflow-hidden bg-white shadow sm:rounded-md">
              {#if models.length === 0}
                <div class="text-center py-12">
                  <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                  </svg>
                  <h3 class="mt-2 text-sm font-medium text-gray-900">No models</h3>
                  <p class="mt-1 text-sm text-gray-500">This GPU doesn't have any models installed yet.</p>
                </div>
              {:else}
                <ul class="divide-y divide-gray-200">
                  {#each models as model}
                    <li class="px-4 py-4 sm:px-6">
                      <div class="flex items-center justify-between">
                        <div class="flex items-center">
                          <p class="text-sm font-medium text-indigo-600 truncate">{model.model_name}</p>
                          <span class="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                            {formatModelType(model.model_type)}
                          </span>
                          {#if model.is_active}
                            <span class="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                              Active
                            </span>
                          {/if}
                        </div>
                        <div class="ml-2 flex-shrink-0 flex">
                          <p class="text-sm text-gray-500">{formatDate(model.updated_at || model.created_at)}</p>
                        </div>
                      </div>
                      {#if model.model_path}
                        <div class="mt-1">
                          <p class="text-xs text-gray-500 truncate">Path: {model.model_path}</p>
                        </div>
                      {/if}
                    </li>
                  {/each}
                </ul>
              {/if}
            </div>
          {/if}
        </div>

        <!-- Actions -->
        <div class="px-4 py-4 bg-gray-50 text-right sm:px-6">
          <button
            on:click={() => goto(`/gpus/${gpu.id}/edit`)}
            class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            <svg class="-ml-1 mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
            Edit GPU
          </button>
        </div>
      </div>
    {/if}
  </div>
</div>