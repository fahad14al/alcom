# orders/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Order, OrderItem, ShippingMethod
from .serializers import (
    OrderListSerializer, OrderDetailSerializer, 
    OrderCreateSerializer, ShippingMethodSerializer
)
from cart.models import Cart

class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Order.objects.none()
        return Order.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        elif self.action == 'retrieve':
            return OrderDetailSerializer
        return OrderListSerializer

    def create(self, request, *args, **kwargs):
        # Get user's cart
        try:
            cart = Cart.objects.get(user=request.user)
        except Cart.DoesNotExist:
            return Response(
                {'error': 'Cart is empty'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        if cart.items.count() == 0:
            return Response(
                {'error': 'Cart is empty'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create order from cart
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Calculate total amount from cart
        total_amount = cart.total_price
        order = serializer.save(user=request.user, total_amount=total_amount)

        # Move cart items to order
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price_at_purchase=cart_item.product.base_price
            )

        # Clear cart
        cart.items.all().delete()
        cart.coupon = None
        cart.save()

        # Return order details
        order_serializer = OrderDetailSerializer(order)
        return Response(order_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        order = self.get_object()
        if order.can_cancel():
            order.status = 'cancelled'
            order.save()
            serializer = OrderDetailSerializer(order)
            return Response(serializer.data)
        return Response(
            {'error': 'Order cannot be cancelled'},
            status=status.HTTP_400_BAD_REQUEST
        )

class ShippingMethodViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ShippingMethod.objects.filter(is_active=True)
    serializer_class = ShippingMethodSerializer