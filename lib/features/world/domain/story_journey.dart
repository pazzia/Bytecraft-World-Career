import 'world_state.dart';

enum StoryDestination { expedition, project, boss, course }

/// Describes the next real action, including migrated project progress that
/// earned rewards but has not yet been verified by running the player's code.
class StoryJourney {
  StoryJourney(this.world, {this.verifiedComponents = 0});
  final WorldState world;
  final int verifiedComponents;
  int get projectCount =>
      world.hasVerifiedProject ? 4 : verifiedComponents.clamp(0, 4);
  int get completedStages =>
      (world.expeditionProgress == 5 ? 1 : 0) +
      (world.hasVerifiedProject ? 1 : 0) +
      (world.bossCleared ? 1 : 0);
  StoryDestination get destination =>
      world.expeditionProgress < 5 || !world.expeditionChestClaimed
      ? StoryDestination.expedition
      : !world.hasVerifiedProject
      ? StoryDestination.project
      : !world.bossCleared
      ? StoryDestination.boss
      : StoryDestination.course;
  String get title => switch (destination) {
    StoryDestination.expedition =>
      world.expeditionProgress < 5 ? 'Восстанови API' : 'Забери сундук',
    StoryDestination.project => 'Напиши калькулятор',
    StoryDestination.boss => 'Исправь уязвимости босса',
    StoryDestination.course => 'История завершена',
  };
  String get action => switch (destination) {
    StoryDestination.expedition =>
      world.expeditionProgress < 5
          ? 'Продолжить историю: API ${world.expeditionProgress}/5'
          : 'Забрать сундук экспедиции',
    StoryDestination.project => 'Собрать калькулятор: $projectCount/4',
    StoryDestination.boss => 'Победить Bug Lord: ${world.bossHp} HP',
    StoryDestination.course => 'История пройдена · продолжить курс',
  };
  String get instruction => switch (destination) {
    StoryDestination.expedition =>
      world.expeditionProgress < 5
          ? 'Реши ${5 - world.expeditionProgress} оставшихся задач. Ошибка не перемещает персонажа.'
          : 'Нажми «Открыть сундук» в экспедиции. Награда выдаётся один раз.',
    StoryDestination.project =>
      'Проверено $projectCount/4 компонентов твоего кода. Старые ответы на вопросы не заменяют запуск программы.',
    StoryDestination.boss =>
      'Реши оставшиеся уязвимости. Каждый верный ответ снимает 25 HP.',
    StoryDestination.course =>
      'Продолжай курс и применяй знания в новых задачах.',
  };
  String get result => switch (destination) {
    StoryDestination.expedition =>
      world.expeditionProgress < 5
          ? 'После 5 задач откроются сундук и проект калькулятора.'
          : '+100 XP, +80 монет и +2 алмаза. Следом — свой код калькулятора.',
    StoryDestination.project => 'После 14 успешных проверок сохранится рабочая программа и откроется босс.',
    StoryDestination.boss => 'Победа завершит историю восстановления API.',
    StoryDestination.course =>
      'Прогресс, программа и полученные награды сохранены.',
  };
}
