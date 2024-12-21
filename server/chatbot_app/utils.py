# chatbot_app/utils.py

import pytesseract
from PIL import Image
from transformers import pipeline
import os
import torch
import json
import logging
import re

logger = logging.getLogger(__name__)

def clean_user_message(message):
    """
    Cleans the user message by removing unnecessary punctuation and normalizing spaces.
    """
   
    message = re.sub(r'[^\w\s,]', '', message)
   
    message = re.sub(r'\s+', ' ', message)
    return message


def parse_text_file(file_path):
    """
    Parses a structured text file to extract recipe details.
    """
   
    pass 


def parse_unstructured_text(text):
    """
    Uses an LLM to parse unstructured recipe text into structured fields.
    """
   
    if not hasattr(parse_unstructured_text, "parser"):
        api_key = os.getenv('LLM_API_KEY')
        parse_unstructured_text.parser = pipeline(
            "text2text-generation",
            model="google/flan-t5-small",
            tokenizer="google/flan-t5-small",
            device=0 if torch.cuda.is_available() else -1,
            use_auth_token=api_key if api_key else None
        )

   
    prompt = (
        "You are an assistant that extracts food preferences and available ingredients from user messages.\n"
        "Given the user's message, identify their taste preference and list of available ingredients.\n"
        "Respond ONLY with a JSON object containing the keys: 'preference' and 'available_ingredients'.\n"
        "Ensure the JSON is properly formatted.\n\n"
        f"Recipe Text: {text}"
    )

   
    try:
        response = parse_unstructured_text.parser(prompt, max_length=512, num_return_sequences=1)
        structured_data = response[0]['generated_text']
        logger.debug(f"LLM Response for recipe text: {structured_data}")
        
       
        recipe_data = json.loads(structured_data)
        logger.debug(f"Parsed Recipe Data: {recipe_data}")
    except json.JSONDecodeError as jde:
        logger.error(f"JSON decoding failed: {jde}")
        recipe_data = {}
    except Exception as e:
       
        logger.error(f"Error parsing recipe with LLM: {e}")
        recipe_data = {}

    return recipe_data

from transformers import pipeline
import os
import logging
import json
import re

logger = logging.getLogger(__name__)

def parse_user_message(message):
    """
    Uses an LLM to parse the user's free-form message into structured preferences and ingredients.
    """
   
    cleaned_message = re.sub(r'[^\w\s,]', '', message).strip()
    logger.debug(f"Cleaned User Message: {cleaned_message}")

   
    if not hasattr(parse_user_message, "parser"):
        parse_user_message.parser = pipeline(
            "text2text-generation",
            model="t5-small", 
            tokenizer="t5-small",
            device=0 if torch.cuda.is_available() else -1
        )

   
    prompt = (
        "You are an assistant that extracts food preferences and available ingredients from user messages.\n"
        "Respond ONLY with a JSON object containing 'preference' (a string) and 'available_ingredients' (a list of strings).\n"
        "Example input:\n"
        "\"I want something sweet today and I have flour, sugar, eggs, butter.\"\n"
        "Example output:\n"
        "{\n"
        "  \"preference\": \"sweet\",\n"
        "  \"available_ingredients\": [\"flour\", \"sugar\", \"eggs\", \"butter\"]\n"
        "}\n"
        "User Message:\n"
        f"{cleaned_message}"
    )

   
    try:
        response = parse_user_message.parser(prompt, max_length=150, num_return_sequences=1)
        print(response)
        structured_data = response[0]['generated_text']
        print(structured_data)
        logger.debug(f"LLM Response for user message: {structured_data}")

       
        parsed_data = json.loads(structured_data)
        logger.debug(f"Parsed User Data: {parsed_data}")
        
       
        if 'preference' not in parsed_data or 'available_ingredients' not in parsed_data:
            logger.error("Required keys missing in parsed data.")
            parsed_data = {}
    except json.JSONDecodeError as jde:
        logger.error(f"JSON decoding failed: {jde}")
        parsed_data = {}
    except Exception as e:
        logger.error(f"Error parsing user message with LLM: {e}")
        parsed_data = {}

    return parsed_data

def parse_recipe_image(image_path):
    """
    Extracts and parses recipe details from an image using OCR and LLM.
    """
   
    text = pytesseract.image_to_string(Image.open(image_path))
    logger.debug(f"Extracted Text from Image: {text}")
    
   
    recipe_data = parse_unstructured_text(text)
    
    return recipe_data
