from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import Customer


class CustomerRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = Customer
        fields = ('email', 'first_name', 'last_name', 'phone', 
                 'date_of_birth', 'password', 'password_confirm')

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        customer = Customer.objects.create_user(password=password, **validated_data)
        return customer


class CustomerLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            customer = authenticate(
                request=self.context.get('request'),
                username=email,
                password=password
            )
            
            if not customer:
                raise serializers.ValidationError('Invalid email or password')
            
            if not customer.is_active:
                raise serializers.ValidationError('Customer account is disabled')
            
            if customer.is_deleted:
                raise serializers.ValidationError('Customer account has been deleted')
            
            attrs['customer'] = customer
            return attrs
        else:
            raise serializers.ValidationError('Must include email and password')


class CustomerSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = Customer
        fields = ('id', 'email', 'first_name', 'last_name', 'full_name', 
                 'phone', 'date_of_birth', 'is_active', 'created_at', 'updated_at')
        read_only_fields = ('id', 'is_active', 'created_at', 'updated_at')


class CustomerUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ('first_name', 'last_name', 'phone', 'date_of_birth')

    def update(self, instance, validated_data):
        # Set updated_by if available in context
        if 'request' in self.context:
            instance.updated_by = self.context['request'].user
        return super().update(instance, validated_data)