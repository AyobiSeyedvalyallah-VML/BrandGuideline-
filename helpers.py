import openai
import pandas as pd
from io import StringIO
import os 
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import requests
from io import BytesIO
import re

project_dir = Path(__file__).parent.parent
project_path = os.path.join(project_dir,'brandguideline-')
openai.api_key = os.getenv('OPENAI_API_KEY')
MODEL = "gpt-4o"
def capitalize_if_needed(s):
    if not s[:1].isupper():  # Check if the first character is not uppercase
        return s.capitalize()
    return s
def fix_trailing_commas(json_string):
    """
    Fix trailing commas in a JSON string.
    :param json_string: The raw JSON string with potential trailing commas
    :return: A corrected JSON string
    """
    # Regex to find trailing commas
    pattern = r',\s*([\]}])'
    # Replace the trailing comma with just the closing bracket or brace
    fixed_json = re.sub(pattern, r'\1', json_string)
    return fixed_json

def fix_missing_commas(json_string):
    """
    Fix missing commas in a JSON string.
    :param json_string: The raw JSON string with potential formatting issues
    :return: A corrected JSON string
    """
    # Regex to detect missing commas between object properties
    # Matches: "value"} or "value"] and inserts a comma between them
    pattern = r'(["\}\]])\s*([{"\[])'
    fixed_json = re.sub(pattern, r'\1,\2', json_string)
    return fixed_json

def config(html_content):
    """
    Transforms the user input into an optimized prompt using OpenAI GPT-4.
    """
    response = openai.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content":  """you will receive an html and try to extract information from it. return the output ONLY in the following format:

{
    "configuration" = {
				"logo":{
					"data":[
						{
						"type":string,
						"description":string,
						"link":string
						}
						]
					},
				"color":{
					"data":[
						{
						 "category":string,
						 "description":string,
						 "RGB_code":string
						}
							]
					},
				"font":{	
					"data":[
						{
						 "name":string,
						 "link":string,
						 "description":string
						}
						]
					},
				"General_brand_guidline":{
							   "data":[
									 {
									"category":string
									"description":string
									 }
								  ]
							 }
}
}
"""},
            {"role": "user", "content": f'{html_content}'}
        ]
    )
    data = response.choices[0].message.content.replace('json','').strip()
    data = fix_trailing_commas(data)
    data = fix_missing_commas(data)
    # df = pd.read_csv(StringIO(data),quotechar='"')
    return data
 
def prompt_transformer(html_content: str) -> str:
    """
    Transforms the user input into an optimized prompt using OpenAI GPT-4.
    """
    response = openai.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content":  """you will receive a html file of my brand guideline
I want you to generate a table the one column is image_link and one column is description (if it doesn't have return None for description) and one column category of image (this should not be long) and don't over categorized.
if the category is font, only return the name of the font in the description
Only return the table that has image_link, description, category columns in JSON format """},
            {"role": "user", "content": f'{html_content}'}
        ]
    )
    data = response.choices[0].message.content.strip().replace('```csv','').replace('```','')
    # df = pd.read_csv(StringIO(data),quotechar='"')
    return data

def fix_csv(text):
    response = openai.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content":  """fix the following JSON . Only return the JSON"""},
            {"role": "user", "content": f'{text}'}
        ]
    )
    data = response.choices[0].message.content.strip().replace('```csv','').replace('```','')
    # df = pd.read_csv(StringIO(data),quotechar='"')
    return data

def image_font_generation(font,folder):
    logo_urls = {
    'KB': 'https://brand.kb.cz/m/6d636a1c2be0aea5/webimage-KB_104_Noir-Quadri.png',
    'Adobe': 'https://www.pngplay.com/wp-content/uploads/9/Adobe-Systems-Logo-PNG-Clipart-Background.png'
    }
    logo = logo_urls[folder]
    response = requests.get(logo)
    if response.status_code == 200:
        logo = Image.open(BytesIO(response.content))
    else:
        raise Exception("Failed to download the logo. Check the URL.")
    
    # image_path = Path(project_dir)/'BrandGuideline-'/'image'/'input'
    image_folder = os.path.join(project_path,'image')
    image_path = os.path.join(image_folder,'input')
    image = Image.open(os.path.join(image_path,'image.jpg'))
    draw = ImageDraw.Draw(image)

# Specify the font and size
    # print(f"./fonts/{font}")
    # font = ImageFont.truetype(f"./fonts/{font}", size=300)

    # Text details
    text = f"This is a test to show case {font}"

    image_width, image_height = image.size
    logo_size = (image_width // 5, image_height // 10)
    logo_resized = logo.resize(logo_size, Image.Resampling.LANCZOS)
    
    # Position the logo at the bottom-left corner
    logo_x = 10  # Padding from the left
    logo_y = image_height - logo_size[1] - 10  # Padding from the bottom
    
    # Paste the logo on the image (handle transparency)
    image.paste(logo_resized, (logo_x, logo_y), logo_resized if logo_resized.mode == "RGBA" else None)
    # Dynamically adjust font size to fit the image
    font_size = 10  # Start with a small font size
    # font_folder = Path(project_dir) /'BrandGuideline-'/'fonts'/folder  # Path to the font file
    font_folder = os.path.join(project_path,'fonts')
    font_folder = os.path.join(font_folder,folder)
    font_path = os.path.join(font_folder,font)
    while True:
        font = ImageFont.truetype(font_path, font_size)
        # Use font.getbbox() to measure text size
        text_bbox = font.getbbox(text)
        text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]
        if text_width > image_width * 0.8 or text_height > image_height * 0.2:  # Adjust fit constraints as needed
            font_size -= 1
            break
        font_size += 1

    # Final font
    font = ImageFont.truetype(font_path, font_size-20)

    # Calculate position to center the text
    text_bbox = font.getbbox(text)
    text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]
    text_x = (image_width - text_width) // 2
    text_y = (image_height - text_height) // 2

    # Text color
    text_color = (0, 0, 0)  # Black

    # Add the text to the image
    draw.text((text_x, text_y), text, fill=text_color, font=font)
    # logging.info(font)
    # Save or display the image
    # image.save(f"./image/output/output_image_{font.replace('.otf','')}.jpg")
    # image.show()
    return image
