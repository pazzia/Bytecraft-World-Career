import '../../../core/time/clock.dart';
import '../../../core/storage/game_save_store.dart';
import '../../../services/analytics/analytics_service.dart';
import '../../../services/monetization/monetization_service.dart';
import '../../gamification/domain/game_rules.dart';
import '../../gamification/domain/lives.dart';
import '../../progress/domain/progress_repository.dart';

enum ShopItemKind { streakFreeze, livesRefill }

class ShopItem {
  const ShopItem({
    required this.kind,
    required this.title,
    required this.description,
    required this.icon,
    required this.price,
  });

  final ShopItemKind kind;
  final String title;
  final String description;
  final String icon;
  final int price;

  static List<ShopItem> catalog(GameRules rules) => [
        ShopItem(
          kind: ShopItemKind.streakFreeze,
          title: 'Заморозка серии',
          description: 'Сохранит серию, если пропустите день',
          icon: '🧊',
          price: rules.streakFreezePrice,
        ),
        ShopItem(
          kind: ShopItemKind.livesRefill,
          title: 'Полные жизни',
          description: 'Мгновенно восстановит все жизни',
          icon: '❤️',
          price: rules.livesRefillPrice,
        ),
      ];
}

enum ShopPurchaseOutcome { success, notEnoughCoins, limitReached, notNeeded }

/// Coins, shop items, rewarded ads and premium — everything that changes
/// the player's wallet or entitlements goes through here.
class EconomyService {
  EconomyService({
    required ProgressRepository progress,
    required MonetizationService monetization,
    required AnalyticsService analytics,
    required GameRules rules,
    required Clock clock,
    GameSaveStore? saveStore,
  })  : _saveStore = saveStore,
        _progress = progress,
        _monetization = monetization,
        _analytics = analytics,
        _rules = rules,
        _clock = clock;

  final GameSaveStore? _saveStore;
  Future<T> _atomic<T>(Future<T> Function() action) =>
      _saveStore == null ? action() : _saveStore.transaction(action);
  final ProgressRepository _progress;
  final MonetizationService _monetization;
  final AnalyticsService _analytics;
  final GameRules _rules;
  final Clock _clock;

  Future<ShopPurchaseOutcome> buy(ShopItem item) => _atomic(() => _buy(item));

  Future<ShopPurchaseOutcome> _buy(ShopItem item) async {
    final profile = await _progress.loadProfile();
    if (profile.coins < item.price) return ShopPurchaseOutcome.notEnoughCoins;
    final now = _clock.now();
    switch (item.kind) {
      case ShopItemKind.streakFreeze:
        if (profile.streak.freezes >= _rules.maxStreakFreezes) {
          return ShopPurchaseOutcome.limitReached;
        }
        await _progress.saveProfile(
          profile.copyWith(
            coins: profile.coins - item.price,
            streak: profile.streak
                .copyWith(freezes: profile.streak.freezes + 1),
          ),
        );
      case ShopItemKind.livesRefill:
        if (LivesPolicy(_rules, capacity: profile.lifeCapacity).regenerate(profile.lives, now).current >= (profile.lifeCapacity ?? _rules.maxLives)) {
          return ShopPurchaseOutcome.notNeeded;
        }
        await _progress.saveProfile(
          profile.copyWith(
            coins: profile.coins - item.price,
            lives: LivesState(current: profile.lifeCapacity ?? _rules.maxLives),
          ),
        );
    }
    return ShopPurchaseOutcome.success;
  }

  /// Rewarded ad → +1 life. Returns true when the reward was granted.
  Future<bool> watchAdForLife() => _atomic(() => _watchAdForLife());

  Future<bool> _watchAdForLife() async {
    final watched = await _monetization.showRewardedAd();
    if (!watched) return false;
    _analytics.track(AnalyticsEvent.adWatched, {'reward': 'life'});
    final profile = await _progress.loadProfile();
    await _progress.saveProfile(
      profile.copyWith(lives: LivesPolicy(_rules, capacity: profile.lifeCapacity).addLives(profile.lives, _clock.now())),
    );
    return true;
  }

  Future<bool> purchasePremium(SubscriptionPlan plan) => _atomic(() => _purchasePremium(plan));

  Future<bool> _purchasePremium(SubscriptionPlan plan) async {
    final result = await _monetization.purchasePremium(plan);
    if (!result.isSuccess) return false;
    _analytics.track(AnalyticsEvent.subscriptionStarted, {'plan': plan.id});
    await _setPremium(isPremium: true);
    return true;
  }

  Future<bool> restorePurchases() => _atomic(() => _restorePurchases());

  Future<bool> _restorePurchases() async {
    final result = await _monetization.restorePurchases();
    final active = result.isSuccess && (result.subscription?.isActive ?? false);
    if (active) await _setPremium(isPremium: true);
    return active;
  }

  Future<int> purchaseCoins(CoinPack pack) => _atomic(() => _purchaseCoins(pack));

  Future<int> _purchaseCoins(CoinPack pack) async {
    final result = await _monetization.purchaseCoins(pack);
    if (!result.isSuccess) return 0;
    final profile = await _progress.loadProfile();
    await _progress.saveProfile(
      profile.copyWith(coins: profile.coins + result.coinsGranted),
    );
    return result.coinsGranted;
  }

  Future<void> _setPremium({required bool isPremium}) async {
    final profile = await _progress.loadProfile();
    await _progress.saveProfile(profile.copyWith(isPremium: isPremium));
  }
}
