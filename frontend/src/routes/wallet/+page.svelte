<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { user } from '$lib/stores/auth';
  import { api } from '$lib/api/client';
  import { API_ENDPOINTS } from '$lib/api/config';
  import type { WalletsResponse, CryptoWallet, FiatWallet } from '$lib/types/wallet';
  import Card from '$lib/components/ui/Card.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  
  let loading = true;
  let activeTab: 'crypto' | 'fiat' = 'crypto';
  let cryptoWallets: CryptoWallet[] = [];
  let fiatWallets: FiatWallet[] = [];
  let error: string | null = null;

  async function fetchWallets() {
    try {
      loading = true;
      error = null;
      
      // Fetch both wallets in parallel
      const [cryptoResponse, fiatResponse] = await Promise.all([
        api.get<{ data: CryptoWallet[] }>(API_ENDPOINTS.WALLETS.CRYPTO),
        api.get<{ data: FiatWallet[] }>(API_ENDPOINTS.WALLETS.FIAT)
      ]);
      
      cryptoWallets = Array.isArray(cryptoResponse?.data) ? cryptoResponse.data : [];
      fiatWallets = Array.isArray(fiatResponse?.data) ? fiatResponse.data : [];
      
    } catch (err) {
      console.error('Error fetching wallets:', err);
      error = 'Failed to load wallet data. Please try again later.';
      // Re-throw to ensure the error is caught by any parent error boundaries
      throw err;
    } finally {
      loading = false;
    }
  }

  function formatCurrency(amount: number, currency: string = 'USD'): string {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: 2,
      maximumFractionDigits: 8
    }).format(amount);
  }

  onMount(() => {
    fetchWallets();
  });
</script>

<div class="min-h-screen bg-gray-50 py-8">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-8 gap-4">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Wallets</h1>
        <p class="mt-1 text-sm text-gray-500">Manage your crypto and fiat wallets</p>
      </div>
      <div class="flex space-x-3">
        <Button variant="primary" on:click={() => activeTab = 'crypto'}>
          Add Crypto Wallet
        </Button>
        <Button variant="secondary" on:click={() => activeTab = 'fiat'}>
          Add Bank Account
        </Button>
      </div>
    </div>

    <!-- Tabs -->
    <div class="border-b border-gray-200 mb-8">
      <nav class="-mb-px flex space-x-8">
        <button
          class="py-4 px-1 border-b-2 font-medium text-sm"
          class:border-indigo-500={activeTab === 'crypto'}
          class:text-indigo-600={activeTab === 'crypto'}
          class:border-transparent={activeTab !== 'crypto'}
          class:text-gray-500={activeTab !== 'crypto'}
          class:hover:text-gray-700={activeTab !== 'crypto'}
          class:hover:border-gray-300={activeTab !== 'crypto'}
          on:click={() => (activeTab = 'crypto')}
        >
          Crypto Wallets
          {#if cryptoWallets.length > 0}
            <span class="ml-2 bg-gray-100 text-gray-600 text-xs font-medium px-2 py-0.5 rounded-full">
              {cryptoWallets.length}
            </span>
          {/if}
        </button>
        <button
          class="py-4 px-1 border-b-2 font-medium text-sm"
          class:border-indigo-500={activeTab === 'fiat'}
          class:text-indigo-600={activeTab === 'fiat'}
          class:border-transparent={activeTab !== 'fiat'}
          class:text-gray-500={activeTab !== 'fiat'}
          class:hover:text-gray-700={activeTab !== 'fiat'}
          class:hover:border-gray-300={activeTab !== 'fiat'}
          on:click={() => (activeTab = 'fiat')}
        >
          Bank Accounts
          {#if fiatWallets.length > 0}
            <span class="ml-2 bg-gray-100 text-gray-600 text-xs font-medium px-2 py-0.5 rounded-full">
              {fiatWallets.length}
            </span>
          {/if}
        </button>
      </nav>
    </div>

    <!-- Loading State -->
    {#if loading}
      <div class="bg-white shadow rounded-lg p-8 text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
        <p class="mt-4 text-gray-600">Loading wallets...</p>
      </div>

    <!-- Error State -->
    {:else if error}
      <div class="bg-red-50 border-l-4 border-red-400 p-4 mb-6">
        <div class="flex">
          <div class="flex-shrink-0">
            <svg class="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="ml-3">
            <p class="text-sm text-red-700">{error}</p>
          </div>
        </div>
      </div>

    <!-- Content -->
    {:else}
      {#if activeTab === 'crypto'}
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {#if cryptoWallets.length > 0}
            {#each cryptoWallets as wallet}
              <Card padding="lg" className="p-6">
                <div class="flex items-center justify-between mb-4">
                  <div class="flex items-center">
                    <div class="bg-indigo-100 p-2 rounded-lg">
                      <svg class="h-6 w-6 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </div>
                    <div class="ml-4">
                      <h3 class="text-lg font-medium text-gray-900">{wallet.currency}</h3>
                      <p class="text-sm text-gray-500">{wallet.address.slice(0, 6)}...{wallet.address.slice(-4)}</p>
                    </div>
                  </div>
                  {#if wallet.is_primary}
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      Primary
                    </span>
                  {/if}
                </div>
                <div class="mt-4">
                  <p class="text-2xl font-semibold text-gray-900">
                    {formatCurrency(wallet.balance, wallet.currency)}
                  </p>
                  <div class="mt-4 flex space-x-2">
                    <Button variant="outline" size="sm" on:click={() => {}}>Send</Button>
                    <Button variant="outline" size="sm" on:click={() => {}}>Receive</Button>
                  </div>
                </div>
              </Card>
            {/each}
          {:else}
            <div class="bg-white shadow rounded-lg p-8 text-center col-span-3">
              <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <h3 class="mt-2 text-sm font-medium text-gray-900">No crypto wallets</h3>
              <p class="mt-1 text-sm text-gray-500">Get started by adding a new crypto wallet.</p>
              <div class="mt-6">
                <Button variant="primary" on:click={() => {}}>
                  <svg class="-ml-1 mr-2 h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M10 5a1 1 0 011 1v3h3a1 1 0 110 2h-3v3a1 1 0 11-2 0v-3H6a1 1 0 110-2h3V6a1 1 0 011-1z" clip-rule="evenodd" />
                  </svg>
                  Add Crypto Wallet
                </Button>
              </div>
            </div>
          {/if}
        </div>

      {:else}
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {#if fiatWallets.length > 0}
            {#each fiatWallets as wallet}
              <Card padding="lg" className="p-6">
                <div class="flex items-center justify-between mb-4">
                  <div class="flex items-center">
                    <div class="bg-green-100 p-2 rounded-lg">
                      <svg class="h-6 w-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 6l3 1m0 0l-3 9a5.002 5.002 0 006.001 0M6 7l3 9M6 7l6-2m6 2l3-1m-3 1l-3 9a5.002 5.002 0 006.001 0M18 7l3 9m-3-9l-6-2m0-2v2m0 16V5m0 16H9m3 0h3" />
                      </svg>
                    </div>
                    <div class="ml-4">
                      <h3 class="text-lg font-medium text-gray-900">{wallet.bank_name}</h3>
                      <p class="text-sm text-gray-500">•••• {wallet.account_number.slice(-4)}</p>
                    </div>
                  </div>
                  {#if wallet.is_primary}
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      Primary
                    </span>
                  {/if}
                </div>
                <div class="mt-4">
                  <p class="text-2xl font-semibold text-gray-900">
                    {formatCurrency(wallet.balance, wallet.currency)}
                  </p>
                  <div class="mt-4">
                    <Button variant="outline" size="sm" on:click={() => {}}>Withdraw</Button>
                  </div>
                </div>
              </Card>
            {/each}
          {:else}
            <div class="bg-white shadow rounded-lg p-8 text-center col-span-3">
              <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M3 6l3 1m0 0l-3 9a5.002 5.002 0 006.001 0M6 7l3 9M6 7l6-2m6 2l3-1m-3 1l-3 9a5.002 5.002 0 006.001 0M18 7l3 9m-3-9l-6-2m0-2v2m0 16V5m0 16H9m3 0h3" />
              </svg>
              <h3 class="mt-2 text-sm font-medium text-gray-900">No bank accounts</h3>
              <p class="mt-1 text-sm text-gray-500">Get started by adding a new bank account.</p>
              <div class="mt-6">
                <Button variant="primary" on:click={() => {}}>
                  <svg class="-ml-1 mr-2 h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M10 5a1 1 0 011 1v3h3a1 1 0 110 2h-3v3a1 1 0 11-2 0v-3H6a1 1 0 110-2h3V6a1 1 0 011-1z" clip-rule="evenodd" />
                  </svg>
                  Add Bank Account
                </Button>
              </div>
            </div>
          {/if}
        </div>
      {/if}
    {/if}
  </div>
</div>

<style>
  /* Add any custom styles here */
</style>
