import 'achievement.dart';
import 'achievement_catalog.dart';

class AchievementEvaluator {
  const AchievementEvaluator({this.catalog = AchievementCatalog.all});

  final List<Achievement> catalog;

  /// Achievements reached by [stats] that are not in [alreadyUnlocked].
  List<Achievement> newlyUnlocked(
    PlayerStats stats,
    Set<String> alreadyUnlocked,
  ) =>
      catalog
          .where((achievement) => !alreadyUnlocked.contains(achievement.id))
          .where((achievement) => stats.valueOf(achievement) >= achievement.threshold)
          .toList(growable: false);
}
