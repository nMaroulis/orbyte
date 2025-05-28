<script lang="ts">
  import { onMount } from 'svelte';
  import { api } from '$lib/api/client';
  import { API_ENDPOINTS } from '$lib/api/config';
  import Button from '$lib/components/ui/Button.svelte';
  import Card from '$lib/components/ui/Card.svelte';

  interface Message {
    id: string;
    content: string;
    role: 'user' | 'assistant' | 'system';
    timestamp: Date;
  }

  interface Model {
    id: string;
    name: string;
    description: string;
    context_length: number;
  }

  let messages: Message[] = [];
  let inputMessage = '';
  let isLoading = false;
  let selectedModel = '';
  let availableModels: Model[] = [];
  let isModelDropdownOpen = false;

  const loadModels = async () => {
    try {
      isLoading = true;
      // Replace with actual API call to fetch available models
      // const response = await api.get(API_ENDPOINTS.MODELS.LIST);
      // availableModels = response.data;
      
      // Mock data for now
      availableModels = [
        { id: 'llama3-8b', name: 'Llama 3 8B', description: 'Efficient 8 billion parameter model', context_length: 4096 },
        { id: 'llama3-70b', name: 'Llama 3 70B', description: 'Powerful 70 billion parameter model', context_length: 8192 },
        { id: 'mistral-7b', name: 'Mistral 7B', description: 'High-quality 7B parameter model', context_length: 4096 },
      ];
      
      if (availableModels.length > 0) {
        selectedModel = availableModels[0].id;
      }
    } catch (error) {
      console.error('Error loading models:', error);
    } finally {
      isLoading = false;
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || !selectedModel) return;
    
    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputMessage,
      role: 'user',
      timestamp: new Date()
    };
    
    messages = [...messages, userMessage];
    const message = inputMessage;
    inputMessage = '';
    
    try {
      isLoading = true;
      
      // Replace with actual API call to send message
      // const response = await api.post(API_ENDPOINTS.CHAT.SEND, {
      //   message,
      //   model: selectedModel
      // });
      
      // Mock response for now
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: `This is a mock response for: \"${message}\"`,
        role: 'assistant',
        timestamp: new Date()
      };
      
      messages = [...messages, botMessage];
    } catch (error) {
      console.error('Error sending message:', error);
      
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: 'Sorry, I encountered an error processing your request. Please try again.',
        role: 'assistant',
        timestamp: new Date()
      };
      
      messages = [...messages, errorMessage];
    } finally {
      isLoading = false;
      // Scroll to bottom of chat
      setTimeout(() => {
        const chatContainer = document.getElementById('chat-messages');
        if (chatContainer) {
          chatContainer.scrollTop = chatContainer.scrollHeight;
        }
      }, 100);
    }
  };

  const handleKeyDown = (e: KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  onMount(() => {
    loadModels();
  });
</script>

<div class="flex flex-col h-[calc(100vh-4rem)] bg-gray-50">
  <!-- Model Selection -->
  <div class="bg-white border-b border-gray-200">
    <div class="max-w-4xl mx-auto px-4 py-3">
      <div class="relative">
        <button
          type="button"
          on:click={() => isModelDropdownOpen = !isModelDropdownOpen}
          on:keydown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') {
              e.preventDefault();
              isModelDropdownOpen = !isModelDropdownOpen;
            } else if (e.key === 'Escape') {
              isModelDropdownOpen = false;
            }
          }}
          class="flex items-center justify-between w-full px-4 py-2 text-sm font-medium text-left text-gray-700 bg-white border border-gray-300 rounded-md shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
          aria-haspopup="listbox"
          aria-expanded={isModelDropdownOpen}
          aria-labelledby="listbox-label"
        >
          <span class="truncate">
            {availableModels.find(m => m.id === selectedModel)?.name || 'Select a model'}
          </span>
          <svg class="w-5 h-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
            <path fill-rule="evenodd" d="M10 3a1 1 0 01.707.293l3 3a1 1 0 01-1.414 1.414L10 5.414 7.707 7.707a1 1 0 01-1.414-1.414l3-3A1 1 0 0110 3zm-3.707 9.293a1 1 0 011.414 0L10 14.586l2.293-2.293a1 1 0 011.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clip-rule="evenodd" />
          </svg>
        </button>

        {#if isModelDropdownOpen}
          <div class="absolute z-10 w-full mt-1 bg-white shadow-lg rounded-md py-1 text-base ring-1 ring-black ring-opacity-5 focus:outline-none sm:text-sm" tabindex="-1">
            <ul class="max-h-60 overflow-auto" role="listbox" aria-labelledby="listbox-label">
              {#each availableModels as model}
                <li 
                  id="listbox-option-{model.id}" 
                  role="option"
                  aria-selected={selectedModel === model.id}
                  class="cursor-pointer select-none relative py-2 pl-3 pr-9 hover:bg-indigo-50"
                  on:click={() => {
                    selectedModel = model.id;
                    isModelDropdownOpen = false;
                  }}
                  on:keydown={(e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                      e.preventDefault();
                      selectedModel = model.id;
                      isModelDropdownOpen = false;
                    } else if (e.key === 'Escape') {
                      isModelDropdownOpen = false;
                    }
                  }}
                  tabindex="0"
                >
                  <div class="flex items-center">
                    <span class="block font-normal truncate">
                      {model.name}
                    </span>
                  </div>
                  {#if selectedModel === model.id}
                    <span class="absolute inset-y-0 right-0 flex items-center pr-4 text-indigo-600">
                      <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                      </svg>
                    </span>
                  {/if}
                </li>
              {/each}
            </ul>
          </div>
        {/if}
      </div>
    </div>
  </div>

  <!-- Chat Messages -->
  <div id="chat-messages" class="flex-1 overflow-y-auto p-4">
    <div class="max-w-3xl mx-auto space-y-6 w-full">
      {#if messages.length === 0}
        <div class="text-center py-12">
          <div class="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-indigo-100 mb-4">
            <svg class="h-8 w-8 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.308-3.076C3.88 15.611 3 13.9 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
          </div>
          <h3 class="text-lg font-medium text-gray-900">Start a conversation</h3>
          <p class="mt-1 text-sm text-gray-500">Select a model and type a message to begin chatting. Orbyte will take care of the inference GPU 😎</p>
        </div>
      {:else}
        {#each messages as message (message.id)}
          <div class="flex {message.role === 'user' ? 'justify-end' : 'justify-start'}">
            <div class="flex max-w-3xl">
              <div class="flex-shrink-0">
                {#if message.role === 'user'}
                  <div class="h-8 w-8 rounded-full bg-indigo-100 flex items-center justify-center">
                    <svg class="h-5 w-5 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                  </div>
                {:else}
                  <div class="h-8 w-8 rounded-full bg-purple-100 flex items-center justify-center">
                    <svg class="h-5 w-5 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                    </svg>
                  </div>
                {/if}
              </div>
              <div class="ml-3">
                <div class="text-sm font-medium text-gray-900">
                  {message.role === 'user' ? 'You' : 'Orbyte AI'}
                </div>
                <div class="mt-1 text-sm text-gray-700 whitespace-pre-wrap">
                  {message.content}
                </div>
                <div class="mt-1 text-xs text-gray-500">
                  {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </div>
              </div>
            </div>
          </div>
        {/each}
      {/if}
    </div>
  </div>

  <!-- Input Area -->
  <div class="bg-white border-t border-gray-200 p-4">
    <div class="max-w-3xl mx-auto">
      <div class="flex space-x-4">
        <div class="flex-1">
          <label for="message" class="sr-only">Message</label>
          <div class="relative rounded-md shadow-sm">
            <textarea
              id="message"
              rows={1}
              bind:value={inputMessage}
              on:keydown={handleKeyDown}
              class="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              placeholder="Type your message..."
              disabled={isLoading || !selectedModel}
            ></textarea>
          </div>
        </div>
        <div class="flex-shrink-0">
          <Button 
            on:click={sendMessage}
            disabled={!inputMessage.trim() || isLoading || !selectedModel}
            class="h-full px-6"
          >
            {#if isLoading}
              <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            {/if}
            {isLoading ? 'Sending...' : 'Send'}
          </Button>
        </div>
      </div>
      <p class="mt-2 text-xs text-gray-500 text-center">
        Orbyte AI can make mistakes. Consider checking important information.
      </p>
    </div>
  </div>
</div>
