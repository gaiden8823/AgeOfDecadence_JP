# The Age of Decadence 日本語化作業

## 普段使うもの

- 起動：`tools/日本語化ツール.cmd`
- 会話以外の翻訳：`translations/reviewed_translation_targets.csv`
- 画像内文字の翻訳：`translations/image_translation_targets.csv`（文字列ツールでは反映しない）
- 会話の翻訳：`translations/dialogue_translation.csv`
- 用語集・スタイルガイド：`guides/`
- 日本語化した画像：`images/japanese/`

## ツールの使い方

ゲームを終了して起動します。5 は下訳込みの文字列ビルド、1 は確定欄のみ、4 は会話も含めたビルドです。成功したら再度起動し、2 で反映先を確認して YES を入力します。3 は直前の反映を戻します。AoD.exe で起動し日本語を選択します。STOP が出たら反映しないでください。

ビルドは `builds/`、反映前バックアップは `backups/`、最新状態は `tools/state/` です。Python 3 と openpyxl が必要です。既定の Python がない環境では AOD_TOOL_PYTHON を設定してください。ゲーム参照先は `tools/state/settings.json` です。日本語フォント基盤は既存の working 環境を使用します。このリポジトリだけで元ゲームやフォント基盤は再配布しません。

## 参考資料と旧配置

`reference/legacy_work/` は移行時の旧作業の保存コピーです。中の古いツールや CSV は普段の編集に使用しません。`reports/` は移行・検証記録です。既存の `source/`、`working/`、`translation/`、`output/` は変更せず残しています。旧チャットの作業場所も検証のため残しています。以後の編集は上記 translations に統一してください。

## GitHub 管理

Git はこのフォルダー全体をルートとし、.gitignore で追跡対象を限定します。ゲーム本体、抽出画像、参考 MOD、生成物、バックアップ、個人環境設定は登録しません。翻訳 CSV には英語原文が含まれるため、まず非公開リポジトリで管理し、公開や配布の前に権利・配布条件を確認してください。

画像も元ゲームのテクスチャを含むため初期登録から除外しています。GitHub 接続先が決まるまでコミット・アップロードは行いません。
