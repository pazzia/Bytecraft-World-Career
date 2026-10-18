# 25. Повторение

- Задача бэклога: X-11
- Этап: 2
- Спецификация: `design/SPEC.md`
- Куда класть результат: `design/renders/25-review-list/`
- Статус: не начато

## Как отрисовать

1. Откройте новый чат в ChatGPT с генерацией изображений.
2. Скопируйте промпт ниже целиком, включая первую часть с цветами и шрифтами — без неё макет разойдётся с системой.
3. Сохраните результат как PNG в папку из шапки: `light.png`, для тёмной темы `dark.png`, для вариантов — `<вариант>.png`.
4. Если ChatGPT исказил текст или цвет, попросите исправить конкретную деталь («замени текст на кнопке на „Проверить“»), а не перегенерируйте с нуля.

## Промпты

### Макет — 5.8.1

Префикс: ВКЛАДКИ.

```text
Mobile app UI mockup of one iPhone 14 screen, 390×844 pt, flat vector UI, no device frame, no photos, no gradients, no glassmorphism, no blurred shadows. Every pressable element is a mechanical keyboard keycap: a solid face and a solid 4 pt darker bottom edge, corner radius 14 (tiles 16). Fonts: Onest for interface text, JetBrains Mono for code. Page background #EEF2F7, surfaces #FFFFFF, main text #1B2838, secondary text #5B6B7F. Action blue #2F6DB5 with edge #1F4E86. Reward yellow #FFD43B used only for XP, stars and coins icons and numbers, never for buttons. Success green #157A52, error red #D23C42, streak and timer orange #FF5B1F. Code sits on a dark board #1B2838 with radius 22: plain code #E8EEF6, keywords #C792EA, builtins #82AAFF, strings #C3E88D, numbers #F78C6C, comments and line numbers #8796AB. All text in Russian exactly as quoted, sentence case, no emoji, no all caps. Status bar 47 pt at top. Bottom tab bar 68 pt plus 34 pt safe area, white, top hairline #D5DDE8, four tabs with rounded icons and labels: «Сегодня» (house), «Путь» (route), «Практика» (dumbbell), «Профиль» (person).

Screen “Повторение” with back arrow. A 44 pt segmented control with three options “К повторению · 3” (selected, blue), “Мои темы”, “Справочник”. List rows separated by hairlines #D5DDE8: title “Цикл while”, caption “Циклы”, at right a 5-step meter of small vertical bars (2 of 5 blue, rest #DCE3ED); “Срезы строк” / “Строки” (4 of 5); “Словари” / “Словари” (1 of 5). Tab bar, “Практика” selected, badge “3”.
```

## Спецификация

Выдержка из `design/SPEC.md`. Если выдержка и SPEC расходятся, верен SPEC.

### 5.8 Повторение и тема

**5.8.1 Повторение.**
- Шапка: стрелка назад, H1 «Повторение».
- Сегмент-переключатель 44: «К повторению · 3», «Мои темы», «Справочник».
- Строка темы: Title и Caption с названием модуля; справа шкала из 5 делений 6 × 16 (ступени Лейтнера 1 / 3 / 7 / 16 / 35 дней), заполненные `#2F6DB5`, пустые `#DCE3ED`.
- Пустой «К повторению»: Body «Сегодня всё повторено. Следующие темы — завтра» и Quiet «Открыть мои темы».

## Приёмка

- [ ] Тексты совпадают со спецификацией дословно.
- [ ] Цвета соответствуют ролям: жёлтый только у наград, оранжевый только у серии и времени.
- [ ] Не больше одной главной кнопки.
- [ ] Макет прошёл ревизию субагента-критика (виза в `design/README.md`).
