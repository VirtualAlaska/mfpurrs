import json
from collections import defaultdict

# Step 1: Read the JSON File
with open(r"<ENTER FILE PATH HERE FOR MFPURRS METADATA>", 'r') as json_file:
    nft_data = json.load(json_file)
    total_retrieved = len(nft_data['collection_items'])

# Step 2: Print Status
if total_retrieved == 10000:
    print("Retrieved 10,000 mfpurrs.\nCalculating rarity...")
else:
    print(f"Retrieved the wrong number of mfpurrs. Expected 10,000 but retrieved {total_retrieved}.")

# Step 3: Calculate Trait Value Frequencies
trait_value_counts = defaultdict(int)
total_items = len(nft_data['collection_items'])

for item in nft_data['collection_items']:
    for attr in item['item_attributes']:
        trait_type, trait_value = attr['trait_type'], attr['value']
        trait_value_counts[(trait_type, trait_value)] += 1

# Step 4: Calculate Trait Frequencies
for (trait_type, trait_value), count in sorted(trait_value_counts.items(), key=lambda x: x[1]):
    frequency_percentage = (count / total_items) * 100

# Step 5: Calculate Rarity Scores and Rankings
nft_rankings = []

for nft in nft_data['collection_items']:
    nft_traits = nft['item_attributes']
    rarity_scores = []

    for trait in nft_traits:
        trait_type, trait_value = trait['trait_type'], trait['value']
        
        # Skip the 'rarity' trait_type
        if trait_type == 'rarity':
            continue
        
        count = trait_value_counts[(trait_type, trait_value)]
        rarity_score = 1 / (count / total_items)
        rarity_scores.append((trait_type, trait_value, rarity_score))

    if rarity_scores:
        rarity_scores.sort(key=lambda x: x[2], reverse=True)
        nft_rankings.append((nft['name'], rarity_scores[0]))

# Step 6: Order Rarity Rankings by Rarest to Least Rare
nft_rankings.sort(key=lambda x: x[1][2], reverse=True)

# Step 7: Save Rarity Rankings to a File
txt_filename = r"<ENTER FILE PATH HERE FOR TEXT FILE LOCATION>"

honorary_mfpurrs = [
    "mfpurr #9606",
    "mfpurr #9607",
    "mfpurr #9622",
    "mfpurr #9767",
    "mfpurr #9838",
    "mfpurr #9896",
    "mfpurr #9992"
]

with open(txt_filename, 'w') as txt_file:
    for rank, (nft_name, (trait_type, trait_value, _)) in enumerate(nft_rankings, start=1):
        # Check if the current nft is in the honorary_mfpurrs list
        if nft_name in honorary_mfpurrs:
            rank = 1  # Set rank as 1 for honorary mfpurrs, as they are all the rarest in the collection
        
        ethscription_id = next(
            (item['ethscription_id'] for item in nft_data['collection_items'] if item['name'] == nft_name),
            ''
        )
        link = f"https://ethscriptions.com/ethscriptions/{ethscription_id}"
        text = f"Rank {rank} - {nft_name} | Rarest trait = {trait_type} - {trait_value} | Link: {link}\n"
        txt_file.write(text)


# Step 8: Calculate and Print Rarity Scores for Traits
print("\n-------------------------------------------------------------\nRarity Scores for Traits (sorted by most rare to least rare):\n-------------------------------------------------------------")
for trait, count in sorted(trait_value_counts.items(), key=lambda x: (x[1] / total_items)):
    trait_type, trait_value = trait
    
    # Skip the 'rarity' trait_type
    if trait_type == 'rarity':
        continue
    
    rarity_score = 1 / (count / total_items)
    frequency = count
    
    print(f"{trait_type} - {trait_value} | rarity score = {rarity_score:.2f} | frequency = {frequency} / 10,000")
    
print("\nThe terminal output of this script is tracked as a text file here: https://github.com/VirtualAlaska/mfpurrs/blob/main/rarity/rarity-statistics.txt")
print("\nThe full rankings text file that this script produces is tracked here: https://github.com/VirtualAlaska/mfpurrs/blob/main/rarity/rarity-rankings.txt")