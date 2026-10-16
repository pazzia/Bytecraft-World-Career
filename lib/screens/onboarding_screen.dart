import 'package:flutter/material.dart';

class OnboardingScreen extends StatefulWidget {
  const OnboardingScreen({super.key, required this.onDone});
  final Future<void> Function() onDone;

  @override
  State<OnboardingScreen> createState() => _OnboardingScreenState();
}

class _OnboardingScreenState extends State<OnboardingScreen> {
  String selected = 'Новичок';

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const Spacer(),
              const Icon(Icons.code_rounded, size: 72),
              const SizedBox(height: 24),
              Text('CodeQuest', textAlign: TextAlign.center, style: Theme.of(context).textTheme.displaySmall?.copyWith(fontWeight: FontWeight.w800)),
              const SizedBox(height: 12),
              Text('Учись программировать через короткие головоломки.', textAlign: TextAlign.center, style: Theme.of(context).textTheme.titleMedium),
              const SizedBox(height: 32),
              for (final value in ['Новичок', 'Немного знаю', 'Уже программирую'])
                Padding(
                  padding: const EdgeInsets.only(bottom: 10),
                  child: ChoiceChip(
                    label: SizedBox(width: double.infinity, child: Text(value, textAlign: TextAlign.center)),
                    selected: selected == value,
                    onSelected: (_) => setState(() => selected = value),
                    padding: const EdgeInsets.symmetric(vertical: 14),
                  ),
                ),
              const Spacer(),
              FilledButton(
                onPressed: () async => widget.onDone(),
                style: FilledButton.styleFrom(padding: const EdgeInsets.symmetric(vertical: 16)),
                child: const Text('Начать Python'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
