from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, generics
from rest_framework.decorators import api_view
from rest_framework.response import Response

from service.models import Chat
from service.serializers import ChatSerializers


@api_view(["GET"])
def health_check(request):
    return Response({"status": "Ok"}, status.HTTP_200_OK)


class ChatRetrieve(generics.RetrieveUpdateDestroyAPIView):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializers


class ChatList(generics.ListCreateAPIView):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializers
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['title', 'telegram_id', 'group_number']


def week(requests):
    return render(requests, 'week.html')
