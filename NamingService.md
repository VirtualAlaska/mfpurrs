<a align="center" width="100vw" href="https://mfpurrs.com" target="_blank">
<center>
 <img src="https://iili.io/HQyYOtp.png"/>
</center>
</a>

# The MFPurrs Naming Service
### Give your purr a unique name, verifiable on-chain, forever.

The MFPurrsNamingAgency is a Solidity contract that stores and index of all MFPurrs' names. Owned of these MFPurrs are allowed to name each of their purrs one time. This name must be unique and cannot be changed at a later date. The agency takes a 0.0015 ETH fee per name, and the gas costs on average ~0.002 ETH. All cats are available for viewing on the [Official MFPurrs Website](https://mfpurrs.com) by going to `/view/[MFPurr ID]` like this: [https://mfpurrs.com/view/1234](https://mfpurrs.com/view/1234)

The Smart Contract is deployed on the Ethereum mainnet, and the code is viewable [here](https://etherscan.io/address/0x59252a16f7c18d3ca4ace893b2e6975364676102#code). Contract code and verification system created by [@maxbridgland](https://twitter.com/maxbridgland)

## How the system works

When you go to [View Your Cats](https://mfpurrs.com/owned) on the mfpurrs website, you will be able to connect your wallet, select a cat, and give that cat a name if it doesn't already have one. When submitting your name, the following process occurs:

1. You sign a message (**this is not a transaction, you are just verifying your wallet with our verification platform. This is to prevent bad actors from naming cats they don't actually own**) that includes the purr's name, token ID, your address, and a timestamp that relates to when the signature will expire. If you do not confirm the transaction within 5 minutes of creating the signature, your transaction will fail.
2. This signed message is sent to our API and we verify the following:
   - You are who you say you are
   - Your name is not a duplicate
   - Your name does not contain profanity that may be harmful to the project
   - Your the owner of the MFPurr you are trying to name
3. If all of these things are verified and passing, we sign a message that is passed to the contract to verify your name has been approved for being set.
4. You submit a transaction with the previous arguments and the signed message along with a **0.0015 ETH** naming fee and any gas costs associated. On average this will cost ~$6.
5. The transaction is confirmed and your cat has a new name that is verifiable on the blockchain!

## Verifying MFPurr names

### To verify your MFPurr's name, or any MFPurr's name, you have multiple options.

**Option 1: The Official MFPurr Website**

1. Take the MFPurr ID (**this is not the same as item_index. The item_index is MFPurrID-1, so if you are using item_index, add 1 to it!**) from any marketplace with valid metadata.*
2. Go to: `https://mfpurrs.com/view/[id]` but replace `[id]` with the MFPurr ID you got in Step 1, without the brackets. (ex.: https://mfpurrs.com/view/1234)
3. Name will be viewable on this page under the traits and header.

\* ordex.ai listings must be refreshed for new metadata to show up. some may be out of date.

**Option 2: Etherscan.io**

1. Go to [this link](https://etherscan.io/address/0x59252a16f7c18d3ca4ace893b2e6975364676102#readContract).
2. Open the `getName` function.
3. Type the MFPurr ID into the `tokenId` field.

### To check if an MFPurr's name is taken follow these steps:

1. Go to [this link](https://etherscan.io/address/0x59252a16f7c18d3ca4ace893b2e6975364676102#readContract).
2. Open the `nameAvailable` function.
3. Type the name you wish to give. (**No leading or trailing spaces, and has to be all lowercase**)
