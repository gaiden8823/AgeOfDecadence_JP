# The Age of Decadence 日本語化作業

作業ルート：`C:\GameModding\AgeOfDecadence_JP`。更新日：2026-10-08。

## 普段使うもの

- 起動：`tools/日本語化ツール.cmd`
- 操作説明：[使い方](tools/使い方.md)
- 環境・確認範囲・引き継ぎ：[引き継ぎ手順](guides/HANDOFF.md)
- 会話：`translations/dialogue_translation.csv`
- 会話以外：`translations/reviewed_translation_targets.csv`
- 画像文字：`translations/image_translation_targets.csv`（文字列ツールでは反映しない）
- 用語集・スタイルガイド：`guides/`
- 表示基盤コード：`tools/font_basis/`

## ビルドと反映

1で会話以外、4で会話も含めてビルドします。approved限定ではなく作業訳・レビュー訳も使います。保留対象は除外し、CSVの訳文・採用状態は変更しません。訳文列と状態名の統一はまだ行っていません。

ビルドだけではゲームを変更しません。成功後、ゲームを終了して2を選び、workingへの反映を確認してYESを入力します。バックアップ付きで反映します。3は直前の反映を戻します。STOPが出たら反映しません。

AoD.exe、日本語、文字サイズ100%で確認してください。125%は見切れが残ります。全作業訳を含めたビルドは2026-10-08にworkingへ反映済みです。戦闘チュートリアル2～10ページはユーザーが表示問題なしと確認しました。作品名の途中の自動改行は変更しない方針です。表示確認による採用状態の変更は行っていません。全画面確認・全訳校閲は未完了です。

## 環境と保全

Python 3.10以降が必要です。CSVのみなら標準ライブラリ、XLSX入力にはopenpyxlを使います。Pythonの場所はAOD_TOOL_PYTHON、ゲーム参照先はtools/state/settings.jsonで設定します。

workingにはAoDJapaneseFont基盤を導入済みで、旧JapaneseDisplayTestは無効化済みです。正規ゲームとWindows登録フォントBIZ UDPMincho Mediumが必要です。このリポジトリだけでゲーム本体やフォントファイルは取得できません。

旧成果物reference/legacy_workは参照・保全用で、現在の編集正本ではありません。ゲーム本体、画像素材、builds、backups、個人設定はGit管理外です。別媒体にも必要ファイルを保全してください。

## GitHub管理

接続先：gaiden8823/AgeOfDecadence_JP。GitHub Desktopで変更内容を確認し、コミット・Pushします。無断で送信しません。翻訳CSVにも原文が含まれるため、公開・配布前に権利条件を確認してください。
