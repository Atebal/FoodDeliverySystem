from rest_framework import serializers
from accounts.models import Item

class DataSerializer(serializers.ModelSerializer):
    class Meta:
        model=Item
        fields='__all__'