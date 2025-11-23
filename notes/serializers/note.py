from rest_framework.serializers import ModelSerializer
from notes.models import Note


class NoteSerailizer(ModelSerializer):
    class Meta:
        model = Note
        fields = "__all__"
