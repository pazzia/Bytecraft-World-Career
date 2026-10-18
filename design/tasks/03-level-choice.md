# 03. Уровень: предскажи вывод и выбор ответа

- Задача бэклога: X-13, X-14, X-12b
- Этап: 1
- Спецификация: `design/SPEC.md`
- Куда класть результат: `design/renders/03-level-choice/`
- Статус: не начато

## Как отрисовать

1. Откройте новый чат в ChatGPT с генерацией изображений.
2. Скопируйте промпт ниже целиком, включая первую часть с цветами и шрифтами — без неё макет разойдётся с системой.
3. Сохраните результат как PNG в папку из шапки: `light.png`, для тёмной темы `dark.png`, для вариантов — `<вариант>.png`.
4. Если ChatGPT исказил текст или цвет, попросите исправить конкретную деталь («замени текст на кнопке на „Проверить“»), а не перегенерируйте с нуля.

## Промпты

### Макет

Префикс: ПОЛНОЭКРАННЫЙ.

```text
Mobile app UI mockup of one iPhone 14 screen, 390×844 pt, flat vector UI, no device frame, no photos, no gradients, no glassmorphism, no blurred shadows. Every pressable element is a mechanical keyboard keycap: a solid face and a solid 4 pt darker bottom edge, corner radius 14 (tiles 16). Fonts: Onest for interface text, JetBrains Mono for code. Page background #EEF2F7, surfaces #FFFFFF, main text #1B2838, secondary text #5B6B7F. Action blue #2F6DB5 with edge #1F4E86. Reward yellow #FFD43B used only for XP, stars and coins icons and numbers, never for buttons. Success green #157A52, error red #D23C42, streak and timer orange #FF5B1F. Code sits on a dark board #1B2838 with radius 22: plain code #E8EEF6, keywords #C792EA, builtins #82AAFF, strings #C3E88D, numbers #F78C6C, comments and line numbers #8796AB. All text in Russian exactly as quoted, sentence case, no emoji, no all caps. Status bar 47 pt at top. No tab bar. Home indicator area 34 pt at the bottom.

Level screen. At y=47 a 56 pt header: grey close “✕” at left, a segmented progress bar of 8 rounded segments 8 pt tall (4 green #157A52, 1 blue, 3 light grey), red heart with “4” at right. At y=115 bold 20 pt prompt “Что напечатает программа?”. A dark code board with line numbers in #8796AB: “x = 0”, “while x < 3:”, “    x += 1”, “print(x)”. Below, a 2×2 grid of white keycap answer keys 169×64 with 12 pt gaps, monospace labels “2”, “3”, “4”, “0”; key “3” is selected with a 2 pt blue outline and face #E6EFFA. At y=726 a square white keycap 56×56 with a blue #2F6DB5 lightbulb icon, and a wide blue keycap button “Проверить”. Under the lightbulb key a permanent 13 pt grey caption “−1 звезда”.
```

### Макет в тёмной теме

```text
Mobile app UI mockup of one iPhone 14 screen, 390×844 pt, flat vector UI, no device frame, no photos, no gradients, no glassmorphism, no blurred shadows. Every pressable element is a mechanical keyboard keycap: a solid face and a solid 4 pt darker bottom edge, corner radius 14 (tiles 16). Fonts: Onest for interface text, JetBrains Mono for code. Page background #EEF2F7, surfaces #FFFFFF, main text #1B2838, secondary text #5B6B7F. Action blue #2F6DB5 with edge #1F4E86. Reward yellow #FFD43B used only for XP, stars and coins icons and numbers, never for buttons. Success green #157A52, error red #D23C42, streak and timer orange #FF5B1F. Code sits on a dark board #1B2838 with radius 22: plain code #E8EEF6, keywords #C792EA, builtins #82AAFF, strings #C3E88D, numbers #F78C6C, comments and line numbers #8796AB. All text in Russian exactly as quoted, sentence case, no emoji, no all caps. Status bar 47 pt at top. No tab bar. Home indicator area 34 pt at the bottom.

Level screen. At y=47 a 56 pt header: grey close “✕” at left, a segmented progress bar of 8 rounded segments 8 pt tall (4 green #157A52, 1 blue, 3 light grey), red heart with “4” at right. At y=115 bold 20 pt prompt “Что напечатает программа?”. A dark code board with line numbers in #8796AB: “x = 0”, “while x < 3:”, “    x += 1”, “print(x)”. Below, a 2×2 grid of white keycap answer keys 169×64 with 12 pt gaps, monospace labels “2”, “3”, “4”, “0”; key “3” is selected with a 2 pt blue outline and face #E6EFFA. At y=726 a square white keycap 56×56 with a blue #2F6DB5 lightbulb icon, and a wide blue keycap button “Проверить”. Under the lightbulb key a permanent 13 pt grey caption “−1 звезда”.

Dark theme variant: page background #142033, sheets and tiles #1C2B42, answer keys and secondary keycaps #22344F with edge #0D1726 and text #F1F5FA, selected answer key face #213A5C with 2 pt outline #5B95DB, correct answer key #173B33 outlined #2BB57A, wrong answer key #3F2230 outlined #E25B60, main text #F1F5FA, secondary #A9B8CC, code board #0D1726, blue links and selected outlines #5B95DB; primary, success and danger buttons keep their light-theme face colors; wrong-answer panel #3F2230 with title #FF8A8E, correct-answer panel #173B33 with title #5FD39C; tab bar background #0D1726, selected tab #5B95DB, other tabs #A9B8CC.
```

## Спецификация

Выдержка из `design/SPEC.md`. Если выдержка и SPEC расходятся, верен SPEC.

### 5.3 Уровень

#### Общий каркас

```
y=47  ┌──────────────────────────────┐
      │ ✕  ▬▬▬▬▬▭▭▭          ♥ 4      │ шапка 56: выход 48, прогресс модуля, жизни
y=115 │ Что напечатает программа?     │ H3 условие
      │ ┌──────────────────────────┐ │ доска ≤ 55% высоты области под шапкой
      │ │ 1  x = 0                  │ │ номера строк #8796AB
      │ │ 2  while x < 3:           │ │
      │ │ 3      x += 1             │ │
      │ │ 4  print(x)               │ │
      │ └──────────────────────────┘ │
      │ ──── волосяная линия ────── │ появляется при прокрутке ответов
      │ ответы (прокрутка)           │ по механике
y=726 │ [лампа] [     Проверить     ] │ клавиша 56×56 + Primary
      └──────────────────────────────┘
```

Шапка:
- выход — крестик 26 `#5B6B7F` в зоне касания 48 (лист 5.14.1);
- прогресс модуля — сегменты высотой 8: пройденные `#157A52`, текущий `#2F6DB5`, остальные `#DCE3ED`;
- справа жизни: сердце и число;
- если взята подсказка, слева от жизней иконка лампы 18 `#5B6B7F` с подписью для диктора «Подсказка взята».

Клавиша подсказки:
- белая 56 × 56, лампа 24 `#2F6DB5` (жёлтый остаётся только за наградами);
- под клавишей постоянная подпись Caption 13 `#5B6B7F` «−1 звезда»; поэтому нижняя зона на 18 pt выше, чем у кнопки без подписи;
- подпись для диктора — «Подсказка: −1 звезда»;
- после нажатия текст подсказки появляется под ответами блоком: `#FFFFFF`, левая полоса 4 `#2F6DB5`, иконка лампы, Body; клавиша исчезает.

Кнопка «Проверить» неактивна, пока ответ не собран.

Состояния уровня:

| Состояние | Что видно |
|---|---|
| нет ответа | «Проверить» неактивна |
| ответ выбран | выбор отмечен синим, «Проверить» активна |
| не то | панель 5.3.12 перекрывает нижнюю часть |
| верно | панель 5.3.13 |
| ввод заблокирован | после ответа клавиши не нажимаются |

Ниже — механики в порядке частоты в контенте (всего 423 уровня). Механики `robot_puzzle` и `optimization` в контенте пока не используются, их макеты делаются вместе с N-7.

#### 5.3.1 Предскажи вывод и выбор ответа (`predict_output` 151, `multiple_choice` 16)

- Ответы короче 8 символов — сетка 2 × 2: клавиши 169 × 64, зазор 12. Длиннее — столбец клавиш 350 × 64 с зазором 12.
- Код в ответах набирается JetBrains Mono 18, текст — Onest 17/700.

Промпт: «[ПОЛНОЭКРАННЫЙ] Level screen. At y=47 a 56 pt header: grey close “✕” at left, a segmented progress bar of 8 rounded segments 8 pt tall (4 green #157A52, 1 blue, 3 light grey), red heart with “4” at right. At y=115 bold 20 pt prompt “Что напечатает программа?”. A dark code board with line numbers in #8796AB: “x = 0”, “while x < 3:”, “    x += 1”, “print(x)”. Below, a 2×2 grid of white keycap answer keys 169×64 with 12 pt gaps, monospace labels “2”, “3”, “4”, “0”; key “3” is selected with a 2 pt blue outline and face #E6EFFA. At y=726 a square white keycap 56×56 with a blue #2F6DB5 lightbulb icon, and a wide blue keycap button “Проверить”. Under the lightbulb key a permanent 13 pt grey caption “−1 звезда”.»

## Приёмка

- [ ] Тексты совпадают со спецификацией дословно.
- [ ] Цвета соответствуют ролям: жёлтый только у наград, оранжевый только у серии и времени.
- [ ] Не больше одной главной кнопки.
- [ ] Макет прошёл ревизию субагента-критика (виза в `design/README.md`).
