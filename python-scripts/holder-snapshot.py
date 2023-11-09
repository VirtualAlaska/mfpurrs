import requests
import json

# Define the Ethscriptions API base URL
api_base_url = 'https://api.ethscriptions.com/api/ethscriptions/'

# Function to fetch the current owners for a given Ethscription ID
def fetch_current_owner(ethscription_id):
    api_url = f"{api_base_url}{ethscription_id}"
    response = requests.get(api_url)

    if response.status_code == 200:
        ethscription_data = response.json()
        current_owner = ethscription_data.get('current_owner')
        return current_owner
    else:
        print(f"Failed to fetch data for Ethscription ID: {ethscription_id}")
        return None

# Read metadata from a JSON file
metadata_file = r"<replace with file path of the collection's metadata>"  # Update with your file name
with open(metadata_file, 'r') as file:
    metadata = json.load(file)

# Initialize a set to store unique wallet addresses
owners = set()

# Loop through the collection items in the metadata
for item in metadata['collection_items']:
    ethscription_id = item.get('ethscription_id')
    if ethscription_id:
        current_owner = fetch_current_owner(ethscription_id)
        if current_owner:
            owners.add(current_owner)
        print(f"Ethscription ID: {ethscription_id}, Current Owner: {current_owner}")

# Convert the set of owners to a list
unique_owners = list(owners)

# Save the unique wallet addresses to a text file
output_file = r"<replace with file path for where you want it saved>"  # Update with your file name
with open(output_file, 'w') as file:
    for owner in unique_owners:
        file.write(owner + '\n')

print(f"\nUnique Wallet Addresses of Current Owners have been saved to {output_file}")