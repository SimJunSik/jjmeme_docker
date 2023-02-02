from dotenv import load_dotenv
from notion_client import Client

import os
from pprint import pprint

load_dotenv(dotenv_path="./secrets/.env")

 
notion_secret_key = os.environ.get("NOTION_SECRET_KEY")
notion = Client(auth=notion_secret_key)

# print(notion)

databases = notion.search(filter={"property": "object", "value": "database"})
# pprint(databases)

database_id = databases['results'][0]['id']
databases = notion.databases.retrieve(database_id=database_id)
# pprint(databases)

def read():
    resp = notion.databases.query(database_id=database_id)
    results = []
    cursor = None
    while True:
        resp = notion.databases.query(database_id=database_id, start_cursor=cursor)
        results.extend(resp['results'])

        if not resp['has_more']:
            break
        cursor = resp['next_cursor']

    return results


def get_title_list():
    title_list = []
    cursor = None
    while True:
        resp = notion.databases.query(database_id=database_id, start_cursor=cursor)
        results = resp['results']
        for data in results:
            properites = data['properties']
            title = properites['밈 제목']['title'][0]['plain_text']
            title_list.append(title)

        if not resp['has_more']:
            break
        cursor = resp['next_cursor']
    return title_list


def create(name, ext, url):
    resp = notion.databases.query(database_id=database_id)
    results = resp['results']
    sample_page_id = results[-1]['id']

    sample_page = notion.pages.retrieve(page_id=sample_page_id)
    properties_new = sample_page['properties']

    target_key_list = ["밈 제목", "기존 태그", "URL"]
    keys = [key for key in properties_new.keys()]
    for key in keys:
        if key not in target_key_list:
            del properties_new[key]
    
    
    properties_new['밈 제목']['title'] = []
    properties_new['밈 제목']['title'].append({
        "plain_text": name,
        "text": {
            "content": name
        }
    })
    properties_new['기존 태그']['rich_text'] = []
    properties_new['기존 태그']['rich_text'].append({
        "text": {
            "content": ""
        }
    })
    properties_new["URL"]["url"] = url

    result = notion.pages.create(parent={'database_id': database_id}, properties=properties_new)

    page_id = result['id']
    blocks = notion.blocks.children.list(block_id=page_id)

    children_image = {
        "type": "image", 
        "image": {
            "external": {
                "url": url
            }
        }
    }
    children_blocks = [children_image]
    notion.blocks.children.append(block_id=page_id, children=children_blocks)


if __name__ == "__main__":
    # read()
    # create("test22", ".jpg", "https://jjmeme-bucket-2.s3.amazonaws.com/(집에서)엄청바빠~할게많아.jpg")
    # print(len(get_title_list()))
    pprint(databases['properties'].keys())