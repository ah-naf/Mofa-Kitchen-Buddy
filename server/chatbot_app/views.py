

import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.conf import settings

from .models import Ingredient, Recipe
from .serializers import (
    IngredientSerializer,
    RecipeSerializer,
    ChatbotQuerySerializer
)
from .utils import parse_recipe_image, parse_unstructured_text, parse_user_message
from transformers import pipeline
import torch
import json
import logging

logger = logging.getLogger(__name__)

LLM_API_KEY = os.getenv('LLM_API_KEY')


class ChatbotService:
    """
    Service class to handle chatbot interactions using Hugging Face Transformers.
    """
    def __init__(self):        
        self.model = pipeline(
            'text2text-generation',
            model='google/flan-t5-small',
            tokenizer='google/flan-t5-small',
            device=0 if torch.cuda.is_available() else -1,
            use_auth_token=LLM_API_KEY if LLM_API_KEY else None
        )
    
    def recommend_recipes(self, preference, available_ingredients):
        """
        Recommend recipes based on user preference and available ingredients.
        """        
        recipes = Recipe.objects.filter(taste__icontains=preference)
        suggestions = []
                
        available_ingredients = [ing.lower() for ing in available_ingredients]
        
        for recipe in recipes:
            recipe_ingredients = [ing.strip().lower() for ing in recipe.ingredients.split(',')]            
            if all(ing in available_ingredients for ing in recipe_ingredients):
                suggestions.append({
                    'title': recipe.title,
                    'ingredients': recipe.ingredients.split(','),
                    'instructions': recipe.instructions,
                    'taste': recipe.taste,
                    'cuisine_type': recipe.cuisine_type,
                    'preparation_time': recipe.preparation_time
                })
        
        return suggestions

chatbot_service = ChatbotService()


class IngredientListCreateView(APIView):
    """
    GET /ingredients/ - List all ingredients
    POST /ingredients/ - Create a new ingredient
    """
    def get(self, request):
        ingredients = Ingredient.objects.all()
        serializer = IngredientSerializer(ingredients, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = IngredientSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class IngredientDetailView(APIView):
    """
    GET /ingredients/<id>/ - Retrieve a specific ingredient
    PUT /ingredients/<id>/ - Update a specific ingredient
    DELETE /ingredients/<id>/ - Delete a specific ingredient
    """
    def get_object(self, pk):
        return get_object_or_404(Ingredient, pk=pk)
    
    def get(self, request, pk):
        ingredient = self.get_object(pk)
        serializer = IngredientSerializer(ingredient)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request, pk):
        ingredient = self.get_object(pk)
        serializer = IngredientSerializer(ingredient, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        ingredient = self.get_object(pk)
        ingredient.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeListCreateView(APIView):
    """
    GET /recipes/ - List all recipes
    POST /recipes/ - Create a new recipe (supports JSON and image uploads)
    """
    def get(self, request):
        recipes = Recipe.objects.all()
        serializer = RecipeSerializer(recipes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        if 'file' in request.FILES:            
            file_obj = request.FILES['file']
            file_path = os.path.join(settings.MEDIA_ROOT, file_obj.name)
                        
            os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
                        
            with open(file_path, 'wb+') as destination:
                for chunk in file_obj.chunks():
                    destination.write(chunk)
                        
            recipe_data = parse_recipe_image(file_path)
                        
            os.remove(file_path)
                        
            if not recipe_data.get('title'):
                return Response(
                    {'error': 'Could not parse recipe title from image.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                        
            serializer = RecipeSerializer(data=recipe_data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        else:            
            data = request.data            
            if any(key in data for key in ["Title:", "Ingredients:", "Instructions:"]):                
                serializer = RecipeSerializer(data=data)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:                                
                raw_text = data.get('raw_text', '')
                if not raw_text:
                    return Response(
                        {'error': 'No raw_text provided for unstructured recipe.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                                
                recipe_data = parse_unstructured_text(raw_text)
                
                if not recipe_data.get('title'):
                    return Response(
                        {'error': 'Could not parse recipe details from the provided text.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                                
                serializer = RecipeSerializer(data=recipe_data)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RecipeDetailView(APIView):
    """
    GET /recipes/<id>/ - Retrieve a specific recipe
    PUT /recipes/<id>/ - Update a specific recipe
    DELETE /recipes/<id>/ - Delete a specific recipe
    """
    def get_object(self, pk):
        return get_object_or_404(Recipe, pk=pk)
    
    def get(self, request, pk):
        recipe = self.get_object(pk)
        serializer = RecipeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request, pk):
        recipe = self.get_object(pk)
        serializer = RecipeSerializer(recipe, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        recipe = self.get_object(pk)
        recipe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ChatbotView(APIView):
    """
    POST /chatbot/
    {
        "message": "I want something sweet today and I have flour, sugar, eggs, butter."
    }
    """
    def post(self, request):
        print(LLM_API_KEY)
        serializer = ChatbotQuerySerializer(data=request.data)
        if serializer.is_valid():
            message = serializer.validated_data.get('message', '')

            if message:                
                parsed_data = parse_user_message(message)
                preference = parsed_data.get('preference', '')
                available_ingredients = parsed_data.get('available_ingredients', [])
            
                if not preference or not available_ingredients:
                    return Response(
                        {'error': 'Could not extract preference or available ingredients from the message.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                                
                recommendations = chatbot_service.recommend_recipes(preference, available_ingredients)
                
                if recommendations:
                    return Response({'recommendations': recommendations}, status=status.HTTP_200_OK)
                else:
                    return Response({'message': 'No matching recipes found.'}, status=status.HTTP_404_NOT_FOUND)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)