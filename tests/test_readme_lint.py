import os, sys, tempfile, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import readme_lint as r

GOOD = """# Tool

A small tool that does one useful thing very well.

## Install
pip install tool

## Usage
```
tool --help
```
See [docs](docs.md) and [usage](#usage).

## Contributing
PRs welcome.

## License
MIT
"""


class T(unittest.TestCase):
    def test_perfect(self):
        with tempfile.TemporaryDirectory() as d:
            open(os.path.join(d, "docs.md"), "w").close()
            score, f = r.lint(GOOD, d)
            self.assertEqual((score, f), (100, []))

    def test_empty(self):
        score, f = r.lint("hello", ".")
        self.assertEqual(score, 15)  # only the "no broken links" points
        self.assertEqual(len(f), 7)

    def test_broken_links(self):
        with tempfile.TemporaryDirectory() as d:
            bad = r.broken_links("[a](nope.md) [b](https://x.y) [c](#missing) ![i](img.png)", d)
            self.assertEqual(bad, ["nope.md", "#missing", "img.png"])

    def test_links_in_code_ignored(self):
        self.assertEqual(r.broken_links("```\n[a](nope.md)\n```", "."), [])

    def test_japanese_headings(self):
        txt = "# ツール\n\nこれは十分に長い説明文の段落です。\n\n## インストール\nx\n\n## 使い方\n```\nx\n```\n\n## ライセンス\nMIT\n"
        score, f = r.lint(txt, ".")
        self.assertEqual([x["code"] for x in f], ["contributing"])


if __name__ == "__main__":
    unittest.main()
