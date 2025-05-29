<script lang="ts">
  import { page } from '$app/stores';
  import { onMount } from 'svelte';
  import { fade } from 'svelte/transition';
  import { API_BASE_URL } from '$lib/api/config';
  
  let appVersion = '0.04.20';
  
  onMount(async () => {
    try {
      // In a real app, you might fetch this from your API
      // const response = await fetch(`${API_BASE_URL}/version`);
      // const data = await response.json();
      // appVersion = data.version;
    } catch (error) {
      console.error('Failed to fetch version:', error);
    }
  });
  
  const features = [
    {
      name: 'Easy GPU Management',
      description: 'Deploy and manage your GPU resources with just a few clicks and earn money. Find a GPU on the store to deploy and run your own genAI tasks.',
      icon: 'M9 17.25v1.007a3 3 0 01-.879 2.122L7.5 21h9l-.621-.621A3 3 0 0115 18.257V17.25m6-12V15a2.25 2.25 0 01-2.25 2.25H5.25A2.25 2.25 0 013 15V5.25m18 0A2.25 2.25 0 0018.75 3H5.25A2.25 2.25 0 003 5.25m18 0V12a2.25 2.25 0 01-2.25 2.25H5.25A2.25 2.25 0 013 12V5.25'
    },
    {
      name: 'AI-Powered Chat',
      description: 'Interact with various AI models through our intuitive chat interface. Let Orbyte find the inference GPU for you.',
      icon: 'M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.308-3.076C3.88 15.611 3 13.9 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z'
    },
    {
      name: 'Task Automation',
      description: 'Automate repetitive tasks and streamline your AI workflow.',
      icon: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2'
    },
    {
      name: 'Secure & Private',
      description: 'Your data is encrypted and stays under your control.',
      icon: 'M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z'
    }
  ];
  
  const team = [
    {
      name: 'Nikolaos Maroulis',
      role: 'AI Engineer',
      image: 'https://avatars.githubusercontent.com/u/19670139?v=4',
      description: 'Building the future of GPU resource management and AI interactions.'
    }
  ];
</script>

<div class="bg-white">
  <!-- Hero Section -->
  <div class="relative bg-white overflow-hidden">
    <div class="max-w-7xl mx-auto">
      <div class="relative z-10 pb-8 bg-white sm:pb-16 md:pb-20 lg:max-w-2xl lg:w-full lg:pb-28 xl:pb-32">
        <main class="mt-10 mx-auto max-w-7xl px-4 sm:mt-12 sm:px-6 lg:mt-16 lg:px-8 xl:mt-20">
          <div class="sm:text-center lg:text-left">
            <h1 class="text-4xl tracking-tight font-extrabold text-gray-900 sm:text-5xl md:text-6xl">
              <span class="block">About</span>
              <span class="block text-indigo-600">Orbyte</span>
            </h1>
            <p class="mt-3 text-base text-gray-500 sm:mt-5 sm:text-lg sm:max-w-xl sm:mx-auto md:mt-5 md:text-xl lg:mx-0">
              Orbyte is a <strong>decentralized platform</strong> that enables anyone to rent out their idle <strong>GPUs</strong> for <strong>generative AI workloads</strong> — and get rewarded in <strong>crypto</strong> or <strong>USD</strong>. Whether you have spare compute power or need it for inference tasks, Orbyte connects supply and demand in a secure, efficient, and open way.
            </p>  
            <p class="mt-3 text-base text-gray-500 sm:mt-5 sm:text-lg sm:max-w-xl sm:mx-auto md:mt-5 md:text-xl lg:mx-0">
              Our <strong>mission</strong> is to unlock the global GPU grid for AI innovation — powered by open-source code, smart contracts, and a peer-to-peer marketplace
            </p>
            <div class="mt-5 sm:mt-8 sm:flex sm:justify-center lg:justify-start">
              <div class="rounded-md shadow">
                <a href="/dashboard" class="w-full flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 md:py-4 md:text-lg md:px-10">
                  Get started
                </a>
              </div>
              <div class="mt-3 sm:mt-0 sm:ml-3">
                <a href="#features" class="w-full flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-indigo-700 bg-indigo-100 hover:bg-indigo-200 md:py-4 md:text-lg md:px-10">
                  Learn more
                </a>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
    <div class="lg:absolute lg:inset-y-0 lg:right-0 lg:w-1/2">
      <img class="h-56 w-full object-cover sm:h-72 md:h-96 lg:w-full lg:h-full" src="https://www.embl.org/news/wp-content/uploads/2020/10/BRAZMA_Machine_Learning_1000x600.jpg" alt="">
    </div>
  </div>

  <!-- Features Section -->
  <div id="features" class="py-12 bg-white">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="lg:text-center">
        <h2 class="text-base text-indigo-600 font-semibold tracking-wide uppercase">Features</h2>
        <p class="mt-2 text-3xl leading-8 font-extrabold tracking-tight text-gray-900 sm:text-4xl">
          A better way to manage GPU resources
        </p>
        <p class="mt-4 max-w-2xl text-xl text-gray-500 lg:mx-auto">
          Orbyte provides a seamless experience for deploying and managing GPU resources for AI and machine learning workloads.
        </p>
      </div>

      <div class="mt-10">
        <div class="space-y-10 md:space-y-0 md:grid md:grid-cols-2 md:gap-x-8 md:gap-y-10">
          {#each features as feature (feature.name)}
            <div class="relative" in:fade>
              <div class="absolute flex items-center justify-center h-12 w-12 rounded-md bg-indigo-500 text-white">
                <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d={feature.icon} />
                </svg>
              </div>
              <p class="ml-16 text-lg leading-6 font-medium text-gray-900">{feature.name}</p>
              <p class="mt-2 ml-16 text-base text-gray-500">{feature.description}</p>
            </div>
          {/each}
        </div>
      </div>
    </div>
  </div>

  <!-- Team Section -->
  <div class="bg-gray-50">
    <div class="max-w-7xl mx-auto py-12 px-4 text-center sm:px-6 lg:px-8 lg:py-24">
      <div class="space-y-12">
        <div class="space-y-5 sm:space-y-4 md:max-w-xl lg:max-w-3xl xl:max-w-none">
          <h2 class="text-3xl font-extrabold tracking-tight sm:text-4xl">Our Team</h2>
          <p class="text-xl text-gray-500">
            The talented people behind the scenes making Orbyte possible.
          </p>
        </div>
        <ul class="space-y-4 sm:grid sm:grid-cols-2 sm:gap-6 sm:space-y-0 lg:grid-cols-3 lg:gap-8">
          {#each team as person (person.name)}
            <li class="py-10 px-6 bg-white text-center rounded-lg xl:px-10 xl:text-left">
              <div class="space-y-6 xl:space-y-10">
                <img class="mx-auto h-40 w-40 rounded-full xl:w-56 xl:h-56" src={person.image} alt="">
                <div class="space-y-2 xl:flex xl:items-center xl:justify-between">
                  <div class="font-medium text-lg leading-6 space-y-1">
                    <h3>{person.name}</h3>
                    <p class="text-indigo-600">{person.role}</p>
                  </div>
                </div>
                <div class="relative">
                  <p class="text-gray-500">{person.description}</p>
                </div>
              </div>
            </li>
          {/each}
        </ul>
      </div>
    </div>
  </div>

  <!-- CTA Section -->
  <div class="bg-indigo-50">
    <div class="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:py-16 lg:px-8 lg:flex lg:items-center lg:justify-between">
      <h2 class="text-3xl font-extrabold tracking-tight text-gray-900 sm:text-4xl">
        <span class="block">Ready to dive in?</span>
        <span class="block text-indigo-600">Start using Orbyte today.</span>
      </h2>
      <div class="mt-8 flex lg:mt-0 lg:flex-shrink-0">
        <div class="inline-flex rounded-md shadow">
          <a href="/dashboard" class="inline-flex items-center justify-center px-5 py-3 border border-transparent text-base font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700">
            Get started
          </a>
        </div>
        <div class="ml-3 inline-flex rounded-md shadow">
          <a href="/chat" class="inline-flex items-center justify-center px-5 py-3 border border-transparent text-base font-medium rounded-md text-indigo-600 bg-white hover:bg-indigo-50">
            Try Orbyte Chat
          </a>
        </div>
      </div>
    </div>
  </div>
</div>

<footer class="bg-white">
  <div class="max-w-7xl mx-auto py-12 px-4 overflow-hidden sm:px-6 lg:px-8">
    <p class="mt-8 text-center text-base text-gray-400">
      &copy; {new Date().getFullYear()} Orbyte. All rights reserved. v{appVersion}
    </p>
  </div>
</footer>
