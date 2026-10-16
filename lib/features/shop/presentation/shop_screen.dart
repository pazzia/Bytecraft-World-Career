import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../app/di/providers.dart';
import '../../../core/theme/app_spacing.dart';
import '../../../core/theme/game_colors.dart';
import '../../../services/monetization/monetization_service.dart';
import '../../../shared/widgets/app_button.dart';
import '../../../shared/widgets/app_card.dart';
import '../../../shared/widgets/async_value_view.dart';
import '../../../shared/widgets/stat_badges.dart';
import '../../progress/domain/user_profile.dart';
import '../../progress/presentation/progress_providers.dart';
import '../domain/economy_service.dart';

class ShopScreen extends ConsumerWidget {
  const ShopScreen({super.key});

  static String _message(ShopPurchaseOutcome outcome) => switch (outcome) {
        ShopPurchaseOutcome.success => 'Куплено!',
        ShopPurchaseOutcome.notEnoughCoins => 'Не хватает монет',
        ShopPurchaseOutcome.limitReached => 'Достигнут лимит',
        ShopPurchaseOutcome.notNeeded => 'Жизни и так полные',
      };

  Future<void> _buy(BuildContext context, WidgetRef ref, ShopItem item) async {
    final messenger = ScaffoldMessenger.of(context);
    final outcome = await ref.read(economyServiceProvider).buy(item);
    ref.read(progressRevisionProvider.notifier).bump();
    messenger.showSnackBar(SnackBar(content: Text(_message(outcome))));
  }

  Future<void> _buyCoins(
    BuildContext context,
    WidgetRef ref,
    CoinPack pack,
  ) async {
    final messenger = ScaffoldMessenger.of(context);
    final coins = await ref.read(economyServiceProvider).purchaseCoins(pack);
    ref.read(progressRevisionProvider.notifier).bump();
    messenger.showSnackBar(
      SnackBar(
        content: Text(
          coins > 0
              ? '+$coins ${plural(coins, 'монета', 'монеты', 'монет')}'
              : 'Покупка отменена',
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final profile = ref.watch(profileProvider);
    final items = ShopItem.catalog(ref.watch(gameRulesProvider));
    return Scaffold(
      appBar: AppBar(title: const Text('Магазин')),
      body: AsyncValueView<UserProfile>(
        value: profile,
        data: (profile) => ListView(
          padding: const EdgeInsets.all(Spacing.page),
          children: [
            Align(
              alignment: Alignment.centerLeft,
              child: CoinBadge(coins: profile.coins),
            ),
            const SectionTitle('Бонусы'),
            for (final item in items)
              Padding(
                padding: const EdgeInsets.only(bottom: Spacing.md),
                child: AppCard(
                  child: Row(
                    children: [
                      Icon(
                        switch (item.kind) {
                          ShopItemKind.streakFreeze => Icons.ac_unit_rounded,
                          ShopItemKind.livesRefill => Icons.favorite_rounded,
                        },
                        size: 32,
                        color: switch (item.kind) {
                          ShopItemKind.streakFreeze =>
                            Theme.of(context).colorScheme.primary,
                          ShopItemKind.livesRefill => context.gameColors.life,
                        },
                      ),
                      const SizedBox(width: Spacing.md),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              item.title,
                              style: Theme.of(context).textTheme.titleMedium,
                            ),
                            Text(
                              item.description,
                              style: Theme.of(context).textTheme.bodySmall,
                            ),
                            if (item.kind == ShopItemKind.streakFreeze)
                              Text(
                                'У вас: ${profile.streak.freezes}',
                                style: Theme.of(context).textTheme.labelMedium,
                              ),
                          ],
                        ),
                      ),
                      AppButton(
                        label: '${item.price}',
                        icon: Icons.toll_rounded,
                        expand: false,
                        onPressed: () => _buy(context, ref, item),
                      ),
                    ],
                  ),
                ),
              ),
            const SectionTitle('Монеты'),
            for (final pack in CoinPack.defaults)
              Padding(
                padding: const EdgeInsets.only(bottom: Spacing.md),
                child: AppCard(
                  child: Row(
                    children: [
                      Icon(
                        Icons.toll_rounded,
                        size: 32,
                        color: context.gameColors.rewardIcon,
                      ),
                      const SizedBox(width: Spacing.md),
                      Expanded(
                        child: Text(
                          '${pack.coins} ${plural(pack.coins, 'монета', 'монеты', 'монет')}',
                          style: Theme.of(context).textTheme.titleMedium,
                        ),
                      ),
                      AppButton(
                        label: pack.priceLabel,
                        expand: false,
                        variant: AppButtonVariant.secondary,
                        onPressed: () => _buyCoins(context, ref, pack),
                      ),
                    ],
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }
}
