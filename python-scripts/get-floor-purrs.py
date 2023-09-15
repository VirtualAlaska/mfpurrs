import requests
from rich import print
import json
from typing import List, Optional

METADATA = json.load(open('./metadata/metadata-mfpurrs.json', 'r+'))

class Listing:
    id: str
    name: str
    uri: str
    price: int
    priceUsd: int = 0
    market: str
    item_attributes: List[dict[str,str]]

    def __init__(self, _id, name, uri, price, priceUsd, market, item_attributes) -> None:
        self.id = _id
        self.name = name
        self.uri = uri
        self.price = price
        self.priceUsd = priceUsd
        self.market = market
        self.item_attributes = item_attributes

def get_collection_item_by_id(data, ethscription_id):
    for item in data['collection_items']:
        if item['ethscription_id'] == ethscription_id:
            return item['item_attributes']
    return None

def get_lowest_price_listing(listings: List[Listing], trait_type: str, value: str) -> Optional[Listing]:
    # Filter listings that have the specified trait type and value
    valid_listings = [listing for listing in listings if any(attr.get('trait_type') == trait_type and attr.get('value') == value for attr in listing.item_attributes)]
    
    # Find and return the listing with the lowest price
    return min(valid_listings, key=lambda listing: listing.price, default=None)


def get_etch_listings() -> list[Listing]:
    listings = []
    typed_listings = []
    index = 1
    while (True):
        res = requests.get(f'https://www.etch.market/api/markets/ethscriptions/listed?category=nft&collection=mfpurrs&show=OnlyBuyNow&sortBy=PriceAsc&trait=&searchBy=&page.size=100&page.index={index}')
        ethscriptions = res.json()['data']['ethscriptions']
        if (len(ethscriptions) == 0):
            break
        listings += ethscriptions
        index += 1
    for l in listings:
        attrs = get_collection_item_by_id(METADATA, l['order']['ethscriptionId'])
        typed_listings.append(Listing(
            l['order']['ethscriptionId'],
            'mfpurrs ' + l['order']['tokenId'],
            l['order']['content'],
            float(l['order']['price']),
            float(l['order']['priceUsd']),
            'etch',
            attrs
        ))

    return typed_listings

def get_ordex_listings() -> list[Listing]:
    listings = []
    typed_listings = []
    res = requests.post('https://api.ordex.ai/v0.1/items/search/', json={
        'filter': {
            'blockchains': [
                'ETHEREUM_ETHSCRIPTION'
            ],
            'collections': [
                'ETHEREUM_ETHSCRIPTION:mfpurrs'
            ],
            'sellPriceFrom': 0.001,
            'sellPriceTo': 10000000
        },
        'size': 1_000
    }, headers={
        'Content-Type': 'application/json',
        'Host': 'api.ordex.ai',
        'Origin': 'https://ordex.ai',
        'Accept': 'application/json',
    })
    continuation = res.json().get('continuation', None)
    listings = res.json()['items']
    while (continuation != None):
        res = requests.post('https://api.ordex.ai/v0.1/items/search/', json={
            'filter': {
                'blockchains': [
                    'ETHEREUM_ETHSCRIPTION'
                ],
                'collections': [
                    'ETHEREUM_ETHSCRIPTION:mfpurrs'
                ],
                'sellPriceFrom': 0.001,
                'sellPriceTo': 10000000
            },
            'size': 1_000,
            'continuation': continuation
        }, headers={
            'Content-Type': 'application/json',
            'Host': 'api.ordex.ai',
            'Origin': 'https://ordex.ai',
            'Accept': 'application/json',
        })
        new_listings = res.json()['items']
        continuation = res.json().get('continuation', None)
        if (len(new_listings) == 0) or continuation is None:
            break
        listings += new_listings
    
    for l in listings:
        if l.get('bestSellOrder', None) is not None:
            attrs = get_collection_item_by_id(METADATA, l['id'].split(':')[-1])
            typed_listings.append(Listing(
                l['id'].split(':')[-1],
                l['meta']['name'],
                l['meta']['rawContent'],
                float(l['bestSellOrder']['makePrice']),
                float(l['bestSellOrder']['makePriceUsd']),
                'ordex',
                attrs
            ))
    return typed_listings

ordex_listings = get_ordex_listings()
etch_listings = get_etch_listings()

total_listings = ordex_listings + etch_listings

print(f'Total Etch.Market Listings: {len(etch_listings)}')
print(f'Total Ordex Listings: {len(ordex_listings)}')

trait_type = ''
value = ''

while True:
    tt = input('\nEnter a trait type: ')
    v = input('Enter a value to search for: ')
    print('\n')
    listing = get_lowest_price_listing(total_listings, tt, v)
    if (listing != None):
        print(f'Found an MFPurr on the floor!'.center(45, '='))
        print(f'Market: {listing.market}')
        print(f'Name: {listing.name}')
        print(f'View on ethscriptions.com:\nhttps://ethscriptions.com/ethscriptions/{listing.id}')
        print(f'Price in USD: ${listing.priceUsd}')
        print(f'Price in ETH: {listing.price}')
        print(f''.center(45, '='))
