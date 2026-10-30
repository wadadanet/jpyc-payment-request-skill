#!/bin/sh
# Run by scripts/validate-local.sh; first failure stops the push.
run_check 'python -c "import ast,pathlib; ast.parse(pathlib.Path("scripts/build_payment_link.py").read_text(encoding="utf-8"))"'

# 既存の自動試験はありません。Python 標準ライブラリの AST 解析で補助スクリプトの構文を確認します。送金・署名・RPC 呼出しは実行しません。Git、POSIX sh、Python 3 が必要です。
