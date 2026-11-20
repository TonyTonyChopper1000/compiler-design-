# Assignment 3 — `wc` in Lex, ignoring C comments

| File | What it is |
|---|---|
| `part_one.txt` | Part 1 scanner. Skips `/* ... */` comments with `input()`, the way Example 2.23 does. |
| `part_two.txt` | Part 2 scanner. Skips comments with an exclusive start condition (`%x COMMENT`). |
| `fact.c` | The sample input from the course folder. |
| `build_submission.py` | Puts your name and number into the files, runs the commands, takes the screenshots and builds the PDFs. |
| `submission/` | The four files to upload. They still contain the `STUDENT_NAME` / `STUDENT_NUMBER` placeholders. |

## Build and run by hand

```bash
lex part_one.txt
gcc lex.yy.c -o part_one
./part_one fact.c        #  19  51  383   (lines words chars)
```

Part 2 works the same way with `part_two.txt`.

The scanners count the way `wc` does: every newline is a line, a word is a run of characters
that are not whitespace, and every byte is a character. Nothing inside a comment is counted,
including the `/*` and `*/` delimiters. A comment does not split a word, so `ab/*x*/cd`
counts as the single word `abcd`. A comment with no closing `*/` runs to the end of the input.
For `fact.c` the output matches `wc` run on a copy with the comments stripped out.

## Making the submission files with your details

```bash
sudo apt install build-essential flex -y
pip install reportlab playwright && python3 -m playwright install chromium
python3 build_submission.py "First Last" "StudentNumber"
```

This writes `submission/part_one.txt`, `part_one.pdf`, `part_two.txt` and `part_two.pdf`.
Each PDF has your name and number in the header of every page. Page 1 holds the source file,
and each screenshot gets its own page.

The script draws the screenshots from the real command output. If your instructor wants actual
screenshots of your own editor and terminal, take them yourself (steps 4, 8, 12, 20, 24 and 27).
