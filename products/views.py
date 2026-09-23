from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .kafka_producer import publish_stock_updated
from .models import Product
from .pagination import DefaultLimitOffsetPagination
from .serializers import ProductSerializer, ProductUpdateSerializer, StockUpdateSerializer

ALLOWED_ORDERING_FIELDS = ['created_at', 'updated_at', 'name', 'price', 'stock_quantity']


class ProductViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultLimitOffsetPagination
    serializer_class = ProductSerializer

    def get_queryset(self):
        qs = Product.objects.all()
        if self.action == 'list':
            qs = qs.filter(status=Product.Status.ACTIVE)
        ordering = self.request.query_params.get('ordering')
        if ordering:
            field = ordering.lstrip('-')
            if field in ALLOWED_ORDERING_FIELDS:
                qs = qs.order_by(ordering)
        return qs

    def get_serializer_class(self):
        if self.action in ('update', 'partial_update'):
            return ProductUpdateSerializer
        return ProductSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(ProductSerializer(instance).data)

    @action(detail=True, methods=['patch'], url_path='stock')
    def stock(self, request, pk=None):
        product = self.get_object()
        serializer = StockUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        previous_quantity = product.stock_quantity
        if 'quantity' in data:
            new_quantity = data['quantity']
        else:
            new_quantity = previous_quantity + data['delta']

        if new_quantity < 0:
            raise ValidationError({'detail': 'Stock quantity cannot be negative.'})

        product.stock_quantity = new_quantity
        product.save(update_fields=['stock_quantity', 'updated_at'])

        publish_stock_updated(
            product_id=product.id,
            previous_quantity=previous_quantity,
            new_quantity=new_quantity,
            timestamp=timezone.now().isoformat(),
        )

        return Response(ProductSerializer(product).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'], url_path='deactivate')
    def deactivate(self, request, pk=None):
        product = self.get_object()
        if product.status == Product.Status.INACTIVE:
            raise ValidationError({'detail': 'Product is already inactive.'})
        product.status = Product.Status.INACTIVE
        product.save(update_fields=['status', 'updated_at'])
        return Response(ProductSerializer(product).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'], url_path='activate')
    def activate(self, request, pk=None):
        product = self.get_object()
        if product.status == Product.Status.ACTIVE:
            raise ValidationError({'detail': 'Product is already active.'})
        product.status = Product.Status.ACTIVE
        product.save(update_fields=['status', 'updated_at'])
        return Response(ProductSerializer(product).data, status=status.HTTP_200_OK)
