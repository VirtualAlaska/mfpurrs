import os
import re
import json
import sys
from collections import defaultdict

# Ask user for input metadata file path
raw_input_path = input("Enter path to metadata JSON file: ").strip()
# Expand user tilde
expanded_path = os.path.expanduser(raw_input_path)
# First, try as absolute/relative to current working directory
abs_path = os.path.abspath(expanded_path)

base_dir = os.path.dirname(os.path.realpath(__file__))
# If not found at abs_path, try relative to project root (parent of script) using the raw input
if not os.path.isfile(abs_path):
    project_root = os.path.normpath(os.path.join(base_dir, '..'))
    # Construct a candidate path under project root
    candidate = os.path.normpath(os.path.join(project_root, raw_input_path))
    if os.path.isfile(candidate):
        input_meta = candidate
    else:
        print(f"Error: File not found: {abs_path}")
        sys.exit(1)
else:
    input_meta = abs_path

# Normalize path
input_meta = os.path.normpath(input_meta)
metadata_dir = os.path.dirname(input_meta)

# Determine base name without extension
base_name = os.path.splitext(os.path.basename(input_meta))[0]

# Set up rarity directory (relative to script)
rarity_dir = os.path.normpath(os.path.join(base_dir, '..', 'rarity'))

# Ensure directories exist
os.makedirs(metadata_dir, exist_ok=True)
os.makedirs(rarity_dir, exist_ok=True)

# Function to determine next version based on existing files
def next_version(dir_path, pattern):
    max_ver = 0
    for fname in os.listdir(dir_path):
        match = re.match(pattern, fname)
        if match:
            try:
                ver = int(match.group(1))
                if ver > max_ver:
                    max_ver = ver
            except ValueError:
                continue
    return max_ver + 1

# Patterns and static filenames (updated traits-stats naming)
json_pattern = rf"^{re.escape(base_name)}-new(\d+)\.json$"
rank_static = os.path.join(rarity_dir, f"{base_name}-rarity-ranks.txt")
# changed from trait-rarity-stats to traits-stats
stats_static = os.path.join(rarity_dir, f"{base_name}-traits-stats.txt")
rank_pattern = rf"^{re.escape(base_name)}-rarity-ranks-new(\d+)\.txt$"
stats_pattern = rf"^{re.escape(base_name)}-traits-stats-new(\d+)\.txt$"

# Determine next version numbers
new_json_ver = next_version(metadata_dir, json_pattern)
new_rank_ver = next_version(rarity_dir, rank_pattern) if os.path.exists(rank_static) else None
new_stats_ver = next_version(rarity_dir, stats_pattern) if os.path.exists(stats_static) else None

# Define output file paths
output_meta = os.path.join(metadata_dir, f"{base_name}-new{new_json_ver}.json")
output_rank = os.path.join(rarity_dir, f"{base_name}-rarity-ranks-new{new_rank_ver}.txt") if new_rank_ver else rank_static
output_stats = os.path.join(rarity_dir, f"{base_name}-traits-stats-new{new_stats_ver}.txt") if new_stats_ver else stats_static

# Load metadata
with open(input_meta, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Extract items from possible keys
if isinstance(data, list):
    items = data
elif 'collection_items' in data:
    items = data['collection_items']
elif 'items' in data:
    items = data['items']
else:
    items = []

if not items:
    print("No items found in metadata.")
    sys.exit(1)

total_items = len(items)
print(f"Retrieved {total_items} items. Version: new{new_json_ver}\nCalculating rarity...")

# Identify honorary or "1 of 1" items by checking for 'honorary' trait or trait_type '1 of 1'
honorary_ids = set()
for item in items:
    eid = item.get('ethscription_id', item.get('id'))
    for attr in item.get('item_attributes', []):
        trait = str(attr.get('trait_type', '')).lower()
        if trait == 'honorary' or trait == '1 of 1':
            honorary_ids.add(eid)
            break

# Count trait frequencies (include honorary items in frequency calc)
trait_counts = defaultdict(int)
for item in items:
    for attr in item.get('item_attributes', []):
        if attr.get('trait_type', '').lower() == 'rarity':
            continue
        key = (attr.get('trait_type'), attr.get('value'))
        trait_counts[key] += 1

# Prepare list with scores for all items
rank_list = []
for item in items:
    name = item.get('name', '')
    es_id = item.get('ethscription_id', item.get('id'))
    sum_score = 0.0
    best_score = 0.0
    best_trait = None
    for attr in item.get('item_attributes', []):
        if attr.get('trait_type', '').lower() == 'rarity':
            continue
        freq = trait_counts[(attr['trait_type'], attr['value'])]
        score = total_items / freq if freq else 0
        sum_score += score
        if score > best_score:
            best_score = score
            best_trait = (attr['trait_type'], attr['value'])
    rank_list.append({'id': es_id, 'name': name, 'sum': sum_score, 'best': best_trait})
# Sort by summed rarity descending
grab_list = sorted(rank_list, key=lambda x: x['sum'], reverse=True)

# Assign ranks: honorary or "1 of 1" items get rank 1, others start at 2
display_list = []
ranks = {}
curr_rank = 2
for entry in grab_list:
    eid = entry['id']
    if eid in honorary_ids:
        ranks[eid] = 1
    else:
        ranks[eid] = curr_rank
        curr_rank += 1
    display_list.append(entry)

# Sort display_list by rank to ensure proper ascending order
display_list.sort(key=lambda x: ranks[x['id']])

# Update metadata with rarity value in item_attributes
for item in items:
    eid = item.get('ethscription_id', item.get('id'))
    rank_val = ranks.get(eid)
    if rank_val is None:
        continue
    updated = False
    for attr in item.get('item_attributes', []):
        if attr.get('trait_type', '').lower() == 'rarity':
            attr['value'] = rank_val
            updated = True
            break
    if not updated:
        item.setdefault('item_attributes', []).append({'trait_type': 'rarity', 'value': rank_val})

# Write updated metadata to new JSON
with open(output_meta, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)
print(f"Wrote updated metadata to {output_meta}")

# Write rarity ranks to TXT
with open(output_rank, 'w', encoding='utf-8') as f:
    for entry in display_list:
        eid = entry['id']
        name = entry['name']
        best = entry['best'] if entry['best'] else ('N/A', 'N/A')
        rnk = ranks[eid]
        tr = f"{best[0]} - {best[1]}"
        link = f"https://marketplace.mfpurrs.com/details/{eid}"
        f.write(f"Rank {rnk} - {name} | Rarest trait = {tr} | Link: {link}\n")
print(f"Wrote rankings to {output_rank}")

# Write trait rarity statistics to TXT with honorary/"1 of 1" traits at top
# Separate special traits and others
special_entries = []
other_entries = []
for (tt, tv), cnt in trait_counts.items():
    tt_lower = tt.lower()
    if tt_lower == 'honorary' or tt_lower == '1 of 1':
        special_entries.append(((tt, tv), cnt))
    else:
        other_entries.append(((tt, tv), cnt))
# Sort special entries by rarity score descending (though all likely equal)
special_entries.sort(key=lambda x: (total_items / x[1] if x[1] else 0), reverse=True)
# Sort other entries by rarity score descending
other_entries.sort(key=lambda x: (total_items / x[1] if x[1] else 0), reverse=True)

with open(output_stats, 'w', encoding='utf-8') as f:
    f.write("-------------------------------------------------------------\n")
    f.write("Rarity Scores for Traits (special at top, then others):\n")
    f.write("-------------------------------------------------------------\n")
    # Write special first
    for (tt, tv), cnt in special_entries:
        sc = total_items / cnt if cnt else 0
        f.write(f"{tt} - {tv} | rarity score = {sc:.2f} | frequency = {cnt} / {total_items}\n")
    # Then write others
    for (tt, tv), cnt in other_entries:
        sc = total_items / cnt if cnt else 0
        f.write(f"{tt} - {tv} | rarity score = {sc:.2f} | frequency = {cnt} / {total_items}\n")
print(f"Wrote statistics to {output_stats}")
