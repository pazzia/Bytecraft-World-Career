# 39. Итоги дня

- Задача бэклога: X-4
- Этап: резерв
- Спецификация: `design/SPEC.md`
- Куда класть результат: `design/renders/39-day-summary/`
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

A share card 350×438 on a dark board #1B2838, radius 22: orange flame icon, big white 34 pt “12 дней подряд”, monospace line “streak += 1” in #FF8A57, three stats “5 уровней”, “+65 XP”, “1 тема повторена”, bottom-left a small keycap logo with “{}” and the word “Bytecraft”. Below on #EEF2F7: blue keycap “Поделиться” and link “Закрыть”.
```

## Спецификация

Выдержка из `design/SPEC.md`. Если выдержка и SPEC расходятся, верен SPEC.

### 5.11 Итоги дня — X-4 (P2)

Открывается ссылкой «Итоги дня» на «Сегодня». Карточка для отправки 4:5 (1080 × 1350 в файле, на экране 350 × 438):
- доска `#1B2838`, радиус 22;
- сверху огонёк Ember 40 и «12 дней подряд» (Display, `#F1F5FA`);
- строка кода `streak += 1` JetBrains Mono `#FF8A57` (серия — Ember);
- три числа: «5 уровней», «+65 XP», «1 тема повторена»;
- внизу клавиша-логотип 32 и «Bytecraft».

Под карточкой Primary «Поделиться» и Quiet «Закрыть».

Промпт: «[ПОЛНОЭКРАННЫЙ] A share card 350×438 on a dark board #1B2838, radius 22: orange flame icon, big white 34 pt “12 дней подряд”, monospace line “streak += 1” in #FF8A57, three stats “5 уровней”, “+65 XP”, “1 тема повторена”, bottom-left a small keycap logo with “{}” and the word “Bytecraft”. Below on #EEF2F7: blue keycap “Поделиться” and link “Закрыть”.»

## Приёмка

- [ ] Тексты совпадают со спецификацией дословно.
- [ ] Цвета соответствуют ролям: жёлтый только у наград, оранжевый только у серии и времени.
- [ ] Не больше одной главной кнопки.
- [ ] Макет прошёл ревизию субагента-критика (виза в `design/README.md`).
