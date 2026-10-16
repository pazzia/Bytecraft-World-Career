import 'package:bytecraft/features/learning_map/domain/learning_map_model.dart';
import 'package:bytecraft/features/progress/domain/course_progress.dart';
import 'package:bytecraft/features/progress/domain/level_progress.dart';
import 'package:bytecraft/features/progress/domain/unlock_policy.dart';
import 'package:flutter_test/flutter_test.dart';

import '../helpers/test_env.dart';

CourseProgress completed(List<String> ids) => CourseProgress(
      courseId: testCourseId,
      levels: {
        for (final id in ids)
          id: LevelProgress(levelId: id, completed: true, bestStars: 3),
      },
    );

void main() {
  final course = buildTestCourse();
  const policy = UnlockPolicy();

  group('linear mode', () {
    test('only the first level is open on a fresh course', () {
      final progress = CourseProgress(courseId: testCourseId);
      expect(policy.isUnlocked(course, progress, 'l1'), isTrue);
      expect(policy.isUnlocked(course, progress, 'l2'), isFalse);
      expect(policy.isUnlocked(course, progress, 'l4'), isFalse);
    });

    test('completing a level unlocks the next one', () {
      final progress = completed(['l1']);
      expect(policy.isUnlocked(course, progress, 'l2'), isTrue);
      expect(policy.isUnlocked(course, progress, 'l3'), isFalse);
    });

    test('unsupported levels are skipped and never block the path', () {
      final progress = completed(['l1', 'l2', 'l3', 'l4']);
      expect(policy.isUnlocked(course, progress, 'l5'), isFalse);
      expect(policy.isUnlocked(course, progress, 'l6'), isTrue);
      expect(policy.nextAfter(course, 'l4')?.id, 'l6');
    });

    test('nextToPlay returns the first open, uncompleted level', () {
      expect(
        policy.nextToPlay(course, CourseProgress(courseId: testCourseId))?.id,
        'l1',
      );
      expect(policy.nextToPlay(course, completed(['l1', 'l2']))?.id, 'l3');
      expect(
        policy.nextToPlay(course, completed(['l1', 'l2', 'l3', 'l4', 'l6'])),
        isNull,
      );
    });
  });

  group('modulesOpen mode (experienced players)', () {
    test('first level of each module is open', () {
      final progress = CourseProgress(courseId: testCourseId);
      expect(
        policy.isUnlocked(course, progress, 'l4', mode: UnlockMode.modulesOpen),
        isTrue,
      );
      expect(
        policy.isUnlocked(course, progress, 'l2', mode: UnlockMode.modulesOpen),
        isFalse,
      );
    });
  });

  group('LearningMapBuilder', () {
    test('marks completed, current and locked nodes', () {
      final map = const LearningMapBuilder().build(course, completed(['l1']));
      final nodes = {
        for (final section in map.sections)
          for (final node in section.nodes) node.level.id: node.state,
      };
      expect(nodes['l1'], MapNodeState.completed);
      expect(nodes['l2'], MapNodeState.current);
      expect(nodes['l3'], MapNodeState.locked);
      expect(nodes.containsKey('l5'), isFalse, reason: 'unsupported hidden');
      expect(map.completed, 1);
      expect(map.total, 5);
      expect(map.stars, 3);
      expect(map.nextLevel?.id, 'l2');
    });
  });
}
