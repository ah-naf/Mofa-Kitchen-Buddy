# Mofa-Kitchen-Buddy
- Route: /notices api/chatbot post 
input 
```json
{
    "message": "I want something sweet today and I have flour, sugar, eggs, butter."
}
```
output :

```json

{
    "recommendations": [
        {
            "title": "Chocolate Cake",
            "ingredients": ["flour", "sugar", "eggs", "butter", "cocoa powder"],
            "instructions": "Mix ingredients, bake at 350°F for 30 minutes.",
            "taste": "sweet",
            "cuisine_type": "dessert",
            "preparation_time": 45
        }
    ]
}
```
