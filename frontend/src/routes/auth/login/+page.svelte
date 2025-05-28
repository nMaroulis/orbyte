<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { AuthService } from '$lib/services/auth.service';
  import { user } from '$lib/stores/auth';
  import Button from '$lib/components/ui/Button.svelte';
  import Card from '$lib/components/ui/Card.svelte';
  
  let email = '';
  let password = '';
  let loading = false;
  let error: string | null = null;
  
  // Demo account credentials
  const DEMO_ACCOUNT = {
    email: 'demo@orbyte.com',
    password: 'demopassword123'  // This must match the password in the database
  };
  
  // Function to login with demo account
  async function loginWithDemo() {
    try {
      loading = true;
      error = null;
      
      // Use AuthService to handle the login
      await AuthService.login({
        email: DEMO_ACCOUNT.email,
        password: DEMO_ACCOUNT.password
      });
      
      // Redirect to dashboard
      goto('/dashboard');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to login with demo account';
      error = errorMessage;
      console.error('Demo login error:', errorMessage);
    } finally {
      loading = false;
    }
  }
  
  onMount(() => {
    // Redirect to dashboard if already logged in
    const unsubscribe = user.subscribe(($user) => {
      if ($user) {
        goto('/dashboard');
      }
    });
    
    return () => unsubscribe();
  });
  
  async function handleSubmit() {
    if (!email || !password) {
      error = 'Please fill in all fields';
      return;
    }
    
    try {
      loading = true;
      error = null;
      
      // Use AuthService to handle the login
      await AuthService.login({
        email,
        password
      });
      
      // Redirect to dashboard
      goto('/dashboard');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to login. Please check your credentials.';
      error = errorMessage;
      console.error('Login error:', errorMessage);
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

<div class="min-h-screen flex">
  <!-- Left side with gradient background -->
  <div class="hidden lg:flex flex-col justify-between flex-1 bg-gradient-to-br from-indigo-600 to-purple-600 p-12 text-white">
    <div>
      <h1 class="text-3xl font-bold">Orbyte</h1>
      <p class="mt-2 text-indigo-100">GPU Computing Platform</p>
    </div>
    <div class="max-w-md">
      <h2 class="text-4xl font-bold mb-4">Welcome back!</h2>
      <p class="text-indigo-100 text-lg">Sign in to access your dashboard, manage your GPU resources, and track your tasks.</p>
    </div>
    <div class="flex space-x-4">
      <div class="w-12 h-1 bg-white/30 rounded-full"></div>
      <div class="w-12 h-1 bg-white rounded-full"></div>
      <div class="w-12 h-1 bg-white/30 rounded-full"></div>
    </div>
  </div>
  
  <!-- Right side with login form -->
  <div class="flex-1 flex flex-col justify-center py-12 px-4 sm:px-6 lg:flex-none lg:px-20 xl:px-24">
    <div class="mx-auto w-full max-w-md lg:w-96">
      <div class="lg:hidden mb-8 text-center">
        <h1 class="text-3xl font-bold text-gray-900">Orbyte</h1>
        <p class="mt-2 text-gray-600">GPU Computing Platform</p>
      </div>
      <div class="bg-white rounded-2xl shadow-xl p-8">
        <h2 class="text-2xl font-bold text-gray-900 mb-6">Sign in to your account</h2>


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
      
      <div class="space-y-4">
        <Button 
          type="button" 
          on:click={loginWithDemo}
          class="w-full flex items-center justify-center gap-3 py-3 px-6 rounded-xl text-white font-semibold shadow-lg hover:shadow-xl transition-all duration-200 transform hover:-translate-y-0.5"
          style="background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);"
          disabled={loading}
        >
          <div class="flex items-center justify-center w-6 h-6 bg-white/20 rounded-full">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clip-rule="evenodd" />
            </svg>
          </div>
          {loading ? 'Logging in...' : 'Try Demo Account'}
        </Button>
      </div>
      
      <div class="relative my-6">
        <div class="absolute inset-0 flex items-center">
          <div class="w-full border-t border-gray-200"></div>
        </div>
        <div class="relative flex justify-center text-sm">
          <span class="px-3 bg-white text-gray-500 font-medium">Or continue with email</span>
        </div>
      </div>
      
      <form class="space-y-5" on:submit|preventDefault={handleSubmit}>
        <div class="space-y-1">
          <label for="email" class="block text-sm font-medium text-gray-700">
            Email address
          </label>
          <div class="mt-1">
            <div class="relative">
              <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <svg class="h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                  <path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z" />
                  <path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z" />
                </svg>
              </div>
              <input
                id="email"
                name="email"
                type="email"
                autocomplete="email"
                required
                bind:value={email}
                on:keydown={handleKeyDown}
                class="appearance-none block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-xl shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                placeholder="you@example.com"
              />
            </div>
          </div>
        </div>

        <div class="space-y-1">
          <div class="flex items-center justify-between">
            <label for="password" class="block text-sm font-medium text-gray-700">
              Password
            </label>
            <div class="text-sm">
              <a href="/auth/forgot-password" class="font-medium text-indigo-600 hover:text-indigo-500">
                Forgot password?
              </a>
            </div>
          </div>
          <div class="mt-1">
            <div class="relative">
              <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <svg class="h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                  <path fill-rule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clip-rule="evenodd" />
                </svg>
              </div>
              <input
                id="password"
                name="password"
                type="password"
                autocomplete="current-password"
                required
                bind:value={password}
                on:keydown={handleKeyDown}
                class="appearance-none block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-xl shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                placeholder="••••••••"
              />
            </div>
          </div>
        </div>

        <div class="flex items-center">
          <input
            id="remember-me"
            name="remember-me"
            type="checkbox"
            class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
          />
          <label for="remember-me" class="ml-2 block text-sm text-gray-700">
            Remember me
          </label>
        </div>

        <div>
          <Button 
            type="submit" 
            class="w-full flex justify-center py-2 px-4"
            disabled={loading}
          >
            {#if loading}
              Signing in...
            {:else}
              Sign in
            {/if}
          </Button>
        </div>
      </form>
      
      <div class="mt-6">
        <div class="relative">
          <div class="absolute inset-0 flex items-center">
            <div class="w-full border-t border-gray-200"></div>
          </div>
          <div class="relative flex justify-center text-sm">
            <span class="px-2 bg-white text-gray-500">Don't have an account?</span>
          </div>
        </div>
        
        <div class="mt-6">
          <a href="/register" class="w-full flex justify-center py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
            Create new account
          </a>
        </div>
      </div>
    </div>
  </div>
</div>
</div>
