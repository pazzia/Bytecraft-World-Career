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
    for name in sorted(os.listdir(folder)):
        if not (name.startswith("c") and name.endswith(".py")):
            continue
        spec = importlib.util.spec_from_file_location(name[:-3], os.path.join(folder, name))
        source = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(source)
        modules.extend(source.MODULES)
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


def main(out_dir):
    modules = load_modules()
    levels, topics, tasks = validate(modules)
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
    write_json(os.path.join(out_dir, "practice.json"), dict(schemaVersion=1, tasks=all_tasks))
    kinds = {}
    for module in modules:
        for level in module["levels"]:
            kinds[level["type"]] = kinds.get(level["type"], 0) + 1
    print(f"modules: {len(modules)}  levels: {levels}  topics: {topics}  tasks: {tasks}")
    print("types:", ", ".join(f"{k}={v}" for k, v in sorted(kinds.items())))


if __name__ == "__main__":
    main(sys.argv[1])
