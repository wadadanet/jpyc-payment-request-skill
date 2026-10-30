# ローカル検証

GitHub Actions はデプロイ（配布用成果物の生成を含む）に限定します。
テスト・lint・型チェック・検証ビルドはこのリポジトリのローカル pre-push フックで実行します。

各 clone で一度 `sh scripts/install-hooks.sh` を実行してください。コミット後、tracked 変更のない状態で `sh scripts/validate-local.sh` から同じ検査を手動実行できます。
検査失敗・HEAD と push 対象の不一致・検査前後の tracked 変更があると push を停止します。以前の成功記録を再利用せず、各 push で検査を実行します。

成功時は Git 管理領域の `local-validation/<完全なSHA>.md` に実行環境・時刻・コマンド・結果を記録します。PR 本文へその記録と、未実行・失敗・対象外の項目と理由を転記してください。

## 検査内容

- `git show --format= --check HEAD`
- `python -c "import ast,pathlib; ast.parse(pathlib.Path("scripts/build_payment_link.py").read_text(encoding="utf-8"))"`

既存の自動試験はありません。Python 標準ライブラリの AST 解析で補助スクリプトの構文を確認します。送金・署名・RPC 呼出しは実行しません。Git、POSIX sh、Python 3 が必要です。
