<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  
  export let slides: Array<{ image: string; title: string; description: string }> = [];
  export let interval: number = 5000; // 5 seconds
  
  let currentSlide = 0;
  let timer: number;
  $: slideTransform = `translateX(-${currentSlide * 100}%)`;

  function nextSlide() {
    currentSlide = (currentSlide + 1) % slides.length;
  }
  
  function prevSlide() {
    currentSlide = (currentSlide - 1 + slides.length) % slides.length;
  }
  
  function goToSlide(index: number) {
    currentSlide = index;
    resetTimer();
  }
  
  function startTimer() {
    timer = window.setInterval(nextSlide, interval);
  }
  
  function resetTimer() {
    clearInterval(timer);
    startTimer();
  }
  
  onMount(() => {
    startTimer();
    return () => clearInterval(timer);
  });
  
  onDestroy(() => {
    clearInterval(timer);
  });
</script>

<div class="relative h-full w-full overflow-hidden">
  <!-- Slides -->
  <div 
    class="flex h-full w-full transition-transform duration-500 ease-in-out"
    style="transform: {slideTransform};"
  >
    {#each slides as slide, i}
      <div class="flex-shrink-0 w-full h-full relative">
        <!-- Background Image with Overlay -->
        <div 
          class="absolute inset-0 bg-cover bg-center" 
          style="background-image: url('{slide.image}');"
        >
          <div class="absolute inset-0 bg-black/30"></div>
        </div>
        
        <!-- Content -->
        <div class="relative h-full flex flex-col justify-center p-12 text-white">
          <div class="max-w-md">
            <h2 class="text-4xl font-bold mb-4">{slide.title}</h2>
            <p class="text-lg text-gray-100">{slide.description}</p>
          </div>
        </div>
      </div>
    {/each}
  </div>
  
  <!-- Navigation Dots -->
  <div class="absolute bottom-8 left-0 right-0 flex justify-center space-x-2">
    {#each slides as _, i}
      <button
        class={`w-3 h-3 rounded-full transition-colors ${i === currentSlide ? 'bg-white' : 'bg-white/30'}`}
        on:click={() => goToSlide(i)}
        aria-label={`Go to slide ${i + 1}`}
      ></button>
    {/each}
  </div>
  
  <!-- Navigation Arrows -->
  <button
    class="absolute left-4 top-1/2 -translate-y-1/2 bg-white/20 hover:bg-white/30 text-white p-2 rounded-full transition-colors"
    on:click|stopPropagation={prevSlide}
    aria-label="Previous slide"
  >
    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
    </svg>
  </button>
  
  <button
    class="absolute right-4 top-1/2 -translate-y-1/2 bg-white/20 hover:bg-white/30 text-white p-2 rounded-full transition-colors"
    on:click|stopPropagation={nextSlide}
    aria-label="Next slide"
  >
    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
    </svg>
  </button>
</div>
