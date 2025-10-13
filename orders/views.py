from rest_framework import generics, permissions
from .models import Order
from .serializers import OrderSerializer


class OrderListCreateView(generics.ListCreateAPIView):
    queryset = Order.active_objects.select_related('customer').prefetch_related('items')
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx.update({'request': self.request})
        return ctx

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        # staff/superuser can see all orders; regular users see their own
        if user.is_authenticated and (user.is_staff or user.is_superuser):
            return qs
        return qs.filter(customer=user)


class OrderDetailView(generics.RetrieveAPIView):
    queryset = Order.active_objects.select_related('customer').prefetch_related('items')
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx.update({'request': self.request})
        return ctx

    def get_object(self):
        # reuse DRF's get_object but ensure permissions: non-staff users can only retrieve their own orders
        obj = super().get_object()
        user = self.request.user
        if not (user.is_staff or user.is_superuser) and obj.customer != user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('You do not have permission to access this order')
        return obj
