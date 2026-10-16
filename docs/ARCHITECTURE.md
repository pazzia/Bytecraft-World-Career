# Bytecraft — архитектура MVP

Мобильная игра для обучения программированию короткими (1–3 мин) головоломками. MVP: Flutter (iOS + Android), курс Python Basics.

---

## Этап 1. Architecture Decision Record

| # | Решение | Почему | Альтернатива / когда пересмотреть |
|---|---------|--------|-----------------------------------|
| ADR-1 | **Flutter + Dart**, одна кодовая база | Игровой UI с анимациями, единый рендер на iOS/Android, быстрый hot reload для итераций по геймдизайну | React Native — если команда сильна в TS; нативно — не окупается на MVP |
| ADR-2 | **Модульная Clean Architecture «по фичам»**: `domain / data / presentation` внутри фичи | Маленькая команда видит всё про фичу в одной папке; domain — чистый Dart без Flutter → тестируется без эмулятора | Отдельные пакеты (melos) — когда команда > 6–8 человек |
| ADR-3 | **Data-driven уровни**: JSON → `LevelDefinition` + типизированный `LevelPayload` (sealed) | Контент обновляется без релиза; новый тип задания = payload + parser + validator + renderer, без правок экранов | — |
| ADR-4 | **Level Engine — чистый Dart**, UI-агностичный. Рендереры только собирают `Answer` | Логику (XP, звёзды, жизни, streak, unlock) можно покрыть юнит-тестами целиком | — |
| ADR-5 | **Riverpod 3** — DI + состояние; `providers.dart` — единственный composition root | Compile-safe DI без кодогена, override в тестах, нет глобальных синглтонов | — |
| ADR-6 | **Без кодогенерации на MVP** (Freezed/json_serializable отложены) | Проект собирается сразу после `pub get`; модели — иммутабельные классы с `copyWith`/`toJson` вручную, их ~15 | Включить Freezed, когда моделей станет > 30 или понадобится union-сериализация с бэкенда |
| ADR-7 | **Хранилище: порт `KeyValueStore` + JSON-документы со `schemaVersion`**, адаптер SharedPreferences | Объём прогресса мал (сотни уровней × ~100 байт); нет нативных зависимостей и build_runner; битые документы → дефолты, а не краш | Drift (SQLite) — при истории попыток, лидербордах офлайн, > 5k записей. Меняется только адаптер. Isar не берём: проект фактически заброшен |
| ADR-8 | **Offline-first**: бандл-контент + кэш удалённого; прогресс пишется локально и помечается dirty для синка | Обучение работает без сети; сеть — только оптимизация | — |
| ADR-9 | **Все внешние сервисы за интерфейсами + mock-адаптеры**: Analytics, Monetization, AI Tutor, Code Execution, Auth, CloudSync, Leaderboard, MetaGame, FeatureFlags | Бизнес-логика не знает о Firebase/AdMob/LLM; адаптеры подключаются заменой одной строки в composition root | Firebase не подключён в MVP — требует `google-services.json` / `GoogleService-Info.plist`; добавляется адаптерами |
| ADR-10 | **Код пользователя никогда не исполняется на app-бэкенде.** MVP — предопределённая валидация; в будущем `CodeExecutionService` → изолированный sandbox (timeout, mem, CPU, без сети) | Безопасность | — |
| ADR-11 | **Drag & drop на `LongPressDraggable` + `DragTarget`**, а не `ReorderableListView` | В свежих Flutter у `ReorderableListView.onReorder` сменился API (deprecated → `onReorderItem`); свой виджет не зависит от версии и работает внутри общего скролла | — |
| ADR-12 | **Level Complete — фаза уровня, а не отдельный маршрут** | Результат не теряется при deep link / восстановлении, нет передачи объектов через `extra` | — |
| ADR-13 | Неизвестный тип уровня из удалённого контента → `UnsupportedPayload`, уровень **прозрачен** для разблокировки | Старый клиент не падает и не блокирует путь игрока, если контент опередил версию приложения | — |

---

## 1. Итоговая архитектура

```
┌──────────────── presentation (Flutter) ────────────────┐
│ Screens · Renderers · Riverpod controllers / read models │
└───────────────┬────────────────────────────────────────┘
                │ вызывает
┌───────────────▼──────────── domain (чистый Dart) ───────┐
│ LevelEngine · Validators · UnlockPolicy · LivesPolicy     │
│ StreakPolicy · Reward/Star/AccountLevel calculators       │
│ AchievementEvaluator · модели · интерфейсы репозиториев   │
└───────────────┬────────────────────────────────────────┘
                │ реализуют
┌───────────────▼──────────── data / services ────────────┐
│ DefaultContentRepository (bundled + remote + cache)       │
│ LocalProgressRepository · LocalSettingsRepository         │
│ Mock*/Logging*/Local* адаптеры внешних сервисов           │
└───────────────┬────────────────────────────────────────┘
                ▼
        KeyValueStore (SharedPreferences)  ·  assets/content/*.json  ·  Dio
```

## 2. Дерево проекта

```
lib/
  main.dart
  app/            app.dart · bootstrap.dart · di/providers.dart (composition root)
                  router/ (routes, GoRouter + redirect) · shell/ · startup/
  core/           config · errors · storage (KeyValueStore, JsonDocumentStore, keys)
                  theme (colors, spacing/radius/shadows, typography, GameColors, AppTheme)
                  time (Clock, CalendarDay) · utils (JsonReader, IdGenerator)
  features/
    courses/      domain: Course, CourseModule, LevelDefinition, LevelType/Role, LevelPayload
                  data: ContentParser, Bundled/Remote sources, ContentCache, DefaultContentRepository
    level/        domain: Answer, ValidationOutcome, LevelSession, LevelResult, InitialAnswerFactory
                  engine: LevelEngine, ValidatorRegistry, validators/*
                  renderers: QuestionRenderer + MultipleChoice/FillCode/CodeOrdering/BugFinder/Unsupported
                  presentation: LevelController, LevelUiState, LevelScreen, widgets/*
    progress/     UserProfile, CourseProgress, LevelProgress, UnlockPolicy, LocalProgressRepository
    gamification/ GameRules, Lives, Streak, Reward, Star/Reward/AccountLevel calculators
    achievements/ Achievement, Catalog, Evaluator
    daily_challenge/ DailyChallenge(Service), LocalDailyChallengeService
    learning_map/ LearningMapBuilder (read model) + экран карты
    settings/  onboarding/  splash/  home/  profile/  shop/ (EconomyService)  premium/
    leaderboard/  metagame/        (интерфейсы + mock)
  services/       analytics · feature_flags · monetization · ai_tutor · code_execution · auth · sync
  shared/         widgets (AppButton, AppCard, CodeBlock, AppProgressBar, badges) · utils (PythonHighlighter)
assets/content/   catalog.json · python/course.json · python/modules/*.json
test/             engine, validators, XP/stars, lives, streak, unlock, content, storage, router, widgets
tool/             verify.sh · content/generate_python_course.py (генерация + проверка контента реальным Python)
```

## 3. Основные зависимости

| Пакет | Зачем |
|-------|-------|
| `flutter_riverpod ^3` | DI + состояние |
| `go_router ^17` | декларативный роутинг, redirect, shell с табами |
| `shared_preferences ^2.5` | адаптер `KeyValueStore` |
| `dio ^5` | `DioRemoteContentSource`, будущий бэкенд |
| `flutter_lints ^6` (dev) | линтер |

Отложено осознанно: Freezed/json_serializable (ADR-6), Drift (ADR-7), Firebase (ADR-9).

## 4. Domain models

- **Контент:** `Course` → `CourseModule` → `LevelDefinition { id, type, role, title, prompt, code?, difficulty, xpOverride?, livesPenalty, hint?, explanation, payload }`
- **Payload (sealed):** `MultipleChoicePayload`, `FillCodePayload`, `CodeOrderingPayload` (+ `alternativeOrders`), `BugFinderPayload`, `UnsupportedPayload`
- **Ответ (sealed):** `ChoiceAnswer`, `FillCodeAnswer`, `OrderingAnswer`, `LineSelectionAnswer`
- **Игра:** `LevelSession`, `ValidationOutcome`, `SubmissionResult`, `LevelResult`, `LivesSnapshot`
- **Игрок:** `UserProfile { userId, displayName, avatarId, totalXp, coins, isPremium, createdAt, lastActivityAt, lives: LivesState, streak: StreakState, unlockedAchievements, lastDailyChallengeDay }`; `CourseProgress`; `LevelProgress { attempts, bestStars, xpEarned, completedAt }`. Уровень аккаунта и агрегаты курса **вычисляются**, не хранятся.
- **Прочее:** `Achievement`, `Reward`, `DailyChallenge`, `Subscription`/`SubscriptionPlan`, `ShopItem`, `GameRules` (все числа экономики).

## 5. Data flow (один ответ)

```
Renderer (tap/drag) ─► LevelController.updateAnswer(Answer)       [UI state]
"Проверить"          ─► LevelEngine.submit(session, answer)
                          ├─ ValidatorRegistry → ValidationOutcome
                          ├─ неверно: LivesPolicy.loseLives → saveProfile
                          └─ верно:  Star/Reward calc · Streak · Achievements
                                     → saveCourseProgress → saveProfile (+ dirty для синка)
                       ◄─ SubmissionResult
LevelController ─► LevelUiState (feedback → rewards) ; progressRevision++
Home / Map / Profile (FutureProvider read models) пересчитываются
```

## 6. Level Engine

`LevelEngine.start(courseId, levelId, mode)` → `LevelStarted | LevelStartDenied(notFound | locked | unsupported | noLives)`; фиксирует попытку.
`LevelEngine.submit(session, answer)` → `SubmissionResult { session, outcome, lives, completion? }`.
Расширение — регистрация в двух местах: `ValidatorRegistry.standard()` и `QuestionRendererRegistry.standard` (+ парсер payload в `ContentParser`).

## 7. Repository interfaces

```dart
abstract interface class ContentRepository  { loadCatalog(); loadCourse(id); refreshCourse(id); }
abstract interface class ProgressRepository { loadProfile(); saveProfile(p); loadCourseProgress(id); saveCourseProgress(p); resetAll(); }
abstract interface class SettingsRepository { load(); save(s); }
abstract interface class DailyChallengeService { challengeFor(day, courseId); }
abstract interface class LeaderboardRepository { currentLeague(userId); }
```

## 8. Storage

- `KeyValueStore` (порт) → `SharedPreferencesStore` (namespace `bytecraft.`) / `InMemoryKeyValueStore` (тесты).
- `JsonDocumentStore`: документ = JSON + `schemaVersion`; повреждённый → `null` → дефолты.
- Ключи (`StorageKeys`): `player.profile`, `player.course.<id>`, `app.settings`, `content.cache.<id>`, `sync.dirty`.
- Порядок записи при завершении уровня: сначала прогресс курса, потом профиль — сбой между записями теряет максимум награду, но не факт прохождения.
- Контент: `assets/content` (офлайн, всегда) ← кэш удалённой версии побеждает только при большем `version` и только после успешного парсинга.

## 9. Routing

`/splash` → (`appStartupProvider` готов) → `/onboarding` → `/onboarding/course?experience=` → shell-табы `/home`, `/map`, `/profile`; поверх: `/level/:courseId/:levelId?daily=1`, `/shop`, `/premium`. Все переходы между splash/onboarding/home решает чистая функция `resolveRedirect` (покрыта тестом).

## 10. State management

| Слой | Где | Пример |
|------|-----|--------|
| UI state | `Notifier`/`AsyncNotifier` в presentation | `LevelUiState` (фаза, черновик ответа, подсветка ошибок) |
| Domain state | иммутабельные объекты, которые возвращает engine | `LevelSession`, `LevelResult` |
| Persistence | репозитории | `UserProfile`, `CourseProgress` |
| Read models | `FutureProvider`, зависят от `progressRevisionProvider` | `learningMapProvider`, `homeViewModelProvider` |

Виджеты не содержат бизнес-логики: рендереры только отображают черновик ответа и сообщают об изменениях.

---

## Геймдизайн-константы (`GameRules.standard`)

Жизни 5, +1 каждые 30 мин · XP: урок 10, практика 10, challenge 20, boss 50, +5 за идеальное прохождение, повтор 20% · Звёзды: 0 ошибок → 3, 1 → 2, иначе 1 · Монеты за первое прохождение 1/2/5/15 · Уровень аккаунта N→N+1 = 100·N XP · Задача дня +25 XP +10 монет · Заморозка серии 50 монет (макс 2) · Полные жизни 30 монет.

## Roadmap-готовность

| Этап | Что уже заложено |
|------|------------------|
| 100 уровней Python | контент в JSON + генератор с проверкой реальным Python |
| Daily Challenges | `DailyChallengeService` + бонус в engine (работает) |
| Achievements | каталог + evaluator (работает) |
| Premium / Ads | `MonetizationService`, `EconomyService`, фича-флаг `ads_enabled` |
| JavaScript / SQL | `catalog.json`, `courseId` везде, `CourseSummary.availability` |
| Leaderboards | `LeaderboardRepository` + mock; XP уходит через `CloudSyncService` |
| AI Tutor | `AITutorService` (mock), engine от него не зависит |
| Meta Game | `MetaGameService` + маппинг курс → отдел |
| UGC / PvP | `CodeExecutionService` + sandbox-требования в `ExecutionLimits` |
