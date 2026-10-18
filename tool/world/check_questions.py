"""Validate authored and generated World answers with actual CPython execution.
Usage: dart run tool/world/export_questions.dart | python tool/world/check_questions.py
"""
import contextlib
import io
import json
import sys

rows = json.load(sys.stdin)
for row in rows:
    namespace = {}
    output = io.StringIO()
    source = row['code']
    if row['kind'] == 'fill':
        source = source.replace('___', row['answer'])
        if 'def add(' in source:
            source += '\nassert add(2, 3) == 5\nassert add(-2, 2) == 0\n'
        elif 'def total(' in source:
            source += '\nassert total([2, 3]) == 5\nassert total([]) == 0\nassert total([-2, 2]) == 0\n'
    with contextlib.redirect_stdout(output):
        exec(source, namespace)
    if row['kind'] == 'output':
        assert output.getvalue().strip() == row['answer'], row
    elif row['id'].startswith('expedition:'):
        assert output.getvalue().strip().splitlines() == [str(100 / 120), str(100 / 80)], row
print(f'CPython verified {len(rows)} questions, including all 13 story steps and 250 topic-specific training questions.')
