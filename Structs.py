from google import genai #api to invoke gemini
import os #neded for key
from pydantic import BaseModel #
client = genai.Client(api_key=os.getenv('GEMINI_KEY'))

#set up struct for how we want the replies
class CalendarEvent(BaseModel):
    name: str
    date: str
    participants: list[str]

prompt = "Bob and John will go to the concert on June 6th"

#prime the promtp payload
response = client.models.generate_content(
    model="gemini-2.0-flash", #note  model
    contents=prompt,
    config={ #config block to force a structured json isntead of text
        'response_mime_type': 'application/json',  # no leading slash here
        'response_schema': CalendarEvent, 
    }
)




print(response.parsed)