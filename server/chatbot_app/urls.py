# chatbot_app/urls.py

from django.urls import path
from .views import (
    IngredientListCreateView,
    IngredientDetailView,
    RecipeListCreateView,
    RecipeDetailView,
    ChatbotView,
)

urlpatterns = [
    # Ingredient Endpoints
    path('ingredients/', IngredientListCreateView.as_view(), name='ingredient-list-create'),
    path('ingredients/<int:pk>/', IngredientDetailView.as_view(), name='ingredient-detail'),
    
    # Recipe Endpoints
    path('recipes/', RecipeListCreateView.as_view(), name='recipe-list-create'),
    path('recipes/<int:pk>/', RecipeDetailView.as_view(), name='recipe-detail'),
    
    # Chatbot Endpoint
    path('chatbot/', ChatbotView.as_view(), name='chatbot'),
]
