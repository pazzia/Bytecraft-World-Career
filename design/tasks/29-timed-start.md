# 29. Старт забега (лист)

- Задача бэклога: X-12b
- Этап: 3а
- Спецификация: `design/SPEC.md`
- Куда класть результат: `design/renders/29-timed-start/`
- Статус: не начато

## Как отрисовать

1. Откройте новый чат в ChatGPT с генерацией изображений.
2. Скопируйте промпт ниже целиком, включая первую часть с цветами и шрифтами — без неё макет разойдётся с системой.
3. Сохраните результат как PNG в папку из шапки: `light.png`, для тёмной темы `dark.png`, для вариантов — `<вариант>.png`.
4. Если ChatGPT исказил текст или цвет, попросите исправить конкретную деталь («замени текст на кнопке на „Проверить“»), а не перегенерируйте с нуля.

## Промпты

### Макет — 5.7.2

Префикс: НОЧНОЙ.

```text
Mobile app UI mockup of one iPhone 14 screen, 390×844 pt, flat vector UI, no device frame, no gradients, no blurred shadows, no tab bar. Night theme: background #142033, keycaps #22344F with darker bottom edge #0D1726 (lifted keycap #2F4566), code board #0D1726, main text #F1F5FA, secondary text #A9B8CC. Primary buttons are orange #FF5B1F keycaps with edge #B83A0B and dark text #1B0A02. Timer and record numbers in #FF8A57. Answer keys and secondary keycaps #22344F with text #F1F5FA; selected answer key face #213A5C with 2 pt outline #5B95DB. Wrong-answer panel background #3F2230 with title and captions #FF8A8E; correct-answer panel background #173B33 with title #5FD39C. Fonts: Onest for UI, JetBrains Mono for code with the same syntax colors (keywords #C792EA, builtins #82AAFF, strings #C3E88D, numbers #F78C6C, comments #8796AB). Russian text exactly as quoted, sentence case, no emoji, no all caps.

Bottom sheet #1C2B42 radius 28 over the dimmed runs list. Title “Циклы”, text “10 минут · 8 уровней. Время пойдёт после нажатия „Старт“. Таймер не останавливается, даже если выйти”. Orange keycap button “Старт” with dark text, link “Не сейчас” in #5B95DB.
```

## Спецификация

Выдержка из `design/SPEC.md`. Если выдержка и SPEC расходятся, верен SPEC.

**5.7.2 Старт забега (лист).**
- H2 «Циклы».
- Body «10 минут · 8 уровней. Время пойдёт после нажатия „Старт“. Таймер не останавливается, даже если выйти».
- Primary «Старт», Quiet «Не сейчас».
- При активном забеге другого модуля сверху Caption `#FF8A57` «Текущий забег „Строки“ будет прерван».

## Приёмка

- [ ] Тексты совпадают со спецификацией дословно.
- [ ] Цвета соответствуют ролям: жёлтый только у наград, оранжевый только у серии и времени.
- [ ] Не больше одной главной кнопки.
- [ ] Макет прошёл ревизию субагента-критика (виза в `design/README.md`).
