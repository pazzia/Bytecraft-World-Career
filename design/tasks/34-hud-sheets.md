# 34. Листы HUD: серия, XP, жизни

- Задача бэклога: X-15
- Этап: 4
- Спецификация: `design/SPEC.md`
- Куда класть результат: `design/renders/34-hud-sheets/`
- Статус: не начато

## Как отрисовать

1. Откройте новый чат в ChatGPT с генерацией изображений.
2. Скопируйте промпт ниже целиком, включая первую часть с цветами и шрифтами — без неё макет разойдётся с системой.
3. Сохраните результат как PNG в папку из шапки: `light.png`, для тёмной темы `dark.png`, для вариантов — `<вариант>.png`.
4. Если ChatGPT исказил текст или цвет, попросите исправить конкретную деталь («замени текст на кнопке на „Проверить“»), а не перегенерируйте с нуля.

## Промпты

### Макет — 5.14.3, серия

Префикс: ПОЛНОЭКРАННЫЙ.

```text
Mobile app UI mockup of one iPhone 14 screen, 390×844 pt, flat vector UI, no device frame, no photos, no gradients, no glassmorphism, no blurred shadows. Every pressable element is a mechanical keyboard keycap: a solid face and a solid 4 pt darker bottom edge, corner radius 14 (tiles 16). Fonts: Onest for interface text, JetBrains Mono for code. Page background #EEF2F7, surfaces #FFFFFF, main text #1B2838, secondary text #5B6B7F. Action blue #2F6DB5 with edge #1F4E86. Reward yellow #FFD43B used only for XP, stars and coins icons and numbers, never for buttons. Success green #157A52, error red #D23C42, streak and timer orange #FF5B1F. Code sits on a dark board #1B2838 with radius 22: plain code #E8EEF6, keywords #C792EA, builtins #82AAFF, strings #C3E88D, numbers #F78C6C, comments and line numbers #8796AB. All text in Russian exactly as quoted, sentence case, no emoji, no all caps. Status bar 47 pt at top. No tab bar. Home indicator area 34 pt at the bottom.

Bottom sheet over the “Сегодня” screen: orange flame icon outlined #B83A0B, title “Серия: 12 дней”, a row of 7 small circles for the week (6 orange, 1 grey #DCE3ED) with day labels “пн вт ср чт пт сб вс”, text “Пройдите хотя бы один уровень сегодня, чтобы серия не прервалась. Заморозка сохранит серию в день пропуска”, blue keycap “Начать уровень”, white keycap “Купить заморозку — 50”.
```

## Спецификация

Выдержка из `design/SPEC.md`. Если выдержка и SPEC расходятся, верен SPEC.

**5.14.3 Листы HUD.**

| Бейдж | Заголовок | Текст | Кнопки |
|---|---|---|---|
| Серия | «Серия: 12 дней» | «Пройдите хотя бы один уровень сегодня, чтобы серия не прервалась. Заморозка сохранит серию в день пропуска». Плюс 7 кружков последней недели: пройден — Ember, пропуск — `#DCE3ED` | Primary «Начать уровень», Secondary «Купить заморозку — 50» |
| XP | «Уровень аккаунта 7 · 2 440 XP» | «340 из 700 XP до уровня 8. XP дают уровни, Уровень дня и забеги» | Primary «Начать уровень» |
| Жизни | «4 из 5 жизней» | «Ошибка стоит одну жизнь. Новая — каждые 30 минут, следующая через 12 минут. Повторение жизни не тратит» | Primary «Начать уровень», Secondary «Пополнить за 30 монет» |

## Приёмка

- [ ] Тексты совпадают со спецификацией дословно.
- [ ] Цвета соответствуют ролям: жёлтый только у наград, оранжевый только у серии и времени.
- [ ] Не больше одной главной кнопки.
- [ ] Макет прошёл ревизию субагента-критика (виза в `design/README.md`).
