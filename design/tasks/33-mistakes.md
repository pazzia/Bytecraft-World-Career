# 33. Работа над ошибками

- Задача бэклога: X-5
- Этап: 4
- Спецификация: `design/SPEC.md`
- Куда класть результат: `design/renders/33-mistakes/`
- Статус: не начато

## Как отрисовать

1. Откройте новый чат в ChatGPT с генерацией изображений.
2. Скопируйте промпт ниже целиком, включая первую часть с цветами и шрифтами — без неё макет разойдётся с системой.
3. Сохраните результат как PNG в папку из шапки: `light.png`, для тёмной темы `dark.png`, для вариантов — `<вариант>.png`.
4. Если ChatGPT исказил текст или цвет, попросите исправить конкретную деталь («замени текст на кнопке на „Проверить“»), а не перегенерируйте с нуля.

## Промпты

### Макет

Префикс: ВКЛАДКИ.

```text
Mobile app UI mockup of one iPhone 14 screen, 390×844 pt, flat vector UI, no device frame, no photos, no gradients, no glassmorphism, no blurred shadows. Every pressable element is a mechanical keyboard keycap: a solid face and a solid 4 pt darker bottom edge, corner radius 14 (tiles 16). Fonts: Onest for interface text, JetBrains Mono for code. Page background #EEF2F7, surfaces #FFFFFF, main text #1B2838, secondary text #5B6B7F. Action blue #2F6DB5 with edge #1F4E86. Reward yellow #FFD43B used only for XP, stars and coins icons and numbers, never for buttons. Success green #157A52, error red #D23C42, streak and timer orange #FF5B1F. Code sits on a dark board #1B2838 with radius 22: plain code #E8EEF6, keywords #C792EA, builtins #82AAFF, strings #C3E88D, numbers #F78C6C, comments and line numbers #8796AB. All text in Russian exactly as quoted, sentence case, no emoji, no all caps. Status bar 47 pt at top. Bottom tab bar 68 pt plus 34 pt safe area, white, top hairline #D5DDE8, four tabs with rounded icons and labels: «Сегодня» (house), «Путь» (route), «Практика» (dumbbell), «Профиль» (person).

Screen “Работа над ошибками” with back arrow. Caption “Каждая тема — до 5 пройденных уровней. Жизни не тратятся.” List rows separated by hairlines: “Циклы” with a red circle badge “2”, “Срезы строк” with “1”, “Словари” with “1”, chevrons.
```

## Спецификация

Выдержка из `design/SPEC.md`. Если выдержка и SPEC расходятся, верен SPEC.

#### 5.6.1 Работа над ошибками (F-4, X-5)

- Список тем с ошибками: строка темы — Title, справа число ошибок в красном кружке 24.
- Нажатие открывает прогон из 5 уже пройденных уровней этой темы в режиме без жизней (П3); если пройденных меньше, прогон короче.
- Непройденный уровень с ошибкой показан в теме отдельной строкой «Пройти уровень» и ведёт на путь.
- После прогона — экран итога: «Циклы: ошибок стало 0» или «Осталось 1» (H2), полоса из 5 сегментов (верные Green, неверные Red), Primary «Следующая тема» или «К практике».

Промпт: «[ВКЛАДКИ] Screen “Работа над ошибками” with back arrow. Caption “Каждая тема — до 5 пройденных уровней. Жизни не тратятся.” List rows separated by hairlines: “Циклы” with a red circle badge “2”, “Срезы строк” with “1”, “Словари” with “1”, chevrons.»

## Приёмка

- [ ] Тексты совпадают со спецификацией дословно.
- [ ] Цвета соответствуют ролям: жёлтый только у наград, оранжевый только у серии и времени.
- [ ] Не больше одной главной кнопки.
- [ ] Макет прошёл ревизию субагента-критика (виза в `design/README.md`).
