# readme-lint

**README を 0〜100 点で採点し、足りない項目を教えます。** タイトル、説明文、インストール、使い方、ライセンス、コードブロック、コントリビュート、そして**相対リンク切れ**をチェック。英語・日本語の見出しに対応。Python 3.10+ 標準ライブラリのみ、単一ファイル。

```console
$ python readme_lint.py
✗ -15  no Install / Getting started section
✗ -5   no Contributing section
✗ -15  broken relative links: docs/setup.md, #faq

score: 65/100
```

## 配点
| 項目 | 点 |
|---|---|
| 使い方 / Example の見出し | 20 |
| 説明文(タイトル直後の段落) | 15 |
| インストール / Getting started | 15 |
| リンク切れなし(相対パス・`#アンカー`・画像) | 15 |
| タイトル `# …` | 10 |
| ライセンス | 10 |
| コードブロック | 10 |
| コントリビュート | 5 |

コードブロック内のリンクは無視します。`http(s)://` などの外部リンクは確認しません(ネットワーク不要)。

## インストール
単一ファイルなので、ダウンロードするだけです(pip 不要)。
```
curl -O https://raw.githubusercontent.com/sndryu1/readme-lint/main/readme_lint.py
```

## 使い方
```
python readme_lint.py [README.md] [--min-score N] [--json]
```
- 終了コード: `0` OK / `1` 点数が `--min-score` 未満 / `2` ファイルなし

### CI (GitHub Actions)
```yaml
- uses: actions/checkout@v4
- run: python readme_lint.py --min-score 80
```

## テスト
`python -m unittest discover tests`

## License
MIT
