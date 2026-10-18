"""Checks the topics of one course file without building the whole course.

Usage: python3.12 tool/content/check_topics.py c03_functions
Prints style warnings (lengths, missing example notes...) and fails on hard
errors (broken markup, symbols that render as emoji, unknown links). Link
targets are checked against the topics of all course files.
"""
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import topic_markup  # noqa: E402
from generate_python_course import load_glossary  # noqa: E402


def topic_ids_everywhere():
    """Ids from the built course plus whatever the course files declare now."""
    ids = set()
    built = os.path.join(HERE, "..", "..", "assets", "content", "python", "topics.json")
    if os.path.exists(built):
        ids |= {t["id"] for t in json.load(open(built, encoding="utf-8"))["topics"]}
    return ids


def main(name):
    path = os.path.join(HERE, "course", name if name.endswith(".py") else name + ".py")
    spec = importlib.util.spec_from_file_location("checked", path)
    source = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(source)
    ids = topic_ids_everywhere() | {t["id"] for m in source.MODULES for t in m.get("topics", [])}
    glossary = load_glossary(ids)
    module_ids = [m["id"] for m in json.load(open(os.path.join(HERE, "..", "..", "assets", "content", "python", "course.json")))["modules"]]
    rank = {m: i for i, m in enumerate(module_ids)}
    topic_module = {t["id"]: m["id"] for m in source.MODULES for t in m.get("topics", [])}
    for i in ids - set(topic_module):
        topic_module.setdefault(i, module_ids[0])
    warnings = []
    for module in source.MODULES:
        for topic in module.get("topics", []):
            topic_markup.autolink(topic, glossary, rank, topic_module, rank.get("functions", 99))
            warnings += topic_markup.lint(topic)
            texts = [topic["body"]] + [p["why"] for p in topic["pitfalls"] if isinstance(p, dict)]
            for text in texts:
                for target, _, _ in topic_markup.links_in(text):
                    if target.startswith("g:"):
                        assert target[2:] in glossary["terms"], (topic["id"], "unknown glossary link", target)
                    else:
                        assert target in ids, (topic["id"], "link to an unknown topic", target)
    for warning in warnings:
        print("warning:", warning)
    count = sum(len(m.get("topics", [])) for m in source.MODULES)
    print(f"{name}: {count} topics OK, {len(warnings)} style warnings")


if __name__ == "__main__":
    main(sys.argv[1])
