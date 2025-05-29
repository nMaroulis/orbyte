<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  const API_URL = import.meta.env.VITE_API_URL;
  import { goto } from '$app/navigation';

  interface GPU {
    id: number;
    name: string;
    model: string;
    vram_gb: number;
    price_per_hour: number;
    status: string;
    specs: {
      cuda_cores?: number;
      tensor_cores?: number;
      memory_type?: string;
      memory_bus?: number;
      bandwidth?: number;
      base_clock?: number;
      boost_clock?: number;
    };
    supported_workflows: Array<{ id: number; workflow_type: string; is_active: boolean }>;
    installed_models: Array<{ id: number; model_name: string; is_active: boolean }>;
    created_at: string;
    updated_at: string | null;
  }

  let gpu: GPU | null = null;
  let isLoading = true;
  let error = '';
  let gpuId: string;

  // Get GPU ID from URL
  $: gpuId = $page.params.id;

  // Format date
  function formatDate(dateString: string | null): string {
    if (!dateString) return 'Never';
    return new Date(dateString).toLocaleString();
  }

  // Format workflows for display
  function formatWorkflowType(workflow: string): string {
    return workflow
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  }

  // Fetch GPU details
  async function fetchGPU() {
    try {
      isLoading = true;
      const [gpuRes, workflowsRes, modelsRes] = await Promise.all([
        fetch(`${API_URL}/api/gpus/${gpuId}`, {
          credentials: 'include',
        }),
        fetch(`${API_URL}/api/gpus/${gpuId}/workflows`, {
          credentials: 'include',
        }),
        fetch(`${API_URL}/api/gpus/${gpuId}/models`, {
          credentials: 'include',
        }),
      ]);

      if (!gpuRes.ok) throw new Error('Failed to fetch GPU details');

      const gpuData = await gpuRes.json();
      const workflowsData = workflowsRes.ok ? await workflowsRes.json() : { data: [] };
      const modelsData = modelsRes.ok ? await modelsRes.json() : { data: [] };

      gpu = {
        ...gpuData.data,
        supported_workflows: workflowsData.data,
        installed_models: modelsData.data,
      };
    } catch (err) {
      error = 'Failed to load GPU details. Please try again later.';
      console.error('Error fetching GPU:', err);
    } finally {
      isLoading = false;
    }
  }

  // Initialize
  onMount(() => {
    if (gpuId) {
      fetchGPU();
    } else {
      error = 'GPU ID is required';
      isLoading = false;
    }
  });
</script>

<div class="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
  <div class="max-w-7xl mx-auto">
    <div class="mb-6">
      <button
        on:click={() => goto('/gpus')}
        class="inline-flex items-center text-sm text-blue-600 hover:text-blue-800 mb-4"
      >
        <svg class="h-4 w-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
        </svg>
        Back to GPUs
      </button>
    </div>

    {#if error}
      <div class="bg-red-50 border-l-4 border-red-400 p-4 mb-6">
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
      <div class="flex justify-center items-center h-64">
        <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    {:else if gpu}
      <div class="bg-white shadow overflow-hidden sm:rounded-lg">
        <div class="px-4 py-5 sm:px-6 flex justify-between items-center border-b border-gray-200">
          <div>
            <h3 class="text-lg leading-6 font-medium text-gray-900">
              {gpu?.name || 'GPU Details'}
            </h3>
            <p class="mt-1 max-w-2xl text-sm text-gray-500">
              GPU Details
            </p>
          </div>
          <div class="flex space-x-3">
            {#if gpu}
              <button
                on:click={() => goto(`/gpu/${gpu.id}/configure`)}
                class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Configure
              </button>
            {/if}
          </div>
        </div>
        
        <div class="border-t border-gray-200 px-4 py-5 sm:p-0">
          <dl class="sm:divide-y sm:divide-gray-200">
            <div class="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt class="text-sm font-medium text-gray-500">Model</dt>
              <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{gpu?.model || 'N/A'}</dd>
            </div>
            <div class="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt class="text-sm font-medium text-gray-500">VRAM</dt>
              <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{gpu?.vram_gb ? `${gpu.vram_gb} GB` : 'N/A'}</dd>
            </div>
            <div class="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt class="text-sm font-medium text-gray-500">Price per Hour</dt>
              <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{gpu?.price_per_hour ? `$${gpu.price_per_hour.toFixed(2)}` : 'N/A'}</dd>
            </div>
            <div class="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt class="text-sm font-medium text-gray-500">Status</dt>
              <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                {#if gpu?.status}
                  <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                    {gpu.status}
                  </span>
                {:else}
                  <span class="text-gray-500">N/A</span>
                {/if}
              </dd>
            </div>
            <div class="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt class="text-sm font-medium text-gray-500">Supported Workflows</dt>
              <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                {#if gpu?.supported_workflows?.length > 0}
                  <div class="flex flex-wrap gap-2">
                    {#each gpu.supported_workflows.filter(w => w.is_active) as workflow}
                      <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                        {formatWorkflowType(workflow.workflow_type)}
                      </span>
                    {/each}
                  </div>
                {:else}
                  <span class="text-gray-500">No workflows configured</span>
                {/if}
              </dd>
            </div>
            <div class="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt class="text-sm font-medium text-gray-500">Installed Models</dt>
              <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                {#if gpu?.installed_models?.length > 0}
                  <div class="flex flex-wrap gap-2">
                    {#each gpu.installed_models.filter(m => m.is_active) as model}
                      <span class="inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-medium bg-purple-100 text-purple-800">
                        {model.model_name}
                      </span>
                    {/each}
                  </div>
                {:else}
                  <span class="text-gray-500">No models installed</span>
                {/if}
              </dd>
            </div>
            <div class="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt class="text-sm font-medium text-gray-500">Created At</dt>
              <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                {gpu?.created_at ? formatDate(gpu.created_at) : 'N/A'}
              </dd>
            </div>
            <div class="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt class="text-sm font-medium text-gray-500">Last Updated</dt>
              <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                {gpu?.updated_at ? formatDate(gpu.updated_at) : 'N/A'}
              </dd>
            </div>
            {#if gpu?.specs && Object.keys(gpu.specs).length > 0}
              <div class="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                <dt class="text-sm font-medium text-gray-500">Specifications</dt>
                <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                  <div class="bg-gray-50 p-4 rounded-md">
                    <dl class="grid grid-cols-1 gap-x-4 gap-y-4 sm:grid-cols-2">
                      {#if gpu?.specs?.cuda_cores !== undefined}
                        <div class="sm:col-span-1">
                          <dt class="text-sm font-medium text-gray-500">CUDA Cores</dt>
                          <dd class="mt-1 text-sm text-gray-900">{gpu.specs.cuda_cores.toLocaleString()}</dd>
                        </div>
                      {/if}
                      {#if gpu?.specs?.tensor_cores !== undefined}
                        <div class="sm:col-span-1">
                          <dt class="text-sm font-medium text-gray-500">Tensor Cores</dt>
                          <dd class="mt-1 text-sm text-gray-900">{gpu.specs.tensor_cores.toLocaleString()}</dd>
                        </div>
                      {/if}
                      {#if gpu?.specs?.memory_type}
                        <div class="sm:col-span-1">
                          <dt class="text-sm font-medium text-gray-500">Memory Type</dt>
                          <dd class="mt-1 text-sm text-gray-900">{gpu.specs.memory_type}</dd>
                        </div>
                      {/if}
                      {#if gpu?.specs?.memory_bus !== undefined}
                        <div class="sm:col-span-1">
                          <dt class="text-sm font-medium text-gray-500">Memory Bus</dt>
                          <dd class="mt-1 text-sm text-gray-900">{gpu.specs.memory_bus}-bit</dd>
                        </div>
                      {/if}
                      {#if gpu?.specs?.bandwidth !== undefined}
                        <div class="sm:col-span-1">
                          <dt class="text-sm font-medium text-gray-500">Bandwidth</dt>
                          <dd class="mt-1 text-sm text-gray-900">{gpu.specs.bandwidth} GB/s</dd>
                        </div>
                      {/if}
                      {#if gpu?.specs?.base_clock !== undefined}
                        <div class="sm:col-span-1">
                          <dt class="text-sm font-medium text-gray-500">Base Clock</dt>
                          <dd class="mt-1 text-sm text-gray-900">{gpu.specs.base_clock} MHz</dd>
                        </div>
                      {/if}
                      {#if gpu?.specs?.boost_clock !== undefined}
                        <div class="sm:col-span-1">
                          <dt class="text-sm font-medium text-gray-500">Boost Clock</dt>
                          <dd class="mt-1 text-sm text-gray-900">{gpu.specs.boost_clock} MHz</dd>
                        </div>
                      {/if}
                    </dl>
                  </div>
                </dd>
              </div>
            {/if}
          </dl>
        </div>
      </div>
    {/if}
  </div>
</div>
