# payments/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import stripe
from .models import Payment, PaymentMethod
from .serializers import PaymentSerializer, PaymentCreateSerializer, PaymentMethodSerializer
from orders.models import Order

class PaymentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(order__user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return PaymentCreateSerializer
        return PaymentSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        order = serializer.validated_data['order']
        
        # Verify order belongs to user
        if order.user != request.user:
            return Response(
                {'error': 'Order not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )

        # Create payment
        payment = serializer.save()

        # Process payment based on method
        if payment.payment_method == 'stripe':
            # Implement Stripe payment logic
            try:
                # This is a simplified example
                intent = stripe.PaymentIntent.create(
                    amount=int(payment.amount * 100),  # Convert to cents
                    currency=payment.currency,
                    metadata={'order_id': order.id}
                )
                payment.stripe_payment_intent_id = intent.id
                payment.save()
                
                return Response({
                    'client_secret': intent.client_secret,
                    'payment': PaymentSerializer(payment).data
                })
            except stripe.error.StripeError as e:
                payment.status = 'failed'
                payment.save()
                return Response(
                    {'error': str(e)}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        payment = self.get_object()
        
        if payment.payment_method == 'stripe':
            try:
                intent = stripe.PaymentIntent.retrieve(payment.stripe_payment_intent_id)
                if intent.status == 'succeeded':
                    payment.status = 'completed'
                    payment.save()
                    
                    # Update order status
                    payment.order.status = 'processing'
                    payment.order.save()
                    
                    serializer = PaymentSerializer(payment)
                    return Response(serializer.data)
                
                return Response(
                    {'error': 'Payment not completed'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            except stripe.error.StripeError as e:
                return Response(
                    {'error': str(e)}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

class PaymentMethodViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PaymentMethod.objects.filter(is_active=True)
    serializer_class = PaymentMethodSerializer