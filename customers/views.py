from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import login
from .models import Customer
from .serializers import (
    CustomerRegistrationSerializer, 
    CustomerLoginSerializer, 
    CustomerSerializer,
    CustomerUpdateSerializer
)


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """Register a new customer"""
    serializer = CustomerRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        customer = serializer.save()
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(customer)
        access_token = refresh.access_token
        
        return Response({
            'message': 'Customer registered successfully',
            'customer': CustomerSerializer(customer).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(access_token),
            }
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """Login customer and return JWT tokens"""
    serializer = CustomerLoginSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        customer = serializer.validated_data['customer']
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(customer)
        access_token = refresh.access_token
        
        return Response({
            'message': 'Login successful',
            'customer': CustomerSerializer(customer).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(access_token),
            }
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """Logout customer by blacklisting the refresh token"""
    try:
        refresh_token = request.data.get('refresh_token')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        
        return Response({
            'message': 'Logout successful'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'error': 'Invalid token'
        }, status=status.HTTP_400_BAD_REQUEST)


class CustomerProfileView(generics.RetrieveUpdateAPIView):
    """Get and update customer profile"""
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method == 'PUT' or self.request.method == 'PATCH':
            return CustomerUpdateSerializer
        return CustomerSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_account(request):
    """Soft delete customer account"""
    customer = request.user
    customer.soft_delete(deleted_by=customer)
    
    return Response({
        'message': 'Account deleted successfully'
    }, status=status.HTTP_200_OK)
