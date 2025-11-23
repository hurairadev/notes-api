from django.db import transaction
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny

from notes.serializers import UserRegistrationSerializer
from notes.jwt_utility import encode_token
from notes.models import UserToken
from notes.auth_utility import UserAuthentication
from notes.permissions import IsSuperUser, CanUpdateRetrieveDeleteInfoOfClient


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    authentication_classes = [UserAuthentication]
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ["create", "login"]:
            return [AllowAny()]
        elif self.action in [
            "retrieve",
            "update",
            "partial_update",
            "destroy",
        ]:
            return [
                IsAuthenticated(),
                CanUpdateRetrieveDeleteInfoOfClient(),
            ]
        elif self.action in ["list"]:
            return [
                IsAuthenticated(),
                IsSuperUser(),
            ]

        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                try:
                    serializer = self.get_serializer(data=request.data)

                    if serializer.is_valid():
                        user = serializer.save()
                        token = encode_token({"id": user.id})
                        UserToken.objects.create(user=user, token=token)
                        return Response(
                            status=status.HTTP_201_CREATED,
                            data={
                                "data": serializer.data,
                                "token": token,
                            },
                        )
                    else:
                        return Response(
                            status=status.HTTP_400_BAD_REQUEST,
                            data={"error": serializer.errors},
                        )
                except Exception as e:
                    transaction.set_rollback(True)
                    return Response(
                        data={"error": str(e)},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
        except Exception as e:
            return Response(
                data={"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=False, methods=["post"], url_path="login")
    def login(self, request, *args, **kwargs):
        try:
            username = request.data.get("username")
            password = request.data.get("password")

            user = authenticate(username=username, password=password)

            if not user:
                return Response(
                    status=status.HTTP_401_UNAUTHORIZED,
                    data={"error": "Invalid credentials."},
                )

            token = encode_token({"id": user.id})

            with transaction.atomic():
                UserToken.objects.create(user=user, token=token)
                return Response(
                    status=status.HTTP_200_OK,
                    data={
                        "token": token,
                    },
                )

        except Exception as e:
            return Response(
                data={"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
