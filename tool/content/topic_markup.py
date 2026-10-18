"""Markup of journal topics: validation and automatic links.

The body of a topic is a small subset of Markdown, rendered by
lib/features/journal/presentation/widgets/topic_body.dart:

  paragraphs            separated by an empty line
  ## Heading            a section (no deeper levels)
  - item                bullet list
  1. item               numbered list (real sequences only)
  | a | b |             table (2–3 columns, up to 8 rows, `|---|` after the header)
  ```syntax ... ```     general form of a construct; Cyrillic words are placeholders
  `code`                inline code
  **bold**              emphasis (sparingly)
  [[topic_id|text]]     link to a topic; [[topic_id|`code`|term]] — link made by
                        autolinking, `term` points to the glossary entry for the sheet
  [[g:term|text]]       glossary-only entry (opens the sheet, no topic)

Some symbols are missing in the app's fonts and Android draws them as emoji
squares; they are rejected (see FORBIDDEN).
"""
import re

# Symbols that Android draws from the emoji font (or that Onest lacks).
FORBIDDEN = {
    "↔": "таблица или «и обратно»", "⇒": "«значит», «поэтому»", "➡": "слово", "⬅": "слово",
    "⬆": "слово", "⬇": "слово", "↩": "слово", "↪": "слово", "↕": "слово", "▶": "нумерованный список",
    "◀": "слово", "▸": "список", "✔": "«правильно»", "✅": "«правильно»", "☑": "«правильно»",
    "✖": "«ошибка»", "❌": "«ошибка»", "❎": "«ошибка»", "⚠": "**жирный** или ничего", "❗": "ничего",
    "❓": "ничего", "‼": "ничего", "⁉": "ничего", "ℹ": "ничего", "⭐": "ничего", "⏱": "ничего",
    "⌛": "ничего", "✏": "ничего", "✂": "ничего", "◻": "«-»", "◼": "«-»", "▪": "«-»", "▫": "«-»",
    "⬛": "«-»", "⬜": "«-»", "∞": "`float(\"inf\")`", "√": "`math.sqrt`", "ⁿ": "`n ** k`",
    "‑": "обычный дефис", "️": "удалить",
}

LINK = re.compile(r"\[\[([^\]|]+)\|([^\]|]+)(?:\|([^\]|]+))?\]\]")
CODE = re.compile(r"`([^`]+)`")
TABLE_RULE = re.compile(r"^\|(\s*:?-{3,}:?\s*\|)+$")


def blocks(body):
    """Splits a body into blocks: (kind, lines). Kinds: paragraph, heading,
    bullets, numbered, table, syntax."""
    result, lines, i = [], body.split("\n"), 0
    while i < len(lines):
        line = lines[i].rstrip()
        if not line.strip():
            i += 1
            continue
        if line.startswith("```"):
            assert line.strip() == "```syntax", ("only ```syntax blocks are allowed", line)
            j = i + 1
            while j < len(lines) and lines[j].strip() != "```":
                j += 1
            assert j < len(lines), ("unclosed ```syntax block",)
            result.append(("syntax", lines[i + 1:j]))
            i = j + 1
            continue
        if line.startswith("## "):
            result.append(("heading", [line[3:].strip()]))
            i += 1
            continue
        assert not line.startswith("#"), ("only ## headings are allowed", line)
        kind = ("bullets" if line.startswith("- ") else
                "numbered" if re.match(r"^\d+\. ", line) else
                "table" if line.startswith("|") else "paragraph")
        group = []
        while i < len(lines) and lines[i].strip():
            current = lines[i].rstrip()
            if kind != "paragraph" and group:
                starts = {"bullets": current.startswith("- "),
                          "numbered": bool(re.match(r"^\d+\. ", current)),
                          "table": current.startswith("|")}[kind]
                if not starts:
                    # A wrapped list item continues on the next line.
                    if kind == "table":
                        break
                    group[-1] += " " + current.strip()
                    i += 1
                    continue
            if kind == "paragraph" and (current.startswith(("- ", "## ", "|", "```")) or re.match(r"^\d+\. ", current)):
                break
            group.append(current if kind == "table" else current.strip())
            i += 1
        result.append((kind, group))
    return result


def plain_text(text):
    """Text without markup (for lengths and symbol checks)."""
    text = LINK.sub(lambda m: m.group(2), text)
    return text.replace("**", "")


def check_inline(text, where):
    """Balanced backticks and bold markers, well-formed links."""
    outside = CODE.sub("", LINK.sub(lambda m: CODE.sub("", m.group(2)), text))
    assert "`" not in outside, (where, "unbalanced backtick", text)
    assert outside.count("**") % 2 == 0, (where, "unbalanced **", text)
    assert not re.search(r"\[\[[A-Za-z_][\w:.]*\|", outside), (where, "broken link", text)
    prose = CODE.sub("", plain_text(text))
    for char, instead in FORBIDDEN.items():
        assert char not in prose and char not in text, (where, f"symbol {char!r} renders as an emoji square; use {instead}")


def links_in(text):
    return [(m.group(1), m.group(2), m.group(3)) for m in LINK.finditer(text)]


def lint(topic):
    """Hard errors raise; soft style issues are returned as warnings."""
    tid = topic["id"]
    warnings = []
    check_inline(topic["title"], (tid, "title"))
    check_inline(topic["summary"], (tid, "summary"))
    assert not links_in(topic["summary"]), (tid, "no links in the summary")
    parsed = blocks(topic["body"])
    for kind, lines in parsed:
        if kind == "syntax":
            continue
        for line in lines:
            if kind == "table" and TABLE_RULE.match(line.replace(" ", "")):
                continue
            check_inline(line, (tid, kind))
            if kind == "table":
                assert not links_in(line), (tid, "no links inside table cells", line)
        if kind == "table":
            assert len(lines) >= 3 and TABLE_RULE.match(lines[1].replace(" ", "")), (tid, "table needs a header and |---|")
            columns = lines[0].count("|") - 1
            assert 2 <= columns <= 3, (tid, "a table has 2–3 columns")
            assert len(lines) - 2 <= 8, (tid, "a table has up to 8 rows")
            for row in lines:
                assert row.count("|") - 1 == columns, (tid, "table row width", row)
        if kind == "paragraph":
            text = plain_text(" ".join(lines))
            if len(text) > 320:
                warnings.append(f"{tid}: абзац {len(text)} символов (норма до 280)")
        if kind == "heading" and len(lines[0]) > 32:
            warnings.append(f"{tid}: заголовок раздела длиннее 32 символов")
    if len(topic["summary"]) > 140:
        warnings.append(f"{tid}: summary {len(topic['summary'])} символов (норма до 120)")
    body_len = len(plain_text(topic["body"]))
    if body_len > 1800:
        warnings.append(f"{tid}: body {body_len} символов (норма до 1600)")
    for example in topic["examples"]:
        if not example.get("note"):
            warnings.append(f"{tid}: у примера нет подписи")
        for line in example["code"].split("\n"):
            if len(line) > 48:
                warnings.append(f"{tid}: строка примера длиннее 48: {line.strip()[:40]}…")
                break
    for pitfall in topic["pitfalls"]:
        why = pitfall["why"] if isinstance(pitfall, dict) else pitfall
        check_inline(why, (tid, "pitfall"))
    return warnings


# ------------------------------------------------------------------ autolinks
LEAD = re.compile(r"@?[A-Za-z_][A-Za-z_0-9.]*")


def term_for(code, glossary):
    """Glossary key matching a code fragment: the whole fragment, its leading
    dotted name (json.dumps(x) -> json.dumps) or its method (.get)."""
    text = code.strip()
    if text in glossary["exact"]:
        return glossary["exact"][text]
    lead = LEAD.match(text)
    if not lead:
        return None
    name = lead.group(0).rstrip(".")
    if name in glossary["exact"]:
        return glossary["exact"][name]
    if "." in name:
        attr = "." + name.rsplit(".", 1)[1]
        return glossary["methods"].get(attr)
    return None


def autolink(topic, glossary, module_rank, topic_module, basic_after_rank):
    """Turns `code` fragments of the body and pitfall explanations into links
    to the topics that explain them (first occurrence, ≤2 per paragraph,
    ≤8 per topic; not to itself; the basic vocabulary is not linked once the
    learner is past the functions module)."""
    tid = topic["id"]
    seen = {target for target, _, _ in links_in(topic["body"])}
    budget = [8 - len(seen)]
    rank = module_rank[topic_module[tid]]

    def link_line(line):
        per_line = [2 - len(links_in(line))]

        def replace(match):
            code = match.group(1)
            # `]`/`|` would break the link markup; long fragments (messages,
            # whole statements) are not names of anything.
            if "]" in code or "|" in code or len(code) > 28:
                return match.group(0)
            key = term_for(code, glossary)
            if key is None or per_line[0] <= 0 or budget[0] <= 0:
                return match.group(0)
            entry = glossary["terms"][key]
            target = entry.get("topic") or f"g:{key}"
            if target == tid or target in seen or key in seen:
                return match.group(0)
            if entry.get("basic") and rank >= basic_after_rank:
                return match.group(0)
            seen.add(target)
            seen.add(key)
            per_line[0] -= 1
            budget[0] -= 1
            return f"[[{target}|`{code}`|{key}]]"

        # Only code outside existing links, and never `{`opted out`}`.
        parts = re.split(r"(\[\[[^\]]+\]\]|\{`[^`]+`\})", line)
        out = []
        for part in parts:
            if part.startswith("[[") or part.startswith("{`"):
                out.append(part[1:-1] if part.startswith("{`") else part)
            else:
                out.append(CODE.sub(replace, part))
        return "".join(out)

    new_lines, in_syntax = [], False
    for line in topic["body"].split("\n"):
        if line.strip().startswith("```"):
            in_syntax = not in_syntax
            new_lines.append(line)
            continue
        # Table rows: a link's `|` would split the cell.
        if in_syntax:
            new_lines.append(line)
            continue
        if line.startswith("## ") or line.lstrip().startswith("|"):
            new_lines.append(re.sub(r"\{(`[^`]+`)\}", r"\1", line))
            continue
        new_lines.append(link_line(line))
    topic["body"] = "\n".join(new_lines)
    for pitfall in topic["pitfalls"]:
        if isinstance(pitfall, dict):
            pitfall["why"] = link_line(pitfall["why"])
