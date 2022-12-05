from api.v1.organization.serializers import OrganizationSerializer
from rest_framework import status, generics, permissions
from rest_framework.response import Response
from api.v1.users.permissions import IsAdmin, IsSourcingDirector
from api.v1.users.serializers import (
    LogoutSerializer,
    UserSerializer,
    UserRegisterSerializer,
    UserUpdateSerializer,
    CustomTokenObtainPairSerializer
)
from rest_framework.reverse import reverse
from django.core.exceptions import ValidationError
from api.v1.users.models import User
from rest_framework.views import APIView
from django.contrib.auth.hashers import make_password
from rest_framework.views import APIView
from django.db import transaction
from api.v1.users.services import make_errors
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.sites.shortcuts import get_current_site
import jwt
from django.conf import settings
from api.v1.users.utils import Utils, send_message_register
from rest_framework_simplejwt.views import TokenObtainPairView
from api.v1.commons.pagination import CustomLimitPagination, make_pagination
from django.db.models import Q
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken


class CustomTokenObtainPairView(TokenObtainPairView):
    # Replace the serializer with your custom
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        email = User.objects.get(email=request.data.get('email'))
        serializer.validated_data['role'] = email.role
        return Response(serializer.validated_data)

class CreateSourcDirectorOriganizationAPI(APIView):
    permission_classes = (permissions.IsAuthenticated, IsAdmin)

    def post(self, request, format=None):
        data = request.data
        organization = data.get('organization')
        sourcingDirector = data.get('sourcingDirector')
        
        try:
            with transaction.atomic():
                organization_serializer = OrganizationSerializer(data=organization)
                if not organization_serializer.is_valid():
                    raise ValidationError(make_errors(organization_serializer.errors))
                organization_serializer.save()
                user_data = {
                    'first_name':sourcingDirector.get('first_name'),
                    'email':sourcingDirector.get('email'),
                    'role':'sourcing_director',
                    'phone':sourcingDirector.get('phone'),
                    'organization':organization_serializer.data.get('id'),
                    'organization_name':organization_serializer.data.get('name'),
                    'password':sourcingDirector.get('password'),
                    'password2':sourcingDirector.get('password2'),
                }
                register_serializer = UserRegisterSerializer(data=user_data)
                if not register_serializer.is_valid():
                    raise ValidationError(make_errors(register_serializer.errors))
                register_serializer.save()
                
                # Sending message to the given email
                user = User.objects.get(email=register_serializer.data.get('email'))
                token = RefreshToken.for_user(user).access_token
                current_site = get_current_site(request).domain
                relative_link = reverse('email-verify')
                if settings.DEBUG:
                    absurl = 'http://'+current_site+relative_link+'?token='+str(token)
                else:
                    absurl = 'https://'+current_site+relative_link+'?token='+str(token)
                Utils.send_email(user_data, absurl)
        except ValidationError as e:
            return Response(
                {
                    "success": False,
                    "message": 'Error occured.',
                    "error": str(e),
                    # "org_error": make_errors(organization_serializer.errors),
                    "data": [],
                },status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            {
                "success": True,
                "message": 'Successfuly created sourcing director and organizaton.',
                "error": [],
                "data": {
                    'organization':organization_serializer.data,
                    'sourcing_director':register_serializer.data,
                },
            }, status=status.HTTP_201_CREATED
        )


class EmailVerify(APIView):
    def post(self, request):
        try:
            token = self.request.query_params.get('token')
            # token = request.GET.get('token')
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user = User.objects.get(id=payload['user_id'])
            user.is_varified = True
            user.save()
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": 'Error occurred.',
                    "error": str(e),
                    "data": [],
                    'token': token
                }, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            {
                "success": True,
                "message": 'User verified successfully.',
                "error": [],
                "data": UserSerializer(user).data,
                'token': token
            }, status=status.HTTP_200_OK
        )


class UserRegistrationView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated, IsSourcingDirector | IsAdmin)
    serializer_class = UserRegisterSerializer
    queryset = User.objects.all()

    def post(self, request):
        data = request.data
        data['organization'] = self.request.user.organization.id
        serializer = self.serializer_class(data=data)
        user_data = {
            'first_name': data.get('first_name'),
            'email': data.get('email'),
            'role': data.get('role'),
            'organization': self.request.user.organization.id,
            'organization_name': self.request.user.organization.name,
            'password': data.get('password'),
        }
        if not serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "message": 'Error occurred.',
                    "error": make_errors(serializer.errors),
                    "data": [],
                }, status=status.HTTP_400_BAD_REQUEST
            )
        serializer.save()
        send_message_register(request, user_data)
        return Response(
            {
                "success": True,
                "message": 'User created successfully.',
                "error": [],
                "data": serializer.data,
            }, status=status.HTTP_201_CREATED
        )
        

class LogoutAPIView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = LogoutSerializer

    def post(self, request):
        try:
            serializer = self.serializer_class(data=self.request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": 'User logged out successfully.',
                    "error": [],
                    "data": [],
                }, status=status.HTTP_205_RESET_CONTENT
            )
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": 'Error occurred.',
                    "error": str(e),
                    "data": [],
                }, status=status.HTTP_400_BAD_REQUEST
            )


class DetailUserViews(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = User.objects.all()
    serializer_class = UserUpdateSerializer

    def get(self, request, pk):
        try:
            return Response(
                {
                    "success": True,
                    "message": 'Successfully got user.',
                    "error": [],
                    "data": self.retrieve(request).data,
                }, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": 'Error occured.',
                    "error": str(e),
                    "data": [],
                }, status=status.HTTP_400_BAD_REQUEST
            )

    def patch(self, request, pk):
        try:
            return Response(
                {
                    "success": True,
                    "message": 'Successfully updated.',
                    "error": [],
                    "data": self.partial_update(request).data,
                }, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": 'Error occurred.',
                    "error": str(e),
                    "data": [],
                }, status=status.HTTP_400_BAD_REQUEST
            )

    def delete(self, request, pk):
        try:
            self.destroy(request)
            return Response(
                {
                    "success": True,
                    "message": 'Successfully deleted.',
                    "error": [],
                    "data": [],
                }, status=status.HTTP_204_NO_CONTENT
            )
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": 'Error occurred.',
                    "error": str(e),
                    "data": [],
                }, status=status.HTTP_400_BAD_REQUEST
            )


class UserDetailByAccessToken(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        try:
            serializer = UserUpdateSerializer(self.request.user)
            return Response(
                {
                    "success": True,
                    "message": 'Me, is this really me? 🤗',
                    "error": [],
                    "data": serializer.data,
                }, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": 'Error occurred.',
                    "error": str(e),
                    "data": [],
                }, status=status.HTTP_400_BAD_REQUEST
            )


class UserListView(APIView):
    permission_classes = (permissions.IsAuthenticated,)  # for authentication
    pagination_class = CustomLimitPagination

    def get_queryset(self):
        params = self.request.query_params
        q = params.get('q')
        role = params.get('role')
        b_role = self.request.data.get('role')
        users = User.objects.select_related('organization',).filter(organization_id=self.request.user.organization.id)\
            .order_by('-id')
        if q:
            users = users.filter(
                Q(email__icontains=q) | Q(phone__icontains=q) | Q(first_name__icontains=q) | Q(last_name__icontains=q) |
                Q(street__icontains=q) | Q(city__icontains=q) | Q(country__icontains=q) | Q(role__icontains=q)
            )
        if role:
            users = users.filter(role__in=role.split(','))
        if b_role and isinstance(b_role, list):
            users = users.filter(role__in=b_role)
        return users

    def get(self, request):
        try:
            users = self.get_queryset()
            serializer = UserUpdateSerializer
            return Response(
                make_pagination(request, serializer, users),
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": 'Error occurred.',
                    "error": str(e),
                    "data": [],
                }, status=status.HTTP_400_BAD_REQUEST
            )
    


# class UserDetailListView(APIView):
#     permission_classes = (permissions.IsAuthenticated,)

#     def get(self, request, id):
#         queryset = User.objects.get(id=id)
#         # queryset = User.objects.filter(organization = request.user).get(id=id)
#         serializer = UserSerializer(queryset)
#         return Response(serializer.data, status=status.HTTP_200_OK)

#     def put(self, request, id):
#         queryset = User.objects.get(id=id)
#         # queryset = User.objects.filter(organization = request.user).get(id=id)
#         serializer = UserSerializer(queryset, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def delete(self, request, id):
#         queryset = User.objects.filter(organization = request.user).get(id=id)
#         queryset.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)
