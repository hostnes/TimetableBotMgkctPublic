from django.urls import path

from .views import health_check, ChatList, ChatRetrieve, week

urlpatterns = [
    path('ping/', health_check),

    path('chats/', ChatList.as_view()),
    path('chat/<int:pk>/', ChatRetrieve.as_view()),

    path('week/', week),
]