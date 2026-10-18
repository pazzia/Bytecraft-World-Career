# 21. Практика (хаб)

- Задача бэклога: X-11
- Этап: 2
- Спецификация: `design/SPEC.md`
- Куда класть результат: `design/renders/21-practice/`
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

Screen “Практика”. Title 30 pt “Практика”. Full-width white tile 88 pt with blue circular-arrows icon, title “Повторение”, caption “3 темы к повторению”, chevron. White tile with red pencil icon, title “Работа над ошибками”, caption “Циклы: 2, Строки: 1”, chevron. Navy tile #1C2B42 with orange timer icon, white title “На время”, caption #A9B8CC “4 модуля открыто · рекорд 6:10”, chevron. Two white tiles 169×88: “{ }” icon blue, “Задачи с кодом”, caption “12 из 47”; play icon blue, “Песочница”, caption “Свой код на Python”. Tab bar with “Практика” selected and a small blue badge “3”.
```

## Спецификация

Выдержка из `design/SPEC.md`. Если выдержка и SPEC расходятся, верен SPEC.

### 5.6 Практика — X-11

```
┌──────────────────────────────┐
│ Практика                      │ H1
│ [Повторение — 3 темы к повторению  >] │ плитка, иконка Blue
│ [Работа над ошибками — Циклы: 2, Строки: 1 >] │ иконка Red (после F-4)
│ [На время — 4 модуля открыто · рекорд 6:10 >] │ ночная плитка
│ [Задачи с кодом  ][Песочница    ] │ 169×88
│                   12 из 47      Свой код на Python │
└──────────────────────────────┘
```

- Порядок плиток фиксирован: от срочного к свободному.
- Плитка «Повторение» без тем к повторению: Caption «Сегодня всё повторено».
- «Работа над ошибками» скрыта, пока нет ошибок или пока не выпущена F-4.
- Бейдж вкладки — число тем к повторению.

Промпт: «[ВКЛАДКИ] Screen “Практика”. Title 30 pt “Практика”. Full-width white tile 88 pt with blue circular-arrows icon, title “Повторение”, caption “3 темы к повторению”, chevron. White tile with red pencil icon, title “Работа над ошибками”, caption “Циклы: 2, Строки: 1”, chevron. Navy tile #1C2B42 with orange timer icon, white title “На время”, caption #A9B8CC “4 модуля открыто · рекорд 6:10”, chevron. Two white tiles 169×88: “{ }” icon blue, “Задачи с кодом”, caption “12 из 47”; play icon blue, “Песочница”, caption “Свой код на Python”. Tab bar with “Практика” selected and a small blue badge “3”.»

## Приёмка

- [ ] Тексты совпадают со спецификацией дословно.
- [ ] Цвета соответствуют ролям: жёлтый только у наград, оранжевый только у серии и времени.
- [ ] Не больше одной главной кнопки.
- [ ] Макет прошёл ревизию субагента-критика (виза в `design/README.md`).
