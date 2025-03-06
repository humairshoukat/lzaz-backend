import os
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from app.permissions import IsAuth, IsAdmin
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from app.models import User
from .serializers import (AddUserSerializer, LoginSerializer, UserSerializer, ResetPasswordSerializer,
                          PaginationSerializer)
from app.helpers import save_file_to_blob, delete_file_from_blob, generate_random_string, send_email


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    req_ser = LoginSerializer(data=request.data)
    if not req_ser.is_valid():
        return Response({
            "status": 'error',
            "message": req_ser.errors,
            "code": status.HTTP_400_BAD_REQUEST
        }, status=status.HTTP_400_BAD_REQUEST)

    login_data = req_ser.validated_data
    username = login_data['email']
    password = login_data['password']

    try:
        user = authenticate(username=username, password=password)
        if not user:
            raise User.DoesNotExist

        if user.account_access:
            refresh = RefreshToken.for_user(user)
            serializer = UserSerializer(user)
            return Response({
                'status': 'success',
                'message': 'Login successful',
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": serializer.data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "status": 'error',
                "message": "Your login has been disabled by Admin",
                "code": status.HTTP_400_BAD_REQUEST
            }, status=status.HTTP_400_BAD_REQUEST)

    except User.DoesNotExist:
        return Response({
            "status": 'error',
            "message": "Invalid login credentials",
            "code": status.HTTP_400_BAD_REQUEST
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_users(request):
    req_ser = PaginationSerializer(data=request.GET)
    if not req_ser.is_valid():
        return Response({
            'status': 'error',
            'message': req_ser.errors,
            'code': status.HTTP_400_BAD_REQUEST
        }, status=status.HTTP_400_BAD_REQUEST)

    search = req_ser.validated_data.get('search', None)
    page = req_ser.validated_data.get('page', 1)
    limit = req_ser.validated_data.get('limit', 10)
    start = 0
    end = limit
    if page > 1:
        start = (page - 1) * limit
        end = start + limit

    filters = Q(deleted_at=None)
    if search:
        search_filters = Q(name__icontains=search) | Q(email__icontains=search) | Q(role__icontains=search)
        filters &= search_filters

    users = User.objects.filter(filters)[start:end]
    count = User.objects.filter(filters).count()

    total_pages = (count + limit - 1) // limit  # Calculate total pages
    next_page = page + 1 if end < count else None
    prev_page = page - 1 if page > 1 else None

    serializer = UserSerializer(users, many=True)
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
@permission_classes([IsAdmin])
def add_user(request):
    req_ser = AddUserSerializer(data=request.data)
    if not req_ser.is_valid():
        return Response({
            "status": 'error',
            "message": req_ser.errors,
            "code": status.HTTP_400_BAD_REQUEST
        }, status=status.HTTP_400_BAD_REQUEST)

    signup_data = req_ser.data
    name = signup_data['name']
    email = signup_data['email']
    role = signup_data['role']
    password = signup_data['password']
    picture = signup_data['picture'] if 'picture' in signup_data else None
    picture_url = None
    if picture:
        picture_url = save_file_to_blob(picture)
    already_exists = User.objects.filter(email=email).exists()
    if already_exists:
        return Response({
            'status': 'error',
            'message': 'Email already registered',
            'code': status.HTTP_400_BAD_REQUEST
        }, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(
        name=name,
        email=email,
        username=email,
        role=role,
        profile_picture=picture_url,
        hash=generate_random_string(),
        secret=generate_random_string(),
    )

    user.set_password(password)
    user.save()
    serializer = UserSerializer(user)
    return Response({
        'status': 'success',
        'data': serializer.data
    }, status=status.HTTP_201_CREATED)


@api_view(['PATCH'])
@permission_classes([IsAuth])
def update_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)

        # Check if a new profile picture is provided in the request data
        new_profile_picture = request.data.get('profile_picture', None)

        if new_profile_picture:
            same_picture = False
            # Delete the old profile picture from blob
            if user.profile_picture:
                prev_picture_name = user.profile_picture.split('/')[-1]
                new_picture_name = new_profile_picture.name
                if prev_picture_name != new_picture_name:
                    delete_file_from_blob(user.profile_picture)
                else:
                    same_picture = True

            if not same_picture:
                # Save the new profile picture to S3
                profile_picture_url = save_file_to_blob(new_profile_picture)
                request.data['profile_picture'] = profile_picture_url
            else:
                request.data['profile_picture'] = user.profile_picture

        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'status': 'success',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                "status": "error",
                "message": serializer.errors,
                "code": status.HTTP_400_BAD_REQUEST
            }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print("Exception at updating user: ", str(e))
        return Response({
            "status": 'error',
            "message": 'Error updating user',
            "code": 400
        }, status=400)


@api_view(['DELETE'])
@permission_classes([IsAdmin])
def delete_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        user.delete()
        return Response({
            'status': 'success',
            'message': 'User deleted',
            'code': status.HTTP_200_OK
        }, status=status.HTTP_200_OK)

    except Exception as e:
        print("Exception at deleting user: ", str(e))
        return Response({
            "status": 'error',
            "message": 'Error deleting user',
            "code": 400
        }, status=400)


@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password(request):
    try:
        # Check if email is provided in the request data
        email = request.data.get('email', None)
        if email is None:
            return Response({
                "status": "error",
                "message": "Email is required",
                "code": status.HTTP_400_BAD_REQUEST
            }, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(email=email).first()
        if not user:
            return Response({
                'status': 'error',
                'message': 'Invalid Email',
                'code': status.HTTP_400_BAD_REQUEST
            }, status=status.HTTP_400_BAD_REQUEST)

        user.forgot_password = True
        user.save()
        app_url = os.getenv('APP_URL')
        url_link = f"{app_url}reset-password/?hash={user.hash}&secret={user.secret}"
        subject = 'Lzaz PIM - Please reset your password'
        message = (
            f'Hello,\n\n'
            f'Please rest your password using below link: \n\n'
            f'{url_link}\n\n'
            'Thank you,\n'
            'Lzaz PIM'
        )
        email_sent = send_email(subject, message, [user.email])
        if not email_sent:
            return Response({
                'status': 'error',
                'message': 'Error sending reset password email',
                'code': status.HTTP_400_BAD_REQUEST
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "status": "success",
            "message": "Password reset email sent successfully",
            "code": status.HTTP_200_OK
        }, status=status.HTTP_200_OK)

    except Exception as e:
        print('Error at forgot password api: ', str(e))
        return Response({
            "status": "error",
            "message": str(e),
            "code": status.HTTP_400_BAD_REQUEST
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH'])
@permission_classes([AllowAny])
def reset_password(request):
    try:
        serializer = ResetPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "status": "error",
                "message": serializer.errors,
                "code": status.HTTP_400_BAD_REQUEST
            }, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.data
        new_password = data['password']
        hash_code = data['hash']
        secret = data['secret']

        user = User.objects.filter(hash=hash_code, secret=secret).first()
        if not user:
            print("Error: Invalid hash & secret to reset user password")
            return Response({
                "status": "error",
                "message": "Error re-setting password.",
                "code": status.HTTP_400_BAD_REQUEST
            }, status=status.HTTP_400_BAD_REQUEST)

        if not user.forgot_password:
            return Response({
                "status": "error",
                "message": "This link has been expired.",
                "code": status.HTTP_400_BAD_REQUEST
            }, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.forgot_password = False
        user.save()
        subject = 'Lzaz PIM - Your password has been reset'
        message = (
            f'Hello,\n\n'
            f'This email is intended to let you know that your password has been reset. \n\n'
            'Thank you,\n'
            'Lzaz PIM Inc'
        )
        email_sent = send_email(subject, message, [user.email])
        if not email_sent:
            print('Error sending password reset confirmation email')

        return Response({
            'status': 'success',
            'message': 'Password reset successfully'
        })

    except Exception as e:
        return Response({
            "status": "error",
            "message": str(e),
            "code": status.HTTP_400_BAD_REQUEST
        }, status=status.HTTP_400_BAD_REQUEST)
