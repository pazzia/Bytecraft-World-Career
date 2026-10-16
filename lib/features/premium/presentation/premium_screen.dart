import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../app/di/providers.dart';
import '../../../core/theme/app_spacing.dart';
import '../../../services/monetization/monetization_service.dart';
import '../../../shared/widgets/app_button.dart';
import '../../../shared/widgets/app_card.dart';
import '../../progress/presentation/progress_providers.dart';

class PremiumScreen extends ConsumerStatefulWidget {
  const PremiumScreen({super.key});

  @override
  ConsumerState<PremiumScreen> createState() => _PremiumScreenState();
}

class _PremiumScreenState extends ConsumerState<PremiumScreen> {
  String? _busyPlanId;
  bool _restoring = false;

  static const List<(String, String)> _benefits = [
    ('❤️', 'Бесконечные жизни'),
    ('🚫', 'Без рекламы'),
    ('📊', 'Полная статистика'),
    ('📚', 'Расширенные курсы'),
    ('🤖', 'AI-объяснения и AI-тьютор'),
  ];

  Future<void> _purchase(SubscriptionPlan plan) async {
    setState(() => _busyPlanId = plan.id);
    final ok = await ref.read(economyServiceProvider).purchasePremium(plan);
    if (!mounted) return;
    ref.read(progressRevisionProvider.notifier).bump();
    setState(() => _busyPlanId = null);
    if (ok) {
      context.pop();
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Покупка не завершена')),
      );
    }
  }

  Future<void> _restore() async {
    setState(() => _restoring = true);
    final restored = await ref.read(economyServiceProvider).restorePurchases();
    if (!mounted) return;
    ref.read(progressRevisionProvider.notifier).bump();
    setState(() => _restoring = false);
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(restored ? 'Premium восстановлен' : 'Покупок не найдено'),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    return Scaffold(
      appBar: AppBar(title: const Text('Premium')),
      body: ListView(
        padding: const EdgeInsets.all(Spacing.page),
        children: [
          Text('Учитесь без ограничений ⭐', style: textTheme.headlineSmall),
          const SizedBox(height: Spacing.lg),
          for (final (glyph, text) in _benefits)
            Padding(
              padding: const EdgeInsets.only(bottom: Spacing.sm),
              child: Row(
                children: [
                  Text(glyph, style: const TextStyle(fontSize: 22)),
                  const SizedBox(width: Spacing.md),
                  Text(text, style: textTheme.bodyLarge),
                ],
              ),
            ),
          const SizedBox(height: Spacing.xl),
          for (final plan in SubscriptionPlan.defaults)
            Padding(
              padding: const EdgeInsets.only(bottom: Spacing.md),
              child: AppCard(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Text(
                      plan.period == SubscriptionPeriod.yearly
                          ? 'Годовая подписка'
                          : 'Месячная подписка',
                      style: textTheme.titleMedium,
                    ),
                    Text(plan.priceLabel),
                    const SizedBox(height: Spacing.md),
                    AppButton(
                      label: 'Оформить',
                      isLoading: _busyPlanId == plan.id,
                      onPressed:
                          _busyPlanId == null ? () => _purchase(plan) : null,
                    ),
                  ],
                ),
              ),
            ),
          TextButton(
            onPressed: _restoring ? null : _restore,
            child: const Text('Восстановить покупки'),
          ),
          const SizedBox(height: Spacing.sm),
          Text(
            'Демо-сборка: платежи симулируются.',
            textAlign: TextAlign.center,
            style: textTheme.bodySmall,
          ),
        ],
      ),
    );
  }
}
