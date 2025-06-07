from google import genai
import os #api key is an environment var, need get os
client = genai.Client(api_key=os.getenv('GEMINI_KEY'))
prompt = "Write a poem about C programming"
response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
print("Prompt: " + prompt + '\n')
print("Reply: "+ response.text)