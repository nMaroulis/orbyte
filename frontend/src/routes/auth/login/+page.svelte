<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { AuthService } from '$lib/services/auth.service';
  import { user } from '$lib/stores/auth';
  import Button from '$lib/components/ui/Button.svelte';
  import Card from '$lib/components/ui/Card.svelte';
  import Carousel from '$lib/components/ui/Carousel.svelte';
  
  // Carousel slides data
  const carouselSlides = [
    {
      image: '/login_img1.png',
      title: 'Powerful GPU Resources',
      description: 'Access high-performance GPUs for your machine learning and AI workloads.'
    },
    {
      image: '/login_img3.png',
      title: 'Cost-Effective',
      description: 'Pay only for what you use with our flexible pricing model in both crypto and fiat currencies.'
    }
  ];
  
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
    } catch (err: unknown) {
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
    } catch (err: unknown) {
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

<div class="min-h-screen relative bg-gray-50 overflow-hidden flex">
  <!-- Carousel background (65% width) -->
  <div class="w-[65%] relative z-0 hidden lg:block">
    <Carousel slides={carouselSlides} interval={6000} />
    
    <!-- Logo overlay -->
    <div class="absolute top-0 left-0 p-8 z-10">
      <div class="relative">
        <!-- Glow effect -->
        <div class="absolute -inset-4 bg-gradient-to-r from-amber-400 to-yellow-500 rounded-full blur-2xl opacity-30"></div>
        
        <!-- Main container -->
        <div class="relative">
          <h1 class="text-5xl font-black text-amber-300 drop-shadow-lg">
            <span class="relative">
              <span class="relative z-10">Orbyte</span>
              <span class="absolute inset-0 text-transparent bg-clip-text bg-gradient-to-r from-amber-200 to-yellow-400 opacity-70 blur-md">Orbyte</span>
            </span>
          </h1>
          <div class="flex items-center mt-3 space-x-3">
            <div class="h-0.5 w-8 bg-gradient-to-r from-amber-300 to-yellow-400"></div>
            <p class="text-sm font-semibold text-amber-100 tracking-wider">DATA IN MOTION</p>
            <div class="h-0.5 w-8 bg-gradient-to-r from-yellow-400 to-amber-300"></div>
          </div>
        </div>
      </div>
    </div>
  </div>
  
  <!-- Login form container (35% width) -->
  <div class="w-full lg:w-[35%] flex items-center justify-center p-4 sm:p-6 lg:p-8">
    <div class="w-full max-w-md">
      <div class="lg:hidden mb-8 text-center">
        <h1 class="text-3xl font-bold text-white drop-shadow-lg">Orbyte</h1>
        <p class="mt-2 text-indigo-100 font-medium">GPU Computing Platform</p>
      </div>
      <form 
        class="backdrop-blur-sm bg-white/90 rounded-2xl shadow-2xl p-8 space-y-5 border border-white/20 hover:border-white/30 transition-all duration-300 hover:shadow-indigo-500/20 hover:shadow-lg" 
        on:submit|preventDefault={handleSubmit}
      >
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

        <div class="space-y-5">
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
        </div>

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
      </form>
    </div>
  </div>
</div>
