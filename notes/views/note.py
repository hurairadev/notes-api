from django.db import transaction
from django.core.cache import cache
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from notes.serializers import NoteSerailizer
from notes.models import Note
from notes.auth_utility import UserAuthentication
from notes.permissions import CanUpdateRetrieveDeleteNote


class NoteViewSet(ModelViewSet):
    queryset = Note.objects.all()
    serializer_class = NoteSerailizer
    authentication_classes = [UserAuthentication]
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in [
            "retrieve",
            "update",
            "partial_update",
            "destroy",
        ]:
            return [
                IsAuthenticated(),
                CanUpdateRetrieveDeleteNote(),
            ]

        return super().get_permissions()

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        try:
            data = request.data.copy()
            data["user"] = request.user.id

            with transaction.atomic():
                try:
                    serializer = self.get_serializer(data=data)

                    if serializer.is_valid():
                        note = serializer.save()
                        cache.set(note.id, note, timeout=60 * 60 * 24)
                        return Response(
                            status=status.HTTP_201_CREATED,
                            data={"data": serializer.data},
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

    def retrieve(self, request, *args, **kwargs):
        try:
            pk = kwargs.get("pk")

            note = cache.get(pk)
            if not note:
                note = self.get_object()
                cache.set(pk, note, timeout=60 * 60 * 24)

            serializer = self.get_serializer(note)
            return Response(
                status=status.HTTP_200_OK,
                data={"data": serializer.data},
            )
        except Exception as e:
            return Response(
                data={"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def update(self, request, *args, **kwargs):
        try:
            note = self.get_object()
            data = request.data.copy()
            data["user"] = request.user.id

            with transaction.atomic():
                try:
                    serializer = self.get_serializer(note, data=data)

                    if serializer.is_valid():
                        note = serializer.save()
                        cache.set(note.id, note, timeout=60 * 60 * 24)
                        return Response(
                            status=status.HTTP_200_OK,
                            data={"data": serializer.data},
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

    def partial_update(self, request, *args, **kwargs):
        try:
            note = self.get_object()
            data = request.data.copy()
            data["user"] = request.user.id

            with transaction.atomic():
                try:
                    serializer = self.get_serializer(
                        note, data=request.data, partial=True
                    )

                    if serializer.is_valid():
                        note = serializer.save()
                        cache.set(note.id, note, timeout=60 * 60 * 24)
                        return Response(
                            status=status.HTTP_200_OK,
                            data={"data": serializer.data},
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

    def destroy(self, request, *args, **kwargs):
        try:
            note = self.get_object()

            with transaction.atomic():
                try:
                    note.delete()
                    cache.delete(note.id)
                    return Response(
                        status=status.HTTP_204_NO_CONTENT,
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
