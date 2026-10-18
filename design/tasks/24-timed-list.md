# 24. На время: список забегов

- Задача бэклога: X-11
- Этап: 2
- Спецификация: `design/SPEC.md`
- Куда класть результат: `design/renders/24-timed-list/`
- Статус: не начато

## Как отрисовать

1. Откройте новый чат в ChatGPT с генерацией изображений.
2. Скопируйте промпт ниже целиком, включая первую часть с цветами и шрифтами — без неё макет разойдётся с системой.
3. Сохраните результат как PNG в папку из шапки: `light.png`, для тёмной темы `dark.png`, для вариантов — `<вариант>.png`.
4. Если ChatGPT исказил текст или цвет, попросите исправить конкретную деталь («замени текст на кнопке на „Проверить“»), а не перегенерируйте с нуля.

## Промпты

### Макет — 5.7.1

Префикс: НОЧНОЙ.

```text
Mobile app UI mockup of one iPhone 14 screen, 390×844 pt, flat vector UI, no device frame, no gradients, no blurred shadows, no tab bar. Night theme: background #142033, keycaps #22344F with darker bottom edge #0D1726 (lifted keycap #2F4566), code board #0D1726, main text #F1F5FA, secondary text #A9B8CC. Primary buttons are orange #FF5B1F keycaps with edge #B83A0B and dark text #1B0A02. Timer and record numbers in #FF8A57. Answer keys and secondary keycaps #22344F with text #F1F5FA; selected answer key face #213A5C with 2 pt outline #5B95DB. Wrong-answer panel background #3F2230 with title and captions #FF8A8E; correct-answer panel background #173B33 with title #5FD39C. Fonts: Onest for UI, JetBrains Mono for code with the same syntax colors (keywords #C792EA, builtins #82AAFF, strings #C3E88D, numbers #F78C6C, comments #8796AB). Russian text exactly as quoted, sentence case, no emoji, no all caps.

Screen “На время” with a back arrow and bold 30 pt title. Rules text in #A9B8CC: “Пройдите модуль целиком, пока не вышло время. Ошибка стоит 15 секунд. ×2 XP за уровень, пройденный не больше чем с одной ошибкой, и бонус за скорость за первый забег”. List of navy keycap tiles #22344F 88 pt: “Переменные”, caption “10:00 на 8 уровней”, right “рекорд 6:10” in #FF8A57; “Циклы” tile with a thin orange fuse bar across its top at 40% and caption “Забег идёт: 3 из 8 · осталось 4:12”, with an orange keycap button “Вернуться в забег” (dark text); last tile flat #1C2B42 without edge, grey lock, “Списки”, caption “Откроется после модуля в обучении”.
```

## Спецификация

Выдержка из `design/SPEC.md`. Если выдержка и SPEC расходятся, верен SPEC.

### 5.7 На время

Все экраны — [НОЧНОЙ]. Открываются поверх оболочки, таб-бара нет.

**5.7.1 Список забегов.**
- Шапка: стрелка назад и H1 «На время».
- Правила Body `#A9B8CC`: «Пройдите модуль целиком, пока не вышло время. Ошибка стоит 15 секунд. ×2 XP за уровень, пройденный не больше чем с одной ошибкой, и бонус за скорость за первый забег».
- Плитки модулей (88): название Title; Caption «10:00 на 8 уровней»; справа «рекорд 6:10» `#FF8A57`.
- Активный забег:
  - фитиль 4 высотой во всю ширину плитки, доля оставшегося времени `#FF5B1F`;
  - Caption «Забег идёт: 3 из 8 · осталось 4:12»;
  - Primary «Вернуться в забег».
- Закрытый модуль: плоская плитка `#1C2B42` без ребра, замок `#A9B8CC`, Caption «Откроется после модуля в обучении». Нажатие — лист 5.14.2.

## Приёмка

- [ ] Тексты совпадают со спецификацией дословно.
- [ ] Цвета соответствуют ролям: жёлтый только у наград, оранжевый только у серии и времени.
- [ ] Не больше одной главной кнопки.
- [ ] Макет прошёл ревизию субагента-критика (виза в `design/README.md`).
