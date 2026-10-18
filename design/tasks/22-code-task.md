# 22. Задача с кодом

- Задача бэклога: X-11
- Этап: 2
- Спецификация: `design/SPEC.md`
- Куда класть результат: `design/renders/22-code-task/`
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

Code task screen with back arrow and title “Сумма чётных”. Text “Прочитайте число n и выведите сумму чётных чисел от 1 до n.” Two small boards side by side: “Ввод” with “6” and “Ожидаемый вывод” with “12”. A tall dark editor board with line numbers and code “n = int(input())”, “print(sum(range(2, n + 1, 2)))”. Buttons: white keycap “Запустить” and blue keycap “Проверить”. Result list: “Тест 1” green check, “Тест 2” green check, “Тест 3” red cross with caption “Ожидалось 0, получено 2”.
```

## Спецификация

Выдержка из `design/SPEC.md`. Если выдержка и SPEC расходятся, верен SPEC.

#### 5.6.2 Задачи с кодом

**Список.**
- Сверху Caption «Решено 12 из 47. Программа должна пройти все тесты».
- Строка: название (Title); сложность — три точки 8, заполненные `#2F6DB5` (вместо ★☆, C4); справа галочка Green, если решено.

**Экран задачи.**
- Условие (Body).
- Блок «Пример»: две мини-доски «Ввод» и «Ожидаемый вывод».
- Редактор-доска с номерами строк и панелью символов `⇥ ( ) : " [ ]` над клавиатурой.
- Кнопки «Запустить» (Secondary) и «Проверить» (Primary).
- Результат: строки тестов «Тест 1» с галочкой Green или крестом Red, у непройденных — «Ожидалось» и «Получено».
- Итог: «Все тесты пройдены» (Green) или «Пройдено 2 из 4».

Промпт: «[ПОЛНОЭКРАННЫЙ] Code task screen with back arrow and title “Сумма чётных”. Text “Прочитайте число n и выведите сумму чётных чисел от 1 до n.” Two small boards side by side: “Ввод” with “6” and “Ожидаемый вывод” with “12”. A tall dark editor board with line numbers and code “n = int(input())”, “print(sum(range(2, n + 1, 2)))”. Buttons: white keycap “Запустить” and blue keycap “Проверить”. Result list: “Тест 1” green check, “Тест 2” green check, “Тест 3” red cross with caption “Ожидалось 0, получено 2”.»

## Приёмка

- [ ] Тексты совпадают со спецификацией дословно.
- [ ] Цвета соответствуют ролям: жёлтый только у наград, оранжевый только у серии и времени.
- [ ] Не больше одной главной кнопки.
- [ ] Макет прошёл ревизию субагента-критика (виза в `design/README.md`).
