# 27. Профиль

- Задача бэклога: X-11
- Этап: 2
- Спецификация: `design/SPEC.md`
- Куда класть результат: `design/renders/27-profile/`
- Статус: не начато

## Как отрисовать

1. Откройте новый чат в ChatGPT с генерацией изображений.
2. Скопируйте промпт ниже целиком, включая первую часть с цветами и шрифтами — без неё макет разойдётся с системой.
3. Сохраните результат как PNG в папку из шапки: `light.png`, для тёмной темы `dark.png`, для вариантов — `<вариант>.png`.
4. Если ChatGPT исказил текст или цвет, попросите исправить конкретную деталь («замени текст на кнопке на „Проверить“»), а не перегенерируйте с нуля.

## Промпты

### Макет

Префикс: ВКЛАДКИ.

```text
Mobile app UI mockup of one iPhone 14 screen, 390×844 pt, flat vector UI, no device frame, no photos, no gradients, no glassmorphism, no blurred shadows. Every pressable element is a mechanical keyboard keycap: a solid face and a solid 4 pt darker bottom edge, corner radius 14 (tiles 16). Fonts: Onest for interface text, JetBrains Mono for code. Page background #EEF2F7, surfaces #FFFFFF, main text #1B2838, secondary text #5B6B7F. Action blue #2F6DB5 with edge #1F4E86. Reward yellow #FFD43B used only for XP, stars and coins icons and numbers, never for buttons. Success green #157A52, error red #D23C42, streak and timer orange #FF5B1F. Code sits on a dark board #1B2838 with radius 22: plain code #E8EEF6, keywords #C792EA, builtins #82AAFF, strings #C3E88D, numbers #F78C6C, comments and line numbers #8796AB. All text in Russian exactly as quoted, sentence case, no emoji, no all caps. Status bar 47 pt at top. Bottom tab bar 68 pt plus 34 pt safe area, white, top hairline #D5DDE8, four tabs with rounded icons and labels: «Сегодня» (house), «Путь» (route), «Практика» (dumbbell), «Профиль» (person).

Screen “Профиль”. Header: 64 pt dark keycap avatar #1B2838 with white letter “И”, name “Игрок”, caption “Уровень 7 · 340 из 700 XP”, thin blue progress bar. Section “Боссы” with caption “5 из 37”, a row of five green round keycaps 48 pt with bug icons, blue link “Все боссы”. A 2×2 grid of flat white blocks: “2 440” / “XP всего”, “21” / “лучшая серия”, “126” / “уровней”, “81” / “с первой попытки”. Section “Достижения” with “6 из 9”, row of round badges (6 colored, 3 flat grey). A white tile with yellow coin outlined #9A7400 “42 монеты” and a white keycap “Магазин”. Settings rows: “Имя — Игрок”, “Тема оформления — Авто”, “Напоминание — 20:00”, “Аналитика — разрешена”, red text “Сбросить прогресс”. Tab bar, “Профиль” selected.
```

## Спецификация

Выдержка из `design/SPEC.md`. Если выдержка и SPEC расходятся, верен SPEC.

### 5.9 Профиль — шаг «Доказать»

- Шапка:
  - аватар — клавиша 64 на доске `#1B2838` с инициалом `#F1F5FA` (имя задаётся в профиле; по умолчанию инициал «И» от «Игрок»);
  - имя (H3);
  - Caption «Уровень 7 · 340 из 700 XP»;
  - полоса 8: заливка `#2F6DB5`, фон `#DCE3ED`. Полоса — прогресс, а не награда, поэтому синяя.
- «Боссы» (H3) и Caption «5 из 37». Ряд из 5 последних побед — клавиши-жуки 48 Green. Ссылка «Все боссы» открывает список, где каждый босс проходится снова как повтор.
- После N-3: блок «Навыки». После N-6: плитка «Недельная проверка» (4.4) с Primary «Начать проверку» внутри.
- Статистика 2 × 2: плоские блоки `#FFFFFF` без ребра (не нажимаются) — «2 440 / XP всего», «21 / лучшая серия», «126 / уровней», «81 / с первой попытки».
- «Достижения» и Caption «6 из 9»: ряд клавиш-значков 48; полученные цветные, остальные плоские `#DCE3ED`.
- Плитка «Монеты»: монета Yellow, «42 монеты», справа Secondary «Магазин» (N4).
- Настройки списком строк 56:
  - «Имя»;
  - «Тема оформления — Авто»;
  - «Напоминание — 20:00» (F-3);
  - «Аналитика — разрешена» (X-1);
  - «Сбросить прогресс» — текст `#D23C42`, лист подтверждения с Danger.

Промпт: «[ВКЛАДКИ] Screen “Профиль”. Header: 64 pt dark keycap avatar #1B2838 with white letter “И”, name “Игрок”, caption “Уровень 7 · 340 из 700 XP”, thin blue progress bar. Section “Боссы” with caption “5 из 37”, a row of five green round keycaps 48 pt with bug icons, blue link “Все боссы”. A 2×2 grid of flat white blocks: “2 440” / “XP всего”, “21” / “лучшая серия”, “126” / “уровней”, “81” / “с первой попытки”. Section “Достижения” with “6 из 9”, row of round badges (6 colored, 3 flat grey). A white tile with yellow coin outlined #9A7400 “42 монеты” and a white keycap “Магазин”. Settings rows: “Имя — Игрок”, “Тема оформления — Авто”, “Напоминание — 20:00”, “Аналитика — разрешена”, red text “Сбросить прогресс”. Tab bar, “Профиль” selected.»

## Приёмка

- [ ] Тексты совпадают со спецификацией дословно.
- [ ] Цвета соответствуют ролям: жёлтый только у наград, оранжевый только у серии и времени.
- [ ] Не больше одной главной кнопки.
- [ ] Макет прошёл ревизию субагента-критика (виза в `design/README.md`).
