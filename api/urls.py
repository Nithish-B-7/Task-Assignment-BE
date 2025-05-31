from django.urls import path
from .views import CreateUserView, NoteListCreate, NoteDelete
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


urlpatterns = [
    path("register/", CreateUserView.as_view(), name="register"),
    path("notes/", NoteListCreate.as_view(), name="note_list_create"),
    path("notes/<int:pk>/", NoteDelete.as_view(), name="note_delete"),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]