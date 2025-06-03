# mfpurrs

Tools and assets for the mfpurrs project (Ethscriptions)

What are mfpurrs? - [Learn More](https://medium.com/@virtualalaska/what-are-mfpurrs-1f339403e788)

---

## Rarity Calculation Script

This repository includes a Python script (`calculate-rarity.py`) that computes and updates rarity rankings for all mfpurrs based on their trait frequencies. Starting with version `new1`, every run auto-increments the suffix for all outputs. The script performs three main tasks:

1. **Rarity Score Calculation**

   * **Trait Frequency Counting**: Reads `metadata/metadata-mfpurrs.json` and tallies how often each `(trait_type, value)` pair appears, ignoring any existing `rarity` attributes.
   * **Rarity Scoring**: For each NFT, computes an inverse-frequency score for each trait:

     $$
     \text{score}_{\text{trait}} = \frac{N}{\text{frequency of that trait}}
     $$

     where $N$ is the total number of items (10,000).
   * **Summed Rarity**: Sums every trait’s score to get a total rarity weight per NFT.

2. **Rank Assignment**

   * **Sorting**: Orders NFTs descending by their summed rarity weight.
   * **Honorary Overrides**: Seven special mfpurrs (`#9606, #9607, #9622, #9767, #9838, #9896, #9992`) are forced to rank 1.
   * **Rank Numbering**: Honorary items remain at rank 1; all others begin at rank 2 in the sorted order.

3. **Outputs & Versioning**
   Each run detects existing versioned files and increments to the next `newX` suffix:

   * **Updated Metadata JSON**: `metadata/metadata-mfpurrs-newX.json` – mirrors the input but with each item’s `"rarity"` attribute set to its assigned integer rank.

   * **Rarity Rankings File**:

     * On first run: `rarity/rarity-rankings.txt`
     * Subsequent runs: `rarity/rarity-rankings-newX.txt`
       Lists each NFT’s rank, name, its single rarest trait, and a link:

     ```
     Rank 1 - mfpurr #9606 | Rarest trait = honorary - virtual alaska | Link: https://marketplace.mfpurrs.com/details/<ethscription_id>
     ```

   * **Trait Statistics**:

     * On first run: `rarity/rarity-statistics.txt`
     * Subsequent runs: `rarity/rarity-statistics-newX.txt`
       Details every trait’s rarity score and frequency sorted from most rare to least.

### Usage

1. Place your original metadata at `metadata/metadata-mfpurrs.json`.
2. Run:

   ```bash
   python calculate-rarity.py
   ```
3. Inspect the newly created `newX` files:

   * `metadata/metadata-mfpurrs-newX.json`
   * `rarity/rarity-rankings(-newX).txt`
   * `rarity/rarity-statistics(-newX).txt`

---

*Script maintained by the mfpurrs team.*
