<script lang="ts">
  import { twMerge } from 'tailwind-merge';
  
  export let className: string = '';
  export let padding: 'none' | 'sm' | 'md' | 'lg' = 'md';
  export let hover = false;
  
  const paddingClasses = {
    none: '',
    sm: 'p-3',
    md: 'p-4',
    lg: 'p-6',
  };
  
  $: cardClasses = twMerge(
    'bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden',
    hover ? 'hover:shadow-md transition-shadow duration-200' : '',
    paddingClasses[padding],
    className
  );
</script>

<div class={cardClasses}>
  <slot />
</div>
