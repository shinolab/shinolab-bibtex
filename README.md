# 篠田・牧野研究室 BiBTeX ソース

研究室で共有すべきBibTexソースファイルをまとめたリポジトリです.

## 追加方法

> NOTE: このリポジトリへの書き込み権限が必要になります. 権限の付与を希望する場合は管理者に連絡してください.

このリポジトリを直接クローンしたうえで, 適当な`*.bib`ファイルを追加し, pull requestsを作成してください.

**`all.bib`ファイルは直接変更しないでください.**

追加されたファイル内の各エントリは, 以下のルールに従ってキーが変更された後, [`all.bib`](all.bib)ファイルに自動的にマージされます.
その後, 変更サマリーがPull Requestにコメントされます. 問題がなければ, Pull Requestをマージしてください.

重複しているエントリは無視されるので, 重複分を手動で削除する必要はありません.

GitHubから行う場合は, [メインページ](https://github.com/shinolab/shinolab-bibtex)上部の「Add file」ボタンからファイルを追加してください.

なお, 追加されたファイルは, `<日付>-<時刻>`がファイル名の先頭に付与され, [`bak`](bak)ディレクトリに移動されます.

## キーのネーミングについて

- 各エントリのキーは以下のルールに従って変更されます.
  - `{Author's lastname}-{year}-{short title}`
    - `{Author's lastname}`は通常, 第一著者の性になります
      - ただし, `author`フィールドが`{}`で囲まれている場合は, その中身を小文字に変換して, スペースを`_`に置換したものになります.
    - ここで`{short title}`は`title`の先頭3単語を`_`で結合したものです
      - ただし, `{`, `}`, `,`, `:`などの文字は無視されます

## Limitation

- 既に同一のエントリが存在する場合, フィールドの追加は行えますが, 変更は不可能です
  - フィールドを変更, 修正する必要がある場合は, 管理者に連絡してください.

# Author
Shun Suzuki, 2025
