import 'dart:convert';

import '../../lib/features/world/domain/world_challenge.dart';
import '../../lib/features/world/domain/world_state.dart';

// Machine-readable catalog for independent verification in CPython.
void main() {
  final rows = <Map<String, String>>[];
  for (final mode in WorldMode.values) {
    final length = switch (mode) {
      WorldMode.expedition => 5,
      WorldMode.project || WorldMode.boss => 4,
      WorldMode.training => 20,
      _ => 50,
    };
    for (var i = 0; i < length; i++) {
      final s = WorldState.initial().copyWith(
        expeditionStep: i,
        bossTask: i,
        projectSteps: {
          for (var j = 0; j < 4; j++) WorldState.projectIds[j]: j < i,
        },
        solved: {mode.name: i},
      );
      final categories = mode == WorldMode.training
          ? s.mistakes.keys
          : ['Условия'];
      for (final category in categories) {
        final state = s.copyWith(
          solved: {...s.solved, 'training:$category': i},
        );
        final q = WorldChallenges.at(state, mode, category: category);
        rows.add({
          'id': q.id,
          'title': q.title,
          'category': q.category,
          'code': q.code,
          'answer': q.answer,
          'kind': q.options.isEmpty ? 'output' : 'fill',
          if (q.verificationOutput != null) 'verificationOutput': q.verificationOutput!,
        });
      }
    }
  }
  // ignore: avoid_print
  print(jsonEncode(rows));
}
