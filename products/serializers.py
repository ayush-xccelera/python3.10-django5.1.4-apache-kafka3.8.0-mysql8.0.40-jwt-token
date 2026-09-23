from decimal import Decimal

from rest_framework import serializers

from .models import Product, StockHistory


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'description',
            'price',
            'stock_quantity',
            'status',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'status', 'created_at', 'updated_at']

    def validate_price(self, value):
        if value <= Decimal('0'):
            raise serializers.ValidationError('Price must be greater than 0.')
        return value

    def validate_stock_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError('Stock quantity cannot be negative.')
        return value


class ProductUpdateSerializer(serializers.ModelSerializer):
    """Used for PUT /products/{id} - only name, description, price editable."""

    class Meta:
        model = Product
        fields = ['name', 'description', 'price']

    def validate_price(self, value):
        if value <= Decimal('0'):
            raise serializers.ValidationError('Price must be greater than 0.')
        return value


class StockUpdateSerializer(serializers.Serializer):
    """delta = positive to increase stock, negative to decrease stock."""

    delta = serializers.IntegerField(required=False)
    quantity = serializers.IntegerField(required=False)

    def validate(self, attrs):
        if 'delta' not in attrs and 'quantity' not in attrs:
            raise serializers.ValidationError(
                'Provide either "delta" (relative change) or "quantity" (absolute value).'
            )
        return attrs


class StockHistorySerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = StockHistory
        fields = [
            'id',
            'product',
            'previous_quantity',
            'new_quantity',
            'changed_at',
        ]
        read_only_fields = fields
