# 20. Путь (карта курса)

- Задача бэклога: X-11
- Этап: 2
- Спецификация: `design/SPEC.md`
- Куда класть результат: `design/renders/20-path/`
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

Screen “Путь”. Header: bold 30 pt “Путь” left, caption “48 из 423” right. Module header: bold 20 pt “Циклы”, caption “3 из 8” right; below it a blue text link “Тема модуля”. A vertical zig-zag path, nodes centered with horizontal offsets −48, 0, +48, 0 pt and 88 pt vertical step: node 1 and 2 are green #157A52 round keycaps 64 pt with white check marks and three tiny yellow stars outlined #9A7400 under each; node 3 is a larger blue #2F6DB5 keycap 76 pt with white “3” and a blue label “Начать” to its right; node 4 is a white keycap with “4”; node 5 is a flat light grey #DCE3ED circle with #C3CEDC outline and a grey #5B6B7F lock; at the bottom a wide white keycap 96×64 with a bug icon and caption “Босс модуля”. Then module header “Списки” with “0 из 10” and two flat locked nodes. Tab bar, “Путь” selected.
```

## Спецификация

Выдержка из `design/SPEC.md`. Если выдержка и SPEC расходятся, верен SPEC.

### 5.2 Путь — X-11

Задача: увидеть, где я в курсе, и открыть любой доступный уровень или тему модуля.

```
┌──────────────────────────────┐
│ Путь               48 из 423  │ H1 + Caption
│ Циклы              3 из 8     │ H3 + Caption (заголовок модуля)
│ Тема модуля                   │ Quiet-ссылка
│          (✓)                  │ змейка: x = центр + (−48, 0, +48, 0)
│      (✓)                      │ шаг по вертикали 88
│          (3)  Начать          │ текущий 76
│              ( 4 )            │ доступен
│          (замок)              │ закрыт
│      [ жук  Босс модуля ]      │ 96×64
│ Списки             0 из 10    │
└──────────────────────────────┘
```

Детали:
- При входе экран прокручен так, чтобы текущий узел был на 40% высоты.
- Нажатие на закрытый узел открывает лист 5.14.2 с текстом «Сначала пройдите уровень „Цикл while“» и кнопкой «Перейти к уровню».
- Пройденный узел сразу открывает уровень снова (повтор), без промежуточного листа; правило повтора видно на экране результата («Повтор: 20% XP, без монет»).
- Переключателя «Обучение / На время» нет.

Промпт: «[ВКЛАДКИ] Screen “Путь”. Header: bold 30 pt “Путь” left, caption “48 из 423” right. Module header: bold 20 pt “Циклы”, caption “3 из 8” right; below it a blue text link “Тема модуля”. A vertical zig-zag path, nodes centered with horizontal offsets −48, 0, +48, 0 pt and 88 pt vertical step: node 1 and 2 are green #157A52 round keycaps 64 pt with white check marks and three tiny yellow stars outlined #9A7400 under each; node 3 is a larger blue #2F6DB5 keycap 76 pt with white “3” and a blue label “Начать” to its right; node 4 is a white keycap with “4”; node 5 is a flat light grey #DCE3ED circle with #C3CEDC outline and a grey #5B6B7F lock; at the bottom a wide white keycap 96×64 with a bug icon and caption “Босс модуля”. Then module header “Списки” with “0 из 10” and two flat locked nodes. Tab bar, “Путь” selected.»

## Приёмка

- [ ] Тексты совпадают со спецификацией дословно.
- [ ] Цвета соответствуют ролям: жёлтый только у наград, оранжевый только у серии и времени.
- [ ] Не больше одной главной кнопки.
- [ ] Макет прошёл ревизию субагента-критика (виза в `design/README.md`).
