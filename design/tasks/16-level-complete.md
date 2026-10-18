# 16. Уровень пройден

- Задача бэклога: X-13, X-14
- Этап: 1
- Спецификация: `design/SPEC.md`
- Куда класть результат: `design/renders/16-level-complete/`
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

Level complete screen. Top 45% is a dark board #1B2838 edge to edge with bottom corners radius 36: three large yellow stars 48 pt in a row, white bold 34 pt title “С первой попытки”, then a row of three stats: yellow bolt “+15 XP”, yellow coin “+1 монета”, orange flame “12 дней”. Below, on #EEF2F7: event rows with icons — orange flame “Серия продлена: 12 дней”, yellow trophy “Новое достижение: Десятка”; title “Прогресс курса” with “49 из 423” and a thin progress bar (blue fill on #DCE3ED). Bottom: full-width blue keycap “Следующий уровень” and a blue text link “К пути”.
```

## Спецификация

Выдержка из `design/SPEC.md`. Если выдержка и SPEC расходятся, верен SPEC.

### 5.4 Уровень пройден

Задача: показать, что изменилось, и вести дальше. Награда уже начислена в момент верного ответа, поэтому экран только показывает её.

```
┌──────────────────────────────┐
│ доска во всю ширину, низ R36  │ #1B2838, высота ~45%
│       ★   ★   ★               │ звёзды 48: Yellow / пустые #6B7F9E
│    С первой попытки           │ Display, белый
│ [молния]+15 XP [монета]+1 монета [огонь]12 дней │
│──────────────────────────────│
│ [огонь] Серия продлена: 12 дней  │ строки событий
│ [кубок] Новое достижение: Десятка │
│ Прогресс курса      49 из 423 │ Title + полоса 8
│ [   Следующий уровень    ]    │ Primary
│            К пути              │ Quiet
└──────────────────────────────┘
```

Строки событий — только реальные: серия продлена (огонь Ember), Уровень дня выполнен (календарь Blue), новый уровень аккаунта (щит Yellow, «Уровень аккаунта 8»), новое достижение (кубок Yellow).

Варианты заголовка — по П1.

Повторное прохождение:
- вместо трёх ячеек одна строка Caption `#AFC0D6` «Повтор: 20% XP, без монет»;
- число XP показывается по факту.

Последний уровень модуля:
- заголовок «Модуль пройден!»;
- над звёздами иконка жука, если модуль кончился боссом;
- Primary «Следующий модуль».

Нет следующего уровня (курс окончен): Primary «К пути», Quiet не показывается.

Забег (ночная палитра): звёзд нет; вместо них строки «Время 6:42 · рекорд 6:10» и «Бонус за скорость +40 XP», Primary «Следующий уровень забега».

Анимация: звёзды появляются по одной через 150 мс, при «уменьшить движение» сразу.

Промпт: «[ПОЛНОЭКРАННЫЙ] Level complete screen. Top 45% is a dark board #1B2838 edge to edge with bottom corners radius 36: three large yellow stars 48 pt in a row, white bold 34 pt title “С первой попытки”, then a row of three stats: yellow bolt “+15 XP”, yellow coin “+1 монета”, orange flame “12 дней”. Below, on #EEF2F7: event rows with icons — orange flame “Серия продлена: 12 дней”, yellow trophy “Новое достижение: Десятка”; title “Прогресс курса” with “49 из 423” and a thin progress bar (blue fill on #DCE3ED). Bottom: full-width blue keycap “Следующий уровень” and a blue text link “К пути”.»

## Приёмка

- [ ] Тексты совпадают со спецификацией дословно.
- [ ] Цвета соответствуют ролям: жёлтый только у наград, оранжевый только у серии и времени.
- [ ] Не больше одной главной кнопки.
- [ ] Макет прошёл ревизию субагента-критика (виза в `design/README.md`).
