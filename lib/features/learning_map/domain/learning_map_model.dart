import '../../courses/domain/course.dart';
import '../../courses/domain/level_definition.dart';
import '../../progress/domain/course_progress.dart';
import '../../progress/domain/unlock_policy.dart';

enum MapNodeState { completed, current, available, locked }

class MapNode {
  const MapNode({
    required this.level,
    required this.state,
    required this.stars,
  });

  final LevelDefinition level;
  final MapNodeState state;
  final int stars;

  bool get isPlayable => state != MapNodeState.locked;
}

class MapSection {
  const MapSection({required this.module, required this.nodes});

  final CourseModule module;
  final List<MapNode> nodes;

  int get completed =>
      nodes.where((node) => node.state == MapNodeState.completed).length;

  int get total => nodes.length;
}

/// Read model for the learning map and home screen.
class LearningMapModel {
  const LearningMapModel({
    required this.course,
    required this.sections,
    required this.nextLevel,
  });

  final Course course;
  final List<MapSection> sections;

  /// Level behind "Continue"; null when the course is finished.
  final LevelDefinition? nextLevel;

  int get completed =>
      sections.fold(0, (sum, section) => sum + section.completed);

  int get total => sections.fold(0, (sum, section) => sum + section.total);

  double get progress => total == 0 ? 0 : completed / total;

  int get stars => sections.fold(
        0,
        (sum, section) =>
            sum + section.nodes.fold(0, (acc, node) => acc + node.stars),
      );
}

/// Pure projection: (course, progress, unlock rules) -> map nodes.
class LearningMapBuilder {
  const LearningMapBuilder({this.unlockPolicy = const UnlockPolicy()});

  final UnlockPolicy unlockPolicy;

  LearningMapModel build(
    Course course,
    CourseProgress progress, {
    UnlockMode mode = UnlockMode.linear,
  }) {
    final next = unlockPolicy.nextToPlay(course, progress, mode: mode);
    final sections = course.modules.map((module) {
      final nodes = module.levels
          .where((level) => level.isSupported)
          .map((level) {
        final levelProgress = progress.levelOf(level.id);
        final MapNodeState state;
        if (levelProgress.completed) {
          state = MapNodeState.completed;
        } else if (level.id == next?.id) {
          state = MapNodeState.current;
        } else if (unlockPolicy.isUnlocked(course, progress, level.id,
            mode: mode)) {
          state = MapNodeState.available;
        } else {
          state = MapNodeState.locked;
        }
        return MapNode(
          level: level,
          state: state,
          stars: levelProgress.bestStars,
        );
      }).toList(growable: false);
      return MapSection(module: module, nodes: nodes);
    }).toList(growable: false);
    return LearningMapModel(
      course: course,
      sections: sections,
      nextLevel: next,
    );
  }
}
