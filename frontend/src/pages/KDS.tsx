
import React, { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Grid, List, Clock, Users, Plus, Settings, ShoppingCart, Filter, RefreshCw, MoreVertical, ChevronLeft, AlertCircle, Loader2 } from "lucide-react";
import { Link } from "react-router-dom";
import {
  useActiveOrders,
  useKitchens,
  useUpdateOrder,
  useUpdateOrderStatus,
  useAcceptOrder,
  useMarkOrderReady,
  useCompleteOrder,
  useHoldOrder,
  useResumeOrder
} from "@/hooks";
import { OrderStatus } from "@/types/api";

const KDS = () => {
  const [viewMode, setViewMode] = useState<"grid" | "list">("grid");
  const [isManager, setIsManager] = useState(false);
  const [selectedKitchen, setSelectedKitchen] = useState<string | null>(null);
  const [filterStatus, setFilterStatus] = useState("all");
  const [currentTime, setCurrentTime] = useState(new Date());
  const [newKitchenName, setNewKitchenName] = useState("");
  const [isAddKitchenOpen, setIsAddKitchenOpen] = useState(false);

  // Backend integration
  const { data: orders, isLoading: ordersLoading, isError: ordersError, refetch: refetchOrders } = useActiveOrders();
  const { data: kitchensData, isLoading: kitchensLoading, isError: kitchensError, refetch: refetchKitchens } = useKitchens();

  // Order mutations
  const acceptOrderMutation = useAcceptOrder();
  const markReadyMutation = useMarkOrderReady();
  const completeOrderMutation = useCompleteOrder();
  const holdOrderMutation = useHoldOrder();
  const resumeOrderMutation = useResumeOrder();
  const updateOrderStatusMutation = useUpdateOrderStatus();
  
  // Process backend data
  const kitchens = kitchensData?.kitchens || [];
  const allOrders = orders || [];

  // Update time every minute
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 60000);
    return () => clearInterval(timer);
  }, []);

  const handleAddKitchen = () => {
    if (newKitchenName.trim()) {
      // In a real implementation, this would call a backend API
      console.log("Add kitchen:", newKitchenName.trim());
      setNewKitchenName("");
      setIsAddKitchenOpen(false);
    }
  };

  const handleStatusChange = async (orderId: string, newStatus: OrderStatus) => {
    try {
      // Use the new direct status update API
      await updateOrderStatusMutation.mutateAsync({ orderId, status: newStatus });
    } catch (error) {
      console.error("Failed to update order status:", error);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "pending": return "bg-yellow-500 hover:bg-yellow-600";
      case "accepted": return "bg-blue-500 hover:bg-blue-600";
      case "preparing": return "bg-orange-500 hover:bg-orange-600";
      case "cooking": return "bg-purple-500 hover:bg-purple-600";
      case "ready": return "bg-green-500 hover:bg-green-600";
      case "hold": return "bg-red-500 hover:bg-red-600";
      default: return "bg-gray-500 hover:bg-gray-600";
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "high": return "border-l-red-500 bg-red-50";
      case "medium": return "border-l-yellow-500 bg-yellow-50";
      case "low": return "border-l-green-500 bg-green-50";
      default: return "border-l-gray-500 bg-gray-50";
    }
  };

  const getKitchenStatusColor = (status: string) => {
    switch (status) {
      case "active": return "bg-green-500";
      case "maintenance": return "bg-red-500";
      case "offline": return "bg-gray-500";
      default: return "bg-gray-500";
    }
  };



  const filteredOrders = allOrders.filter(order => {
    if (filterStatus === "all") return true;
    return order.status === filterStatus;
  });

  console.log("Filtered orders:", filteredOrders);

  const kitchenOrders = selectedKitchen
    ? filteredOrders.filter(order => {
        // Find kitchen by name for filtering
        const kitchen = kitchens.find(k => k.name === selectedKitchen);
        return kitchen && order.queue_items?.some(item => item.kitchen_id === kitchen.kitchen_id);
      })
    : filteredOrders;

  const OrderCard = ({ order }: { order: any }) => {
    const priority = order.queue_items?.[0]?.priority || "medium";
    const estimatedTime = order.estimated_completion
      ? new Date(order.estimated_completion).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      : "N/A";
    const orderTime = new Date(order.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    return (
      <Card className={`mb-4 border-l-4 ${getPriorityColor(priority)} hover:shadow-lg transition-all duration-200`}>
        <CardHeader className="pb-3">
          <div className="flex justify-between items-start">
            <div>
              <CardTitle className="text-lg flex items-center gap-2">
                {order.order_id}
                {priority === "high" && <AlertCircle className="w-4 h-4 text-red-500" />}
              </CardTitle>
              <div className="text-sm text-gray-600 mt-1">
                {order.customer_name && (
                  <>
                    <span className="font-medium">
                      {order.table_number ? `Table ${order.table_number}` : 'Customer'}
                    </span> • {order.customer_name}
                  </>
                )}
              </div>
              <div className="text-xs text-gray-500">Ordered at {orderTime}</div>
            </div>
            <Badge className={`${getStatusColor(order.status)} text-white`}>
              {order.status.charAt(0).toUpperCase() + order.status.slice(1)}
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {order.items?.map((itemId: string, index: number) => (
              <div key={index} className="flex items-center gap-3 p-2 bg-white rounded-lg">
                <div className="w-12 h-12 bg-gray-200 rounded flex items-center justify-center">
                  <span className="text-xs font-medium">{itemId.slice(-3)}</span>
                </div>
                <div className="flex-1">
                  <p className="font-medium">Item {itemId}</p>
                  <p className="text-sm text-gray-600">Kitchen Item</p>
                </div>
              </div>
            )) || (
              <div className="text-sm text-gray-500">No items found</div>
            )}
          
            <div className="flex gap-2 pt-4">
              {order.status === OrderStatus.PENDING && (
                <>
                  <Button
                    onClick={() => handleStatusChange(order.order_id, OrderStatus.ACCEPTED)}
                    size="sm"
                    className="bg-blue-500 hover:bg-blue-600"
                    disabled={acceptOrderMutation.isPending}
                  >
                    {acceptOrderMutation.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Accept'}
                  </Button>
                  <Button
                    onClick={() => handleStatusChange(order.order_id, OrderStatus.HOLD)}
                    variant="destructive"
                    size="sm"
                    disabled={holdOrderMutation.isPending}
                  >
                    {holdOrderMutation.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Hold'}
                  </Button>
                </>
              )}

              {(order.status === OrderStatus.ACCEPTED || order.status === OrderStatus.PREPARING || order.status === OrderStatus.COOKING) && (
                <select
                  className="px-3 py-1 border rounded-md bg-white"
                  value={order.status}
                  onChange={(e) => handleStatusChange(order.order_id, e.target.value as OrderStatus)}
                >
                  <option value={OrderStatus.PREPARING}>Preparing</option>
                  <option value={OrderStatus.COOKING}>Cooking</option>
                  <option value={OrderStatus.READY}>Ready for Delivery</option>
                  <option value={OrderStatus.HOLD}>Hold</option>
                </select>
              )}

              {order.status === OrderStatus.READY && (
                <Button
                  onClick={() => handleStatusChange(order.order_id, OrderStatus.COMPLETED)}
                  size="sm"
                  className="bg-green-600 hover:bg-green-700"
                  disabled={completeOrderMutation.isPending}
                >
                  {completeOrderMutation.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Mark Delivered'}
                </Button>
              )}

              {order.status === OrderStatus.HOLD && (
                <Button
                  onClick={() => handleStatusChange(order.order_id, OrderStatus.PREPARING)}
                  size="sm"
                  className="bg-orange-500 hover:bg-orange-600"
                  disabled={resumeOrderMutation.isPending}
                >
                  {resumeOrderMutation.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Resume'}
                </Button>
              )}
            </div>
          
            <div className="flex items-center justify-between pt-2 text-sm text-gray-600">
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-1">
                  <Clock className="w-4 h-4" />
                  {estimatedTime}
                </div>
                <div className="flex items-center gap-1">
                  <Users className="w-4 h-4" />
                  {order.queue_items?.length || 0} items
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  };

  const KitchenCard = ({ kitchen }: { kitchen: any }) => {
    const activeOrders = allOrders.filter(order =>
      order.queue_items?.some((item: any) => item.kitchen_id === kitchen.kitchen_id)
    ).length;

    return (
      <Card className="mb-4 hover:shadow-lg transition-shadow cursor-pointer" onClick={() => setSelectedKitchen(kitchen.name)}>
        <CardHeader>
          <div className="flex justify-between items-center">
            <CardTitle className="text-lg">{kitchen.name}</CardTitle>
            <Badge className={getKitchenStatusColor(kitchen.status || 'active')}>
              {(kitchen.status || 'active').charAt(0).toUpperCase() + (kitchen.status || 'active').slice(1)}
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between text-sm text-gray-600">
            <div className="flex items-center gap-1">
              <Users className="w-4 h-4" />
              {activeOrders} active orders
            </div>
            <div className="flex items-center gap-1">
              <Users className="w-4 h-4" />
              Load: {kitchen.current_load}/{kitchen.capacity}
            </div>
          </div>
        </CardContent>
      </Card>
    );
  };

  // Show loading state
  if (ordersLoading || kitchensLoading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="container mx-auto p-4 lg:p-6">
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4" />
              <p className="text-gray-600">Loading kitchen data...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Show error state
  if (ordersError || kitchensError) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="container mx-auto p-4 lg:p-6">
          <Alert variant="destructive" className="max-w-md mx-auto">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              Failed to load kitchen data. Please check your connection to the backend.
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  refetchOrders();
                  refetchKitchens();
                }}
                className="ml-2"
              >
                <RefreshCw className="h-4 w-4 mr-2" />
                Retry
              </Button>
            </AlertDescription>
          </Alert>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto p-4 lg:p-6">
        {/* Header */}
        <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center mb-6 gap-4">
          <div>
            <h1 className="text-2xl lg:text-3xl font-bold">Kitchen Display System</h1>
            <p className="text-gray-600 mt-1">
              {currentTime.toLocaleDateString()} • {currentTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </p>
            <p className="text-sm text-gray-500">
              {allOrders.length} total orders • {kitchens.length} kitchens
            </p>
          </div>
          
          <div className="flex flex-wrap gap-2">
            {selectedKitchen && (
              <Button
                variant="outline"
                onClick={() => setSelectedKitchen(null)}
                size="sm"
                className="flex items-center gap-2"
              >
                <ChevronLeft className="w-4 h-4" />
                Back to All
              </Button>
            )}
            
            <Button
              variant={isManager ? "default" : "outline"}
              onClick={() => setIsManager(!isManager)}
              size="sm"
              className="flex items-center gap-2"
            >
              <Settings className="w-4 h-4" />
              Manager Mode
            </Button>
            
            <Button
              variant={viewMode === "grid" ? "default" : "outline"}
              onClick={() => setViewMode("grid")}
              size="sm"
            >
              <Grid className="w-4 h-4" />
            </Button>
            
            <Button
              variant={viewMode === "list" ? "default" : "outline"}
              onClick={() => setViewMode("list")}
              size="sm"
            >
              <List className="w-4 h-4" />
            </Button>
          </div>
        </div>

        {/* Manager Section */}
        {isManager && !selectedKitchen && (
          <div className="mb-8">
            <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center mb-4 gap-4">
              <h2 className="text-xl lg:text-2xl font-semibold">Kitchen Management</h2>
              <Dialog open={isAddKitchenOpen} onOpenChange={setIsAddKitchenOpen}>
                <DialogTrigger asChild>
                  <Button className="flex items-center gap-2">
                    <Plus className="w-4 h-4" />
                    Add Kitchen
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Add New Kitchen</DialogTitle>
                  </DialogHeader>
                  <div className="space-y-4">
                    <div>
                      <Label htmlFor="kitchen-name">Kitchen Name</Label>
                      <Input
                        id="kitchen-name"
                        value={newKitchenName}
                        onChange={(e) => setNewKitchenName(e.target.value)}
                        placeholder="Enter kitchen name"
                      />
                    </div>
                    <Button onClick={handleAddKitchen} className="w-full">
                      Add Kitchen
                    </Button>
                  </div>
                </DialogContent>
              </Dialog>
            </div>
            
            <div className={viewMode === "grid" ? "grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 mb-8" : "space-y-4 mb-8"}>
              {kitchens.map((kitchen) => (
                <KitchenCard key={kitchen.kitchen_id} kitchen={kitchen} />
              ))}
            </div>
          </div>
        )}

        {/* Filters */}
        <div className="flex flex-wrap items-center gap-4 mb-6">
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4" />
            <span className="text-sm font-medium">Filter by status:</span>
          </div>
          <select 
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="px-3 py-1 border rounded-md bg-white text-sm"
          >
            <option value="all">All Orders</option>
            <option value="pending">Pending</option>
            <option value="preparing">Preparing</option>
            <option value="cooking">Cooking</option>
            <option value="ready">Ready</option>
            <option value="hold">On Hold</option>
          </select>
          
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              refetchOrders();
              refetchKitchens();
            }}
            className="flex items-center gap-2"
            disabled={ordersLoading || kitchensLoading}
          >
            <RefreshCw className={`w-4 h-4 ${ordersLoading || kitchensLoading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>

        {/* Orders Section */}
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl lg:text-2xl font-semibold">
            {selectedKitchen ? `${selectedKitchen} Orders` : 'Active Orders'}
          </h2>
          <div className="text-sm text-gray-600">
            {kitchenOrders.length} orders
          </div>
        </div>
        
        <div className={viewMode === "grid" ? "grid sm:grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4" : "space-y-4"}>
          {kitchenOrders.map((order) => (
            <OrderCard key={order.order_id} order={order} />
          ))}
        </div>

        {kitchenOrders.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500 text-lg">No orders found for the selected filters.</p>
          </div>
        )}
      </div>

      {/* Floating Order Now Button */}
      <Link
        to="/menu"
        className="fixed bottom-6 left-6 bg-primary hover:bg-primary/90 text-primary-foreground p-4 rounded-full shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105 z-50"
        title="Order Now"
      >
        <ShoppingCart className="w-6 h-6" />
      </Link>
    </div>
  );
};


export default KDS;




