import os
import re
import json
from collections import defaultdict

# Setup paths
base_dir = os.path.dirname(os.path.realpath(__file__))
input_meta = os.path.normpath(os.path.join(base_dir, '..', 'metadata', 'metadata-mfpurrs.json'))
metadata_dir = os.path.dirname(input_meta)
rarity_dir = os.path.normpath(os.path.join(base_dir, '..', 'rarity'))

# Ensure directories exist
os.makedirs(metadata_dir, exist_ok=True)
os.makedirs(rarity_dir, exist_ok=True)

# Determine next version (newX) by scanning existing outputs
def next_version(dir_path, pattern):
    versions = []
    for fname in os.listdir(dir_path):
        m = re.match(pattern, fname)
        if m:
            versions.append(int(m.group(1)))
    return max(versions) + 1 if versions else 1

# Version for JSON: metadata-mfpurrs-newX.json
json_pattern = r'metadata-mfpurrs-new(\d+)\\.json$'
new_json_ver = next_version(metadata_dir, json_pattern)
output_meta = os.path.join(metadata_dir, f'metadata-mfpurrs-new{new_json_ver}.json')

# Version for TXT reports only if static exist
rank_static = os.path.join(rarity_dir, 'rarity-rankings.txt')
stats_static = os.path.join(rarity_dir, 'rarity-statistics.txt')

rank_pattern = r'rarity-rankings-new(\d+)\\.txt$'
stats_pattern = r'rarity-statistics-new(\d+)\\.txt$'
new_rank_ver = next_version(rarity_dir, rank_pattern) if os.path.exists(rank_static) else None
new_stats_ver = next_version(rarity_dir, stats_pattern) if os.path.exists(stats_static) else None

output_rank = (os.path.join(rarity_dir, f'rarity-rankings-new{new_rank_ver}.txt')
               if new_rank_ver else rank_static)
output_stats = (os.path.join(rarity_dir, f'rarity-statistics-new{new_stats_ver}.txt')
                if new_stats_ver else stats_static)

# Load metadata
with open(input_meta, 'r') as f:
    data = json.load(f)
items = data.get('collection_items', [])
total_items = len(items)
print(f"Retrieved {total_items} items. Version: new{new_json_ver}\nCalculating rarity...")

# Count trait frequencies
trait_counts = defaultdict(int)
for item in items:
    for attr in item.get('item_attributes', []):
        if attr.get('trait_type') == 'rarity': continue
        key = (attr['trait_type'], attr['value'])
        trait_counts[key] += 1

# Prepare ranking data
temp = []
honorary = {"mfpurr #9606","mfpurr #9607","mfpurr #9622",
             "mfpurr #9767","mfpurr #9838","mfpurr #9896","mfpurr #9992"}
for item in items:
    name = item.get('name')
    es_id = item.get('ethscription_id')
    sum_score = 0.0
    best_score = 0.0
    best_trait = None
    for attr in item.get('item_attributes', []):
        if attr.get('trait_type') == 'rarity': continue
        freq = trait_counts[(attr['trait_type'], attr['value'])]
        score = total_items / freq
        sum_score += score
        if score > best_score:
            best_score = score
            best_trait = (attr['trait_type'], attr['value'])
    temp.append({'id': es_id, 'name': name, 'sum': sum_score, 'best': best_trait})
# Sort by summed rarity descending
temp.sort(key=lambda x: x['sum'], reverse=True)

# Assign ranks
ranks = {}
curr = 2
for entry in temp:
    nm = entry['name']
    eid = entry['id']
    if nm in honorary:
        ranks[eid] = 1
    else:
        ranks[eid] = curr
        curr += 1

# Update JSON rarity values
for item in items:
    eid = item.get('ethscription_id')
    rank_val = ranks.get(eid)
    if rank_val is None: continue
    updated = False
    for attr in item.get('item_attributes', []):
        if attr.get('trait_type') == 'rarity':
            attr['value'] = rank_val
            updated = True
            break
    if not updated:
        item.setdefault('item_attributes', []).append({'trait_type':'rarity','value':rank_val})

# Write updated metadata JSON
with open(output_meta, 'w') as f:
    json.dump(data, f, indent=4)
print(f"Wrote updated metadata to {output_meta}")

# Write rarity-rankings.txt
with open(output_rank, 'w') as f:
    nr = 2
    for entry in temp:
        nm = entry['name']
        bt = entry['best']
        eid = entry['id']
        if not bt: continue
        if nm in honorary:
            rnk = 1
        else:
            rnk = nr
            nr += 1
        tr = f"{bt[0]} - {bt[1]}"
        link = f"https://marketplace.mfpurrs.com/details/{eid}"
        f.write(f"Rank {rnk} - {nm} | Rarest trait = {tr} | Link: {link}\n")
print(f"Wrote rankings to {output_rank}")

# Write rarity-statistics.txt
with open(output_stats, 'w') as f:
    f.write("-------------------------------------------------------------\n")
    f.write("Rarity Scores for Traits (sorted by most rare to least rare):\n")
    f.write("-------------------------------------------------------------\n")
    for (tt, tv), cnt in sorted(trait_counts.items(), key=lambda x: (total_items/x[1]), reverse=True):
        sc = total_items / cnt
        f.write(f"{tt} - {tv} | rarity score = {sc:.2f} | frequency = {cnt} / {total_items}\n")
print(f"Wrote statistics to {output_stats}")
