# Bytecraft

Игра для обучения программированию короткими головоломками (1–3 минуты). MVP: Flutter, курс **Python Basics** — 5 модулей, 25 уровней, 4 механики.

## Быстрый старт

Нужен Flutter (stable, Dart ≥ 3.8).

```bash
./tool/verify.sh      # создаст android/ios, pub get, проверит контент, analyze + test
flutter run
```

`verify.sh` при первом запуске выполняет `flutter create --platforms=android,ios .` — эта команда добавляет только недостающие платформенные папки и не перезаписывает `lib/`, `test/`, `pubspec.yaml`.

## Что работает

- Onboarding (опыт → язык), Home, карта курса, Profile, Shop, Premium (mock-покупки)
- Механики: Multiple Choice, Fill Missing Code, Code Ordering (drag & drop), Find the Bug
- XP, звёзды, жизни с восстановлением, streak (+ заморозка), монеты, уровень аккаунта
- Достижения, задача дня, разблокировка уровней (для «я уже программист» открыты все модули)
- Прогресс сохраняется локально и переживает перезапуск; светлая и тёмная тема

## Архитектура

См. [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md): ADR, дерево проекта, Level Engine, data flow, хранилище, роутинг, состояние.

## Контент

Уровни — JSON в `assets/content/python/modules/`. Источник истины — `tool/content/generate_python_course.py`: он генерирует JSON и **исполняет каждый сниппет реальным Python**, проверяя ожидаемый вывод, полноту допустимых порядков в ordering-задачах и то, что bug-finder уровни действительно ломаются и чинятся.

```bash
python3 tool/content/generate_python_course.py assets/content/python/modules
```

Удалённый контент: `flutter run --dart-define=CONTENT_BASE_URL=https://cdn.example.com` — клиент будет запрашивать `GET /courses/python` и кэшировать версию, если её `version` выше бандла.

## Как добавить новый тип задания

1. `LevelType` + подкласс `LevelPayload` и парсер в `ContentParser.defaultPayloadParsers`
2. Подкласс `Answer` (если нужна новая форма ответа)
3. `AnswerValidator` → `ValidatorRegistry.standard()`
4. `QuestionRenderer` → `QuestionRendererRegistry.standard`

Экраны, engine и прогресс менять не нужно.

## CI

GitHub Actions (`.github/workflows/android.yml`) on every PR and push to `main`: `flutter analyze`, `flutter test`, release APK. On PRs the results are posted as a comment; on `main` the APK is published as a GitHub Release. Release signing setup: [docs/RELEASE.md](docs/RELEASE.md).
