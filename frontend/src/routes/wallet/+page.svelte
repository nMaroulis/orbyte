<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { user } from '$lib/stores/auth';
  import { api } from '$lib/api/client';
  import { API_ENDPOINTS } from '$lib/api/config';
  import type { WalletsResponse, CryptoWallet, FiatWallet } from '$lib/types/wallet';
  import Card from '$lib/components/ui/Card.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import { toast } from 'svelte-sonner';
  
  // Animation for dropdowns
  const fadeIn = `
    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(-5px); }
      to { opacity: 1; transform: translateY(0); }
    }
    .animate-fade-in {
      animation: fadeIn 0.2s ease-out forwards;
    }
  `;
  
  // Initialize with some demo data
  onMount(() => {
    // Add a demo USD wallet if none exists
    if (fiatWallets.length === 0) {
      const demoWallet: FiatWallet = {
        id: 999, // Demo wallet ID
        bank_name: 'Demo Bank',
        account_number: '****1234',
        currency: 'USD',
        balance: 0,
        is_primary: true,
        iban: '',
        swift_bic: '',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };
      fiatWallets = [demoWallet];
    }
  });
  
  let loading = true;
  let activeTab: 'crypto' | 'fiat' = 'crypto';
  let cryptoWallets: CryptoWallet[] = [];
  let fiatWallets: FiatWallet[] = [];
  let error: string | null = null;
  let showCryptoConnect = false;
  let showFiatDeposit = false;
  let depositAmount = '';

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

  function toggleCryptoConnect() {
    showCryptoConnect = !showCryptoConnect;
  }

  function toggleFiatDeposit() {
    showFiatDeposit = !showFiatDeposit;
  }

  async function connectWallet(provider: string) {
    // Simulate wallet connection
    toast.loading(`Connecting to ${provider}...`);
    await new Promise(resolve => setTimeout(resolve, 1000));
    toast.dismiss();
    toast.success('Please complete the connection in your wallet app');
  }

  async function addDemoFunds() {
    const loadingToastId = toast.loading('Adding demo funds...');
    try {
      // Simulate API call to add demo funds
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Update local state
      const demoWallet = fiatWallets.find(w => w.currency === 'USD');
      if (demoWallet) {
        demoWallet.balance += 1000; // Add $1000 demo money
        fiatWallets = [...fiatWallets]; // Trigger Svelte reactivity
        toast.success('Added $1000 demo funds to your account', { id: loadingToastId });
      }
    } catch (error) {
      console.error('Error adding demo funds:', error);
      toast.error('Failed to add demo funds. Please try again.', { id: loadingToastId });
    }
  }

  async function processDeposit(method: string) {
    if (!depositAmount || isNaN(Number(depositAmount)) || Number(depositAmount) <= 0) {
      toast.error('Please enter a valid amount');
      return;
    }

    const loadingToastId = toast.loading(`Processing ${method} deposit...`);
    try {
      // Simulate API call for deposit
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Update local state
      const usdWallet = fiatWallets.find(w => w.currency === 'USD');
      if (usdWallet) {
        const amount = Number(depositAmount);
        usdWallet.balance += amount;
        fiatWallets = [...fiatWallets]; // Trigger Svelte reactivity
        depositAmount = '';
        showFiatDeposit = false;
        toast.success(`Successfully deposited $${amount.toFixed(2)} via ${method}`, { id: loadingToastId });
      }
    } catch (error) {
      console.error(`Error processing ${method} deposit:`, error);
      toast.error(`Failed to process ${method} deposit. Please try again.`, { id: loadingToastId });
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

<div class="min-h-screen bg-gray-50">
  <style>
    {fadeIn}
  </style>
  <div class="py-8">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-8 gap-4">
        <div>
          <h1 class="text-3xl font-bold text-gray-900">Wallets</h1>
          <p class="mt-1 text-sm text-gray-500">Manage your crypto and fiat wallets</p>
        </div>
        <div class="flex space-x-3">
          <Button variant="primary" on:click={() => activeTab = 'crypto'}>Add Crypto Wallet</Button>
          <Button variant="secondary" on:click={() => activeTab = 'fiat'}>Add Bank Account</Button>
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
            <div class="bg-white/80 backdrop-blur-sm shadow-xl rounded-2xl p-8 text-center col-span-3 border border-white/20">
              <div class="mx-auto h-16 w-16 rounded-full bg-indigo-50 flex items-center justify-center mb-3">
                <svg class="h-8 w-8 text-indigo-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 class="text-lg font-semibold text-gray-800">No Crypto Wallets</h3>
              <p class="mt-1.5 text-sm text-gray-500 max-w-md mx-auto">Connect your favorite wallet to start managing your crypto assets</p>
              <div class="mt-6 space-y-3">
                <button 
                  on:click={toggleCryptoConnect}
                  class="w-full group relative overflow-hidden py-3.5 px-6 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 text-white font-medium transition-all duration-300 transform hover:-translate-y-0.5 shadow-lg hover:shadow-xl"
                >
                  <div class="absolute inset-0 bg-gradient-to-r from-white/10 to-white/0 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                  <div class="relative z-10 flex items-center justify-center">
                    <svg class="h-5 w-5 mr-2.5 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <rect x="1" y="4" width="22" height="16" rx="2" ry="2"></rect>
                      <line x1="1" y1="10" x2="23" y2="10"></line>
                      <path d="M7 15h.01M12 15h.01"></path>
                    </svg>
                    <span class="font-medium tracking-wide">Connect Wallet</span>
                  </div>
                </button>
                
                {#if showCryptoConnect}
                  <div class="backdrop-blur-lg bg-white/80 p-6 rounded-2xl shadow-2xl border border-white/20 mt-4 space-y-4 animate-fade-in overflow-hidden relative">
                    <div class="absolute -top-10 -right-10 w-20 h-20 bg-indigo-400/10 rounded-full"></div>
                    <div class="absolute -bottom-8 -left-8 w-16 h-16 bg-purple-400/10 rounded-full"></div>
                    
                    <div class="relative z-10 text-center mb-5">
                      <h4 class="text-lg font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">Connect Your Wallet</h4>
                      <p class="text-sm text-gray-500 mt-1.5">Select your preferred wallet provider</p>
                    </div>
                    
                    <div class="relative z-10 grid grid-cols-1 gap-3.5">
                      <button 
                        on:click={() => connectWallet('MetaMask')}
                        class="group relative overflow-hidden w-full flex items-center p-3.5 pr-5 rounded-xl bg-white/90 hover:bg-white border border-gray-100 hover:border-indigo-100 transition-all duration-300 hover:shadow-lg hover:shadow-indigo-100/50"
                      >
                        <div class="absolute inset-0 bg-gradient-to-r from-white/0 to-white/50 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                        <div class="relative z-10 flex items-center w-full">
                          <div class="bg-orange-50 p-2.5 rounded-xl mr-4 transition-transform duration-300 group-hover:scale-110">
                            <img src="https://images.ctfassets.net/clixtyxoaeas/1ezuBGezqfIeifWdVtwU4c/d970d4cdf13b163efddddd5709164d2e/MetaMask-icon-Fox.svg" alt="MetaMask" class="h-6 w-6" />
                          </div>
                          <div class="text-left flex-1">
                            <span class="block font-semibold text-gray-800 group-hover:bg-gradient-to-r group-hover:from-indigo-600 group-hover:to-purple-600 group-hover:bg-clip-text group-hover:text-transparent transition-all duration-300">MetaMask</span>
                            <span class="text-xs text-gray-500 mt-0.5 flex items-center">
                              <span class="w-1.5 h-1.5 bg-emerald-400 rounded-full mr-1.5"></span>
                              Browser extension
                            </span>
                        </div>
                        <svg class="ml-auto h-5 w-5 text-gray-300 group-hover:text-indigo-500 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                        </svg>
                      </button>
                      
                      <button 
                        on:click={() => connectWallet('WalletConnect')}
                        class="group w-full flex items-center p-4 rounded-xl bg-white hover:bg-gray-50 border border-gray-200 transition-all duration-200 hover:border-blue-200 hover:shadow-md"
                      >
                        <div class="bg-blue-50 p-2 rounded-xl mr-4 group-hover:scale-105 transition-transform">
                          <img src="https://images.seeklogo.com/logo-png/43/1/walletconnect-logo-png_seeklogo-430923.png" alt="WalletConnect" class="h-7 w-7" />
                        </div>
                        <div class="text-left">
                          <span class="block font-medium text-gray-900 group-hover:text-blue-600">WalletConnect</span>
                          <span class="text-xs text-gray-500">Scan with WalletConnect</span>
                        </div>
                        <svg class="ml-auto h-5 w-5 text-gray-300 group-hover:text-blue-500 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                        </svg>
                      </button>
                      
                      <button 
                        on:click={() => connectWallet('Coinbase Wallet')}
                        class="group w-full flex items-center p-4 rounded-xl bg-white hover:bg-gray-50 border border-gray-200 transition-all duration-200 hover:border-blue-200 hover:shadow-md"
                      >
                        <div class="bg-blue-50 p-2 rounded-xl mr-4 group-hover:scale-105 transition-transform">
                          <img src="https://pbs.twimg.com/profile_images/1499783051974303748/sm3dkwbI_400x400.png" alt="Coinbase Wallet" class="h-7 w-7" />
                        </div>
                        <div class="text-left">
                          <span class="block font-medium text-gray-900 group-hover:text-blue-600">Coinbase Wallet</span>
                          <span class="text-xs text-gray-500">Connect with Coinbase</span>
                        </div>
                        <svg class="ml-auto h-5 w-5 text-gray-300 group-hover:text-blue-500 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                        </svg>
                      </button>
                    </div>
                    
                    <div class="pt-2 text-center">
                      <p class="text-xs text-gray-400">By connecting, I accept the <a href="/terms" class="text-indigo-500 hover:underline">Terms of Service</a></p>
                    </div>
                  </div>
                {/if}
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
              <div class="bg-white/80 backdrop-blur-sm shadow-xl rounded-2xl p-8 text-center col-span-3 border border-white/20">
                <div class="mx-auto h-16 w-16 rounded-full bg-green-50 flex items-center justify-center mb-3">
                  <svg class="h-8 w-8 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 6l3 1m0 0l-3 9a5.002 5.002 0 006.001 0M6 7l3 9M6 7l6-2m6 2l3-1m-3 1l-3 9a5.002 5.002 0 006.001 0M18 7l3 9m-3-9l-6-2m0-2v2m0 16V5m0 16H9m3 0h3" />
                  </svg>
                </div>
                <h3 class="text-lg font-semibold text-gray-800">No Bank Accounts</h3>
                <p class="mt-1.5 text-sm text-gray-500 max-w-md mx-auto">Add your bank account to start managing your fiat assets</p>
              <div class="mt-6 space-y-3">
                <button 
                  on:click={toggleFiatDeposit}
                  class="w-full group relative overflow-hidden py-3.5 px-6 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-600 hover:to-teal-700 text-white font-medium transition-all duration-300 transform hover:-translate-y-0.5 shadow-lg hover:shadow-xl"
                >
                  <div class="absolute inset-0 bg-gradient-to-r from-white/10 to-white/0 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                  <div class="relative z-10 flex items-center justify-center">
                    <svg class="h-5 w-5 mr-2.5 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <line x1="12" y1="5" x2="12" y2="19"></line>
                      <line x1="5" y1="12" x2="19" y2="12"></line>
                    </svg>
                    <span class="font-medium tracking-wide">Add Money</span>
                  </div>
                </button>
                
                <button 
                  on:click={addDemoFunds}
                  class="w-full group relative overflow-hidden py-2.5 px-6 rounded-xl border-2 border-dashed border-indigo-200 hover:border-indigo-300 bg-white/80 hover:bg-white text-indigo-700 font-medium transition-all duration-300"
                >
                  <div class="absolute inset-0 bg-gradient-to-r from-indigo-50/0 to-indigo-50/0 group-hover:from-indigo-50/50 group-hover:to-indigo-100/30 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                  <div class="relative z-10 flex items-center justify-center">
                    <svg class="h-5 w-5 mr-2.5 text-indigo-500 group-hover:scale-110 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span class="font-medium tracking-wide bg-gradient-to-r from-indigo-600 to-purple-600 group-hover:from-indigo-700 group-hover:to-purple-700 bg-clip-text text-transparent">Add Demo Funds ($1000)</span>
                  </div>
                </button>
                
                {#if showFiatDeposit}
                  <div class="bg-white p-5 rounded-xl shadow-lg border border-gray-200 mt-3 space-y-4 animate-fade-in">
                    <h4 class="text-sm font-medium text-gray-500 mb-1">Add funds to your account</h4>
                    <div>
                      <label for="deposit-amount" class="block text-sm font-medium text-gray-700 mb-1">Amount (USD)</label>
                      <div class="relative rounded-md shadow-sm">
                        <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                          <span class="text-gray-500 sm:text-sm">$</span>
                        </div>
                        <input
                          type="number"
                          id="deposit-amount"
                          bind:value={depositAmount}
                          placeholder="0.00"
                          class="focus:ring-indigo-500 focus:border-indigo-500 block w-full pl-7 pr-12 py-3 sm:text-sm border-gray-300 rounded-lg"
                          min="1"
                          step="0.01"
                        />
                        <div class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                          <span class="text-gray-500 sm:text-sm">USD</span>
                        </div>
                      </div>
                    </div>
                    
                    <button 
                      on:click={() => processDeposit('Credit/Debit Card')}
                      class="w-full flex items-center justify-between p-3.5 rounded-xl hover:bg-gray-50 border border-gray-200 transition-all duration-200 hover:border-indigo-300 hover:shadow-sm"
                    >
                      <div class="flex items-center">
                        <svg class="h-6 w-6 text-gray-500 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
                        </svg>
                        <span>Credit/Debit Card</span>
                      </div>
                      <svg class="h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
                      </svg>
                    </button>
                    
                    <button 
                      on:click={() => processDeposit('Apple Pay')}
                      class="w-full flex items-center justify-between p-3.5 rounded-xl hover:bg-gray-50 border border-gray-200 transition-all duration-200 hover:border-indigo-300 hover:shadow-sm"
                    >
                      <div class="flex items-center">
                        <svg class="h-6 w-6 text-black mr-3" viewBox="0 0 24 24" fill="currentColor">
                          <path d="M22.5 18.5c0-1.1-.9-2-2-2h-6.5c-1.1 0-2 .9-2 2s.9 2 2 2h6.5c1.1 0 2-.9 2-2z"/>
                          <path d="M22.5 12c0-1.1-.9-2-2-2h-6.5c-1.1 0-2 .9-2 2s.9 2 2 2h6.5c1.1 0 2-.9 2-2z"/>
                          <path d="M22.5 5.5c0-1.1-.9-2-2-2h-6.5c-1.1 0-2 .9-2 2s.9 2 2 2h6.5c1.1 0 2-.9 2-2z"/>
                          <path d="M9.5 18.5c0-1.1-.9-2-2-2h-6c-1.1 0-2 .9-2 2s.9 2 2 2h6c1.1 0 2-.9 2-2z"/>
                          <path d="M9.5 12c0-1.1-.9-2-2-2h-6c-1.1 0-2 .9-2 2s.9 2 2 2h6c1.1 0 2-.9 2-2z"/>
                          <path d="M9.5 5.5c0-1.1-.9-2-2-2h-6c-1.1 0-2 .9-2 2s.9 2 2 2h6c1.1 0 2-.9 2-2z"/>
                        </svg>
                        <span>Apple Pay</span>
                      </div>
                      <svg class="h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
                      </svg>
                    </button>
                    
                    <button 
                      on:click={() => processDeposit('Bank Transfer')}
                      class="w-full flex items-center justify-between p-3.5 rounded-xl hover:bg-gray-50 border border-gray-200 transition-all duration-200 hover:border-indigo-300 hover:shadow-sm"
                    >
                      <div class="flex items-center">
                        <svg class="h-6 w-6 text-blue-600 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 6l3 1m0 0l-3 9a5.002 5.002 0 006.001 0M6 7l3 9M6 7l6-2m6 2l3-1m-3 1l-3 9a5.002 5.002 0 006.001 0M18 7l3 9m-3-9l-6-2m0-2v2m0 16V5m0 16H9m3 0h3" />
                        </svg>
                        <span>Bank Transfer</span>
                      </div>
                      <svg class="h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
                      </svg>
                    </button>
                  </div>
                {/if}
              </div>
            </div>
          {/if}
          </div>
        {/if}
      {/if}
      </div>
    </div>
  </div>

<style>
  /* Add any custom styles here */
</style>
