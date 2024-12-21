

from rest_framework import serializers
from .models import Ingredient, Recipe

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'

class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = '__all__'


class ChatbotQuerySerializer(serializers.Serializer):
    
    preference = serializers.CharField(max_length=200, required=False)
    available_ingredients = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=False
    )
    
    
    message = serializers.CharField(
        max_length=1000,
        required=False,
        help_text="Free-form message containing preferences and available ingredients."
    )
    
    def validate(self, data):
        """
        Ensure that either:
        - 'message' is provided, or
        - Both 'preference' and 'available_ingredients' are provided.
        """
        if not data.get('message') and not (data.get('preference') and data.get('available_ingredients')):
            raise serializers.ValidationError("Either 'message' or both 'preference' and 'available_ingredients' must be provided.")
        return data
