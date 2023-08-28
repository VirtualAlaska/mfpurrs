import requests
import os
import base64

OUTPUT_FOLDER = r'<path_to_folder_to_save_images_in>'

if not (os.path.exists(OUTPUT_FOLDER)):
    os.mkdir(OUTPUT_FOLDER)

index = 10000

def parse_data_uri(data_uri: str) -> tuple[str, str]:
    meta, data = data_uri.split(",", 1)
    mime_type = meta.split(";")[0][5:]
    return mime_type, data

while (index != 0):
    res = requests.get(f'https://api.ethscriptions.com/api/ethscriptions/filtered?collection=mfpurrs&sort_by=collection_item_index&collection_item_index={index}')
    data = res.json()
    ethscriptions = data['ethscriptions']
    for ethscription in ethscriptions:
        name = ethscription['collection_items'][0]['name']
        mime_type, base64_data = parse_data_uri(ethscription['content_uri'])
        with open(f'{OUTPUT_FOLDER}/{name}.{"png" if mime_type == "image/png" else "gif"}', 'wb') as f:
            f.write(base64.decodebytes(base64_data.encode('utf-8')))
    index -= 50