<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { page } from '$app/stores';
  const API_URL = import.meta.env.VITE_API_URL;

  // Available workflow options
  const workflowOptions = [
    { value: 'pytorch_inference', label: 'PyTorch Inference' },
    { value: 'fine_tuning', label: 'Fine Tuning' },
    { value: 'orbyte_chatbot', label: 'Orbyte Chatbot' },
    { value: 'training', label: 'Training' },
    { value: 'inference', label: 'Generic Inference' },
    { value: 'embedding', label: 'Embedding Generation' },
    { value: 'model_serving', label: 'Model Serving' },
  ];

  // Form state
  let gpuId: string;
  let supportedWorkflows = [];
  let installedModels = [];
  let newModel = '';
  let isLoading = true;
  let error = '';
  let success = '';

  // Get GPU ID from URL
  $: gpuId = $page.params.id;

  // Load GPU configuration
  async function loadGpuConfig() {
    try {
      isLoading = true;
      const [workflowsRes, modelsRes] = await Promise.all([
        fetch(`${API_URL}/api/gpus/${gpuId}/workflows`, {
          credentials: 'include',
        }),
        fetch(`${API_URL}/api/gpus/${gpuId}/models`, {
          credentials: 'include',
        }),
      ]);

      if (workflowsRes.ok) {
        const data = await workflowsRes.json();
        supportedWorkflows = data.data.map((wf) => wf.workflow_type);
      }

      if (modelsRes.ok) {
        const data = await modelsRes.json();
        installedModels = data.data.map((m) => m.model_name);
      }
    } catch (err) {
      error = 'Failed to load GPU configuration';
      console.error(err);
    } finally {
      isLoading = false;
    }
  }

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

  // Handle form submission
  async function handleSubmit(e: Event) {
    e.preventDefault();
    
    try {
      isLoading = true;
      error = '';
      success = '';

      const response = await fetch(`${API_URL}/api/gpus/${gpuId}/configure-workflows`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          supported_workflows: supportedWorkflows,
          installed_models: installedModels,
        }),
      });

      if (response.ok) {
        success = 'GPU configuration updated successfully!';
        // Reload the configuration
        await loadGpuConfig();
      } else {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to update configuration');
      }
    } catch (err) {
      error = err.message || 'Failed to update configuration';
      console.error(err);
    } finally {
      isLoading = false;
    }
  }

  // Load initial data
  onMount(() => {
    if (gpuId) {
      loadGpuConfig();
    } else {
      error = 'GPU ID is required';
      isLoading = false;
    }
  });
</script>

<div class="max-w-4xl mx-auto p-6">
  <h1 class="text-3xl font-bold mb-6">Configure GPU Workflows & Models</h1>
  
  {#if error}
    <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4" role="alert">
      <span class="block sm:inline">{error}</span>
    </div>
  {/if}
  
  {#if success}
    <div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4" role="alert">
      <span class="block sm:inline">{success}</span>
    </div>
  {/if}

  {#if isLoading}
    <div class="flex justify-center items-center h-64">
      <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
    </div>
  {:else}
    <form on:submit={handleSubmit} class="space-y-6">
      <!-- Supported Workflows Section -->
      <div class="bg-white shadow overflow-hidden sm:rounded-lg p-6">
        <h2 class="text-xl font-semibold mb-4">Supported Workflows</h2>
        <p class="text-gray-600 mb-4">Select the types of workloads this GPU can handle:</p>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          {#each workflowOptions as option}
            <label class="flex items-center space-x-3">
              <input
                type="checkbox"
                class="form-checkbox h-5 w-5 text-blue-600"
                checked={supportedWorkflows.includes(option.value)}
                on:change={() => toggleWorkflow(option.value)}
              />
              <span class="text-gray-700">{option.label}</span>
            </label>
          {/each}
        </div>
      </div>

      <!-- Installed Models Section -->
      <div class="bg-white shadow overflow-hidden sm:rounded-lg p-6">
        <h2 class="text-xl font-semibold mb-4">Installed Models</h2>
        <p class="text-gray-600 mb-4">Add models that are pre-installed on this GPU:</p>
        
        <div class="flex space-x-2 mb-4">
          <input
            type="text"
            bind:value={newModel}
            class="flex-1 min-w-0 block w-full px-3 py-2 rounded-md border border-gray-300 shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            placeholder="e.g., llama3-7b"
            on:keydown={(e) => e.key === 'Enter' && (e.preventDefault(), addModel())}
          />
          <button
            type="button"
            on:click={addModel}
            class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            Add Model
          </button>
        </div>
        
        {#if installedModels.length > 0}
          <div class="flex flex-wrap gap-2">
            {#each installedModels as model}
              <span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
                {model}
                <button
                  type="button"
                  on:click={() => removeModel(model)}
                  class="ml-2 text-blue-500 hover:text-blue-700"
                >
                  &times;
                </button>
              </span>
            {/each}
          </div>
        {:else}
          <p class="text-gray-500 italic">No models added yet</p>
        {/if}
      </div>

      <!-- Form Actions -->
      <div class="flex justify-end space-x-3">
        <button
          type="button"
          on:click={() => goto(`/gpus/${gpuId}`)}
          class="bg-white py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          Cancel
        </button>
        <button
          type="submit"
          disabled={isLoading}
          class="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? 'Saving...' : 'Save Configuration'}
        </button>
      </div>
    </form>
  {/if}
</div>
