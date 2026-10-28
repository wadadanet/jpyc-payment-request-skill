# JPYC Payment Requests

## Keep custody with the user

- Let the user hold the wallet and the only private key. Never create, receive or store a key for the user's funds, and never ask for a seed phrase or private key.

- Prepare the payment request with the exact token contract, recipient and amount, and let the user review and sign it inside their own wallet app. Your approval step never replaces the wallet signature.

- Verify the result on chain yourself with a public RPC instead of trusting a screenshot or a success message.

## Identify the token first

- Know that two different tokens answer to JPYC. The regulated JPYC issued in 2025 uses contract 0xE7C3D8C9a439feDe00D2600032D5dB0Be71C3c29, and the older JPY Coin v2 uses 0x431D5dfF03120AFA4bDf332c61A6e1766eF37BDB.

- Confirm which token the user holds before building any request, from the contract address shown in their wallet or by reading the token over RPC. Both tokens use 18 decimals and keep the same contract address across EVM chains.

- Read token facts with `muse.exec` and curl against a public Polygon RPC. Call decimals with data 0x313ce567 and balanceOf with selector 0x70a08231 followed by the padded address.

- Prefer https://polygon-bor-rpc.publicnode.com and https://polygon.drpc.org, which both answered in testing. Expect free tiers to cap eth_getLogs ranges, and switch endpoints instead of retrying a capped one.

## Ask which wallet, then build that wallet's link

- Ask the user which wallet app they will pay from before building anything, unless the conversation already establishes it. Remember the answer for next time instead of asking again.

- Look the wallet up in the supported list below and generate its link exactly in that format with scripts/build_payment_link.py. Each wallet defines its own format and its own amount convention, so never reuse one wallet's link shape for another.

- Say plainly that a wallet is not supported when it is missing from the list, and hand over the recipient address and the exact amount as copyable text for manual entry. Never improvise a link format, and never substitute a hosted payment page.

- Encode the transfer internally as an EIP-681 URI in the form ethereum:<contract>@<chainId>/transfer?address=<recipient>&uint256=<amount>, multiplying the JPYC amount by 10^18 and using chainId 137 for Polygon. Offer it as a QR code only when the user has a second screen or a printed copy to scan.

## Supported wallets

- MetaMask, verified end to end in a real payment. Token link https://metamask.app.link/send/<contract>@<chainId>/transfer?address=<recipient>&uint256=<raw amount>, and native coin link https://metamask.app.link/send/<address>@<chainId>?value=<wei>. Current MetaMask docs use the host link.metamask.io with the same structure.

- Trust Wallet, format verified in the official developer docs. Link https://link.trustwallet.com/send?asset=c<coin>_t<contract>&address=<recipient>&amount=<amount>, where <coin> is the SLIP-44 coin id, 966 for Polygon, 60 for Ethereum and 714 for BNB Chain. The docs example passes the amount in human units, though the docs never state the unit, so confirm with a small test payment on first use.

- Bitget Wallet, format verified in the official docs and not yet device tested. Android universal link https://bkcode.vip?action=send&chain=<chain>&contract=<contract>&to=<recipient>&amount=<amount>&actionId=<uuid>&version=1, with the iOS scheme bitkeep://bkconnect carrying the same parameters. The Polygon chain name is matic. The docs do not state the amount unit, so confirm with a small test payment on first use.

- TokenPocket, format verified in the official docs and not yet device tested. Link tpoutside://pull.activity?param=<url encoded JSON> with action transfer, a decimal amount and a separate decimal field. Confirm with a small test payment on first use.

## Wallets without a documented send link

- Coinbase Wallet, OKX Wallet, Phantom, Rabby, Rainbow, imToken, SafePal, Uniswap Wallet, Backpack and Ginco publish no prefilled send link as of October 2026, so treat them as not supported and fall back to the address and amount as text.

- HashPort Wallet publishes no send link either, even though it is the most common wallet among Japanese JPYC holders, renewed from the Expo 2025 digital wallet. Its documented payment flows use QR codes inside its own merchant system, and its developer integrations are partner only, so treat it as not supported and fall back to the address and amount as text.

- Zerion documents EIP-681 QR scanning in its store release notes, so the EIP-681 QR code can work there when the user has a second screen. Treat that as the only documented exception.

## Verify the transfer

- Read the recipient balanceOf before and after the expected transfer, and report the exact amount that arrived.

- Find the sender of a past transfer from the Transfer event log. Filter eth_getLogs by the token contract, the Transfer topic 0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef and the recipient as the third topic, and read the sender from the second topic.

## Size gas money honestly

- Price the gas before asking the user to fund it. Read the current POL price in yen and eth_gasPrice, and multiply a transfer estimate of about 65,000 gas to get the real cost.

- Ask for at most about twice the estimated cost. In October 2026 a Polygon JPYC transfer used about 60,000 gas and cost roughly 0.012 POL, about 0.2 yen, while 0.1 POL was worth about 1.45 yen and overshot the amount being recovered.

## Sign only from throwaway addresses

- Sign with `muse.exec` and the eth_account package in a Python virtual environment when a test address you created has to send funds back. Keep any throwaway key file outside this skill, with owner-only permissions.

- Keep the gas price bump near 1.05 times the network suggestion and the gas limit near 1.1 times the estimate, so the transaction cost stays under a small funded balance.
