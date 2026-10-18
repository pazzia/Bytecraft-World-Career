# 01. Онбординг: выбор опыта

- Задача бэклога: X-2
- Этап: 1
- Спецификация: `design/SPEC.md`
- Куда класть результат: `design/renders/01-onboarding/`
- Статус: не начато

## Как отрисовать

1. Откройте новый чат в ChatGPT с генерацией изображений.
2. Скопируйте промпт ниже целиком, включая первую часть с цветами и шрифтами — без неё макет разойдётся с системой.
3. Сохраните результат как PNG в папку из шапки: `light.png`, для тёмной темы `dark.png`, для вариантов — `<вариант>.png`.
4. Если ChatGPT исказил текст или цвет, попросите исправить конкретную деталь («замени текст на кнопке на „Проверить“»), а не перегенерируйте с нуля.

## Промпты

### Макет — опыт

Префикс: ПОЛНОЭКРАННЫЙ.

```text
Mobile app UI mockup of one iPhone 14 screen, 390×844 pt, flat vector UI, no device frame, no photos, no gradients, no glassmorphism, no blurred shadows. Every pressable element is a mechanical keyboard keycap: a solid face and a solid 4 pt darker bottom edge, corner radius 14 (tiles 16). Fonts: Onest for interface text, JetBrains Mono for code. Page background #EEF2F7, surfaces #FFFFFF, main text #1B2838, secondary text #5B6B7F. Action blue #2F6DB5 with edge #1F4E86. Reward yellow #FFD43B used only for XP, stars and coins icons and numbers, never for buttons. Success green #157A52, error red #D23C42, streak and timer orange #FF5B1F. Code sits on a dark board #1B2838 with radius 22: plain code #E8EEF6, keywords #C792EA, builtins #82AAFF, strings #C3E88D, numbers #F78C6C, comments and line numbers #8796AB. All text in Russian exactly as quoted, sentence case, no emoji, no all caps. Status bar 47 pt at top. No tab bar. Home indicator area 34 pt at the bottom.

Onboarding screen. Top: small dark code board showing `print("Привет!")` and below it output “Привет!”. Bold 30 pt title “Код за пару минут в день”, text “Короткие головоломки на Python. С чего начнём?”. Three white keycaps 350×72 stacked with 12 pt gap, each with bold title and grey caption: “Я новичок в коде” / “Начнём с самых основ”; “Немного знаю” / “Освежим базу и пойдём дальше”; “Пишу код” / “Все модули открыты сразу”.
```

### Макет в тёмной теме

```text
Mobile app UI mockup of one iPhone 14 screen, 390×844 pt, flat vector UI, no device frame, no photos, no gradients, no glassmorphism, no blurred shadows. Every pressable element is a mechanical keyboard keycap: a solid face and a solid 4 pt darker bottom edge, corner radius 14 (tiles 16). Fonts: Onest for interface text, JetBrains Mono for code. Page background #EEF2F7, surfaces #FFFFFF, main text #1B2838, secondary text #5B6B7F. Action blue #2F6DB5 with edge #1F4E86. Reward yellow #FFD43B used only for XP, stars and coins icons and numbers, never for buttons. Success green #157A52, error red #D23C42, streak and timer orange #FF5B1F. Code sits on a dark board #1B2838 with radius 22: plain code #E8EEF6, keywords #C792EA, builtins #82AAFF, strings #C3E88D, numbers #F78C6C, comments and line numbers #8796AB. All text in Russian exactly as quoted, sentence case, no emoji, no all caps. Status bar 47 pt at top. No tab bar. Home indicator area 34 pt at the bottom.

Onboarding screen. Top: small dark code board showing `print("Привет!")` and below it output “Привет!”. Bold 30 pt title “Код за пару минут в день”, text “Короткие головоломки на Python. С чего начнём?”. Three white keycaps 350×72 stacked with 12 pt gap, each with bold title and grey caption: “Я новичок в коде” / “Начнём с самых основ”; “Немного знаю” / “Освежим базу и пойдём дальше”; “Пишу код” / “Все модули открыты сразу”.

Dark theme variant: page background #142033, sheets and tiles #1C2B42, answer keys and secondary keycaps #22344F with edge #0D1726 and text #F1F5FA, selected answer key face #213A5C with 2 pt outline #5B95DB, correct answer key #173B33 outlined #2BB57A, wrong answer key #3F2230 outlined #E25B60, main text #F1F5FA, secondary #A9B8CC, code board #0D1726, blue links and selected outlines #5B95DB; primary, success and danger buttons keep their light-theme face colors; wrong-answer panel #3F2230 with title #FF8A8E, correct-answer panel #173B33 with title #5FD39C; tab bar background #0D1726, selected tab #5B95DB, other tabs #A9B8CC.
```

## Спецификация

Выдержка из `design/SPEC.md`. Если выдержка и SPEC расходятся, верен SPEC.

### 5.10 Онбординг и согласие — X-1, X-2

До первого решённого уровня — один экран (F-1).

**Экран опыта.**
- Сверху мини-доска с `print("Привет!")` и выводом «Привет!».
- H1 «Код за пару минут в день».
- Body «Короткие головоломки на Python. С чего начнём?»
- Три клавиши-варианта 350 × 72: «Я новичок в коде» / «Начнём с самых основ»; «Немного знаю» / «Освежим базу и пойдём дальше»; «Пишу код» / «Все модули открыты сразу».
- Нажатие сразу открывает первый уровень. Выбора курса нет, пока курс один.

**Лист согласия (X-1).**
- Когда: после первого верного ответа, перед экраном результата. До этого события копятся только на телефоне.
- H2 «Помогите сделать курс лучше».
- Body «Мы видим, какие уровни проходят и где ошибаются. Без имени и контактов».
- Ссылка «Политика конфиденциальности».
- Primary «Разрешаю», Quiet «Не сейчас».
- «Не сейчас» удаляет накопленную на телефоне очередь событий; отправка не начинается.
- Изменить решение можно в профиле.

## Приёмка

- [ ] Тексты совпадают со спецификацией дословно.
- [ ] Цвета соответствуют ролям: жёлтый только у наград, оранжевый только у серии и времени.
- [ ] Не больше одной главной кнопки.
- [ ] Макет прошёл ревизию субагента-критика (виза в `design/README.md`).
