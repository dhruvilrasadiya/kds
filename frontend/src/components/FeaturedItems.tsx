
import React from "react";
import { Carousel, CarouselContent, CarouselItem, CarouselNext, CarouselPrevious } from "@/components/ui/carousel";
import MenuItemCard from "./MenuItemCard";

const FeaturedItems = () => {
  const featuredItems = [
    {
      id: 'f1',
      name: 'Signature Burger',
      category: 'hamburger',
      price: 15.99,
      calories: 750,
      image: 'https://images.unsplash.com/photo-1604909052743-94e838986d24?q=80&w=1160&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D',
      description: 'Our signature beef burger with special sauce and premium ingredients',
      addOns: ['Extra Cheese', 'Bacon', 'Avocado', 'Onion Rings']
    },
    {
      id: 'f2',
      name: 'Supreme Pizza',
      category: 'pizza',
      price: 18.99,
      calories: 820,
      image: 'https://images.unsplash.com/photo-1604909052743-94e838986d24?q=80&w=1160&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D',
      description: 'Loaded with pepperoni, mushrooms, bell peppers, and mozzarella',
      addOns: ['Extra Cheese', 'Olives', 'Hot Sauce']
    },
    {
      id: 'f3',
      name: 'Grilled Chicken Salad',
      category: 'salad',
      price: 11.99,
      calories: 420,
      image: 'https://images.unsplash.com/photo-1604909052743-94e838986d24?q=80&w=1160&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D',
      description: 'Fresh mixed greens with grilled chicken and house dressing',
      addOns: ['Avocado', 'Nuts', 'Extra Chicken']
    },
    {
      id: 'f4',
      name: 'Deluxe Chocolate Cake',
      category: 'dessert',
      price: 8.99,
      calories: 520,
      image: 'https://images.unsplash.com/photo-1604909052743-94e838986d24?q=80&w=1160&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D',
      description: 'Rich triple chocolate cake with ganache frosting',
      addOns: ['Ice Cream', 'Berries', 'Whipped Cream']
    },
  ];

  return (
    <section className="section-container">
      <div className="text-center mb-12">
        <h2 className="section-title mb-4">Top Featured Items</h2>
        <p className="section-subtitle">Our most popular dishes that customers love</p>
      </div>
      
      <Carousel className="w-full max-w-6xl mx-auto height-full">
        <CarouselContent className="-ml-2 md:-ml-4">
          {featuredItems.map((item) => (
            <CarouselItem key={item.id} className="pl-2 md:pl-4 md:basis-1/2 lg:basis-1/3">
              <MenuItemCard item={item} />
            </CarouselItem>
          ))}
        </CarouselContent>
        <CarouselPrevious />
        <CarouselNext />
      </Carousel>
    </section>
  );
};

export default FeaturedItems;
