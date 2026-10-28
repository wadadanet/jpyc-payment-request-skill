#!/usr/bin/env python3
"""Build an EIP-681 payment request URI and a MetaMask deep link for an ERC-20 transfer.

Example:
    python3 build_payment_link.py \
        --contract 0xE7C3D8C9a439feDe00D2600032D5dB0Be71C3c29 \
        --to 0xRecipientAddress --amount 100 --chain 137

Add --qr out.png to also write a QR code image (requires: pip install qrcode[pil]).
"""
import argparse
from decimal import Decimal

KNOWN_JPYC = {
    "0xe7c3d8c9a439fede00d2600032d5db0be71c3c29": "JPYC (2025, regulated)",
    "0x431d5dff03120afa4bdf332c61a6e1766ef37bdb": "JPY Coin v2 (legacy)",
}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--contract", required=True, help="ERC-20 token contract address")
    ap.add_argument("--to", required=True, help="Recipient address")
    ap.add_argument("--amount", required=True, help="Amount in token units, e.g. 100 or 1.5")
    ap.add_argument("--decimals", type=int, default=18, help="Token decimals (default 18)")
    ap.add_argument("--chain", type=int, default=137, help="Chain ID (default 137 = Polygon)")
    ap.add_argument("--qr", help="Optional path to write a QR code PNG of the EIP-681 URI")
    args = ap.parse_args()

    raw = int(Decimal(args.amount) * (10 ** args.decimals))
    uri = (
        f"ethereum:{args.contract}@{args.chain}/transfer"
        f"?address={args.to}&uint256={raw}"
    )
    link = (
        f"https://metamask.app.link/send/{args.contract}@{args.chain}/transfer"
        f"?address={args.to}&uint256={raw}"
    )

    kind = KNOWN_JPYC.get(args.contract.lower())
    if kind:
        print(f"Token: {kind}")
    else:
        print("Token: unknown contract, double-check the address before use")
    print(f"EIP-681 URI: {uri}")
    print(f"MetaMask deep link: {link}")

    if args.qr:
        import qrcode

        img = qrcode.make(uri)
        img.save(args.qr)
        print(f"QR code written to {args.qr}")


if __name__ == "__main__":
    main()
