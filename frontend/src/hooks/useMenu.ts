/**
 * React hooks for Menu API
 * Provides React Query integration for menu management
 */

import { useQuery } from '@tanstack/react-query';
import { menuApi } from '@/services/menu-api';

// Query keys
export const menuKeys = {
  all: ['menu'] as const,
  items: () => [...menuKeys.all, 'items'] as const,
  item: (id: string) => [...menuKeys.items(), id] as const,
  categories: () => [...menuKeys.all, 'categories'] as const,
  category: (category: string) => [...menuKeys.items(), 'category', category] as const,
  search: (query: string) => [...menuKeys.items(), 'search', query] as const,
  featured: () => [...menuKeys.items(), 'featured'] as const,
};

/**
 * Hook to fetch all menu items
 */
export const useMenuItems = () => {
  return useQuery({
    queryKey: menuKeys.items(),
    queryFn: () => menuApi.getMenuItems(),
    staleTime: 300000, // 5 minutes
    refetchInterval: 600000, // Refetch every 10 minutes
  });
};

/**
 * Hook to fetch menu items by category
 */
export const useMenuItemsByCategory = (category: string) => {
  return useQuery({
    queryKey: menuKeys.category(category),
    queryFn: () => menuApi.getMenuItemsByCategory(category),
    enabled: !!category && category !== 'all',
    staleTime: 300000,
  });
};

/**
 * Hook to fetch menu categories
 */
export const useMenuCategories = () => {
  return useQuery({
    queryKey: menuKeys.categories(),
    queryFn: () => menuApi.getCategories(),
    staleTime: 600000, // 10 minutes
  });
};

/**
 * Hook to fetch a specific menu item
 */
export const useMenuItem = (itemId: string) => {
  return useQuery({
    queryKey: menuKeys.item(itemId),
    queryFn: () => menuApi.getMenuItem(itemId),
    enabled: !!itemId,
    staleTime: 300000,
  });
};

/**
 * Hook to search menu items
 */
export const useMenuSearch = (query: string) => {
  return useQuery({
    queryKey: menuKeys.search(query),
    queryFn: () => menuApi.searchMenuItems(query),
    enabled: !!query && query.length > 2,
    staleTime: 60000, // 1 minute
  });
};

/**
 * Hook to fetch featured menu items
 */
export const useFeaturedItems = () => {
  return useQuery({
    queryKey: menuKeys.featured(),
    queryFn: () => menuApi.getFeaturedItems(),
    staleTime: 300000,
  });
};

/**
 * Hook to get filtered menu items (combines category and search)
 */
export const useFilteredMenuItems = (category: string, searchTerm: string) => {
  const allItems = useMenuItems();
  const categoryItems = useMenuItemsByCategory(category);
  const searchResults = useMenuSearch(searchTerm);

  // Determine which data to use
  let data = allItems.data || [];
  let isLoading = allItems.isLoading;
  let isError = allItems.isError;

  if (searchTerm && searchTerm.length > 2) {
    data = searchResults.data || [];
    isLoading = searchResults.isLoading;
    isError = searchResults.isError;
  } else if (category && category !== 'all') {
    data = categoryItems.data || [];
    isLoading = categoryItems.isLoading;
    isError = categoryItems.isError;
  }

  // Apply additional client-side filtering if needed
  if (searchTerm && searchTerm.length <= 2 && searchTerm.length > 0) {
    data = data.filter(item => 
      item.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.description?.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }

  return {
    data,
    isLoading,
    isError,
    refetch: () => {
      allItems.refetch();
      if (category && category !== 'all') categoryItems.refetch();
      if (searchTerm && searchTerm.length > 2) searchResults.refetch();
    }
  };
};
