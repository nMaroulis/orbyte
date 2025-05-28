<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { user } from '$lib/stores/auth';
  import { onDestroy } from 'svelte';
  import { API_ENDPOINTS } from '$lib/api/config';
  import { api } from '$lib/api/client';
  
  // Form state
  let formData = {
    email: '',
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
    wallet_address: ''
  };
  
  let isLoading = false;
  let error = '';
  let success = '';
  
  // Load user data
  onMount(async () => {
    try {
      isLoading = true;
      const response = await api.get(API_ENDPOINTS.AUTH.ME);
      if (response.data) {
        formData.email = response.data.email || '';
        formData.wallet_address = response.data.wallet_address || '';
      }
    } catch (err) {
      error = 'Failed to load user data';
      console.error('Error loading user data:', err);
    } finally {
      isLoading = false;
    }
  });
  
  async function handleSubmit() {
    // Basic validation
    if (formData.newPassword && formData.newPassword !== formData.confirmPassword) {
      error = 'New passwords do not match';
      return;
    }
    
    try {
      isLoading = true;
      error = '';
      success = '';
      
      // Prepare update data
      const updateData: any = {};
      if (formData.newPassword) {
        updateData.password = formData.newPassword;
        updateData.current_password = formData.currentPassword;
      }
      
      if (formData.wallet_address) {
        updateData.wallet_address = formData.wallet_address;
      }
      
      // Send update request
      const response = await api.patch(API_ENDPOINTS.AUTH.ME, updateData);
      
      if (response.success) {
        success = 'Account updated successfully';
        // Update user store if email changed
        if (response.data?.email) {
          user.update(u => ({
            ...u,
            email: response.data.email
          }));
        }
      }
    } catch (err) {
      console.error('Error updating account:', err);
      error = err.response?.data?.detail || 'Failed to update account';
    } finally {
      isLoading = false;
    }
  }
</script>

<div class="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
  <div class="max-w-4xl mx-auto">
    <div class="text-center mb-8">
      <h1 class="text-3xl font-extrabold text-gray-900">Account Settings</h1>
      <p class="mt-2 text-sm text-gray-600">Manage your account information and security settings</p>
    </div>
    
    {#if error}
      <div class="mb-6 bg-red-50 border-l-4 border-red-400 p-4">
        <div class="flex">
          <div class="flex-shrink-0">
            <svg class="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="ml-3">
            <p class="text-sm text-red-700">{error}</p>
          </div>
        </div>
      </div>
    {/if}
    
    {#if success}
      <div class="mb-6 bg-green-50 border-l-4 border-green-400 p-4">
        <div class="flex">
          <div class="flex-shrink-0">
            <svg class="h-5 w-5 text-green-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="ml-3">
            <p class="text-sm text-green-700">{success}</p>
          </div>
        </div>
      </div>
    {/if}
    
    <div class="bg-white shadow overflow-hidden sm:rounded-lg">
      <div class="px-4 py-5 sm:px-6 border-b border-gray-200">
        <h3 class="text-lg leading-6 font-medium text-gray-900">Profile Information</h3>
        <p class="mt-1 max-w-2xl text-sm text-gray-500">Update your account's profile information and email address.</p>
      </div>
      
      <form on:submit|preventDefault={handleSubmit} class="divide-y divide-gray-200">
        <div class="px-4 py-5 sm:p-6">
          <div class="grid grid-cols-6 gap-6">
            <div class="col-span-6 sm:col-span-4">
              <label for="email" class="block text-sm font-medium text-gray-700">Email address</label>
              <input
                type="email"
                id="email"
                name="email"
                bind:value={formData.email}
                class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                disabled={isLoading}
              />
            </div>
            
            <div class="col-span-6 sm:col-span-4">
              <label for="wallet_address" class="block text-sm font-medium text-gray-700">Wallet Address</label>
              <input
                type="text"
                id="wallet_address"
                name="wallet_address"
                bind:value={formData.wallet_address}
                class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                disabled={isLoading}
                placeholder="0x..."
              />
            </div>
          </div>
        </div>
        
        <div class="px-4 py-5 sm:p-6">
          <div class="grid grid-cols-6 gap-6">
            <div class="col-span-6">
              <h3 class="text-lg font-medium text-gray-900">Change Password</h3>
              <p class="mt-1 text-sm text-gray-500">Leave blank to keep your current password.</p>
            </div>
            
            <div class="col-span-6 sm:col-span-4">
              <label for="current_password" class="block text-sm font-medium text-gray-700">Current Password</label>
              <input
                type="password"
                id="current_password"
                name="current_password"
                bind:value={formData.currentPassword}
                class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                disabled={isLoading}
              />
            </div>
            
            <div class="col-span-6 sm:col-span-4">
              <label for="new_password" class="block text-sm font-medium text-gray-700">New Password</label>
              <input
                type="password"
                id="new_password"
                name="new_password"
                bind:value={formData.newPassword}
                class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                disabled={isLoading}
              />
            </div>
            
            <div class="col-span-6 sm:col-span-4">
              <label for="confirm_password" class="block text-sm font-medium text-gray-700">Confirm New Password</label>
              <input
                type="password"
                id="confirm_password"
                name="confirm_password"
                bind:value={formData.confirmPassword}
                class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                disabled={isLoading}
              />
            </div>
          </div>
        </div>
        
        <div class="px-4 py-3 bg-gray-50 text-right sm:px-6">
          <button
            type="button"
            on:click={() => goto('/dashboard')}
            class="bg-white py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            disabled={isLoading}
          >
            Cancel
          </button>
          <button
            type="submit"
            class="ml-3 inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
            disabled={isLoading}
          >
            {isLoading ? 'Saving...' : 'Save Changes'}
          </button>
        </div>
      </form>
    </div>
    
    <div class="mt-8 bg-white shadow sm:rounded-lg">
      <div class="px-4 py-5 sm:p-6">
        <h3 class="text-lg leading-6 font-medium text-gray-900">Danger Zone</h3>
        <div class="mt-2 max-w-xl text-sm text-gray-500">
          <p>Once you delete your account, there is no going back. Please be certain.</p>
        </div>
        <div class="mt-5">
          <button
            type="button"
            class="inline-flex items-center justify-center px-4 py-2 border border-transparent font-medium rounded-md text-red-700 bg-red-100 hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 sm:text-sm"
            disabled={isLoading}
            on:click={() => {
              if (confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
                // TODO: Implement account deletion
              }
            }}
          >
            Delete Account
          </button>
        </div>
      </div>
    </div>
  </div>
</div>
