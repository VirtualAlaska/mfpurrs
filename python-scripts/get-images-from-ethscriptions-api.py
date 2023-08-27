import requests
import os
import base64

OUTPUT_FOLDER = r'path_to_folder_to_save_images_in'

if not os.path.exists(OUTPUT_FOLDER):
    os.mkdir(OUTPUT_FOLDER)

page = 0
total_pages = 501

def parse_data_uri(data_uri: str) -> tuple[str, str]:
    meta, data = data_uri.split(",", 1)
    mime_type = meta.split(";")[0][5:]
    return mime_type, data

while page < total_pages:
    print(f"Processing page {page+1} of {total_pages}...")
    
    res = requests.get(f'https://api.ethscriptions.com/api/ethscriptions/filtered?collection=mfpurrs&page={page}&per_page=25')
    data = res.json()
    ethscriptions = data['ethscriptions']
    
    for idx, ethscription in enumerate(ethscriptions, start=1):
        name = ethscription['collection_items'][0]['name']
        mime_type, base64_data = parse_data_uri(ethscription['content_uri'])
        filename = f'{OUTPUT_FOLDER}/{name}.{"png" if mime_type == "image/png" else "gif"}'
        
        with open(filename, 'wb') as f:
            f.write(base64.decodebytes(base64_data.encode('utf-8')))
        
        print(f"    Downloaded {idx}/{len(ethscriptions)} images from page {page+1}")
    
    page += 1

print("Download completed.")