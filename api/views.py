from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import generics
from .serializers import UserSerializer, NoteSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.serializers import ModelSerializer
from .models import Note
import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import os


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class NoteListCreate(generics.ListCreateAPIView):
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Note.objects.filter(author=user)

    def perform_create(self, serializer):
        if serializer.is_valid():
            serializer.save(author=self.request.user)
        else:
            print(serializer.errors)


class NoteDelete(generics.DestroyAPIView):
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Note.objects.filter(author=user)


@api_view(["POST"])
def chat_with_ai(request):
    user_message = request.data.get("message")
    messages = request.data.get("messages", [])

    if not user_message:
        return Response({"error": "Message is required"}, status=status.HTTP_400_BAD_REQUEST)

    messages.append({"role": "user", "content": user_message})

    groq_api_url = "https://api.groq.com/openai/v1/chat/completions"
    groq_api_key = os.getenv("GROQ_API_KEY")

    try:
        groq_response = requests.post(
            groq_api_url,
            headers={
                "Authorization": f"Bearer {groq_api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama3-8b-8192",
                "messages": messages
            }
        )
        groq_response.raise_for_status()
        ai_message = groq_response.json()["choices"][0]["message"]
        return Response({"reply": ai_message, "messages": messages + [ai_message]})
    except requests.exceptions.RequestException as e:
        return Response({"error": str(e)}, status=500)