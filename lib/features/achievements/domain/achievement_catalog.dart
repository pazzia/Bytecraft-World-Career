import 'achievement.dart';

/// Built-in achievements. Kept as data so a remote catalog can replace it.
abstract final class AchievementCatalog {
  static const String pythonCourseId = 'python';

  static const List<Achievement> all = [
    Achievement(
      id: 'first_code',
      title: 'Первый код',
      description: 'Пройдите первый уровень',
      icon: '🚀',
      metric: AchievementMetric.levelsCompleted,
      threshold: 1,
    ),
    Achievement(
      id: 'levels_10',
      title: 'Десятка',
      description: 'Пройдите 10 уровней',
      icon: '🔟',
      metric: AchievementMetric.levelsCompleted,
      threshold: 10,
    ),
    Achievement(
      id: 'xp_1000',
      title: '1000 XP',
      description: 'Наберите 1000 опыта',
      icon: '⚡',
      metric: AchievementMetric.totalXp,
      threshold: 1000,
    ),
    Achievement(
      id: 'streak_7',
      title: 'Неделя в деле',
      description: 'Серия 7 дней',
      icon: '🔥',
      metric: AchievementMetric.longestStreak,
      threshold: 7,
    ),
    Achievement(
      id: 'streak_30',
      title: 'Месяц кода',
      description: 'Серия 30 дней',
      icon: '🌋',
      metric: AchievementMetric.longestStreak,
      threshold: 30,
    ),
    Achievement(
      id: 'perfect_level',
      title: 'Без единой ошибки',
      description: 'Пройдите уровень на 3 звезды',
      icon: '💎',
      metric: AchievementMetric.perfectLevels,
      threshold: 1,
    ),
    Achievement(
      id: 'python_beginner',
      title: 'Python Beginner',
      description: 'Пройдите 25% курса Python',
      icon: '🐍',
      metric: AchievementMetric.coursePercent,
      threshold: 25,
      courseId: pythonCourseId,
    ),
    Achievement(
      id: 'python_explorer',
      title: 'Python Explorer',
      description: 'Пройдите 60% курса Python',
      icon: '🧭',
      metric: AchievementMetric.coursePercent,
      threshold: 60,
      courseId: pythonCourseId,
    ),
    Achievement(
      id: 'python_master',
      title: 'Python Master',
      description: 'Пройдите весь курс Python',
      icon: '👑',
      metric: AchievementMetric.coursePercent,
      threshold: 100,
      courseId: pythonCourseId,
    ),
  ];
}
