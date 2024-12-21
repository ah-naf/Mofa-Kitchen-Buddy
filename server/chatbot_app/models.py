from django.db import models

class Ingredient(models.Model):
    name = models.CharField(max_length=100)
    quantity = models.FloatField(default=0.0)
    unit = models.CharField(max_length=30, null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.quantity} {self.unit})"


class Recipe(models.Model):
    title = models.CharField(max_length=200)
    ingredients = models.TextField()  # Comma-separated list or JSON structure
    instructions = models.TextField()
    taste = models.CharField(max_length=100, null=True, blank=True)       # e.g., sweet, spicy
    cuisine_type = models.CharField(max_length=100, null=True, blank=True)
    preparation_time = models.IntegerField(default=0)  # In minutes
    reviews = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
