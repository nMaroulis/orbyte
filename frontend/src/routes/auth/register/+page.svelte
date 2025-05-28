<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { AuthService } from '$lib/services/auth.service';
  import { user } from '$lib/stores/auth';
  import Button from '$lib/components/ui/Button.svelte';
  import Card from '$lib/components/ui/Card.svelte';
  
  let email = '';
  let password = '';
  let confirmPassword = '';
  let walletAddress = '';
  let loading = false;
  let error: string | null = null;
  
  onMount(() => {
    // Redirect to dashboard if already logged in
    const unsubscribe = user.subscribe(($user) => {
      if ($user) {
        goto('/dashboard');
      }
    });
    
    return () => unsubscribe();
  });
  
  function validateForm(): boolean {
    if (!email || !password || !confirmPassword || !walletAddress) {
      error = 'All fields are required';
      return false;
    }
    
    if (password !== confirmPassword) {
      error = 'Passwords do not match';
      return false;
    }
    
    if (password.length < 8) {
      error = 'Password must be at least 8 characters long';
      return false;
    }
    
    // Basic email validation
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      error = 'Please enter a valid email address';
      return false;
    }
    
    // Basic wallet address validation (starts with 0x and has 42 chars)
    if (!/^0x[a-fA-F0-9]{40}$/.test(walletAddress)) {
      error = 'Please enter a valid Ethereum wallet address';
      return false;
    }
    
    return true;
  }
  
  async function handleSubmit() {
    if (!validateForm()) return;
    
    try {
      loading = true;
      error = null;
      
      await AuthService.register({
        email,
        password,
        wallet_address: walletAddress,
      });
      
      // AuthService.register will handle login and redirection
    } catch (err: any) {
      console.error('Registration failed:', err);
      error = err.response?.data?.detail || 'Registration failed. Please try again.';
    } finally {
      loading = false;
    }
  }
  
  function handleKeyDown(event: KeyboardEvent) {
    if (event.key === 'Enter') {
      handleSubmit();
    }
  }
</script>

<div class="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
  <div class="sm:mx-auto sm:w-full sm:max-w-md">
    <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
      Create a new account
    </h2>
    <p class="mt-2 text-center text-sm text-gray-600">
      Or{' '}
      <a href="/login" class="font-medium text-blue-600 hover:text-blue-500">
        sign in to your existing account
      </a>
    </p>
  </div>

  <div class="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
    <Card class="py-8 px-4 sm:px-10">
      {#if error}
        <div class="mb-4 bg-red-50 border-l-4 border-red-400 p-4">
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
      {/if}
      
      <form class="space-y-6" on:submit|preventDefault={handleSubmit}>
        <div>
          <label for="email" class="block text-sm font-medium text-gray-700">
            Email address
          </label>
          <div class="mt-1">
            <input
              id="email"
              name="email"
              type="email"
              autocomplete="email"
              required
              bind:value={email}
              on:keydown={handleKeyDown}
              class="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            />
          </div>
        </div>

        <div>
          <label for="wallet-address" class="block text-sm font-medium text-gray-700">
            Ethereum Wallet Address
          </label>
          <div class="mt-1">
            <input
              id="wallet-address"
              name="wallet-address"
              type="text"
              placeholder="0x..."
              required
              bind:value={walletAddress}
              on:keydown={handleKeyDown}
              class="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm font-mono"
            />
          </div>
          <p class="mt-1 text-xs text-gray-500">
            This address will receive payments for your GPU rentals
          </p>
        </div>

        <div>
          <label for="password" class="block text-sm font-medium text-gray-700">
            Password
          </label>
          <div class="mt-1">
            <input
              id="password"
              name="password"
              type="password"
              autocomplete="new-password"
              required
              bind:value={password}
              on:keydown={handleKeyDown}
              class="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            />
          </div>
          <p class="mt-1 text-xs text-gray-500">
            Must be at least 8 characters long
          </p>
        </div>

        <div>
          <label for="confirm-password" class="block text-sm font-medium text-gray-700">
            Confirm Password
          </label>
          <div class="mt-1">
            <input
              id="confirm-password"
              name="confirm-password"
              type="password"
              autocomplete="new-password"
              required
              bind:value={confirmPassword}
              on:keydown={handleKeyDown}
              class="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            />
          </div>
        </div>

        <div class="flex items-center">
          <input
            id="terms"
            name="terms"
            type="checkbox"
            required
            class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
          />
          <label for="terms" class="ml-2 block text-sm text-gray-700">
            I agree to the{' '}
            <a href="/terms" class="text-blue-600 hover:text-blue-500">Terms of Service</a> and{' '}
            <a href="/privacy" class="text-blue-600 hover:text-blue-500">Privacy Policy</a>
          </label>
        </div>

        <div>
          <Button 
            type="submit" 
            class="w-full flex justify-center py-2 px-4"
            disabled={loading}
          >
            {#if loading}
              Creating account...
            {:else}
              Create account
            {/if}
          </Button>
        </div>
      </form>
    </Card>
  </div>
</div>
