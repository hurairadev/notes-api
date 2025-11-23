from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from django.urls import reverse
from notes.models import Note, UserToken
from notes.jwt_utility import encode_token

class NotesAPITest(APITestCase):

    def setUp(self):
        self.user_data = {"username": "testuser", "password": "testpassword", "confirm_password": "testpassword"}
        self.note_data = {"title": "Test Note", "content": "This is a test note."}

    def test_create_user_endpoint(self):
        url = reverse("users-list")
        response = self.client.post(url, self.user_data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertTrue(User.objects.filter(username="testuser").exists())
        user = User.objects.get(username="testuser")
        self.assertTrue(user.check_password("testpassword"))

    def test_get_users_endpoint(self):
        url = reverse("users-list")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 403)
    

    def test_create_note_endpoint(self):
        user = User.objects.create_user(username="apiuser", password="pass123")
        self.note_data["user"] = user.id

        url = reverse("notes-list")
        response = self.client.post(url, self.note_data, format="json")
        self.assertEqual(response.status_code, 403)
        
        token = encode_token({"id": user.id})
        UserToken.objects.create(user=user, token=token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = self.client.post(url, self.note_data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Note.objects.filter(title="Test Note").exists())


