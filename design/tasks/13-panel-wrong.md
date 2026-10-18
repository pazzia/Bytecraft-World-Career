# 13. Панель «Не то»

- Задача бэклога: X-13, X-14, X-12b
- Этап: 1
- Спецификация: `design/SPEC.md`
- Куда класть результат: `design/renders/13-panel-wrong/`
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

The level screen with a bottom panel #FBE3E4 sliding over the lower part, radius 28 on top, 20 pt padding. Inside: red circle with a white cross, title “Не то” 24 pt bold dark red #9E272C, at right caption “Осталось 4 жизни” in #9E272C; text “С вашим вариантом программа выдаст” and a small dark board showing “2”; 17 pt text “Подсказка: range не включает правую границу”; two buttons in a row: white keycap “Разбор” (40% width) and red keycap #D23C42 with edge #9E272C and white text “Ещё раз” (60%). The answer key “2” above has a red outline and face #FBE3E4.
```

### Макет в тёмной теме

```text
Mobile app UI mockup of one iPhone 14 screen, 390×844 pt, flat vector UI, no device frame, no photos, no gradients, no glassmorphism, no blurred shadows. Every pressable element is a mechanical keyboard keycap: a solid face and a solid 4 pt darker bottom edge, corner radius 14 (tiles 16). Fonts: Onest for interface text, JetBrains Mono for code. Page background #EEF2F7, surfaces #FFFFFF, main text #1B2838, secondary text #5B6B7F. Action blue #2F6DB5 with edge #1F4E86. Reward yellow #FFD43B used only for XP, stars and coins icons and numbers, never for buttons. Success green #157A52, error red #D23C42, streak and timer orange #FF5B1F. Code sits on a dark board #1B2838 with radius 22: plain code #E8EEF6, keywords #C792EA, builtins #82AAFF, strings #C3E88D, numbers #F78C6C, comments and line numbers #8796AB. All text in Russian exactly as quoted, sentence case, no emoji, no all caps. Status bar 47 pt at top. No tab bar. Home indicator area 34 pt at the bottom.

The level screen with a bottom panel #FBE3E4 sliding over the lower part, radius 28 on top, 20 pt padding. Inside: red circle with a white cross, title “Не то” 24 pt bold dark red #9E272C, at right caption “Осталось 4 жизни” in #9E272C; text “С вашим вариантом программа выдаст” and a small dark board showing “2”; 17 pt text “Подсказка: range не включает правую границу”; two buttons in a row: white keycap “Разбор” (40% width) and red keycap #D23C42 with edge #9E272C and white text “Ещё раз” (60%). The answer key “2” above has a red outline and face #FBE3E4.

Dark theme variant: page background #142033, sheets and tiles #1C2B42, answer keys and secondary keycaps #22344F with edge #0D1726 and text #F1F5FA, selected answer key face #213A5C with 2 pt outline #5B95DB, correct answer key #173B33 outlined #2BB57A, wrong answer key #3F2230 outlined #E25B60, main text #F1F5FA, secondary #A9B8CC, code board #0D1726, blue links and selected outlines #5B95DB; primary, success and danger buttons keep their light-theme face colors; wrong-answer panel #3F2230 with title #FF8A8E, correct-answer panel #173B33 with title #5FD39C; tab bar background #0D1726, selected tab #5B95DB, other tabs #A9B8CC.
```

## Спецификация

Выдержка из `design/SPEC.md`. Если выдержка и SPEC расходятся, верен SPEC.

#### 5.3.12 Панель «Не то»

Фон `#FBE3E4`, радиус 28 сверху, поля 20. Сверху вниз:
1. Красный круг 28 с белым крестиком и заголовок «Не то» (H2, `#9E272C`). Справа Caption `#9E272C` «Осталось 4 жизни». В забеге — ночная версия, см. 5.7.5.
2. Если программа запускалась: Caption «С вашим вариантом программа выдаст» и мини-доска с выводом.
3. «Подсказка: …» (Body L, Ink).
4. Строка «Тема „Циклы“ добавлена в работу над ошибками» (Caption `#5B6B7F`) — после выхода F-4, при первой ошибке на теме.
5. Кнопки в ряд: «Разбор» (Secondary, 40%) и «Ещё раз» (Danger, 60%).

Выбранный ответ выше панели получает красную обводку. Хаптик — сильный.

Промпт: «[ПОЛНОЭКРАННЫЙ] The level screen with a bottom panel #FBE3E4 sliding over the lower part, radius 28 on top, 20 pt padding. Inside: red circle with a white cross, title “Не то” 24 pt bold dark red #9E272C, at right caption “Осталось 4 жизни” in #9E272C; text “С вашим вариантом программа выдаст” and a small dark board showing “2”; 17 pt text “Подсказка: range не включает правую границу”; two buttons in a row: white keycap “Разбор” (40% width) and red keycap #D23C42 with edge #9E272C and white text “Ещё раз” (60%). The answer key “2” above has a red outline and face #FBE3E4.»

## Приёмка

- [ ] Тексты совпадают со спецификацией дословно.
- [ ] Цвета соответствуют ролям: жёлтый только у наград, оранжевый только у серии и времени.
- [ ] Не больше одной главной кнопки.
- [ ] Макет прошёл ревизию субагента-критика (виза в `design/README.md`).
