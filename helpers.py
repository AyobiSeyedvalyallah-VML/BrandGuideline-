import openai
import pandas as pd
from io import StringIO
import os 

openai.api_key = os.getenv('OPENAI_API_KEY')
MODEL = "gpt-4o"
def prompt_transformer(html_content: str) -> str:
    """
    Transforms the user input into an optimized prompt using OpenAI GPT-4.
    """
    response = openai.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content":  """you will receive a html file of my brand guideline
I want you to generate a table the one column is image_link and one column is description (if it doesn't have return None for description) and one column category of image (this should not be long) and don't over categorized.
Only return the table in CSV format"""},
            {"role": "user", "content": f'{html_content}'}
        ]
    )
    data = response.choices[0].message.content.strip().replace('```csv','').replace('```','')
    # df = pd.read_csv(StringIO(data),quotechar='"')
    return data
