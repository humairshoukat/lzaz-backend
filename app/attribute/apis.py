from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from app.permissions import IsAuth, IsAdmin
from rest_framework.response import Response
from rest_framework import status
from app.models import AttributeGroup
from .serializers import AttributeGroupSerializer


@api_view(['GET'])
@permission_classes([IsAuth])
def get_attribute_groups(request):
    search = request.GET.get('search')
    if search:
        attribute_groups = AttributeGroup.objects.filter(name__icontains=search)
    else:
        attribute_groups = AttributeGroup.objects.all()

    serializer = AttributeGroupSerializer(attribute_groups, many=True)
    return Response({
        'status': 'success',
        'data': serializer.data,
    }, status=200)


@api_view(['POST'])
@permission_classes([IsAuth])
def create_attribute_group(request):
    serializer = AttributeGroupSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            'status': 'success',
            'data': serializer.data,
        }, status=201)
    else:
        return Response({
            'status': 'error',
            'message': serializer.errors,
            'code': 400
        }, status=400)


@api_view(['PATCH'])
@permission_classes([IsAuth])
def update_attribute_group(request, ag_id):
    attribute_group = AttributeGroup.objects.get(id=ag_id)
    serializer = AttributeGroupSerializer(attribute_group, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            'status': 'success',
            'data': serializer.data,
        }, status=200)
    else:
        return Response({
            'status': 'error',
            'message': serializer.errors,
            'code': 400
        }, status=400)


@api_view(['DELETE'])
@permission_classes([IsAuth])
def delete_attribute_group(request, ag_id):
    attribute_group = AttributeGroup.objects.get(id=ag_id)
    attribute_group.delete()
    return Response({
        'status': 'success',
        'message': 'Attribute group deleted successfully',
    }, status=200)
