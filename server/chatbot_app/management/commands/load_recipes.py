

from django.core.management.base import BaseCommand
from chatbot_app.models import Recipe
from chatbot_app.utils import parse_text_file, parse_unstructured_text
import os

class Command(BaseCommand):
    help = "Load recipes from a text file into the database."

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the my_fav_recipes.txt file')

    def handle(self, *args, **options):
        file_path = options['file_path']
        self.stdout.write(f"Loading recipes from {file_path}...")
        
        try:
            
            recipes_data = parse_text_file(file_path)
            if not recipes_data:
                self.stdout.write("No structured recipes found. Attempting unstructured parsing.")
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    raw_text = f.read()
                recipe_data = parse_unstructured_text(raw_text)
                if recipe_data:
                    recipes_data = [recipe_data]
                else:
                    self.stdout.write(self.style.WARNING("No recipes parsed from unstructured text."))
                    recipes_data = []
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error parsing file: {str(e)}"))
            return

        for r in recipes_data:
            title = r.get('title')
            ingredients = r.get('ingredients', '')
            instructions = r.get('instructions', '')
            taste = r.get('taste', '')
            cuisine_type = r.get('cuisine_type', '')
            preptime = int(r.get('preparation_time', 0))
            reviews = int(r.get('reviews', 0))

            if not title:
                self.stdout.write(self.style.WARNING("Skipping recipe with no title."))
                continue

            
            recipe, created = Recipe.objects.update_or_create(
                title=title,
                defaults={
                    'ingredients': ingredients,
                    'instructions': instructions,
                    'taste': taste,
                    'cuisine_type': cuisine_type,
                    'preparation_time': preptime,
                    'reviews': reviews,
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Recipe '{title}' created."))
            else:
                self.stdout.write(self.style.WARNING(f"Recipe '{title}' updated."))
