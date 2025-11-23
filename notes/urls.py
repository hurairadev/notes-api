from rest_framework.routers import DefaultRouter
from notes.views import NoteViewSet, UserViewSet

router = DefaultRouter()
router.register(r"notes", NoteViewSet, basename="notes")
router.register(r"users", UserViewSet, basename="users")
urlpatterns = router.urls
