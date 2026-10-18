# 17. Жизни закончились

- Задача бэклога: X-13, X-14
- Этап: 1
- Спецификация: `design/SPEC.md`
- Куда класть результат: `design/renders/17-out-of-lives/`
- Статус: не начато

## Как отрисовать

1. Откройте новый чат в ChatGPT с генерацией изображений.
2. Скопируйте промпт ниже целиком, включая первую часть с цветами и шрифтами — без неё макет разойдётся с системой.
3. Сохраните результат как PNG в папку из шапки: `light.png`, для тёмной темы `dark.png`, для вариантов — `<вариант>.png`.
4. Если ChatGPT исказил текст или цвет, попросите исправить конкретную деталь («замени текст на кнопке на „Проверить“»), а не перегенерируйте с нуля.

## Промпты

### Макет — вариант до выхода F-4

Префикс: ПОЛНОЭКРАННЫЙ.

```text
Mobile app UI mockup of one iPhone 14 screen, 390×844 pt, flat vector UI, no device frame, no photos, no gradients, no glassmorphism, no blurred shadows. Every pressable element is a mechanical keyboard keycap: a solid face and a solid 4 pt darker bottom edge, corner radius 14 (tiles 16). Fonts: Onest for interface text, JetBrains Mono for code. Page background #EEF2F7, surfaces #FFFFFF, main text #1B2838, secondary text #5B6B7F. Action blue #2F6DB5 with edge #1F4E86. Reward yellow #FFD43B used only for XP, stars and coins icons and numbers, never for buttons. Success green #157A52, error red #D23C42, streak and timer orange #FF5B1F. Code sits on a dark board #1B2838 with radius 22: plain code #E8EEF6, keywords #C792EA, builtins #82AAFF, strings #C3E88D, numbers #F78C6C, comments and line numbers #8796AB. All text in Russian exactly as quoted, sentence case, no emoji, no all caps. Status bar 47 pt at top. No tab bar. Home indicator area 34 pt at the bottom.

Bottom sheet over a dimmed level screen, radius 28, handle. Red broken heart icon 56 pt, title “Жизни закончились”, text “Новая жизнь через 24 минуты. Повторение жизни не тратит”. Stacked buttons: blue keycap “Повторить темы”; white keycap with a small yellow coin icon “Пополнить за 30 монет”; white keycap “Посмотреть рекламу: +1 жизнь”; blue text links “Без лимита жизней с Premium” and “Выйти из уровня”.
```

## Спецификация

Выдержка из `design/SPEC.md`. Если выдержка и SPEC расходятся, верен SPEC.

### 5.5 Жизни закончились (лист)

Открывается поверх уровня, чтобы было видно, где игрок остановился:
- иконка разбитого сердца Red 56;
- H2 «Жизни закончились»;
- Body «Новая жизнь через 24 минуты. Повторение и работа над ошибками жизни не тратят» (правило П3). До выхода F-4: «Новая жизнь через 24 минуты. Повторение жизни не тратит».

Кнопки столбцом:
1. «Повторить темы» — Primary. Если тем к повторению нет: «Работа над ошибками» (только после выхода F-4). Если нет и ошибок — Primary «Пополнить за 30 монет». Если и монет не хватает — Primary «Выйти из уровня», а время до новой жизни остаётся в тексте.
2. «Пополнить за 30 монет» — Secondary с монетой; при нехватке неактивна, под ней Caption «У вас 12 монет».
3. «Посмотреть рекламу: +1 жизнь» — Secondary, только при флаге ads (S-9).
4. «Без лимита жизней с Premium» — Quiet, только если Premium продаётся (S-4).
5. «Выйти из уровня» — Quiet.

Жёлтых кнопок нет.

Промпт (вариант до выхода F-4): «[ПОЛНОЭКРАННЫЙ] Bottom sheet over a dimmed level screen, radius 28, handle. Red broken heart icon 56 pt, title “Жизни закончились”, text “Новая жизнь через 24 минуты. Повторение жизни не тратит”. Stacked buttons: blue keycap “Повторить темы”; white keycap with a small yellow coin icon “Пополнить за 30 монет”; white keycap “Посмотреть рекламу: +1 жизнь”; blue text links “Без лимита жизней с Premium” and “Выйти из уровня”.»

## Приёмка

- [ ] Тексты совпадают со спецификацией дословно.
- [ ] Цвета соответствуют ролям: жёлтый только у наград, оранжевый только у серии и времени.
- [ ] Не больше одной главной кнопки.
- [ ] Макет прошёл ревизию субагента-критика (виза в `design/README.md`).
