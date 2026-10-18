# 30. «Не то» в забеге

- Задача бэклога: X-12b
- Этап: 3а
- Спецификация: `design/SPEC.md`
- Куда класть результат: `design/renders/30-timed-wrong/`
- Статус: не начато

## Как отрисовать

1. Откройте новый чат в ChatGPT с генерацией изображений.
2. Скопируйте промпт ниже целиком, включая первую часть с цветами и шрифтами — без неё макет разойдётся с системой.
3. Сохраните результат как PNG в папку из шапки: `light.png`, для тёмной темы `dark.png`, для вариантов — `<вариант>.png`.
4. Если ChatGPT исказил текст или цвет, попросите исправить конкретную деталь («замени текст на кнопке на „Проверить“»), а не перегенерируйте с нуля.

## Промпты

### Макет — 5.7.5

Префикс: НОЧНОЙ.

```text
Mobile app UI mockup of one iPhone 14 screen, 390×844 pt, flat vector UI, no device frame, no gradients, no blurred shadows, no tab bar. Night theme: background #142033, keycaps #22344F with darker bottom edge #0D1726 (lifted keycap #2F4566), code board #0D1726, main text #F1F5FA, secondary text #A9B8CC. Primary buttons are orange #FF5B1F keycaps with edge #B83A0B and dark text #1B0A02. Timer and record numbers in #FF8A57. Answer keys and secondary keycaps #22344F with text #F1F5FA; selected answer key face #213A5C with 2 pt outline #5B95DB. Wrong-answer panel background #3F2230 with title and captions #FF8A8E; correct-answer panel background #173B33 with title #5FD39C. Fonts: Onest for UI, JetBrains Mono for code with the same syntax colors (keywords #C792EA, builtins #82AAFF, strings #C3E88D, numbers #F78C6C, comments #8796AB). Russian text exactly as quoted, sentence case, no emoji, no all caps.

Night level screen with the orange fuse at the top showing “7:27”. A bottom panel #3F2230 with radius 28: circle with a cross in #FF8A8E, title “Не то” in #FF8A8E, right caption “−15 секунд” in #FF8A57, text “Подсказка: range не включает правую границу” in #F1F5FA, buttons: navy keycap #22344F “Разбор” and red keycap #D23C42 with white text “Ещё раз”. The chosen answer key is outlined #E25B60 on face #3F2230. The orange “Проверить” button is hidden under the panel.
```

## Спецификация

Выдержка из `design/SPEC.md`. Если выдержка и SPEC расходятся, верен SPEC.

**5.7.5 «Не то» в забеге.** Фон панели `#3F2230`, крестик в круге `#FF8A8E`, заголовок «Не то» `#FF8A8E`, справа Caption `#FF8A57` «−15 секунд». Жизней нет. Подсказка Body L `#F1F5FA`. Кнопки: «Разбор» (Secondary `#22344F`) и «Ещё раз» (Danger). Фитиль сверху сдвигается на 15 секунд с короткой вспышкой `#FF8A57` (без неё при «уменьшить движение»).

## Приёмка

- [ ] Тексты совпадают со спецификацией дословно.
- [ ] Цвета соответствуют ролям: жёлтый только у наград, оранжевый только у серии и времени.
- [ ] Не больше одной главной кнопки.
- [ ] Макет прошёл ревизию субагента-критика (виза в `design/README.md`).
