import 'package:bytecraft/features/world/domain/world_challenge.dart';
import 'package:bytecraft/features/world/domain/world_rules.dart';
import 'package:bytecraft/features/world/domain/world_state.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('all DNA topics have 20 concepts, separate progress and a finite finish', () {
    final now = DateTime(2026, 10, 18);
    for (final category in WorldState.initial().mistakes.keys) {
      var s = WorldState.initial();
      final codes = <String>{};
      final concepts = <String>{};
      for (var n = 0; n < 20; n++) {
        final q = WorldChallenges.at(s, WorldMode.training, category: category);
        expect(codes.add(q.code), isTrue);
        expect(concepts.add(q.title), isTrue);
        final wrong = WorldRules.submit(s, WorldMode.training, q.id, 'WRONG', now, category: category);
        expect(wrong.state.solved, s.solved);
        expect(wrong.state.failures[q.id], 1);
        final result = WorldRules.submit(wrong.state, WorldMode.training, q.id, q.answer, now, category: category);
        expect(result.correct, isTrue);
        s = result.state;
        expect(s.solved['training:$category'], n + 1);
      }
      expect(WorldChallenges.finished(s, WorldMode.training, category: category), isTrue);
      final duplicate = WorldRules.submit(s, WorldMode.training, 'training:$category:19', 'anything', now, category: category);
      expect(duplicate.correct, isFalse);
      expect(duplicate.state, same(s));
      expect(s.solved.length, 1);
    }
  });
}
