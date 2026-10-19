"""Build independent, executable examples for concrete learning gaps.

Existing authored programs retain their topic. Variants change one literal
input at a time and are executed in isolated CPython; no answer is guessed.
The bundled Pyodide check independently verifies the resulting catalogue.
"""
import ast
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import re
import runpy
import subprocess
import sys
import tokenize

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tool/content'))
from bclib import run

def category(module):
    if module in {'conditions', 'exceptions', 'testing'}: return 'Условия'
    if module in {'loops', 'loops_control', 'comprehensions', 'generators', 'async', 'concurrency'}: return 'Циклы'
    if module in {'lists', 'tuples_sets', 'dicts', 'strings', 'files', 'textdata'}: return 'Индексы'
    if module in {'variables', 'types', 'operators', 'io', 'dataclasses', 'typing', 'classes', 'inheritance', 'dunder', 'properties'}: return 'Типы данных'
    return 'Функции'

def output(code, stdin=''):
    with contextlib.redirect_stderr(io.StringIO()):
        result = run(code, stdin, time_limit=1, output_limit=512)
    answer = result.out.strip()
    return answer if result.ok and answer and len(answer) <= 480 and len(answer.splitlines()) <= 15 else None

def variants(code, stdin=''):
    """Distinct literal data, not renamed variables or cosmetic wrappers."""
    found = set()
    def accept(source, data):
        key = source + '\0' + data
        if key in found: return None
        found.add(key)
        answer = output(source, data)
        return (source, data, answer) if answer is not None else None
    base = accept(code, stdin)
    if base: yield base
    if stdin:
        lines_in = stdin.strip().splitlines()
        count_header = len(lines_in) > 1 and lines_in[0].isdigit() and int(lines_in[0]) == len(lines_in) - 1
        for match in list(re.finditer(r'-?\d+', stdin))[:3]:
            if count_header and match.start() == 0: continue
            for delta in [3, 7, 11, 17]:
                data = stdin[:match.start()] + str(int(match.group()) + delta) + stdin[match.end():]
                item = accept(code, data)
                if item: yield item
        word = re.search(r'[^\W\d_]+', stdin)
        if word:
            for suffix in ['xy', 'ab', 'cd']:
                data = re.sub(r'\b' + re.escape(word.group()) + r'\b', word.group() + suffix, stdin)
                item = accept(code, data)
                if item: yield item
    lines = code.splitlines(keepends=True)
    # Change literal data at the call site or module input assignments. Keep
    # function algorithms, comparison operators and loop bodies intact.
    try:
        tree = ast.parse(code)
        allowed = set()
        for statement in tree.body:
            expression = statement.value if isinstance(statement, (ast.Assign, ast.AnnAssign, ast.Expr)) else statement.iter if isinstance(statement, ast.For) else None
            if expression is not None:
                allowed.update((node.lineno, node.col_offset) for node in ast.walk(expression)
                    if isinstance(node, ast.Constant))
    except SyntaxError: return
    try: tokens = list(tokenize.generate_tokens(io.StringIO(code).readline))
    except (tokenize.TokenError, IndentationError): return
    for token in tokens:
        if token.start not in allowed: continue
        if token.start[0] != token.end[0]: continue
        replacements = []
        if token.type == tokenize.NUMBER:
            try: value = ast.literal_eval(token.string)
            except (ValueError, SyntaxError): continue
            if type(value) not in (int, float) or not 0 <= value <= 100: continue
            replacements = [repr(value + 3), repr(-value - 1), repr(value + 11)]
        elif token.type == tokenize.STRING:
            try: value = ast.literal_eval(token.string)
            except (ValueError, SyntaxError): continue
            if isinstance(value, str) and value.isalpha() and 1 <= len(value) <= 20:
                replacements = [repr(value + suffix) for suffix in ['xy', 'ab', 'cd']]
        for replacement in replacements:
            changed = list(lines)
            line = token.start[0] - 1
            changed[line] = changed[line][:token.start[1]] + replacement + changed[line][token.end[1]:]
            item = accept(''.join(changed), stdin)
            if item: yield item
        if len(found) >= 10: return

skills = {}
origins = {}
def origin(key, skill, code, stdin=''):
    item = origins.setdefault(key, {'skillId': skill, 'sources': []})
    source = {'code': code, 'stdin': stdin}
    if source not in item['sources']: item['sources'].append(source)
def add(skill, title, group, code, stdin='', exclude_data=()):
    entry = skills.setdefault(skill, {'title': title, 'category': group, 'examples': []})
    if len(entry['examples']) >= 8: return
    known = {x['id'] for x in entry['examples']}
    for source, data, answer in variants(code, stdin):
        if source == code and data in exclude_data: continue
        ident = hashlib.sha256((source + '\0' + data).encode()).hexdigest()[:20]
        if ident in known: continue
        known.add(ident)
        entry['examples'].append({'id': ident, 'code': source, 'stdin': data, 'answer': answer})
        if len(entry['examples']) >= 8: break

args = sys.argv[:]
sys.argv = ['generate_dna.py', '--check']
with contextlib.redirect_stdout(io.StringIO()):
    dna = runpy.run_path(str(ROOT / 'tool/world/generate_dna.py'))['lessons']
sys.argv = args
for group, lessons in dna.items():
    for index, lesson in enumerate(lessons):
        source = lesson['code'].replace('___', lesson['answer'])
        add(f'dna:{group}:{index}', lesson['concept'], group, source)
        origin(f'training:{group}:{index}', f'dna:{group}:{index}', source)

content = ROOT / 'assets/content/python'
topics = json.loads((content / 'topics.json').read_text())['topics']
titles = {t['id']: t for t in topics}
for topic in topics:
    for example in topic['examples']:
        if not example.get('nativeOnly'):
            add('topic:python:' + topic['id'], topic['title'], category(topic['module']), example['code'])
for file in sorted((content / 'modules').glob('*.json')):
    for level in json.loads(file.read_text())['levels']:
        solution = level.get('solution')
        if not solution: continue
        topic = titles[level['topic']]
        origin('lesson:python:' + level['id'], 'topic:python:' + topic['id'], solution['code'], solution.get('stdin', ''))
        if not solution.get('nativeOnly'):
            add('topic:python:' + topic['id'], topic['title'], category(topic['module']), solution['code'], solution.get('stdin', ''))
for task in json.loads((content / 'practice.json').read_text())['tasks']:
    for case in task['tests']:
        add('practice:python:' + task['id'], task['title'], category(task['module']), task['solution'], case['stdin'],
            exclude_data=[item['stdin'] for item in task['tests']])
        origin('practice:python:' + task['id'], 'practice:python:' + task['id'], task['solution'], case['stdin'])

rows = json.loads(subprocess.check_output([os.environ.get('BYTECRAFT_DART', 'dart'),
    str(ROOT / 'tool/world/export_questions.dart')], cwd=ROOT, text=True))
groups = ['Условия', 'Циклы', 'Индексы', 'Типы данных', 'Функции']
story_groups = {'expedition': ['Типы данных', 'Условия', 'Индексы', 'Циклы', 'Функции'],
                'boss': ['Циклы', 'Циклы', 'Функции', 'Условия']}
for row in rows:
    mode, _, cursor = row['id'].partition(':')
    if mode not in {'expedition', 'boss', 'ghost', 'guild', 'rival', 'infinite'}: continue
    n = int(cursor)
    repeat = mode in {'ghost', 'guild', 'rival', 'infinite'}
    group = row['category']
    skill = f'world:repeat:{group}' if repeat else f'world:{mode}:{n}'
    source = row['code'].replace('___', row['answer'])
    origin(row['id'], skill, source)
    if repeat and (mode != 'ghost' or n >= 5): continue
    if mode == 'boss' and n == 0: source += '\nprint(total([4, 8, -2]))'
    add(skill, row['title'], group, source)

# These concepts have no mutable literal inputs in the original illustration.
# Provide actual independently authored examples instead of cosmetic changes.
extra = {
  'dna:Условия:4': [('active = True\nprint(not active)', ''), ('active = False\nprint("start" if not active else "wait")', '')],
  'dna:Условия:17': [('items = ["ready"]\nif items:\n    print(items[0])\nelse:\n    print("empty")', ''), ('items = ["new", "data"]\nprint(items[0] if items else "empty")', '')],
  'dna:Функции:2': [('def greet(name="visitor"):\n    return "Hi " + name\nprint(greet())', ''), ('def greet(name="visitor"):\n    return "Hi " + name\nprint(greet("Mira"))', '')],
  'dna:Функции:4': [('def bounds():\n    return -3, 9\nlow, high = bounds()\nprint(high - low)', ''), ('def bounds():\n    return 5, 12\nlow, high = bounds()\nprint(low + high)', '')],
  'dna:Функции:18': [('def values():\n    yield 5\n    yield 8\n    yield 13\nprint(list(values()))', ''), ('def values():\n    yield 1\n    yield 7\nprint(sum(values()))', '')],
  'dna:Условия:3': [('is_admin = True\nis_owner = False\nprint(is_admin or is_owner)', ''), ('is_admin = False\nis_owner = False\nprint(is_admin or is_owner)', '')],
  'dna:Условия:14': [('print(True or False and False)', ''), ('print(False or True and True)', '')],
  'dna:Условия:15': [('print((True or False) and not True)', ''), ('print((False or False) and not False)', '')],
  'dna:Циклы:9': [('for n in [2, 3, 5]:\n    if n % 2 == 0:\n        break\nelse:\n    print("not found")\nprint("done")', ''), ('for n in [7, 9, 11]:\n    if n % 2 == 0:\n        break\nelse:\n    print("not found")', '')],
  'dna:Типы данных:1': [('print("4" + "56")', ''), ('print("7" + "89")', '')],
  'dna:Типы данных:16': [('print(False + False + True)', ''), ('print(True + False + True + True)', '')],
  'dna:Условия:16': [('value = None\nprint(value is None)', ''), ('items = [None, 0]\nprint(items[0] is None, items[1] is None)', '')],
  'dna:Типы данных:15': [('value = None\nprint(type(value).__name__)', ''), ('items = [None, 1]\nprint(type(items[0]).__name__)', '')],
}
for skill, examples in extra.items():
    if skill in skills:
        for code, data in examples: add(skill, skills[skill]['title'], skills[skill]['category'], code, data)

# Native process spawning is not available in Pyodide. These authored scenario
# questions assess the same selection criterion without pretending to run it.
skill = skills['topic:python:conc_processes']
for number, prompt, options, answer in [
    (1, 'В CPython с GIL нужно распределить тяжёлые вычисления на чистом Python между ядрами. Что выбрать?', ['Несколько процессов', 'Только потоки одного процесса'], 'Несколько процессов'),
    (2, 'Программа в основном ждёт сетевые ответы, а расчётов почти нет. Какой подход обычно подходит?', ['Потоки или asyncio', 'Всегда отдельный процесс для каждого запроса'], 'Потоки или asyncio'),
]:
    skill['examples'].append({'id': f'process-scenario-{number}', 'code': '# Выбор подхода для описанной нагрузки',
        'stdin': '', 'answer': answer, 'prompt': prompt, 'options': options})

short = {k: len(v['examples']) for k,v in skills.items() if len(v['examples']) < 2}
if short: raise AssertionError(('Need independent examples', short))
target = ROOT / 'assets/projects/repair_catalog.json'
text = json.dumps({'schemaVersion': 1, 'skills': skills, 'origins': origins}, ensure_ascii=False, separators=(',', ':')) + '\n'
if '--check' in sys.argv:
    assert target.read_text() == text, 'Regenerate repair catalogue'
else: target.write_text(text)
print(f"Verified {sum(len(v['examples']) for v in skills.values())} repair examples for {len(skills)} concrete skills")
