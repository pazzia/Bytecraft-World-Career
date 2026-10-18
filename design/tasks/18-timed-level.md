# 18. Уровень в забеге (один таймер)

- Задача бэклога: X-12a
- Этап: 1
- Спецификация: `design/SPEC.md`
- Куда класть результат: `design/renders/18-timed-level/`
- Статус: не начато

## Как отрисовать

1. Откройте новый чат в ChatGPT с генерацией изображений.
2. Скопируйте промпт ниже целиком, включая первую часть с цветами и шрифтами — без неё макет разойдётся с системой.
3. Сохраните результат как PNG в папку из шапки: `light.png`, для тёмной темы `dark.png`, для вариантов — `<вариант>.png`.
4. Если ChatGPT исказил текст или цвет, попросите исправить конкретную деталь («замени текст на кнопке на „Проверить“»), а не перегенерируйте с нуля.

## Промпты

### Макет — 5.7.3

Префикс: НОЧНОЙ.

```text
Mobile app UI mockup of one iPhone 14 screen, 390×844 pt, flat vector UI, no device frame, no gradients, no blurred shadows, no tab bar. Night theme: background #142033, keycaps #22344F with darker bottom edge #0D1726 (lifted keycap #2F4566), code board #0D1726, main text #F1F5FA, secondary text #A9B8CC. Primary buttons are orange #FF5B1F keycaps with edge #B83A0B and dark text #1B0A02. Timer and record numbers in #FF8A57. Answer keys and secondary keycaps #22344F with text #F1F5FA; selected answer key face #213A5C with 2 pt outline #5B95DB. Wrong-answer panel background #3F2230 with title and captions #FF8A8E; correct-answer panel background #173B33 with title #5FD39C. Fonts: Onest for UI, JetBrains Mono for code with the same syntax colors (keywords #C792EA, builtins #82AAFF, strings #C3E88D, numbers #F78C6C, comments #8796AB). Russian text exactly as quoted, sentence case, no emoji, no all caps.

Level screen. A 6 pt orange #FF5B1F fuse bar across the very top at 70% with “7:42” in #FF8A57 tabular digits at its right end. Header: close icon, progress segments; no hearts. White 20 pt prompt “Что напечатает программа?”, code board #0D1726, answer keycaps #22344F with white monospace “2”, “3”, “4”, “0”, key “3” outlined #5B95DB. Orange keycap “Проверить” with dark text.
```

## Спецификация

Выдержка из `design/SPEC.md`. Если выдержка и SPEC расходятся, верен SPEC.

### 5.7 На время

Все экраны — [НОЧНОЙ]. Открываются поверх оболочки, таб-бара нет.

**5.7.3 Уровень в забеге.** Как 5.3, но:
- над шапкой фитиль 6 во всю ширину `#FF5B1F`, у правого края цифры «7:42» Caption `#FF8A57` табличные;
- `CountdownBadge` в шапке не показывается (M4);
- жизней в шапке нет, клавиши подсказки нет (П2);
- последние 60 секунд фитиль и цифры пульсируют раз в секунду (без пульса при «уменьшить движение»).

## Приёмка

- [ ] Тексты совпадают со спецификацией дословно.
- [ ] Цвета соответствуют ролям: жёлтый только у наград, оранжевый только у серии и времени.
- [ ] Не больше одной главной кнопки.
- [ ] Макет прошёл ревизию субагента-критика (виза в `design/README.md`).
