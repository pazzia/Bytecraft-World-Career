# 35. Магазин

- Задача бэклога: S-4
- Этап: 4
- Спецификация: `design/SPEC.md`
- Куда класть результат: `design/renders/35-shop/`
- Статус: не начато

## Как отрисовать

1. Откройте новый чат в ChatGPT с генерацией изображений.
2. Скопируйте промпт ниже целиком, включая первую часть с цветами и шрифтами — без неё макет разойдётся с системой.
3. Сохраните результат как PNG в папку из шапки: `light.png`, для тёмной темы `dark.png`, для вариантов — `<вариант>.png`.
4. Если ChatGPT исказил текст или цвет, попросите исправить конкретную деталь («замени текст на кнопке на „Проверить“»), а не перегенерируйте с нуля.

## Промпты

### Макет — магазин

Префикс: ВКЛАДКИ.

```text
Mobile app UI mockup of one iPhone 14 screen, 390×844 pt, flat vector UI, no device frame, no photos, no gradients, no glassmorphism, no blurred shadows. Every pressable element is a mechanical keyboard keycap: a solid face and a solid 4 pt darker bottom edge, corner radius 14 (tiles 16). Fonts: Onest for interface text, JetBrains Mono for code. Page background #EEF2F7, surfaces #FFFFFF, main text #1B2838, secondary text #5B6B7F. Action blue #2F6DB5 with edge #1F4E86. Reward yellow #FFD43B used only for XP, stars and coins icons and numbers, never for buttons. Success green #157A52, error red #D23C42, streak and timer orange #FF5B1F. Code sits on a dark board #1B2838 with radius 22: plain code #E8EEF6, keywords #C792EA, builtins #82AAFF, strings #C3E88D, numbers #F78C6C, comments and line numbers #8796AB. All text in Russian exactly as quoted, sentence case, no emoji, no all caps. Status bar 47 pt at top. Bottom tab bar 68 pt plus 34 pt safe area, white, top hairline #D5DDE8, four tabs with rounded icons and labels: «Сегодня» (house), «Путь» (route), «Практика» (dumbbell), «Профиль» (person).

Screen “Магазин” with back arrow, balance at top right: yellow coin outlined #9A7400 and “42”. Two white keycap rows 350×88: snowflake icon blue, title “Заморозка серии”, caption “Сохраняет серию на день пропуска · у вас 1 из 2”, small white price keycap with coin and “50”; red heart icon, “Пополнить жизни”, caption “Все 5 жизней сразу”, price keycap “30”.
```

## Спецификация

Выдержка из `design/SPEC.md`. Если выдержка и SPEC расходятся, верен SPEC.

### 5.12 Магазин и Premium

**Магазин.**
- H1 «Магазин», справа баланс: монета и «42».
- Клавиши-товары 350 × 88: «Заморозка серии» / «Сохраняет серию на день пропуска · у вас 1 из 2» / цена-клавиша «50» с монетой; «Пополнить жизни» / «Все 5 жизней сразу» / «30».
- При нехватке цена неактивна, Caption «Не хватает 8 монет».
- После покупки на клавише 2 секунды Caption Green «Куплено». Снэкбара нет.

**Premium** (только после S-4):
- H1 «Premium»;
- список реальных выгод с галочками: «Без лимита жизней», «Без рекламы», «Поддержка проекта»;
- две клавиши-тарифа 350 × 72: «Год — 2 990 ₽» с обводкой Blue и Caption «Выгоднее на N%», где N считается из цен стора; «Месяц — 399 ₽». Цены — заглушки до S-1;
- Primary «Оформить», Quiet «Восстановить покупки»;
- строка о демо-платежах — только в демо-сборке.

## Приёмка

- [ ] Тексты совпадают со спецификацией дословно.
- [ ] Цвета соответствуют ролям: жёлтый только у наград, оранжевый только у серии и времени.
- [ ] Не больше одной главной кнопки.
- [ ] Макет прошёл ревизию субагента-критика (виза в `design/README.md`).
