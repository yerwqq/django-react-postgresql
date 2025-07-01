from django.contrib.auth import authenticate
from rest_framework.views import APIView, Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import *
from .exceptions import *
from .responses import SuccessResponse, ErrorResponse


class AuthenticateView(APIView):
    permission_classes = [IsAuthenticated]


class LoginView(APIView):
    """
    Авторизация пользователя
    """

    permission_classes = [AllowAny]

    @swagger_auto_schema(
    security=[],
    request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "email": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Почта пользователя'
                ),
                "password": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Пароль пользователя'
                )
            },
            description="Авторизация.",
        ),
        responses = {
            "200": openapi.Response(
                description="Успешный вход в систему",
                examples={
                    "application/json": {
                        "status": 200,
                        "data": "token"
                    }
                }
            ),
            "400": openapi.Response(
                description='Ошибка валидации данных',
                examples={
                    'application/json': {
                        'status': status.HTTP_400_BAD_REQUEST,
                        'error': 'Username and password are required.'
                    }
                }
            ),
            "404": openapi.Response(
                description='Неверный логин или пароль',
                examples={
                    'application/json': {
                        'status': status.HTTP_404_NOT_FOUND,
                        'error': "Email or password are incorrect!"
                    }
                }
            )
        }
    )
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            username = serializer.validated_data['email']
            password = serializer.validated_data['password']

            user = authenticate(username=username, password=password)

            if user:
                refresh = RefreshToken.for_user(user)
                return SuccessResponse({
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                })
            else:
                return ErrorResponse('Email or password are incorrect.', status=status.HTTP_401_UNAUTHORIZED)


class RegisterView(APIView):
    """
    Регистрация пользователя
    """

    permission_classes = [AllowAny]

    @swagger_auto_schema(
    security=[],
    request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "fio": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='ФИО Клиента'
                ),
                "email": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Почта пользователя'
                ),
                "password": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Пароль пользователя'
                )
            },
            description="Авторизация.",
        ), 
        responses = {
            "201": openapi.Response(
                description="Пользователь успешно зарегистрирован",
                examples={
                    "application/json": {
                        "status": status.HTTP_201_CREATED,
                        "detail": "User successfully registered, please, log in"
                    }
                }
            ),
            "400": openapi.Response(
                description='Ошибка валидации данных или email уже используется',
                examples={
                    "application/json": {
                        "status": status.HTTP_400_BAD_REQUEST,
                        "error": "Email already used, try another one."
                    }
                }
            ),
            "500": openapi.Response(
                description='Внутренняя ошибка сервера',
                examples={
                    "application/json": {
                        "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
                        "error": "Some internal server error message"
                    }
                }
            )
        }
    )
    def post(self, request):
        serializer = UserRegSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save(serializer.validated_data)
            return Response({'status': status.HTTP_200_OK, 'detail': "User successfully registered, please, log in"}, status=status.HTTP_201_CREATED)
        except EmailAlreadyUsed as e:
            return ErrorResponse(e.detail, status=status.HTTP_400_BAD_REQUEST)
        except serializers.ValidationError as e:
            return ErrorResponse(e.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return ErrorResponse(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProfileView(AuthenticateView):
    """
    Профиль пользователя и действия с ним
    """

    @swagger_auto_schema(
        security=[{'Auth': []}],
        responses = {
            "200": openapi.Response(
                description="Получение данных о профиле",
                examples={
                    "application/json": {
                        "status": 200,
                        "data": {
                            "user": {
                                "id": 1,
                                "username": "hello@email.com"
                            },
                            "fio": "Иванов Иван Иванович",
                            "email": "hello@email.com",
                            "phone": "+79008001020",
                        }
                    }
                }
            ),
            "404": openapi.Response(
                description="Профиль не найден",
                examples={
                    "application/json": {
                        "error": "Profile not found."
                    }
                }
            )
        }
    )
    def get(self, request):
        try:
            profile = Profile.objects.get(user=request.user)
            serializer = UserProfileSerializer(profile)
            return Response({"status": status.HTTP_200_OK, "data": serializer.data}, status=status.HTTP_200_OK)
        except Profile.DoesNotExist:
            return Response({"error": "Profile not found."}, status=404)
    
    @swagger_auto_schema(
        security=[{'Auth': []}],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'fio': openapi.Schema(type=openapi.TYPE_STRING, description='ФИО пользователя'),
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email пользователя'),
                'phone': openapi.Schema(type=openapi.TYPE_STRING, description='Телефон пользователя'),
            },
            required=[]
        ),
        responses={
            "200": openapi.Response(
                description="Получение данных о профиле",
                examples={
                    "application/json": {
                        "status": 200,
                        "data": {
                            "user": {
                                "id": 7,
                                "username": "hello@guys.com"
                            },
                            "fio": "Иванов Иван Иванович",
                            "email": "hello@guys.com",
                            "phone": "+",
                        }
                    }
                }
            ),
            "404": openapi.Response(
                description="Профиль не найден",
                examples={
                    "application/json": {
                        "error": "Profile not found."
                    }
                }
            )
        }
    )
    def patch(self, request):
        try:
            profile = Profile.objects.get(user=request.user)
            serializer = UserProfileSerializer(profile, data=request.data, partial=True)
            
            if serializer.is_valid(raise_exception=True):
                if 'email' in serializer.validated_data:
                    return ErrorResponse("User cant edit email field. Ask admins", status=status.HTTP_403_FORBIDDEN)
                serializer.save()
                return SuccessResponse(serializer.data)
        except Profile.DoesNotExist:
            return ErrorResponse('Profile not found.', status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return ErrorResponse(str(e), status=status.HTTP_400_BAD_REQUEST)


class UserView(AuthenticateView):
    """
    Аккаунты пользователей, смена паролей, почт.
    """

    @swagger_auto_schema(
        security=[{'Auth': []}],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'current_password': openapi.Schema(type=openapi.TYPE_STRING, description='Текущий пароль пользователя'),
                'new_password': openapi.Schema(type=openapi.TYPE_STRING, description='Новый пароль пользователя'),
                'confirm_password': openapi.Schema(type=openapi.TYPE_STRING, description='Подтверждение нового пароля'),
            },
            required=['current_password', 'new_password', 'confirm_password']
        ),
        responses={
            "200": openapi.Response(
                description="Пароль успешно изменен",
                examples={
                    "application/json": {
                        "status": 200,
                        "detail": "Password changed successfully."
                    }
                }
            ),
            "400": openapi.Response(
                description="Ошибка при изменении пароля",
                examples={
                    "application/json": {
                        "status": 400,
                        "error": "Current password is incorrect."
                    },
                    "application/json; error_type=password_mismatch": {
                        "status": 400,
                        "error": "New password didn't match with confirm password."
                    },
                    "application/json; error_type=same_password": {
                        "status": 400,
                        "error": "New password should not be the same as current password."
                    }
                }
            )
        }
    )
    def patch(self, request):
        try:
            serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return SuccessResponse('Password changed successfully.', status=status.HTTP_200_OK)
        except ValidationError as e:
            error_messages = []
            if 'non_field_errors' in e.detail:
                error_messages.extend(e.detail['non_field_errors'])
            for field, messages in e.detail.items():
                if field != 'non_field_errors':
                    error_messages.extend(messages)
            error_message_str = ', '.join(str(msg) for msg in error_messages)
            return ErrorResponse(error_message_str, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(AuthenticateView):
    """
    Выход из аккаунта
    """

    @swagger_auto_schema(
        security=[{'Auth': []}],
        operation_description="Выход из аккаунта",
        responses={
            200: openapi.Response(
                description="Успешный выход",
                examples={
                    'application/json': {
                        'status': status.HTTP_200_OK,
                        'description': 'Вы успешно вышли из системы'
                    }
                }
            ),
            401: openapi.Response(
                description="Неавторизованный доступ"
            )
        },
    )
    def get(self, request):
        token = Token.objects.get(user=request.user)
        token.delete()
        return SuccessResponse('Вы успешно вышли из системы', status=status.HTTP_200_OK)