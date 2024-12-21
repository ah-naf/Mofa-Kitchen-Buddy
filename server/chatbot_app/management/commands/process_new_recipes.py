# chatbot_app/management/commands/process_new_recipes.py

from django.core.management.base import BaseCommand
from chatbot_app.models import Recipe
from chatbot_app.utils import parse_recipe_image, parse_unstructured_text
import os
import glob

class Command(BaseCommand):
    help = "Process new recipe posts and images and load them into the database."

    def add_arguments(self, parser):
        parser.add_argument('input_directory', type=str, help='Directory containing new recipe files and images')

    def handle(self, *args, **options):
        input_dir = options['input_directory']
        self.stdout.write(f"Processing new recipes from {input_dir}...")

        # Process text files
        text_files = glob.glob(os.path.join(input_dir, '*.txt'))
        for file_path in text_files:
            self.stdout.write(f"Processing text file: {file_path}")
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    raw_text = f.read()
                recipe_data = parse_unstructured_text(raw_text)
                
                if not recipe_data.get('title'):
                    self.stdout.write(self.style.WARNING(f"Could not parse recipe from {file_path}. Skipping."))
                    continue

                # Create or update the recipe
                recipe, created = Recipe.objects.update_or_create(
                    title=recipe_data['title'],
                    defaults={
                        'ingredients': recipe_data['ingredients'],
                        'instructions': recipe_data['instructions'],
                        'taste': recipe_data['taste'],
                        'cuisine_type': recipe_data['cuisine_type'],
                        'preparation_time': int(recipe_data['preparation_time'] or 0),
                        'reviews': int(recipe_data['reviews'] or 0),
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Recipe '{recipe.title}' created."))
                else:
                    self.stdout.write(self.style.WARNING(f"Recipe '{recipe.title}' updated."))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Error processing {file_path}: {e}"))

        # Process image files
        image_files = glob.glob(os.path.join(input_dir, '*.jpg')) + glob.glob(os.path.join(input_dir, '*.png'))
        for image_path in image_files:
            self.stdout.write(f"Processing image file: {image_path}")
            try:
                recipe_data = parse_recipe_image(image_path)
                
                if not recipe_data.get('title'):
                    self.stdout.write(self.style.WARNING(f"Could not parse recipe from {image_path}. Skipping."))
                    continue

                # Create or update the recipe
                recipe, created = Recipe.objects.update_or_create(
                    title=recipe_data['title'],
                    defaults={
                        'ingredients': recipe_data['ingredients'],
                        'instructions': recipe_data['instructions'],
                        'taste': recipe_data['taste'],
                        'cuisine_type': recipe_data['cuisine_type'],
                        'preparation_time': int(recipe_data['preparation_time'] or 0),
                        'reviews': int(recipe_data['reviews'] or 0),
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Recipe '{recipe.title}' created."))
                else:
                    self.stdout.write(self.style.WARNING(f"Recipe '{recipe.title}' updated."))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Error processing {image_path}: {e}"))
        
        self.stdout.write(self.style.SUCCESS("Processing completed."))
