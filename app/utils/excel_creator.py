"""
Utility to create sample Excel configuration file for the kitchen system.
"""

import pandas as pd
from datetime import datetime, timedelta
import os


def create_sample_excel(file_path: str):
    """Create a sample Excel file with all required sheets and data."""
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        
        # Sheet 1: kitchens (synced with frontend data)
        kitchens_data = {
            'kitchen_id': ['KITCHEN_001', 'KITCHEN_002', 'KITCHEN_003', 'KITCHEN_004'],
            'kitchen_name': ['Main Kitchen', 'Pizza Station', 'Salad Station', 'Dessert Corner'],
            'capacity': [5, 3, 2, 4],
            'specialization': ['Burgers & Mains', 'Pizza & Italian', 'Salads & Healthy', 'Desserts & Beverages'],
            'status': ['active', 'active', 'active', 'active'],
            'current_load': [0, 0, 0, 0],
            'staff_count': [4, 2, 1, 1]
        }
        kitchens_df = pd.DataFrame(kitchens_data)
        kitchens_df.to_excel(writer, sheet_name='kitchens', index=False)
        
        # Sheet 2: items (synced with frontend data)
        items_data = {
            'item_id': [
                'ITM_001', 'ITM_002', 'ITM_003', 'ITM_004', 'ITM_005', 'ITM_006'
            ],
            'item_name': [
                'Burger Deluxe', 'French Fries', 'Pizza Margherita', 'Caesar Salad', 'Grilled Chicken', 'Chocolate Cake'
            ],
            'kitchen_id': [
                'KITCHEN_001', 'KITCHEN_001', 'KITCHEN_002', 'KITCHEN_003', 'KITCHEN_001', 'KITCHEN_004'
            ],
            'prep_time_minutes': [15, 8, 20, 10, 18, 5],
            'difficulty_level': [
                'medium', 'easy', 'medium', 'easy', 'medium', 'easy'
            ],
            'description': [
                'Juicy beef patty with fresh vegetables and special sauce',
                'Crispy golden fries with sea salt',
                'Classic pizza with tomato sauce, mozzarella, and fresh basil',
                'Fresh romaine lettuce with Caesar dressing and croutons',
                'Perfectly grilled chicken breast with herbs',
                'Rich chocolate cake with chocolate frosting'
            ],
            'price': [12.99, 4.99, 14.99, 9.99, 16.99, 6.99],
            'image': [
                '/lovable-uploads/22d31f51-c174-40a7-bd95-00e4ad00eaf3.png',
                '/lovable-uploads/5663820f-6c97-4492-9210-9eaa1a8dc415.png',
                '/lovable-uploads/af412c03-21e4-4856-82ff-d1a975dc84a9.png',
                '/lovable-uploads/c3d5522b-6886-4b75-8ffc-d020016bb9c2.png',
                '/placeholder.svg',
                '/placeholder.svg'
            ],
            'calories': [650, 350, 800, 320, 450, 520],
            'category': ['burgers', 'sides', 'pizza', 'salads', 'mains', 'desserts'],
            'available': [True, True, True, True, True, True]
        }
        items_df = pd.DataFrame(items_data)
        items_df.to_excel(writer, sheet_name='items', index=False)
        
        # Sheet 3: historical_performance (sample data for last 30 days)
        historical_data = []
        base_date = datetime.now() - timedelta(days=30)
        
        for i in range(100):  # 100 sample records
            date = base_date + timedelta(days=i % 30)
            kitchen_id = ['KITCHEN_A', 'KITCHEN_B', 'KITCHEN_C'][i % 3]
            item_id = items_data['item_id'][i % len(items_data['item_id'])]
            scheduled_time = items_data['prep_time_minutes'][i % len(items_data['prep_time_minutes'])]
            actual_time = scheduled_time + (i % 5 - 2)  # Some variation
            delay = max(0, actual_time - scheduled_time)
            
            historical_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'kitchen_id': kitchen_id,
                'item_id': item_id,
                'actual_prep_time': actual_time,
                'scheduled_prep_time': scheduled_time,
                'delay_minutes': delay,
                'kitchen_load': (i % 3) + 1,
                'order_id': f'ORD_{i+1:03d}'
            })
        
        historical_df = pd.DataFrame(historical_data)
        historical_df.to_excel(writer, sheet_name='historical_performance', index=False)
        
        # Sheet 4: kitchen_load_patterns
        load_patterns_data = {
            'hour': list(range(24)),
            'kitchen_a_avg_load': [
                0.5, 0.3, 0.2, 0.2, 0.3, 0.5, 0.8, 1.2, 1.5, 1.8,
                2.0, 2.2, 2.5, 2.3, 2.0, 1.8, 1.5, 1.3, 1.0, 0.8,
                0.6, 0.5, 0.4, 0.3
            ],
            'kitchen_b_avg_load': [
                0.3, 0.2, 0.1, 0.1, 0.2, 0.3, 0.5, 0.8, 1.1, 1.4,
                1.6, 1.8, 1.9, 1.7, 1.5, 1.3, 1.1, 0.9, 0.7, 0.5,
                0.4, 0.3, 0.3, 0.2
            ],
            'kitchen_c_avg_load': [
                0.8, 0.5, 0.3, 0.2, 0.3, 0.5, 0.7, 1.0, 1.5, 2.0,
                2.5, 3.0, 3.2, 3.0, 2.8, 2.5, 2.0, 1.5, 1.2, 1.0,
                0.8, 0.7, 0.6, 0.5
            ]
        }
        load_patterns_df = pd.DataFrame(load_patterns_data)
        load_patterns_df.to_excel(writer, sheet_name='kitchen_load_patterns', index=False)
    
    print(f"Sample Excel file created at: {file_path}")


if __name__ == "__main__":
    create_sample_excel("data/kitchen_config.xlsx")
