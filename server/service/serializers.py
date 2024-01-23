from rest_framework import serializers
from service.models import Chat


class ChatSerializers(serializers.ModelSerializer):

    class Meta:
        model = Chat
        fields = '__all__'

