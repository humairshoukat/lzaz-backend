from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from app.permissions import IsAuth, IsAdmin
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from app.models import Product, ProductFamily, ProductFamilyAttribute
from .serializers import ProductSerializer, AddProductSerializer, PaginationSerializer, AddMultipleProductSerializer
from app.helpers import save_file_to_blob, delete_file_from_blob


@api_view(['GET'])
@permission_classes([IsAuth])
def get_products(request):
    req_ser = PaginationSerializer(data=request.GET)
    if not req_ser.is_valid():
        return Response({
            'status': 'error',
            'message': req_ser.errors,
            'code': status.HTTP_400_BAD_REQUEST
        }, status=status.HTTP_400_BAD_REQUEST)

    search = req_ser.validated_data.get('search', None)
    archived = req_ser.validated_data.get('archived', None)
    published = req_ser.validated_data.get('published', None)
    page = req_ser.validated_data.get('page', 1)
    limit = req_ser.validated_data.get('limit', 10)
    start = 0
    end = limit
    if page > 1:
        start = (page - 1) * limit
        end = start + limit

    filters = Q(deleted_at=None)

    if search:
        search_filters = Q(name__icontains=search)
        filters &= search_filters

    if archived:
        archived_filters = Q(is_archived=True) & Q(is_published=False)
        filters &= archived_filters

    if published:
        published_filters = Q(is_published=True)
        filters &= published_filters

    products = Product.objects.filter(filters)[start:end]
    count = Product.objects.filter(filters).count()

    total_pages = (count + limit - 1) // limit  # Calculate total pages
    next_page = page + 1 if end < count else None
    prev_page = page - 1 if page > 1 else None

    serializer = ProductSerializer(products, many=True)
    return Response({
        'status': 'success',
        'data': serializer.data,
        'meta': {
            'pagination': {
                'page': page,
                'limit': limit,
                'total_pages': total_pages,
                'prev_page': prev_page,
                'next_page': next_page
            }
        }
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuth])
def create_product(request):
    serializer = AddProductSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({
            'status': 'error',
            'message': serializer.errors,
            'code': 400
        }, status=400)

    data = serializer.validated_data
    sku = data.get('sku')
    already_exists = Product.objects.filter(sku=sku).exists()
    if already_exists:
        return Response({
            'status': 'error',
            'message': f'Product with sku {sku} already exist',
            'code': status.HTTP_400_BAD_REQUEST
        }, status=status.HTTP_400_BAD_REQUEST)

    name = data.get('name')
    description = data.get('description')
    price = data.get('price')
    family = data.get('family', None)
    details = data.get('details', None)
    images = data.get('images', None)
    product_images = []
    if images:
        for image in images:
            image_url = save_file_to_blob(image)
            product_images.append(image_url)
    is_archived = data.get('is_archived')
    is_published = data.get('is_published')

    product = Product.objects.create(
        sku=sku,
        name=name,
        description=description,
        price=price,
        family=family,
        details=details,
        images=product_images,
        is_archived=is_archived,
        is_published=is_published,
    )

    serializer = ProductSerializer(product)
    return Response({
        'status': 'success',
        'data': serializer.data
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def add_multiple_products(request):
    serializer = AddMultipleProductSerializer(data=request.data)
    if serializer.is_valid():
        product_objects = [Product(**data) for data in serializer.validated_data]
        Product.objects.bulk_create(product_objects)  # Efficient bulk insert
        return Response({
            'status': 'success',
            'message': f'{len(product_objects)} products inserted successfully'
        }, status=status.HTTP_201_CREATED)
    else:
        return Response({
            'status': 'error',
            'message': serializer.errors,
            'code': 400
        }, status=400)


@api_view(['PATCH'])
@permission_classes([IsAuth])
def update_product(request, pd_id):
    try:
        product = Product.objects.get(id=pd_id, deleted_at=None)
    except Product.DoesNotExist:
        return Response({
            'status': 'error',
            'message': 'Product not found',
            'code': 404
        }, status=status.HTTP_404_NOT_FOUND)

    serializer = ProductSerializer(product, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({
            'status': 'success',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'status': 'error',
            'message': serializer.errors,
            'code': 400
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuth])
def delete_product(request, pd_id):
    try:
        product = Product.objects.get(id=pd_id, deleted_at=None)
        product.delete()
        return Response({
            'status': 'success',
            'message': 'Product deleted successfully'
        }, status=status.HTTP_200_OK)
    except Product.DoesNotExist:
        return Response({
            'status': 'error',
            'message': 'Product not found',
            'code': 404
        }, status=status.HTTP_404_NOT_FOUND)