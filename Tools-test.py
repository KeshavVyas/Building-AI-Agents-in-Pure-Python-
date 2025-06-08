import os
import json
import requests
from google import genai
from google.genai import types

client = genai.Client(api_key=os.getenv('GEMINI_KEY'))
prompt = "What are Mel's abilities in LOL?"

get_ability_details_declaration = types.FunctionDeclaration(
    name="get_ability_details",
    description="Fetch mana cost, damage, and description for a given champion",
    parameters={
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "Champion name"},
        },
        "required": ["name"],
    },
)

tool = types.Tool(function_declarations=[get_ability_details_declaration])

def get_champion_abilities(champion_name: str) -> dict:
    url = f"https://ddragon.leagueoflegends.com/cdn/15.11.1/data/en_US/champion/{champion_name}.json"
    r = requests.get(url)
    if r.status_code != 200:
        return {"error": f"Could not fetch data for {champion_name}"}
    data = r.json()["data"][champion_name]
    partype = data.get("partype", "")
    abilities = []
    for s in data["spells"]:
        burn = s.get("costBurn", "")
        costs = [int(x) for x in burn.split("/")] if burn and burn[0].isdigit() else burn
        abilities.append({
            "name": s["name"],
            "costs": costs,
            "resource": partype
        })
    return {"passive": data["passive"]["name"], "resource": partype, "abilities": abilities}

def ask_gemini(query: str) -> str:
    r1 = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[types.Content(role="user", parts=[types.Part(text=query)])],
        config=types.GenerateContentConfig(
            tools=[tool],
            tool_config=types.ToolConfig(
                function_calling_config=types.FunctionCallingConfig(mode="ANY")
            ),
        ),
    )
    fc = r1.candidates[0].content.parts[0].function_call
    if fc and fc.name == "get_ability_details":
        details = get_champion_abilities(fc.args["name"])
        format_prompt = "Format these ability details in a simple table:\n" + json.dumps(details, indent=2)
        r2 = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[types.Content(role="user", parts=[types.Part(text=format_prompt)])],
        )
        return r2.candidates[0].content.parts[0].text
    return r1.candidates[0].content.parts[0].text

print(ask_gemini(prompt))
