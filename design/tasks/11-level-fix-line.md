# 11. Уровень: исправь строку

- Задача бэклога: X-13, X-14
- Этап: 1
- Спецификация: `design/SPEC.md`
- Куда класть результат: `design/renders/11-level-fix-line/`
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

Level screen, retype the broken line. Prompt “Исправьте строку с ошибкой”. Dark code board, line 3 “    if n % 2 = 0:” highlighted with translucent red and a small label “строка 3” in #FF8A8E at right. Below, grey label “Исправленная строка 3” and a one-line dark input board with monospace “if n % 2 == 0:” and a thin cursor. Caption “Отступ можно не набирать. Пробелы и вид кавычек не важны”. Blue “Проверить” button above the keyboard.
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

#### 5.3.9 Исправь строку (`fix_line` 18)

- Доска с кодом: неверная строка подсвечена `#D23C42` 25% и подписана справа Caption `#FF8A8E` «строка 3».
- Под доской Caption «Исправленная строка 3» и поле-доска на одну строку, предзаполненное текущим текстом строки.
- Под полем Caption «Отступ можно не набирать. Пробелы и вид кавычек не важны».

Промпт: «[ПОЛНОЭКРАННЫЙ] Level screen, retype the broken line. Prompt “Исправьте строку с ошибкой”. Dark code board, line 3 “    if n % 2 = 0:” highlighted with translucent red and a small label “строка 3” in #FF8A8E at right. Below, grey label “Исправленная строка 3” and a one-line dark input board with monospace “if n % 2 == 0:” and a thin cursor. Caption “Отступ можно не набирать. Пробелы и вид кавычек не важны”. Blue “Проверить” button above the keyboard.»

## Приёмка

- [ ] Тексты совпадают со спецификацией дословно.
- [ ] Цвета соответствуют ролям: жёлтый только у наград, оранжевый только у серии и времени.
- [ ] Не больше одной главной кнопки.
- [ ] Макет прошёл ревизию субагента-критика (виза в `design/README.md`).
