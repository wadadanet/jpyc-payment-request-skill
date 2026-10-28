# JPYC Payment Requests

AIエージェントが秘密鍵を持たずに、JPYCの支払いリクエストを作成し、ユーザーが自分のウォレットで承認・署名して送金するためのスキル（手順書）です。

エージェントは「宛先と金額を正確に用意して届ける」ところまでを担当し、送金の署名は必ずユーザー本人のウォレットの中で行われます。エージェント単独では1円も動かせない設計がポイントです。

## 仕組み

1. エージェントが送金内容（トークンのコントラクト、宛先、金額）を埋め込んだ支払いリクエストを作成する
2. モバイルではQRコードではなく、ウォレットアプリを開くディープリンク（MetaMask形式）で渡す。QRは相手が別画面で読める場合だけ使う
3. ユーザーがウォレットアプリで宛先と金額を確認し、承認・署名して送信する
4. エージェントが公開RPCで残高とTransferイベントを確認し、着金を報告する

リクエストはEIP-681形式のURIで表現します。

```text
ethereum:<contract>@<chainId>/transfer?address=<recipient>&uint256=<amount>
```

MetaMaskディープリンク形式:

```text
https://metamask.app.link/send/<contract>@<chainId>/transfer?address=<recipient>&uint256=<amount>
```

## 重要な注意：JPYCは2種類ある

同じ「JPYC」を名乗るトークンが2つ存在します。コントラクトアドレスを必ず確認してください。

| 種類 | コントラクトアドレス（EVM各チェーン共通） |
| --- | --- |
| 新JPYC（2025年発行、資金決済法に基づく電子決済手段） | `0xE7C3D8C9a439feDe00D2600032D5dB0Be71C3c29` |
| 旧JPY Coin v2 | `0x431D5dfF03120AFA4bDf332c61A6e1766eF37BDB` |

どちらも decimals は 18 です。偽トークンも多数存在するため、上記以外のアドレスは使わないでください。

## ファイル構成

- `SKILL.md` — エージェント向けの手順書本体（このリポジトリの主役）
- `skill.yaml` — スキルのメタデータ
- `scripts/build_payment_link.py` — ウォレット別に支払いリンクを生成するスクリプト

## 対応ウォレット

ディープリンクはウォレットごとに仕様がバラバラです。このスキルでは、まずユーザーに「どのウォレットを使っているか」を聞き、対応表にあるウォレットだけ、その形式でリンクを生成します。対応表にないウォレットは、無理に代替案を作らず「対応していない」と正直に伝え、宛先アドレスと金額を手入力用に渡します。

| ウォレット | 送金リンク | 金額の形式 | 根拠 |
| --- | --- | --- | --- |
| MetaMask | `https://metamask.app.link/send/<contract>@<chain>/transfer?address=<to>&uint256=<raw>` | 最小単位の整数 | 実送金で検証済み |
| Trust Wallet | `https://link.trustwallet.com/send?asset=c<coin>_t<contract>&address=<to>&amount=<amount>` | 人間単位（ドキュメントの例より） | 公式開発者ドキュメント |
| Bitget Wallet | `https://bkcode.vip?action=send&chain=matic&contract=<contract>&to=<to>&amount=<amount>&actionId=<uuid>&version=1` | ドキュメントに明記なし | 公式ドキュメント（実機未検証） |
| TokenPocket | `tpoutside://pull.activity?param=<URLエンコードしたJSON>`（action: transfer） | 10進数＋decimalフィールド | 公式ドキュメント（実機未検証） |

対応していないウォレット（2026年10月時点、公式に送金リンクの形式が無いもの）：Coinbase Wallet、OKX Wallet、Phantom、Rabby、Rainbow、imToken、SafePal、Uniswap Wallet、Backpack、Ginco、HashPort Wallet など。HashPort Walletは日本のJPYC保有者では最も使われているウォレット（万博のEXPO2025デジタルウォレットの後継）ですが、送金リンクは公開されておらず、決済は自社加盟店のQRコード経由が公式の導線です。Zerionのみ、EIP-681のQR読み取りがストアの更新情報で言及されています。

## 使い方

`SKILL.md` と `skill.yaml` を、利用するAIエージェントのスキルフォルダにコピーしてください（例：Muse の `~/workspace/custom-skills/jpyc_payment_request/`）。SKILL.md形式に対応した他のエージェントでも利用できます。

サンプルスクリプト（`--wallet` でウォレットを選びます）:

```bash
python3 scripts/build_payment_link.py \
  --wallet metamask \
  --to 0xRecipientAddress \
  --amount 100 \
  --chain 137
```

`--wallet` には `metamask` / `trust` / `bitget` / `tokenpocket` が指定でき、そのウォレットの形式の送金リンクを出力します。コントラクトのデフォルトは新JPYC（Polygon）です。

## ガス代について

Polygonなどで送金する際は、ガス代として少額のネイティブ通貨（POL）が必要です。2026年10月の実測では、JPYCのtransfer 1件は約60,000 gas、約0.012 POL（約0.2円）でした。ガス代の補充を頼むときは、価格とガス単価から実費を見積もってからにしてください。多めに頼むと「1円を取り戻すのに1.45円分のPOL」のような本末転倒が起きます。

## セキュリティ

- エージェントに秘密鍵やシードフレーズを渡さないでください。このスキルは「エージェントが鍵を持たない」ことが前提です
- 署名する前に、ウォレットの画面で宛先アドレスと金額を必ず目で確認してください
- 初めての宛先には、まず少額でテスト送金してください

## ライセンス

MIT License
