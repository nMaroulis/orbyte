import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params }) => {
  try {
    const { id } = params;
    
    // Validate that ID exists and is a number
    if (!id || isNaN(Number(id))) {
      throw error(404, 'GPU not found');
    }
    
    return {
      params: {
        id: id.toString()
      }
    };
  } catch (err) {
    console.error('Error loading GPU details:', err);
    throw error(500, 'Failed to load GPU details');
  }
};
