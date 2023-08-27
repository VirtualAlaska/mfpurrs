import json
from collections import defaultdict

# Step 1: Read the JSON File
with open(r'<path_to_mfpurrs_metadata_in_json>', 'r') as json_file:
    nft_data = json.load(json_file)
    total_retrieved = len(nft_data['collection_items'])

# Step 2: Print Status
if total_retrieved == 10000:
    print("Retrieved 10,000 mfpurrs.")
else:
    print(f"Retrieved the wrong number of mfpurrs. Expected 10,000 but retrieved {total_retrieved}.")

# Step 3: Calculate Trait Value Frequencies
trait_value_counts = defaultdict(int)
total_items = len(nft_data['collection_items'])

for item in nft_data['collection_items']:
    for attr in item['item_attributes']:
        trait_type, trait_value = attr['trait_type'], attr['value']
        trait_value_counts[(trait_type, trait_value)] += 1

# Step 4: Calculate and Print Trait Frequencies
print("\nTrait Frequencies (sorted by least common to most common):")
for (trait_type, trait_value), count in sorted(trait_value_counts.items(), key=lambda x: x[1]):
    frequency_percentage = (count / total_items) * 100
    print(f"{trait_type} - {trait_value} = {frequency_percentage:.2f}% ({count}/{total_items})")

# Step 5: Calculate Rarity Scores and Rankings
nft_rankings = []

for nft in nft_data['collection_items']:
    nft_traits = nft['item_attributes']
    rarity_scores = []

    for trait in nft_traits:
        trait_type, trait_value = trait['trait_type'], trait['value']
        count = trait_value_counts[(trait_type, trait_value)]
        rarity_score = 1 / (count / total_items)
        rarity_scores.append((trait_type, trait_value, rarity_score))

    rarity_scores.sort(key=lambda x: x[2], reverse=True)
    nft_rankings.append((nft['name'], rarity_scores[0]))

# Step 6: Order Rarity Rankings by Rarest to Least Rare
nft_rankings.sort(key=lambda x: x[1][2], reverse=True)

# Step 7: Save Rarity Rankings to a File
txt_filename = r'<path_to_file_to_write_to>'

with open(txt_filename, 'w') as txt_file:
    for rank, (nft_name, (trait_type, trait_value, _)) in enumerate(nft_rankings, start=1):
        ethscription_id = next((item['ethscription_id'] for item in nft_data['collection_items'] if item['name'] == nft_name), '')
        link = f"https://ethscriptions.com/ethscriptions/{ethscription_id}"
        text = f"Rank {rank} - {nft_name} | Rarest trait = {trait_type} - {trait_value} | Link: {link}\n"
        txt_file.write(text)

# Step 8: Calculate and Print Rarity Scores for Traits
print("\nRarity Scores for Traits (sorted by least rarest):")
for trait, count in sorted(trait_value_counts.items(), key=lambda x: (x[1] / total_items)):
    trait_type, trait_value = trait
    rarity_score = 1 / (count / total_items)
    rarity_calculation = f"(1 / ({count}/{total_items}))"
    print(f"{trait_type} - {trait_value} = {rarity_score:.6f} | calculation = {rarity_calculation}")