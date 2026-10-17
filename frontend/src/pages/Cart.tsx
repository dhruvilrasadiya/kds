
import React, { useState } from "react";
import { useCart } from "@/contexts/CartContext";
import { Button } from "@/components/ui/button";
import { Minus, Plus, Trash2, Calendar, Clock, CreditCard, Smartphone, Loader2 } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { Link } from "react-router-dom";
import Navbar from "@/components/Navbar";
import FloatingKDS from "@/components/FloatingKDS";
import { Calendar as CalendarComponent } from "@/components/ui/calendar";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { format } from "date-fns";
import { cn } from "@/lib/utils";
import { useCreateOrder } from "@/hooks";
import { CreateOrderRequest } from "@/types/api";

const Cart = () => {
  const { cartItems, updateQuantity, removeFromCart, getCartTotal, clearCart } = useCart();
  const { toast } = useToast();
  const [deliveryOption, setDeliveryOption] = useState("dine-in");
  const [onlineDate, setOnlineDate] = useState<Date>();
  const [onlineTime, setOnlineTime] = useState("");
  const [showPaymentOptions, setShowPaymentOptions] = useState(false);
  const [paymentMethod, setPaymentMethod] = useState("");
  const [showInvoice, setShowInvoice] = useState(false);
  const [orderNumber, setOrderNumber] = useState("");
  const [customerName, setCustomerName] = useState("");
  const [tableNumber, setTableNumber] = useState("");

  // Backend integration
  const createOrderMutation = useCreateOrder();

  const handlePayment = () => {
    if (deliveryOption === "online" && (!onlineDate || !onlineTime)) {
      toast({
        title: "Please select date and time",
        description: "Online order requires date and time selection",
        variant: "destructive",
      });
      return;
    }
    setShowPaymentOptions(true);
  };

  const processPayment = async () => {
    if (!paymentMethod) {
      toast({
        title: "Please select payment method",
        description: "Choose UPI or Card to proceed",
        variant: "destructive",
      });
      return;
    }

    if (!customerName.trim()) {
      toast({
        title: "Please enter customer name",
        description: "Customer name is required for order processing",
        variant: "destructive",
      });
      return;
    }

    try {
      // Prepare order data for backend
      const orderData: CreateOrderRequest = {
        items: cartItems.map(item => item.id), // Assuming item.id maps to backend item IDs
        customer_name: customerName,
        table_number: tableNumber || undefined,
        notes: deliveryOption === "online" && onlineDate && onlineTime
          ? `Online order for ${format(onlineDate, "PPP")} at ${onlineTime}. Delivery option: ${deliveryOption}`
          : `Delivery option: ${deliveryOption}`
      };

      // Create order via backend API
      const response = await createOrderMutation.mutateAsync(orderData);

      if (response.success && response.order) {
        setOrderNumber(response.order.order_id);
        setShowInvoice(true);

        toast({
          title: "Order Created Successfully!",
          description: `Your order ${response.order.order_id} has been sent to the kitchen. Thank you for dining with us!`,
        });
      }
    } catch (error) {
      console.error('Order creation failed:', error);
      toast({
        title: "Order Failed",
        description: "Failed to create order. Please try again or contact support.",
        variant: "destructive",
      });
    }
  };

  const continueShopping = () => {
    clearCart();
    setShowInvoice(false);
    setShowPaymentOptions(false);
    setDeliveryOption("dine-in");
    setOnlineDate(undefined);
    setOnlineTime("");
    setPaymentMethod("");
  };

  if (cartItems.length === 0 && !showInvoice) {
    return (
      <>
        <Navbar />
        <div className="min-h-screen flex items-center justify-center bg-gray-50 pt-20">
          <div className="text-center">
            <h2 className="text-2xl font-bold mb-4">Your cart is empty</h2>
            <p className="text-gray-600 mb-6">Add some delicious items to your cart</p>
            <Link to="/menu">
              <Button>Browse Menu</Button>
            </Link>
          </div>
        </div>
        <FloatingKDS />
      </>
    );
  }

  const subtotal = getCartTotal();
  const tax = subtotal * 0.1;
  const total = subtotal + tax;

  if (showInvoice) {
    return (
      <>
        <Navbar />
        <div className="min-h-screen bg-gray-50 py-8 pt-20">
          <div className="container mx-auto px-4 max-w-2xl">
            <div className="bg-white rounded-lg shadow-md p-8">
              <div className="text-center mb-8">
                <h1 className="text-3xl font-bold text-green-600 mb-2">Payment Successful!</h1>
                <p className="text-gray-600">Thank you for your order</p>
              </div>
              
              <div className="border-b pb-4 mb-4">
                <h2 className="text-xl font-semibold mb-4">Order Invoice</h2>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <p><strong>Order Number:</strong> {orderNumber}</p>
                    <p><strong>Date:</strong> {format(new Date(), "PPP")}</p>
                    <p><strong>Time:</strong> {format(new Date(), "p")}</p>
                  </div>
                  <div>
                    <p><strong>Delivery:</strong> {deliveryOption === "online" ? "Online Order" : deliveryOption}</p>
                    {deliveryOption === "online" && onlineDate && onlineTime && (
                      <>
                        <p><strong>Order Date:</strong> {format(onlineDate, "PPP")}</p>
                        <p><strong>Order Time:</strong> {onlineTime}</p>
                      </>
                    )}
                    <p><strong>Payment:</strong> {paymentMethod}</p>
                  </div>
                </div>
              </div>
              
              <div className="mb-6">
                <h3 className="font-semibold mb-3">Order Items</h3>
                {cartItems.map((item) => (
                  <div key={item.id} className="flex justify-between py-2 border-b">
                    <div>
                      <p className="font-medium">{item.name}</p>
                      <p className="text-sm text-gray-600">Qty: {item.quantity}</p>
                    </div>
                    <p className="font-medium">${(item.price * item.quantity).toFixed(2)}</p>
                  </div>
                ))}
              </div>
              
              <div className="border-t pt-4 mb-6">
                <div className="flex justify-between mb-2">
                  <span>Subtotal</span>
                  <span>${subtotal.toFixed(2)}</span>
                </div>
                <div className="flex justify-between mb-2">
                  <span>Tax</span>
                  <span>${tax.toFixed(2)}</span>
                </div>
                <div className="flex justify-between font-bold text-lg">
                  <span>Total</span>
                  <span>${total.toFixed(2)}</span>
                </div>
              </div>
              
              <Button onClick={continueShopping} className="w-full">
                Continue Shopping
              </Button>
            </div>
          </div>
        </div>
        <FloatingKDS />
      </>
    );
  }

  if (showPaymentOptions) {
    return (
      <>
        <Navbar />
        <div className="min-h-screen bg-gray-50 py-8 pt-20">
          <div className="container mx-auto px-4 max-w-md">
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-2xl font-bold mb-6 text-center">Order Details & Payment</h2>

              {/* Customer Information */}
              <div className="space-y-4 mb-6">
                <div>
                  <label className="block text-sm font-medium mb-2">Customer Name *</label>
                  <input
                    type="text"
                    value={customerName}
                    onChange={(e) => setCustomerName(e.target.value)}
                    placeholder="Enter customer name"
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pulse-500 focus:border-transparent"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Table Number (Optional)</label>
                  <input
                    type="text"
                    value={tableNumber}
                    onChange={(e) => setTableNumber(e.target.value)}
                    placeholder="Enter table number"
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pulse-500 focus:border-transparent"
                  />
                </div>
              </div>

              <div className="space-y-4 mb-6">
                <button
                  onClick={() => setPaymentMethod("UPI")}
                  className={cn(
                    "w-full p-4 border rounded-lg flex items-center justify-center space-x-3 transition-colors",
                    paymentMethod === "UPI" ? "border-pulse-500 bg-pulse-50" : "border-gray-300 hover:border-gray-400"
                  )}
                >
                  <Smartphone className="w-6 h-6" />
                  <span className="text-lg font-medium">UPI Payment</span>
                </button>
                
                <button
                  onClick={() => setPaymentMethod("Card")}
                  className={cn(
                    "w-full p-4 border rounded-lg flex items-center justify-center space-x-3 transition-colors",
                    paymentMethod === "Card" ? "border-pulse-500 bg-pulse-50" : "border-gray-300 hover:border-gray-400"
                  )}
                >
                  <CreditCard className="w-6 h-6" />
                  <span className="text-lg font-medium">Card Payment</span>
                </button>
              </div>
              
              <div className="border-t pt-4 mb-6">
                <div className="flex justify-between font-bold text-lg">
                  <span>Total Amount</span>
                  <span>${total.toFixed(2)}</span>
                </div>
              </div>
              
              <div className="space-y-3">
                <Button
                  onClick={processPayment}
                  className="w-full"
                  disabled={createOrderMutation.isPending || !customerName.trim()}
                >
                  {createOrderMutation.isPending ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Creating Order...
                    </>
                  ) : (
                    'Create Order & Pay'
                  )}
                </Button>
                <Button variant="outline" onClick={() => setShowPaymentOptions(false)} className="w-full">
                  Back to Cart
                </Button>
              </div>
            </div>
          </div>
        </div>
        <FloatingKDS />
      </>
    );
  }

  return (
    <>
      <Navbar />
      <div className="min-h-screen bg-gray-50 py-8 pt-20">
        <div className="container mx-auto px-4">
          <h1 className="text-3xl font-bold mb-8">Your Cart</h1>
          
          <div className="grid lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2">
              {cartItems.map((item) => (
                <div key={item.id} className="bg-white rounded-lg shadow-md p-6 mb-4">
                  <div className="flex items-center gap-4">
                    <img 
                      src={item.image} 
                      alt={item.name}
                      className="w-20 h-20 object-cover rounded-lg"
                    />
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold">{item.name}</h3>
                      <p className="text-gray-600">{item.category}</p>
                      <p className="text-pulse-500 font-bold">${item.price}</p>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => updateQuantity(item.id, item.quantity - 1)}
                      >
                        <Minus className="w-4 h-4" />
                      </Button>
                      <span className="px-3 py-1 bg-gray-100 rounded">{item.quantity}</span>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => updateQuantity(item.id, item.quantity + 1)}
                      >
                        <Plus className="w-4 h-4" />
                      </Button>
                      <Button
                        variant="destructive"
                        size="sm"
                        onClick={() => removeFromCart(item.id)}
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
            
            <div className="lg:col-span-1">
              <div className="bg-white rounded-lg shadow-md p-6 sticky top-8">
                <h3 className="text-xl font-bold mb-4">Order Summary</h3>
                
                <div className="space-y-2 mb-4">
                  <div className="flex justify-between">
                    <span>Subtotal</span>
                    <span>${subtotal.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Tax</span>
                    <span>${tax.toFixed(2)}</span>
                  </div>
                  <div className="border-t pt-2">
                    <div className="flex justify-between font-bold">
                      <span>Total</span>
                      <span>${total.toFixed(2)}</span>
                    </div>
                  </div>
                </div>
                
                <div className="space-y-3">
                  <div>
                    <label className="block text-sm font-medium mb-2">Delivery Options</label>
                    <select 
                      value={deliveryOption}
                      onChange={(e) => setDeliveryOption(e.target.value)}
                      className="w-full p-2 border border-gray-300 rounded"
                    >
                      <option value="dine-in">Dine-in</option>
                      <option value="take-away">Take away</option>
                      <option value="online">Online Order</option>
                    </select>
                  </div>
                  
                  {deliveryOption === "online" && (
                    <div className="space-y-3">
                      <div>
                        <label className="block text-sm font-medium mb-2">Select Date</label>
                        <Popover>
                          <PopoverTrigger asChild>
                            <Button
                              variant="outline"
                              className={cn(
                                "w-full justify-start text-left font-normal",
                                !onlineDate && "text-muted-foreground"
                              )}
                            >
                              <Calendar className="mr-2 h-4 w-4" />
                              {onlineDate ? format(onlineDate, "PPP") : <span>Pick a date</span>}
                            </Button>
                          </PopoverTrigger>
                          <PopoverContent className="w-auto p-0">
                            <CalendarComponent
                              mode="single"
                              selected={onlineDate}
                              onSelect={setOnlineDate}
                              initialFocus
                              className="pointer-events-auto"
                            />
                          </PopoverContent>
                        </Popover>
                      </div>

                      <div>
                        <label className="block text-sm font-medium mb-2">Select Time</label>
                        <select
                          value={onlineTime}
                          onChange={(e) => setOnlineTime(e.target.value)}
                          className="w-full p-2 border border-gray-300 rounded"
                        >
                          <option value="">Select time</option>
                          <option value="09:00">09:00 AM</option>
                          <option value="10:00">10:00 AM</option>
                          <option value="11:00">11:00 AM</option>
                          <option value="12:00">12:00 PM</option>
                          <option value="13:00">01:00 PM</option>
                          <option value="14:00">02:00 PM</option>
                          <option value="15:00">03:00 PM</option>
                          <option value="16:00">04:00 PM</option>
                          <option value="17:00">05:00 PM</option>
                          <option value="18:00">06:00 PM</option>
                          <option value="19:00">07:00 PM</option>
                          <option value="20:00">08:00 PM</option>
                        </select>
                      </div>

                      {onlineDate && onlineTime && (
                        <div className="p-3 bg-pulse-50 rounded-lg">
                          <p className="text-sm font-medium text-pulse-600">
                            Online order for: {format(onlineDate, "PPP")} at {onlineTime}
                          </p>
                        </div>
                      )}
                    </div>
                  )}
                  
                  <Button onClick={handlePayment} className="w-full">
                    Process to Payment
                  </Button>
                  
                  <Link to="/menu">
                    <Button variant="outline" className="w-full">
                      Add More Items
                    </Button>
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <FloatingKDS />
    </>
  );
};

export default Cart;
