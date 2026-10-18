# 19. Сегодня (главная)

- Задача бэклога: X-11, X-3
- Этап: 2
- Спецификация: `design/SPEC.md`
- Куда класть результат: `design/renders/19-today/`
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

Screen “Сегодня”. At y=47 a 44 pt HUD row, left-aligned with 16 pt gaps: orange flame icon outlined #B83A0B with “12”, yellow bolt icon outlined #9A7400 with “2 440”, red heart with “4”, numbers bold 17 pt #1B2838. At y=111 grey 13 pt label “Python: от основ до профи”, then bold 30 pt title “Циклы”. At y=171 a dark code board 350 pt wide, radius 22, 20 pt padding: first row “Уровень 3 из 8” in #AFC0D6 and “+15 XP” in yellow at the right; two code lines “for i in range(3):” and “    print(i)”; white 17 pt bold “Что напечатает цикл?”; a full-width blue keycap button 56 pt tall “Начать уровень”. At y=441 a thin bar of 37 tiny rounded segments (5 green, 1 blue, 31 light grey #DCE3ED) and caption “48 из 423 уровней · 96 звёзд”. At y=497 two keycap tiles 169×88 with a 12 pt gap: left white tile, blue calendar icon, title “Уровень дня”, caption “+25 XP и 10 монет”; right navy tile #1C2B42 with orange timer icon, white title “На время”, caption #A9B8CC “×2 XP за первый забег”. At y=597 a full-width white tile 88 pt: blue circular-arrows icon, title “К повторению”, caption “3 темы”, grey chevron right. Tab bar with “Сегодня” selected in blue.
```

### Макет в тёмной теме

```text
Mobile app UI mockup of one iPhone 14 screen, 390×844 pt, flat vector UI, no device frame, no photos, no gradients, no glassmorphism, no blurred shadows. Every pressable element is a mechanical keyboard keycap: a solid face and a solid 4 pt darker bottom edge, corner radius 14 (tiles 16). Fonts: Onest for interface text, JetBrains Mono for code. Page background #EEF2F7, surfaces #FFFFFF, main text #1B2838, secondary text #5B6B7F. Action blue #2F6DB5 with edge #1F4E86. Reward yellow #FFD43B used only for XP, stars and coins icons and numbers, never for buttons. Success green #157A52, error red #D23C42, streak and timer orange #FF5B1F. Code sits on a dark board #1B2838 with radius 22: plain code #E8EEF6, keywords #C792EA, builtins #82AAFF, strings #C3E88D, numbers #F78C6C, comments and line numbers #8796AB. All text in Russian exactly as quoted, sentence case, no emoji, no all caps. Status bar 47 pt at top. Bottom tab bar 68 pt plus 34 pt safe area, white, top hairline #D5DDE8, four tabs with rounded icons and labels: «Сегодня» (house), «Путь» (route), «Практика» (dumbbell), «Профиль» (person).

Screen “Сегодня”. At y=47 a 44 pt HUD row, left-aligned with 16 pt gaps: orange flame icon outlined #B83A0B with “12”, yellow bolt icon outlined #9A7400 with “2 440”, red heart with “4”, numbers bold 17 pt #1B2838. At y=111 grey 13 pt label “Python: от основ до профи”, then bold 30 pt title “Циклы”. At y=171 a dark code board 350 pt wide, radius 22, 20 pt padding: first row “Уровень 3 из 8” in #AFC0D6 and “+15 XP” in yellow at the right; two code lines “for i in range(3):” and “    print(i)”; white 17 pt bold “Что напечатает цикл?”; a full-width blue keycap button 56 pt tall “Начать уровень”. At y=441 a thin bar of 37 tiny rounded segments (5 green, 1 blue, 31 light grey #DCE3ED) and caption “48 из 423 уровней · 96 звёзд”. At y=497 two keycap tiles 169×88 with a 12 pt gap: left white tile, blue calendar icon, title “Уровень дня”, caption “+25 XP и 10 монет”; right navy tile #1C2B42 with orange timer icon, white title “На время”, caption #A9B8CC “×2 XP за первый забег”. At y=597 a full-width white tile 88 pt: blue circular-arrows icon, title “К повторению”, caption “3 темы”, grey chevron right. Tab bar with “Сегодня” selected in blue.

Dark theme variant: page background #142033, sheets and tiles #1C2B42, answer keys and secondary keycaps #22344F with edge #0D1726 and text #F1F5FA, selected answer key face #213A5C with 2 pt outline #5B95DB, correct answer key #173B33 outlined #2BB57A, wrong answer key #3F2230 outlined #E25B60, main text #F1F5FA, secondary #A9B8CC, code board #0D1726, blue links and selected outlines #5B95DB; primary, success and danger buttons keep their light-theme face colors; wrong-answer panel #3F2230 with title #FF8A8E, correct-answer panel #173B33 with title #5FD39C; tab bar background #0D1726, selected tab #5B95DB, other tabs #A9B8CC.
```

## Спецификация

Выдержка из `design/SPEC.md`. Если выдержка и SPEC расходятся, верен SPEC.

### 5.1 Сегодня — X-3

Задача: за секунду понять, что делать сейчас, и начать одним касанием.

```
y=47  ┌──────────────────────────────┐
      │ [огонь]12 [молния]2 440 [♥]4  │ HUD 44, слева
y=111 │ Python: от основ до профи     │ Caption #5B6B7F
      │ Циклы                         │ H1
y=171 │ ┌──────────────────────────┐ │ доска 350×~250, поля 20
      │ │ Уровень 3 из 8     +15 XP │ │ Caption #AFC0D6 / Yellow
      │ │ for i in range(3):        │ │ превью кода 2–4 строки
      │ │     print(i)              │ │
      │ │ Что напечатает цикл?      │ │ Title #E8EEF6
      │ │ [    Начать уровень    ]  │ │ Primary во всю ширину доски
      │ └──────────────────────────┘ │
y=441 │ 37 сегментов по 6 + зазор 2.6 │ полоса модулей
      │ 48 из 423 уровней · 96 звёзд  │ Caption
y=497 │ [Уровень дня ][ На время    ] │ две плитки 169×88, зазор 12
y=597 │ [ К повторению — 3 темы    >] │ плитка 350×88
      └ Сегодня  Путь  Практика  Профиль┘
```

Детали:
- В HUD три бейджа (4.4). Кнопки профиля нет (N3).
- Полоса модулей: 37 сегментов шириной 6,9 и высотой 8 с зазором 2,6. Пройденный модуль `#157A52`, текущий `#2F6DB5`, остальные `#DCE3ED`. Под полосой подпись «48 из 423 уровней · 96 звёзд».
- Плитка «Уровень дня»: иконка календаря Blue, Title «Уровень дня», Caption «+25 XP и 10 монет». Выполнен: иконка-галочка Green, Caption «Выполнен. Следующий — завтра».
- Плитка «На время»: ночная, Title «На время», Caption «×2 XP за первый забег». Ведёт на 5.7.1.
- Плитка «К повторению»: иконка круговых стрелок Blue, Title «К повторению», Caption «3 темы». Если темы к повторению нет, на её месте плитка «Работа над ошибками» (Caption «2 темы с ошибками», после F-4), иначе ничего.
- После третьего уровня за день над заголовком модуля появляется Quiet-ссылка «Итоги дня» (5.11).

Состояния:

| Состояние | Что показываем |
|---|---|
| сразу после онбординга | первый уровень уже пройден: HUD «1 · 15 · 5», доска со вторым уровнем модуля «Переменные», плитка «Уровень дня»; плиток повторения нет |
| курс пройден | на доске Title «Курс пройден», Caption «423 из 423», Secondary «Открыть путь»; плитки остаются |
| загрузка | шаблон 5.15 |

Промпт: «[ВКЛАДКИ] Screen “Сегодня”. At y=47 a 44 pt HUD row, left-aligned with 16 pt gaps: orange flame icon outlined #B83A0B with “12”, yellow bolt icon outlined #9A7400 with “2 440”, red heart with “4”, numbers bold 17 pt #1B2838. At y=111 grey 13 pt label “Python: от основ до профи”, then bold 30 pt title “Циклы”. At y=171 a dark code board 350 pt wide, radius 22, 20 pt padding: first row “Уровень 3 из 8” in #AFC0D6 and “+15 XP” in yellow at the right; two code lines “for i in range(3):” and “    print(i)”; white 17 pt bold “Что напечатает цикл?”; a full-width blue keycap button 56 pt tall “Начать уровень”. At y=441 a thin bar of 37 tiny rounded segments (5 green, 1 blue, 31 light grey #DCE3ED) and caption “48 из 423 уровней · 96 звёзд”. At y=497 two keycap tiles 169×88 with a 12 pt gap: left white tile, blue calendar icon, title “Уровень дня”, caption “+25 XP и 10 монет”; right navy tile #1C2B42 with orange timer icon, white title “На время”, caption #A9B8CC “×2 XP за первый забег”. At y=597 a full-width white tile 88 pt: blue circular-arrows icon, title “К повторению”, caption “3 темы”, grey chevron right. Tab bar with “Сегодня” selected in blue.»

## Приёмка

- [ ] Тексты совпадают со спецификацией дословно.
- [ ] Цвета соответствуют ролям: жёлтый только у наград, оранжевый только у серии и времени.
- [ ] Не больше одной главной кнопки.
- [ ] Макет прошёл ревизию субагента-критика (виза в `design/README.md`).
