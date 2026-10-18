# 15. Разбор (лист)

- Задача бэклога: X-14
- Этап: 1
- Спецификация: `design/SPEC.md`
- Куда класть результат: `design/renders/15-review-sheet/`
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

A bottom sheet covering 90% of a dimmed level screen, radius 28, grab handle. Title “Разбор”. White keycap button “Сохранить тему”. Section “Что не так” with caption “С вашим вариантом программа выдаст” and a small board “2”. Section “Почему так” with two lines of text. Section “Решение” with a disabled grey keycap “Показать решение” and caption “Откроется после верного ответа или после 3 ошибок”. Section “Тема” with a white tile “Цикл while” and a blue link “Открыть тему”.
```

## Спецификация

Выдержка из `design/SPEC.md`. Если выдержка и SPEC расходятся, верен SPEC.

#### 5.3.14 Разбор (лист)

Лист на 90% высоты. Сверху вниз:
- H2 «Разбор»;
- Secondary «Сохранить тему» (или «Убрать тему», если уже сохранена);
- «Что не так» (H3) и мини-доска «С вашим вариантом программа выдаст» — только после ошибки;
- «Почему так» (H3) — объяснение;
- «Решение» (H3): до верного ответа или трёх ошибок — Secondary «Показать решение» неактивна с подписью Caption «Откроется после верного ответа или после 3 ошибок»; после — доска с решением;
- «Тема» (H3) — карточка темы со ссылкой «Открыть тему».

Промпт: «[ПОЛНОЭКРАННЫЙ] A bottom sheet covering 90% of a dimmed level screen, radius 28, grab handle. Title “Разбор”. White keycap button “Сохранить тему”. Section “Что не так” with caption “С вашим вариантом программа выдаст” and a small board “2”. Section “Почему так” with two lines of text. Section “Решение” with a disabled grey keycap “Показать решение” and caption “Откроется после верного ответа или после 3 ошибок”. Section “Тема” with a white tile “Цикл while” and a blue link “Открыть тему”.»

## Приёмка

- [ ] Тексты совпадают со спецификацией дословно.
- [ ] Цвета соответствуют ролям: жёлтый только у наград, оранжевый только у серии и времени.
- [ ] Не больше одной главной кнопки.
- [ ] Макет прошёл ревизию субагента-критика (виза в `design/README.md`).
