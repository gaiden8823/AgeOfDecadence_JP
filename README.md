# The Age of Decadence 日本語化MOD

The Age of Decadence 日本語化MOD。本文・UI・画像内の文字を日本語化。CMD形式の導入ツール付き、Python不要。フォント差し替え対応。

## ダウンロードと導入

[リリースページ](https://github.com/gaiden8823/AgeOfDecadence_JP/releases)から `AgeOfDecadence_JP_20261010.zip` をダウンロードしてください。GitHubが自動生成する「Source code」のZIPは導入用ではありません。

ZIPを展開し、`日本語化.cmd` と `AoDJP` フォルダを `AoD.exe` と同じゲームフォルダに置きます。ゲームを終了して `日本語化.cmd` を起動し、2を入力してEnterを押します。導入後はオプションの言語一覧で「日本語」を選びます。

詳しい手順は配布物の `導入手順.txt`、または[導入手順](tools/release/導入手順.txt)をご覧ください。

## フォント・更新・注意事項

- フォントは同梱しません。標準ではWindows側の BIZ UDPMincho Medium を使用します。存在しない場合は日本語対応フォントの用意が必要です。
- `AoDJP/fonts/` に日本語対応のttf・otf・ttcを置き、ツールの4で変更できます。全フォントの互換性は保証しません。画像内の文字は変わりません。
- 元に戻す場合はゲームを終了して3を選びます。更新時は以前のツールで復元してから新しい配布物を導入してください。
- 画面のちらつきは日本語化MODではなく元のゲーム由来の不具合です。`AoD64.exe` ではなく `AoD.exe` から起動してください。
- 導入・復元のファイル照合は検証済みですが、全画面・全ミッションの通しプレイは未完了です。文字サイズ125%は見切れが残る場合があります。

## 開発・検証用の記録

以下は開発者向けの作業記録です。配布版の利用にPythonは不要です。

## 2026-10-10 の最新検証構成

最新修正は `addon_validation` の混合方式で検証しています。更新内容・確認範囲・制限は [更新記録](guides/UPDATE_20261010.md) を参照してください。表示コードは `tools/runtime_modules/`、配布候補作成・導入・復元の手順は [配布手順](tools/release/README_ja.md) に保存しています。ゲーム本体・画像素材・配布ZIP・フォントはGitHubに含めません。旧ビルドの再適用による表示修正の巻き戻りに注意してください。

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
