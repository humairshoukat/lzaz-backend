from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from app.permissions import IsAuth, IsAdmin
from rest_framework.response import Response
from rest_framework import status
from app.models import ProductFamily, ProductFamilyAttribute, AttributeGroup
from .serializers import ProductFamilySerializer, AddProductFamilySerializer, AttributeGroupSerializer


@api_view(['GET'])
@permission_classes([IsAuth])
def get_product_families(request):
    search = request.GET.get('search')
    if search:
        families = ProductFamily.objects.filter(name__icontains=search)
    else:
        families = ProductFamily.objects.all()

    serializer = ProductFamilySerializer(families, many=True)
    return Response({
        'status': 'success',
        'data': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuth])
def get_family_attributes(request, pf_id):
    family = ProductFamily.objects.get(id=pf_id)
    if not family:
        return Response({
            'status': 'error',
            'message': 'Product family does not exist',
            'code': 400
        }, status=status.HTTP_400_BAD_REQUEST)

    family_attributes = ProductFamilyAttribute.objects.filter(family=family).values_list('attribute', flat=True)
    attribute_groups = AttributeGroup.objects.filter(id__in=family_attributes, deleted_at=None)
    serializer = AttributeGroupSerializer(attribute_groups, many=True)
    return Response({
        'status': 'success',
        'data': serializer.data
    })


@api_view(['POST'])
@permission_classes([IsAuth])
def add_product_family(request):
    req_ser = AddProductFamilySerializer(data=request.data)
    if not req_ser.is_valid():
        return Response({
            'status': 'error',
            'message': req_ser.errors,
            'code': 400
        }, status=status.HTTP_400_BAD_REQUEST)

    data = req_ser.validated_data
    name = data['name'] if 'name' in data else None
    if not name:
        return Response({
            'status': 'error',
            'message': 'Product family name is required',
            'code': 400
        }, status=status.HTTP_400_BAD_REQUEST)

    exists = ProductFamily.objects.filter(name=name).exists()
    if exists:
        return Response({
            'status': 'error',
            'message': 'Product family already exists',
            'code': 400
        }, status=status.HTTP_400_BAD_REQUEST)

    # Create product family
    family = ProductFamily.objects.create(name=name)
    attributes = data['attributes'] if 'attributes' in data else []
    if attributes:
        for attr in attributes:
            ProductFamilyAttribute.objects.create(family=family, attribute=attr)

    serializer = ProductFamilySerializer(family)
    return Response({
        'status': 'success',
        'data': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['PATCH'])
@permission_classes([IsAuth])
def update_product_family(request, pf_id):
    family = ProductFamily.objects.get(id=pf_id)
    if not family:
        return Response({
            'status': 'error',
            'message': 'Product family does not exist',
            'code': 400
        }, status=status.HTTP_400_BAD_REQUEST)

    req_ser = AddProductFamilySerializer(data=request.data)
    if not req_ser.is_valid():
        return Response({
            'status': 'error',
            'message': req_ser.errors,
            'code': 400
        }, status=status.HTTP_400_BAD_REQUEST)

    data = req_ser.validated_data
    name = data['name'] if 'name' in data else None
    if name:
        family.name = name
        family.save()

    attributes = data['attributes'] if 'attributes' in data else []
    if attributes:
        for attr in attributes:
            family_attr, created = ProductFamilyAttribute.objects.get_or_create(family=family, attribute=attr)

    serializer = ProductFamilySerializer(family)
    return Response({
        'status': 'success',
        'data': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuth])
def delete_product_family(request, pf_id):
    product_family = ProductFamily.objects.get(id=pf_id)
    if product_family:
        product_family.delete()
        return Response({
            'status': 'success',
            'message': 'Product family deleted successfully'
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'status': 'error',
            'message': 'Product family does not exist',
            'code': 400
        }, status=status.HTTP_400_BAD_REQUEST)