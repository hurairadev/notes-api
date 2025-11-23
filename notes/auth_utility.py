from django.contrib.auth.models import User
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from notes.jwt_utility import decode_token
from notes.models import UserToken


class UserAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            return None

        token = auth_header.split(" ")[1]

        try:
            payload = decode_token(token=token)
            user_id = payload.get("id")
            user = User.objects.get(id=user_id)
            _ = UserToken.objects.get(user=user, token=token)

            return (user, None)
        except Exception as e:
            raise AuthenticationFailed(str(e))
