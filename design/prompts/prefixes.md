# Префиксы промптов

Каждый промпт в `tasks/` уже содержит нужный префикс. Этот файл нужен, если вы описываете новый экран сами: вставьте один префикс в начало.

## Вкладки — экраны с нижними вкладками

```text
Mobile app UI mockup of one iPhone 14 screen, 390×844 pt, flat vector UI, no device frame, no photos, no gradients, no glassmorphism, no blurred shadows. Every pressable element is a mechanical keyboard keycap: a solid face and a solid 4 pt darker bottom edge, corner radius 14 (tiles 16). Fonts: Onest for interface text, JetBrains Mono for code. Page background #EEF2F7, surfaces #FFFFFF, main text #1B2838, secondary text #5B6B7F. Action blue #2F6DB5 with edge #1F4E86. Reward yellow #FFD43B used only for XP, stars and coins icons and numbers, never for buttons. Success green #157A52, error red #D23C42, streak and timer orange #FF5B1F. Code sits on a dark board #1B2838 with radius 22: plain code #E8EEF6, keywords #C792EA, builtins #82AAFF, strings #C3E88D, numbers #F78C6C, comments and line numbers #8796AB. All text in Russian exactly as quoted, sentence case, no emoji, no all caps. Status bar 47 pt at top. Bottom tab bar 68 pt plus 34 pt safe area, white, top hairline #D5DDE8, four tabs with rounded icons and labels: «Сегодня» (house), «Путь» (route), «Практика» (dumbbell), «Профиль» (person).
```

## Полноэкранный — уровень, листы, онбординг, результат

```text
Mobile app UI mockup of one iPhone 14 screen, 390×844 pt, flat vector UI, no device frame, no photos, no gradients, no glassmorphism, no blurred shadows. Every pressable element is a mechanical keyboard keycap: a solid face and a solid 4 pt darker bottom edge, corner radius 14 (tiles 16). Fonts: Onest for interface text, JetBrains Mono for code. Page background #EEF2F7, surfaces #FFFFFF, main text #1B2838, secondary text #5B6B7F. Action blue #2F6DB5 with edge #1F4E86. Reward yellow #FFD43B used only for XP, stars and coins icons and numbers, never for buttons. Success green #157A52, error red #D23C42, streak and timer orange #FF5B1F. Code sits on a dark board #1B2838 with radius 22: plain code #E8EEF6, keywords #C792EA, builtins #82AAFF, strings #C3E88D, numbers #F78C6C, comments and line numbers #8796AB. All text in Russian exactly as quoted, sentence case, no emoji, no all caps. Status bar 47 pt at top. No tab bar. Home indicator area 34 pt at the bottom.
```

## Ночной — экраны забега «На время»

```text
Mobile app UI mockup of one iPhone 14 screen, 390×844 pt, flat vector UI, no device frame, no gradients, no blurred shadows, no tab bar. Night theme: background #142033, keycaps #22344F with darker bottom edge #0D1726 (lifted keycap #2F4566), code board #0D1726, main text #F1F5FA, secondary text #A9B8CC. Primary buttons are orange #FF5B1F keycaps with edge #B83A0B and dark text #1B0A02. Timer and record numbers in #FF8A57. Answer keys and secondary keycaps #22344F with text #F1F5FA; selected answer key face #213A5C with 2 pt outline #5B95DB. Wrong-answer panel background #3F2230 with title and captions #FF8A8E; correct-answer panel background #173B33 with title #5FD39C. Fonts: Onest for UI, JetBrains Mono for code with the same syntax colors (keywords #C792EA, builtins #82AAFF, strings #C3E88D, numbers #F78C6C, comments #8796AB). Russian text exactly as quoted, sentence case, no emoji, no all caps.
```

## Тёмная тема — добавляется в конец промпта

```text
Dark theme variant: page background #142033, sheets and tiles #1C2B42, answer keys and secondary keycaps #22344F with edge #0D1726 and text #F1F5FA, selected answer key face #213A5C with 2 pt outline #5B95DB, correct answer key #173B33 outlined #2BB57A, wrong answer key #3F2230 outlined #E25B60, main text #F1F5FA, secondary #A9B8CC, code board #0D1726, blue links and selected outlines #5B95DB; primary, success and danger buttons keep their light-theme face colors; wrong-answer panel #3F2230 with title #FF8A8E, correct-answer panel #173B33 with title #5FD39C; tab bar background #0D1726, selected tab #5B95DB, other tabs #A9B8CC.
```
