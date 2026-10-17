/**
 * Menu API Service
 * Handles menu items and categories API calls
 */

import { apiClient } from '@/lib/api-client';
import { MenuItem } from '@/types/api';

export class MenuApiService {
  private readonly basePath = '/api/menu';

  /**
   * Get all menu items
   */
  async getMenuItems(): Promise<MenuItem[]> {
    try {
      // Try to get from backend first
      const response = await apiClient.get<{ items: MenuItem[] }>(`${this.basePath}/items`);
      return response.items;
    } catch (error) {
      // Fallback to mock data if backend is not available
      console.warn('Backend not available, using mock menu data');
      return this.getMockMenuItems();
    }
  }

  /**
   * Get menu items by category
   */
  async getMenuItemsByCategory(category: string): Promise<MenuItem[]> {
    try {
      const response = await apiClient.get<{ items: MenuItem[] }>(`${this.basePath}/items?category=${category}`);
      return response.items;
    } catch (error) {
      const allItems = await this.getMenuItems();
      return allItems.filter(item => item.category === category);
    }
  }

  /**
   * Get menu categories
   */
  async getCategories(): Promise<Array<{ id: string; name: string }>> {
    try {
      const response = await apiClient.get<{ categories: Array<{ id: string; name: string }> }>(`${this.basePath}/categories`);
      return response.categories;
    } catch (error) {
      // Fallback to mock categories
      return this.getMockCategories();
    }
  }

  /**
   * Get specific menu item
   */
  async getMenuItem(itemId: string): Promise<MenuItem | null> {
    try {
      const response = await apiClient.get<{ item: MenuItem }>(`${this.basePath}/items/${itemId}`);
      return response.item;
    } catch (error) {
      const allItems = await this.getMenuItems();
      return allItems.find(item => item.item_id === itemId) || null;
    }
  }

  /**
   * Mock menu items (fallback when backend is not available)
   */
  private getMockMenuItems(): MenuItem[] {
    return [
      {
        item_id: "ITM_001",
        name: "Burger Deluxe",
        kitchen_id: "KITCHEN_001",
        prep_time: 15,
        difficulty: "medium" as any,
        description: "Juicy beef patty with fresh vegetables and special sauce",
        price: 12.99,
        image: "/lovable-uploads/22d31f51-c174-40a7-bd95-00e4ad00eaf3.png",
        calories: 650,
        category: "burgers"
      },
      {
        item_id: "ITM_002",
        name: "French Fries",
        kitchen_id: "KITCHEN_001",
        prep_time: 8,
        difficulty: "easy" as any,
        description: "Crispy golden fries with sea salt",
        price: 4.99,
        image: "/lovable-uploads/5663820f-6c97-4492-9210-9eaa1a8dc415.png",
        calories: 350,
        category: "sides"
      },
      {
        item_id: "ITM_003",
        name: "Pizza Margherita",
        kitchen_id: "KITCHEN_002",
        prep_time: 20,
        difficulty: "medium" as any,
        description: "Classic pizza with tomato sauce, mozzarella, and fresh basil",
        price: 14.99,
        image: "/lovable-uploads/af412c03-21e4-4856-82ff-d1a975dc84a9.png",
        calories: 800,
        category: "pizza"
      },
      {
        item_id: "ITM_004",
        name: "Caesar Salad",
        kitchen_id: "KITCHEN_003",
        prep_time: 10,
        difficulty: "easy" as any,
        description: "Fresh romaine lettuce with Caesar dressing and croutons",
        price: 9.99,
        image: "/lovable-uploads/c3d5522b-6886-4b75-8ffc-d020016bb9c2.png",
        calories: 320,
        category: "salads"
      },
      {
        item_id: "ITM_005",
        name: "Grilled Chicken",
        kitchen_id: "KITCHEN_001",
        prep_time: 18,
        difficulty: "medium" as any,
        description: "Perfectly grilled chicken breast with herbs",
        price: 16.99,
        image: "/placeholder.svg",
        calories: 450,
        category: "mains"
      },
      {
        item_id: "ITM_006",
        name: "Chocolate Cake",
        kitchen_id: "KITCHEN_004",
        prep_time: 5,
        difficulty: "easy" as any,
        description: "Rich chocolate cake with chocolate frosting",
        price: 6.99,
        image: "/placeholder.svg",
        calories: 520,
        category: "desserts"
      }
    ];
  }

  /**
   * Mock categories (fallback when backend is not available)
   */
  private getMockCategories(): Array<{ id: string; name: string }> {
    return [
      { id: "all", name: "All Items" },
      { id: "burgers", name: "Burgers" },
      { id: "pizza", name: "Pizza" },
      { id: "salads", name: "Salads" },
      { id: "mains", name: "Main Courses" },
      { id: "sides", name: "Sides" },
      { id: "desserts", name: "Desserts" },
      { id: "beverages", name: "Beverages" }
    ];
  }

  /**
   * Search menu items
   */
  async searchMenuItems(query: string): Promise<MenuItem[]> {
    const allItems = await this.getMenuItems();
    return allItems.filter(item => 
      item.name.toLowerCase().includes(query.toLowerCase()) ||
      item.description?.toLowerCase().includes(query.toLowerCase())
    );
  }

  /**
   * Get featured menu items
   */
  async getFeaturedItems(): Promise<MenuItem[]> {
    const allItems = await this.getMenuItems();
    // Return first 6 items as featured (in real implementation, this would be marked in backend)
    return allItems.slice(0, 6);
  }
}

// Export singleton instance
export const menuApi = new MenuApiService();
