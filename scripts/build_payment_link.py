#!/usr/bin/env python3
"""Build a JPYC payment-request deep link for the user's wallet.

Ask the user which wallet they use, then generate that wallet's link with
this script. Only wallets with a documented send format are supported.

Supported wallets and amount conventions (see SKILL.md for sources):
  metamask    raw integer amount (uint256). Verified end to end.
  trust       human units, Trust Wallet universal asset id.
  bitget      amount unit is not stated in Bitget's docs. Test small first.
  tokenpocket decimal amount plus a separate decimal field, JSON payload.

Usage:
  build_payment_link.py --wallet metamask --to 0xRecipient --amount 100
  build_payment_link.py --wallet trust --to 0xRecipient --amount 100
"""
import argparse
import json
import sys
import urllib.parse
import uuid

JPYC_NEW = "0xE7C3D8C9a439feDe00D2600032D5dB0Be71C3c29"  # 2025 JPYC (Polygon/Ethereum/Avalanche)

SLIP44 = {1: 60, 137: 966, 56: 714}  # Trust Wallet coin ids
BITGET_CHAIN = {1: "eth", 137: "matic", 56: "bnb", 8453: "base", 42161: "arbitrum", 10: "optimism"}
TOKENPOCKET_NETWORK = {1: "ethereum", 137: "polygon"}


def raw_amount(amount: str, decimals: int) -> int:
    """Convert a human amount (up to 6 decimal places) to the raw integer."""
    return int(round(float(amount) * 1_000_000)) * 10 ** (decimals - 6)


def metamask(contract, to, raw, chain, native, value_wei):
    if native:
        return f"https://metamask.app.link/send/{to}@{chain}?value={value_wei}"
    return (
        f"https://metamask.app.link/send/{contract}@{chain}/transfer"
        f"?address={to}&uint256={raw}"
    )


def trust(contract, to, amount, chain):
    if chain not in SLIP44:
        sys.exit(f"Trust Wallet: no verified SLIP-44 coin id for chain {chain}")
    asset = f"c{SLIP44[chain]}_t{contract}"
    q = urllib.parse.urlencode({"asset": asset, "address": to, "amount": amount})
    print("note: Trust amount units follow the docs example (human units); "
          "the docs do not state the unit explicitly.", file=sys.stderr)
    return f"https://link.trustwallet.com/send?{q}"


def bitget(contract, to, amount, chain):
    if chain not in BITGET_CHAIN:
        sys.exit(f"Bitget Wallet: no verified chain name for chain {chain}")
    q = urllib.parse.urlencode({
        "action": "send", "chain": BITGET_CHAIN[chain], "contract": contract,
        "to": to, "amount": amount, "actionId": str(uuid.uuid4()), "version": "1",
    })
    print("note: Bitget docs do not state the amount unit, and the format "
          "has not been device-tested.", file=sys.stderr)
    return f"https://bkcode.vip?{q}"


def tokenpocket(contract, to, amount, chain, decimals, symbol):
    if chain not in TOKENPOCKET_NETWORK:
        sys.exit(f"TokenPocket: no verified network name for chain {chain}")
    payload = {
        "action": "transfer",
        "amount": float(amount),
        "contract": contract,
        "decimal": decimals,
        "symbol": symbol,
        "to": to,
        "blockchains": [{"chainId": str(chain), "network": TOKENPOCKET_NETWORK[chain]}],
        "protocol": "TokenPocket",
        "version": "1.0",
        "dappName": "JPYC Payment Request",
        "actionId": str(uuid.uuid4()),
    }
    print("note: TokenPocket format follows the official docs "
          "(Ethereum example).", file=sys.stderr)
    return "tpoutside://pull.activity?param=" + urllib.parse.quote(
        json.dumps(payload, separators=(",", ":")), safe="")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--wallet", default="metamask",
                    choices=["metamask", "trust", "bitget", "tokenpocket"],
                    help="the wallet the user will pay from")
    ap.add_argument("--to", required=True, help="recipient address")
    ap.add_argument("--amount", default="1", help="amount in token units, e.g. 100 or 1.5")
    ap.add_argument("--value-wei", help="native coin amount in wei (MetaMask --native)")
    ap.add_argument("--contract", default=JPYC_NEW,
                    help=f"token contract (default: 2025 JPYC {JPYC_NEW})")
    ap.add_argument("--chain", type=int, default=137, help="chain id (default: 137 Polygon)")
    ap.add_argument("--decimals", type=int, default=18)
    ap.add_argument("--symbol", default="JPYC")
    ap.add_argument("--native", action="store_true", help="native coin instead of a token")
    args = ap.parse_args()

    raw = raw_amount(args.amount, args.decimals)
    if args.wallet == "metamask":
        print(metamask(args.contract, args.to, raw, args.chain, args.native, args.value_wei))
    elif args.wallet == "trust":
        print(trust(args.contract, args.to, args.amount, args.chain))
    elif args.wallet == "bitget":
        print(bitget(args.contract, args.to, args.amount, args.chain))
    elif args.wallet == "tokenpocket":
        print(tokenpocket(args.contract, args.to, args.amount, args.chain,
                          args.decimals, args.symbol))


if __name__ == "__main__":
    main()
