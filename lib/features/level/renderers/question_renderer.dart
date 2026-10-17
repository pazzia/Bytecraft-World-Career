import 'package:flutter/material.dart';

import '../../courses/domain/level_definition.dart';
import '../../courses/domain/level_type.dart';
import '../domain/answer.dart';
import '../domain/validation_outcome.dart';
import 'bug_finder_renderer.dart';
import 'code_ordering_renderer.dart';
import 'fill_code_renderer.dart';
import 'match_pairs_renderer.dart';
import 'multi_select_renderer.dart';
import 'multiple_choice_renderer.dart';
import 'type_output_renderer.dart';
import 'unsupported_renderer.dart';

/// Everything a renderer needs. Renderers are stateless with respect to
/// the answer: the controller owns the draft, the renderer only displays
/// it and reports changes.
class QuestionContext {
  const QuestionContext({
    required this.level,
    required this.answer,
    required this.onChanged,
    required this.isLocked,
    this.outcome,
  });

  final LevelDefinition level;
  final Answer? answer;
  final ValueChanged<Answer> onChanged;

  /// True while feedback is shown — inputs must ignore taps.
  final bool isLocked;

  /// Last validation result, used to highlight mistakes / success.
  final ValidationOutcome? outcome;
}

/// UI strategy for one level type.
abstract class QuestionRenderer {
  const QuestionRenderer();

  /// Whether the level screen should show `level.code` above the renderer.
  /// Renderers that draw the code themselves return false.
  bool get showsLevelCode => true;

  Widget build(BuildContext context, QuestionContext question);
}

/// Level type -> renderer. Adding a mechanic = one entry here.
class QuestionRendererRegistry {
  const QuestionRendererRegistry(this._renderers);

  static const QuestionRendererRegistry standard = QuestionRendererRegistry({
    LevelType.multipleChoice: MultipleChoiceRenderer(),
    LevelType.predictOutput: MultipleChoiceRenderer(),
    LevelType.fillCode: FillCodeRenderer(),
    LevelType.codeOrdering: CodeOrderingRenderer(),
    LevelType.bugFinder: BugFinderRenderer(),
    LevelType.typeOutput: TypeOutputRenderer(),
    LevelType.matchPairs: MatchPairsRenderer(),
    LevelType.multiSelect: MultiSelectRenderer(),
  });

  final Map<LevelType, QuestionRenderer> _renderers;

  QuestionRenderer resolve(LevelType type) =>
      _renderers[type] ?? const UnsupportedRenderer();
}
