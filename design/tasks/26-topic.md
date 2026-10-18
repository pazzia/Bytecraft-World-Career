# 26. Тема

- Задача бэклога: X-11
- Этап: 2
- Спецификация: `design/SPEC.md`
- Куда класть результат: `design/renders/26-topic/`
- Статус: не начато

## Как отрисовать

1. Откройте новый чат в ChatGPT с генерацией изображений.
2. Скопируйте промпт ниже целиком, включая первую часть с цветами и шрифтами — без неё макет разойдётся с системой.
3. Сохраните результат как PNG в папку из шапки: `light.png`, для тёмной темы `dark.png`, для вариантов — `<вариант>.png`.
4. Если ChatGPT исказил текст или цвет, попросите исправить конкретную деталь («замени текст на кнопке на „Проверить“»), а не перегенерируйте с нуля.

## Промпты

### Макет — 5.8.2

Префикс: ПОЛНОЭКРАННЫЙ.

```text
Mobile app UI mockup of one iPhone 14 screen, 390×844 pt, flat vector UI, no device frame, no photos, no gradients, no glassmorphism, no blurred shadows. Every pressable element is a mechanical keyboard keycap: a solid face and a solid 4 pt darker bottom edge, corner radius 14 (tiles 16). Fonts: Onest for interface text, JetBrains Mono for code. Page background #EEF2F7, surfaces #FFFFFF, main text #1B2838, secondary text #5B6B7F. Action blue #2F6DB5 with edge #1F4E86. Reward yellow #FFD43B used only for XP, stars and coins icons and numbers, never for buttons. Success green #157A52, error red #D23C42, streak and timer orange #FF5B1F. Code sits on a dark board #1B2838 with radius 22: plain code #E8EEF6, keywords #C792EA, builtins #82AAFF, strings #C3E88D, numbers #F78C6C, comments and line numbers #8796AB. All text in Russian exactly as quoted, sentence case, no emoji, no all caps. Status bar 47 pt at top. No tab bar. Home indicator area 34 pt at the bottom.

Topic screen with back arrow. Title “Цикл while”, body text two paragraphs and a small code board “while x < 3:”, “    x += 1”. A blue underlined link “Цикл for”. Bottom pinned panel white with top hairline: blue keycap “Повторить: решить уровень”.
```

## Спецификация

Выдержка из `design/SPEC.md`. Если выдержка и SPEC расходятся, верен SPEC.

**5.8.2 Тема.**
- H1 с названием темы, текст Body с примерами на мини-досках, ссылки на связанные темы (Blue, подчёркивание 1 px).
- Нижняя закреплённая панель:

| Состояние темы | Панель |
|---|---|
| к повторению, есть уровень | Primary «Повторить: решить уровень» — уровень в режиме повторения (П3); результат двигает тему по ступеням |
| к повторению, уровня нет | Caption «Помните тему?», Secondary «Повторить ещё» и Primary «Помню» |
| не к повторению | Caption «Следующее повторение через 7 дней», Quiet «Убрать тему» |
| тема не сохранена | Secondary «Сохранить тему» |

## Приёмка

- [ ] Тексты совпадают со спецификацией дословно.
- [ ] Цвета соответствуют ролям: жёлтый только у наград, оранжевый только у серии и времени.
- [ ] Не больше одной главной кнопки.
- [ ] Макет прошёл ревизию субагента-критика (виза в `design/README.md`).
