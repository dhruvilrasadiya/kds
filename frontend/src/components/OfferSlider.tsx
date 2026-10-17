
import React from "react";
import { Carousel, CarouselContent, CarouselItem, CarouselNext, CarouselPrevious } from "@/components/ui/carousel";
import { Button } from "@/components/ui/button";

const OfferSlider = () => {
  const offers = [
    {
      id: 1,
      title: "20% Off on Orders Above $50",
      description: "Get amazing discount on your favorite meals",
      code: "SAVE20",
      image: "/lovable-uploads/22d31f51-c174-40a7-bd95-00e4ad00eaf3.png",
      validUntil: "Dec 31, 2024"
    },
    {
      id: 2,
      title: "Free Delivery Weekend",
      description: "Enjoy free delivery on all orders this weekend",
      code: "FREEDEL",
      image: "/lovable-uploads/af412c03-21e4-4856-82ff-d1a975dc84a9.png",
      validUntil: "Jan 15, 2024"
    },
    {
      id: 3,
      title: "Buy 2 Get 1 Free Pizza",
      description: "Order any 2 pizzas and get 1 free",
      code: "PIZZA3",
      image: "/lovable-uploads/c3d5522b-6886-4b75-8ffc-d020016bb9c2.png",
      validUntil: "Jan 30, 2024"
    },
    {
      id: 4,
      title: "Happy Hour Special",
      description: "30% off on beverages from 3-6 PM",
      code: "HAPPY30",
      image: "/lovable-uploads/dc13e94f-beeb-4671-8a22-0968498cdb4c.png",
      validUntil: "Ongoing"
    }
  ];

  return (
    <section className="section-container bg-gradient-to-r from-pulse-50 to-orange-50">
      <div className="text-center mb-12">
        <h2 className="section-title mb-4">Special Offers</h2>
        <p className="section-subtitle">Don't miss out on our amazing deals</p>
      </div>
      
      <Carousel 
        className="w-full max-w-5xl mx-auto"
        opts={{
          align: "start",
          loop: true,
        }}
      >
        <CarouselContent className="-ml-2 md:-ml-4">
          {offers.map((offer) => (
            <CarouselItem key={offer.id} className="pl-2 md:pl-4 md:basis-1/2">
              <div className="bg-white rounded-xl shadow-lg overflow-hidden hover:shadow-xl transition-shadow">
                <div className="h-40 overflow-hidden">
                  <img
                    src={offer.image}
                    alt={offer.title}
                    className="w-full h-full object-cover"
                  />
                </div>
                <div className="p-6">
                  <h3 className="text-xl font-bold text-gray-900 mb-2">{offer.title}</h3>
                  <p className="text-gray-600 mb-4">{offer.description}</p>
                  <div className="flex items-center justify-between">
                    <div className="bg-pulse-100 text-pulse-600 px-3 py-1 rounded-full text-sm font-semibold">
                      Code: {offer.code}
                    </div>
                    <div className="text-sm text-gray-500">
                      Valid until: {offer.validUntil}
                    </div>
                  </div>
                  <Button className="w-full mt-4 bg-pulse-500 hover:bg-pulse-600">
                    Claim Offer
                  </Button>
                </div>
              </div>
            </CarouselItem>
          ))}
        </CarouselContent>
        <CarouselPrevious />
        <CarouselNext />
      </Carousel>
    </section>
  );
};

export default OfferSlider;
