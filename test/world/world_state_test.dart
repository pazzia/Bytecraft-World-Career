import 'package:bytecraft/features/world/domain/world_state.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('world state round-trips through JSON', () {
    final state = WorldState.initial().copyWith(
      coins: 999,
      bossHp: 50,
      expeditionStep: 3,
      infiniteRecord: 41,
      cityLevels: const {
        'office': 3,
        'python': 4,
        'rnd': 2,
        'servers': 2,
        'team': 3,
      },
    );

    final restored = WorldState.fromJson(state.toJson());
    expect(restored.coins, 999);
    expect(restored.bossHp, 50);
    expect(restored.expeditionStep, 3);
    expect(restored.infiniteRecord, 41);
    expect(restored.cityLevels['python'], 4);
  });

  test('project is unlocked only after all four steps', () {
    final initial = WorldState.initial();
    expect(initial.projectUnlocked, isFalse);
    final done = initial.copyWith(
      projectSteps: const {
        'basic': true,
        'history': true,
        'errors': true,
        'ui': true,
      },
    );
    expect(done.projectUnlocked, isTrue);
  });
}
