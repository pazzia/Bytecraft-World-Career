# 07. Уровень: найди пары

- Задача бэклога: X-13, X-14
- Этап: 1
- Спецификация: `design/SPEC.md`
- Куда класть результат: `design/renders/07-level-match/`
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

Level screen, match pairs. Prompt “Соедините код и результат”, caption “Нажмите слева, затем пару справа”. Two columns of keycaps 169×56 with 12 pt gap: left monospace “len("abc")”, “"ab" * 2”, “3 // 2”; right “1”, “3”, “abab”. Left “len("abc")” and right “3” are paired: both have a 2 pt blue outline and a small blue circle badge “1” in the corner. Left “"ab" * 2” is selected (light blue face). Blue “Проверить” button.
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

#### 5.3.5 Найди пары (`match_pairs` 36)

- Над колонками Caption «Нажмите слева, затем пару справа».
- Две колонки клавиш шириной 169 с зазором 12, высота 56.
- Выбранная левая — синяя по 4.4.
- Собранная пара: обе клавиши получают одинаковую метку-цифру 18 в кружке `#2F6DB5` и обводку `#2F6DB5`. Цвет пары не меняется до проверки, чтобы не путать с «верно».
- После проверки верные пары зелёные, неверные красные.

Промпт: «[ПОЛНОЭКРАННЫЙ] Level screen, match pairs. Prompt “Соедините код и результат”, caption “Нажмите слева, затем пару справа”. Two columns of keycaps 169×56 with 12 pt gap: left monospace “len("abc")”, “"ab" * 2”, “3 // 2”; right “1”, “3”, “abab”. Left “len("abc")” and right “3” are paired: both have a 2 pt blue outline and a small blue circle badge “1” in the corner. Left “"ab" * 2” is selected (light blue face). Blue “Проверить” button.»

## Приёмка

- [ ] Тексты совпадают со спецификацией дословно.
- [ ] Цвета соответствуют ролям: жёлтый только у наград, оранжевый только у серии и времени.
- [ ] Не больше одной главной кнопки.
- [ ] Макет прошёл ревизию субагента-критика (виза в `design/README.md`).
