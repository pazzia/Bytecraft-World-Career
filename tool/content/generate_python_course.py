"""Source of truth for the bundled Python course.

Builds assets/content/python/ from tool/content/course/c*.py:
  course.json          module list
  modules/<id>.json    levels of each module
  topics.json          journal topics (explanations + verified examples)
  practice.json        coding exercises (verified solutions and tests)

Every level, example and exercise is executed while building (see
bclib.py). Any wrong answer, ambiguous option or failing example stops the
build with the id of the broken item.

Usage: python3 tool/content/generate_python_course.py assets/content/python
"""
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

COURSE = dict(
    schemaVersion=1,
    id="python",
    title="Python: от основ до профи",
    language="python",
    version=2,
)

ROLES = {"lesson", "practice", "challenge", "boss"}
MIN_LEVELS_PER_MODULE = 6
SECONDS_PER_LEVEL = 70


def load_modules():
    folder = os.path.join(HERE, "course")
    modules = []
    extras = []
    for name in sorted(os.listdir(folder)):
        if not (name.startswith("c") and name.endswith(".py")):
            continue
        spec = importlib.util.spec_from_file_location(name[:-3], os.path.join(folder, name))
        source = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(source)
        modules.extend(source.MODULES)
        extras.append(getattr(source, "EXTRA_LEVELS", {}))
    # Levels kept in separate files (e.g. new mechanics) join their module
    # right before its boss.
    by_id = {module["id"]: module for module in modules}
    for extra in extras:
        for module_id, levels in extra.items():
            assert module_id in by_id, ("extra levels for unknown module", module_id)
            target = by_id[module_id]["levels"]
            target[-1:-1] = levels
    return modules


def validate(modules):
    level_ids, topic_ids, task_ids, module_ids = set(), {}, set(), set()
    for module in modules:
        assert module["id"] not in module_ids, ("duplicate module", module["id"])
        module_ids.add(module["id"])
        for topic in module.get("topics", []):
            assert topic["id"] not in topic_ids, ("duplicate topic", topic["id"])
            topic_ids[topic["id"]] = module["id"]
    used_topics = set()
    for module in modules:
        levels = module["levels"]
        assert len(levels) >= MIN_LEVELS_PER_MODULE, ("too few levels", module["id"], len(levels))
        assert levels[-1]["role"] == "boss", ("last level must be the boss", module["id"])
        for level in levels:
            assert level["id"] not in level_ids, ("duplicate level", level["id"])
            level_ids.add(level["id"])
            assert level["role"] in ROLES, (level["id"], level["role"])
            assert level["topic"] in topic_ids, (level["id"], "unknown topic", level["topic"])
            used_topics.add(level["topic"])
        for task in module.get("tasks", []):
            assert task["id"] not in task_ids, ("duplicate task", task["id"])
            task_ids.add(task["id"])
    unused = set(topic_ids) - used_topics
    assert not unused, ("topics without levels", sorted(unused))
    return len(level_ids), len(topic_ids), len(task_ids)


def write_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1, sort_keys=False)
        f.write("\n")


def load_glossary(topic_ids):
    """glossary.py -> entries with verified example outputs and the lookup
    tables used by autolinking."""
    import bclib
    import glossary
    terms, exact, methods = {}, {}, {}
    for entry in glossary.TERMS:
        key = entry["key"]
        assert key not in terms, ("duplicate glossary term", key)
        assert entry["topic"] is None or entry["topic"] in topic_ids, ("glossary: unknown topic", key, entry["topic"])
        item = dict(brief=entry["brief"])
        if entry["topic"]:
            item["topic"] = entry["topic"]
        if entry["basic"]:
            item["basic"] = True
        if entry["example"]:
            code = bclib.dedent(entry["example"])
            result = bclib.run(code)
            assert result.ok and result.out, ("glossary example fails or prints nothing", key, result.error, result.message)
            item["example"] = code
            item["output"] = result.out
        terms[key] = item
        if entry["auto"]:
            for spelling in [key, *entry["match"]]:
                table = methods if spelling.startswith(".") else exact
                assert spelling not in table or table[spelling] == key, ("glossary: spelling used twice", spelling)
                table[spelling] = key
    return dict(terms=terms, exact=exact, methods=methods)


def link_topics(modules):
    """Autolinks, link validation and style warnings for every topic."""
    import topic_markup
    topic_module = {t["id"]: m["id"] for m in modules for t in m.get("topics", [])}
    module_rank = {m["id"]: i for i, m in enumerate(modules)}
    glossary = load_glossary(set(topic_module))
    basic_after = module_rank.get("functions", len(modules))
    warnings = []
    for module in modules:
        for topic in module.get("topics", []):
            topic_markup.autolink(topic, glossary, module_rank, topic_module, basic_after)
            try:
                warnings += topic_markup.lint(topic)
            except AssertionError as error:
                # Strict once every topic is migrated to the markup.
                if os.environ.get("BYTECRAFT_STRICT_TOPICS", "1") == "1":
                    raise
                warnings.append(f"ERROR {error}")
            texts = [topic["body"]] + [p["why"] for p in topic["pitfalls"] if isinstance(p, dict)]
            for text in texts:
                for target, _, term in topic_markup.links_in(text):
                    if target.startswith("g:"):
                        assert target[2:] in glossary["terms"], (topic["id"], "unknown glossary link", target)
                    else:
                        assert target in topic_module, (topic["id"], "link to an unknown topic", target)
                        assert target != topic["id"], (topic["id"], "link to itself")
                    assert term is None or term in glossary["terms"], (topic["id"], "unknown term", term)
    return glossary, warnings


def main(out_dir):
    # The app runs Pyodide 0.27 (CPython 3.12): outputs and error messages
    # must come from the same Python version.
    assert sys.version_info[:2] == (3, 12), "run the generator with python3.12"
    modules = load_modules()
    levels, topics, tasks = validate(modules)
    glossary, warnings = link_topics(modules)
    os.makedirs(os.path.join(out_dir, "modules"), exist_ok=True)
    for stale in os.listdir(os.path.join(out_dir, "modules")):
        os.remove(os.path.join(out_dir, "modules", stale))
    manifest = dict(COURSE, modules=[])
    all_topics, all_tasks = [], []
    for module in modules:
        manifest["modules"].append(dict(
            id=module["id"],
            title=module["title"],
            description=module["description"],
            icon=module["icon"],
            file=f"modules/{module['id']}.json",
            timedRunSeconds=60 + SECONDS_PER_LEVEL * len(module["levels"]),
        ))
        write_json(os.path.join(out_dir, "modules", f"{module['id']}.json"),
                   dict(schemaVersion=1, levels=module["levels"]))
        for topic in module.get("topics", []):
            all_topics.append(dict(topic, module=module["id"]))
        for task in module.get("tasks", []):
            all_tasks.append(dict(task, module=module["id"]))
    write_json(os.path.join(out_dir, "course.json"), manifest)
    write_json(os.path.join(out_dir, "topics.json"), dict(schemaVersion=1, topics=all_topics))
    write_json(os.path.join(out_dir, "glossary.json"), dict(schemaVersion=1, terms=glossary["terms"]))
    with open(os.path.join(HERE, "requirements_checker.py"), encoding="utf-8") as f:
        checker = f.read()
    write_json(os.path.join(out_dir, "practice.json"),
               dict(schemaVersion=1, checker=checker, tasks=all_tasks))
    kinds = {}
    for module in modules:
        for level in module["levels"]:
            kinds[level["type"]] = kinds.get(level["type"], 0) + 1
    print(f"modules: {len(modules)}  levels: {levels}  topics: {topics}  tasks: {tasks}  "
          f"glossary: {len(glossary['terms'])}  style warnings: {len(warnings)}")
    print("types:", ", ".join(f"{k}={v}" for k, v in sorted(kinds.items())))


if __name__ == "__main__":
    main(sys.argv[1])
