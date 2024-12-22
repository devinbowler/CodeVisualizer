import os
from openai import OpenAI

client = OpenAI()

api_key = os.getenv('OPENAI_API_KEY')

completion = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": (
            "You are an AI that only responds with large, detailed ASCII visuals followed by a concise, clear explanation. Do not provide any context, description, or introductory text before the ASCII visual. "
            "The ASCII visual must be large, well-structured, and as detailed as possible. Use clear spacing, alignment, and shapes to make the visual precise and intuitive. "
            "After the ASCII visual, you must provide a concise explanation (no more than 2 paragraphs) that explains the concept illustrated by the ASCII. The explanation must be clear and informative, and must never come before the visual. "
        )},
        {"role": "user", "content": (
            "Draw a large, detailed ASCII visual of a depth-first search (DFS) traversal on a binary tree with 5 nodes."
        )}
    ],
    temperature=0.9,
    max_tokens=2000,  # Allow more tokens for larger ASCII visuals and explanations
    n=1  # Only return one image
)

# Access the content as an attribute, not as a dictionary key
print(completion.choices[0].message.content)

