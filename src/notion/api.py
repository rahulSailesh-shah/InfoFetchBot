import requests
import json
import os
import dotenv

dotenv.load_dotenv()

url = "https://api.notion.com/v1/pages/"

tags_map = {
  "red": "7c9c6d5a-e7b2-4a19-942c-3e65216fd41b", # Job
  "blue": "1a7bd404-76af-4fed-b968-ebc140313df4", # Projects
  "green": "91f16e7c-00d4-4298-af18-677c0616265d", # Resources
  "yellow": "bc75cd92-a4b2-4c1f-892c-498569dd374d" # Other
}

def build_payload(tag, name, date, content):
  return json.dumps({
    "parent": {
      "database_id": "103e049ccba081d7934eef53502756bb"
    },
    "properties": {
      "Name": {
        "id": "title",
        "type": "title",
        "title": [
          {
            "type": "text",
            "text": {
              "content": name
            }
          }
        ]
      },
      "Type": {
        "id": "WoQg",
        "type": "select",
        "select": {
          "id": tags_map[tag],
          "name": "Job",
          "color": tag
        }
      },
      "Date": {
        "id": "sJMi",
        "type": "date",
        "date": {
          "start": date,
          "end": None,
          "time_zone": None
        }
      }
    },
    "children": [
      {
        "object": "block",
        "type": "heading_2",
        "heading_2": {
          "rich_text": [
            {
              "type": "text",
              "text": {
                "content": name
              }
            }
          ]
        }
      },
      {
        "object": "block",
        "type": "paragraph",
        "paragraph": {
          "rich_text": [
            {
              "type": "text",
              "text": {
                "content": content
              }
            }
          ]
        }
      }
    ]
  })

def create_notion_page(tag, name, date, content):
  print(f"Creating Notion page with tag: {tag}, name: {name}, date: {date}, content: {content}")
  payload = build_payload(tag, name, date, content)
  headers = {
    'Authorization': f'Bearer {os.getenv("NOTION_TOKEN")}',
    'Content-Type': 'application/json',
    'Notion-Version': '2022-06-28'
  }

  result = requests.request("POST", url, headers=headers, data=payload)
  print(result.text)
