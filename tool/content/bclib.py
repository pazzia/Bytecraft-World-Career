"""Building blocks of the Bytecraft Python course.

Every helper RUNS the code it describes in real Python and fails loudly
(AssertionError with the level id) when the content is wrong:

* predicted outputs are never typed by hand: they are computed;
* options that are not the answer must not produce the answer;
* fill-in levels must not be solvable by another combination of tokens;
* ordering puzzles accept every order that produces the same output;
* bug-finder code must really fail, and the fix must really work;
* topic examples and practice tasks are executed, outputs are computed.
"""
import builtins
import contextlib
import io
import itertools
import os
import sys
import tempfile
import textwrap

# Short, real Python messages shown to the player for a wrong fill-in.
MAX_RESULT_CHARS = 160
MAX_RESULT_LINES = 4
MAX_ORDER_LINES = 7
MAX_FILL_COMBOS = 400


class Run:
    def __init__(self, out, error=None, message=""):
        self.out = out
        self.error = error  # exception class name or None
        self.message = message

    @property
    def ok(self):
        return self.error is None

    def summary(self):
        """What the player sees for their version of the program."""
        if self.error:
            text = f"{self.error}: {self.message}" if self.message else self.error
            return text[:MAX_RESULT_CHARS]
        lines = self.out.rstrip("\n").split("\n")
        if len(lines) > MAX_RESULT_LINES:
            lines = lines[:MAX_RESULT_LINES] + ["…"]
        text = "\n".join(line[:MAX_RESULT_CHARS] for line in lines)
        return text if text else "(ничего не выводит)"


def run(code, stdin=""):
    """Executes code as a fresh __main__ module in a temporary directory."""
    out = io.StringIO()
    old_stdin = sys.stdin
    old_cwd = os.getcwd()
    tmp = tempfile.mkdtemp(prefix="bytecraft_")
    try:
        sys.stdin = io.StringIO(stdin)
        os.chdir(tmp)
        with contextlib.redirect_stdout(out):
            compiled = compile(code, "main.py", "exec")
            exec(compiled, {"__name__": "__main__", "__builtins__": builtins})
    except SyntaxError as error:
        return Run(out.getvalue(), type(error).__name__, error.msg)
    except SystemExit as error:
        if error.code not in (None, 0):
            return Run(out.getvalue(), "SystemExit", str(error.code))
    except BaseException as error:  # noqa: BLE001 - we report every failure
        message = str(error).split("\n")[0]
        return Run(out.getvalue(), type(error).__name__, message)
    finally:
        sys.stdin = old_stdin
        os.chdir(old_cwd)
    return Run(out.getvalue())


def _solution(code, output, stdin="", native_only=False):
    """Working program of a level. `native_only` marks code that CPython
    runs but the in-app interpreter (Pyodide in a browser sandbox) can't,
    e.g. threads; the Pyodide check in CI skips it."""
    solution = dict(code=code, output=output)
    if stdin:
        solution["stdin"] = stdin
    if native_only:
        solution["nativeOnly"] = True
    return solution


def dedent(code):
    return textwrap.dedent(code).strip("\n")


def _ok(level_id, code, stdin=""):
    result = run(code, stdin)
    assert result.ok, (level_id, "code fails", result.error, result.message, code)
    return result


def _base(level_id, kind, role, title, prompt, topic, difficulty, hint, explanation, code=None):
    assert topic, (level_id, "every level needs a topic")
    assert hint and explanation, (level_id, "hint and explanation are required")
    level = dict(id=level_id, type=kind, role=role, title=title, prompt=prompt, topic=topic,
                 difficulty=difficulty, hint=hint, explanation=explanation)
    if code is not None:
        level["code"] = code
    return level


def predict(level_id, title, code, distractors, *, topic, hint, explanation, position=1,
            prompt="Что выведет код?", role="lesson", difficulty=1, feedback=None):
    """Multiple choice "what does this print": the right option is the real
    output (computed), distractors must all differ from it."""
    code = dedent(code)
    result = _ok(level_id, code)
    actual = result.out.rstrip("\n")
    assert actual, (level_id, "prints nothing")
    for option in distractors:
        assert option != actual, (level_id, "distractor equals the output", option)
    assert len(set(distractors)) == len(distractors), (level_id, "duplicate distractors")
    options = list(distractors)
    position = min(position, len(options))
    options.insert(position, actual)
    level = _base(level_id, "predict_output", role, title, prompt, topic, difficulty, hint,
                  explanation, code)
    payload = dict(options=options, correctIndex=position)
    if feedback:
        payload["optionFeedback"] = _feedback(level_id, options, distractors, feedback)
    level["payload"] = payload
    level["solution"] = dict(code=code, output=result.out)
    return level


def _feedback(level_id, options, distractors, feedback):
    assert set(feedback) <= set(distractors), (level_id, "feedback for unknown option")
    return [feedback.get(option, "") for option in options]


def choice(level_id, title, prompt, options, correct, *, topic, hint, explanation, code=None,
           check=None, role="lesson", difficulty=1, feedback=None):
    """Conceptual multiple choice. With `check(option) -> bool` every option
    is verified: exactly the correct one must pass."""
    if code is not None:
        code = dedent(code)
    if check is not None:
        verdicts = [bool(check(option)) for option in options]
        assert verdicts.count(True) == 1 and verdicts[correct], (level_id, "check", verdicts)
    level = _base(level_id, "multiple_choice", role, title, prompt, topic, difficulty, hint,
                  explanation, code)
    payload = dict(options=list(options), correctIndex=correct)
    if feedback:
        wrong = [option for i, option in enumerate(options) if i != correct]
        payload["optionFeedback"] = _feedback(level_id, options, wrong, feedback)
    level["payload"] = payload
    if code is not None and run(code).ok:
        level["solution"] = dict(code=code, output=run(code).out)
    return level


def fill(level_id, title, prompt, template, options, answers, *, topic, hint, explanation,
         expect=None, stdin="", role="lesson", difficulty=1):
    """Fill-in-the-blanks. The filled program must run (and print `expect`
    if given); no other combination of options may print the same."""
    template = dedent(template)

    def filled(tokens):
        code = template
        for index, token in enumerate(tokens):
            code = code.replace("{{%d}}" % index, token)
        return code

    for answer in answers:
        assert answer in options, (level_id, "answer not in options", answer)
    assert len(set(options)) == len(options), (level_id, "duplicate options")
    solution = filled(answers)
    correct = _ok(level_id, solution, stdin)
    if expect is not None:
        assert correct.out == expect, (level_id, "unexpected output", correct.out, expect)
    assert correct.out, (level_id, "fill level must print something")
    variants = {}
    combos = list(itertools.product(options, repeat=len(answers)))
    assert len(combos) <= MAX_FILL_COMBOS, (level_id, "too many combinations", len(combos))
    for combo in combos:
        if list(combo) == list(answers):
            continue
        other = run(filled(combo), stdin)
        assert not (other.ok and other.out == correct.out), (level_id, "ambiguous", combo)
        variants["\u0001".join(combo)] = other.summary()
    level = _base(level_id, "fill_code", role, title, prompt, topic, difficulty, hint, explanation)
    level["payload"] = dict(template=template, options=list(options), answers=list(answers),
                            variantResults=variants)
    level["solution"] = _solution(solution, correct.out, stdin)
    return level


def order(level_id, title, prompt, lines, *, topic, hint, explanation, role="practice",
          difficulty=2):
    """Ordering puzzle. Lines are given in a correct order; every other
    permutation that runs and prints the same is accepted too."""
    lines = [line for line in lines]
    assert 2 <= len(lines) <= MAX_ORDER_LINES, (level_id, "line count", len(lines))
    assert len(set(lines)) == len(lines), (level_id, "duplicate lines")
    canonical = _ok(level_id, "\n".join(lines))
    assert canonical.out, (level_id, "ordering level must print something")
    alternatives = []
    for perm in itertools.permutations(range(len(lines))):
        if list(perm) == list(range(len(lines))):
            continue
        other = run("\n".join(lines[i] for i in perm))
        if other.ok and other.out == canonical.out:
            alternatives.append(list(perm))
    total = 1
    for n in range(2, len(lines) + 1):
        total *= n
    assert len(alternatives) + 1 < total, (level_id, "every order works")
    level = _base(level_id, "code_ordering", role, title, prompt, topic, difficulty, hint,
                  explanation)
    payload = dict(lines=lines)
    if alternatives:
        payload["alternativeOrders"] = alternatives
    level["payload"] = payload
    level["solution"] = dict(code="\n".join(lines), output=canonical.out)
    return level


def bug(level_id, title, code, fixes, *, topic, hint, explanation, prompt="Найдите строку с ошибкой",
        expect_error=None, role="challenge", difficulty=2):
    """Bug finder. `fixes` maps buggy line index -> fixed line. The code
    must fail (raise `expect_error`, or print something other than the
    fixed program) and the fixed program must run."""
    code = dedent(code)
    lines = code.split("\n")
    fixed_lines = list(lines)
    for index, fixed in fixes.items():
        assert 0 <= index < len(lines), (level_id, "line out of range", index)
        assert lines[index] != fixed, (level_id, "fix changes nothing", index)
        fixed_lines[index] = fixed
    fixed_code = "\n".join(fixed_lines)
    good = _ok(level_id, fixed_code)
    assert good.out, (level_id, "fixed program must print something")
    buggy = run(code)
    if expect_error:
        assert buggy.error == expect_error, (level_id, "expected", expect_error, buggy.error,
                                             buggy.message)
    else:
        assert buggy.ok and buggy.out != good.out, (level_id, "bug does not show", buggy.out)
    # Each buggy line matters: fixing all but one keeps the program broken.
    if len(fixes) > 1:
        for skip in fixes:
            partial = list(lines)
            for index, fixed in fixes.items():
                if index != skip:
                    partial[index] = fixed
            other = run("\n".join(partial))
            assert not (other.ok and other.out == good.out), (level_id, "line not needed", skip)
    level = _base(level_id, "bug_finder", role, title, prompt, topic, difficulty, hint,
                  explanation, code)
    level["payload"] = dict(buggyLines=sorted(fixes))
    level["solution"] = dict(code=fixed_code, output=good.out)
    return level


def typed(level_id, title, code, *, topic, hint, explanation, prompt="Напишите, что выведет код",
          role="practice", difficulty=2):
    """Type-the-output level. The expected output is computed."""
    code = dedent(code)
    result = _ok(level_id, code)
    expected = result.out.rstrip("\n")
    assert expected.strip(), (level_id, "prints nothing")
    assert "\t" not in expected, (level_id, "tabs cannot be typed")
    assert all(line == line.rstrip() for line in expected.split("\n")), \
        (level_id, "trailing spaces are invisible")
    level = _base(level_id, "type_output", role, title, prompt, topic, difficulty, hint,
                  explanation, code)
    level["payload"] = dict(expectedOutput=expected)
    level["solution"] = dict(code=code, output=result.out)
    return level


def match(level_id, title, lefts, *, topic, hint, explanation, setup="",
          prompt="Сопоставьте выражения и результаты", role="practice", difficulty=2,
          rights=None):
    """Match pairs. By default each left item is an expression and its pair
    is what print(expression) shows (computed). With `rights`, pairs are
    given explicitly (for concepts) and are not executed."""
    setup = dedent(setup)
    assert 2 <= len(lefts) <= 6, (level_id, "pair count")
    if rights is None:
        rights = []
        for left in lefts:
            result = _ok(level_id, (setup + "\n" if setup else "") + f"print({left})")
            rights.append(result.out.rstrip("\n"))
        solution = (setup + "\n" if setup else "") + "\n".join(f"print({left})" for left in lefts)
        solution_out = _ok(level_id, solution).out
    else:
        assert len(rights) == len(lefts), (level_id, "pairs")
        solution = None
    assert len(set(rights)) == len(rights), (level_id, "results are not unique", rights)
    assert len(set(lefts)) == len(lefts), (level_id, "left items are not unique")
    level = _base(level_id, "match_pairs", role, title, prompt, topic, difficulty, hint,
                  explanation, setup or None)
    level["payload"] = dict(pairs=[dict(left=l, right=r) for l, r in zip(lefts, rights)])
    if solution is not None:
        level["solution"] = dict(code=solution, output=solution_out)
    return level


def raises(snippet):
    return not run(dedent(snippet)).ok


def multi(level_id, title, prompt, options, correct, *, topic, hint, explanation, check,
          code=None, role="practice", difficulty=2, feedback=None):
    """Pick-all-correct. `check(option) -> bool` must agree with `correct`
    for every option."""
    assert len(options) >= 3, (level_id, "need at least 3 options")
    assert 1 <= len(correct) < len(options), (level_id, "correct count")
    for index, option in enumerate(options):
        verdict = bool(check(option))
        assert verdict == (index in correct), (level_id, "check disagrees", option, verdict)
    if code is not None:
        code = dedent(code)
    level = _base(level_id, "multi_select", role, title, prompt, topic, difficulty, hint,
                  explanation, code)
    payload = dict(options=list(options), correctIndexes=sorted(correct))
    if feedback:
        wrong = [option for i, option in enumerate(options) if i not in correct]
        payload["optionFeedback"] = _feedback(level_id, options, wrong, feedback)
    level["payload"] = payload
    return level


def topic(topic_id, title, summary, body, examples, pitfalls=()):
    """A journal topic. `examples` are (code, note) pairs; outputs are computed."""
    built = []
    for item in examples:
        code, note = item[0], item[1]
        flags = item[2] if len(item) > 2 else {}
        assert set(flags) <= {"native_only"}, (topic_id, "unknown flags", flags)
        code = dedent(code)
        result = run(code)
        assert result.ok, (topic_id, "example fails", result.error, result.message, code)
        example = dict(code=code, output=result.out)
        if note:
            example["note"] = note
        if flags.get("native_only"):
            example["nativeOnly"] = True
        built.append(example)
    assert built, (topic_id, "a topic needs an example")
    return dict(id=topic_id, title=title, summary=summary, body=dedent(body),
                examples=built, pitfalls=list(pitfalls))


def task(task_id, title, prompt, *, solution, tests, starter="", hint=None, difficulty=1):
    """A coding exercise. Expected outputs are computed from the solution.
    The starter must not pass, and the tests must not share one output (so
    printing a constant can't pass)."""
    solution = dedent(solution)
    starter = dedent(starter)
    built = []
    for stdin in tests:
        result = run(solution, stdin)
        assert result.ok, (task_id, "solution fails", stdin, result.error, result.message)
        assert result.out.strip(), (task_id, "solution prints nothing", stdin)
        built.append(dict(stdin=stdin, expected=result.out))
    assert len(built) >= 3, (task_id, "need at least 3 tests")
    assert len({test["expected"] for test in built}) >= 2, (task_id, "all tests print the same")
    starter_passes = all(
        run(starter, test["stdin"]).ok and run(starter, test["stdin"]).out == test["expected"]
        for test in built)
    assert not starter_passes, (task_id, "starter already passes")
    item = dict(id=task_id, title=title, prompt=prompt, starter=starter, solution=solution,
                tests=built, difficulty=difficulty)
    if hint:
        item["hint"] = hint
    return item


def native(level):
    """Marks a level whose code needs real CPython (threads, processes...):
    the Pyodide check in CI skips its solution."""
    assert "solution" in level, (level["id"], "no solution to mark")
    level["solution"]["nativeOnly"] = True
    return level
