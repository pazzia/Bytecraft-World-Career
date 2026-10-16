enum SubscriptionPeriod { monthly, yearly }

class SubscriptionPlan {
  const SubscriptionPlan({
    required this.id,
    required this.period,
    required this.priceLabel,
  });

  static const List<SubscriptionPlan> defaults = [
    SubscriptionPlan(
      id: 'premium_monthly',
      period: SubscriptionPeriod.monthly,
      priceLabel: '399 ₽ / мес',
    ),
    SubscriptionPlan(
      id: 'premium_yearly',
      period: SubscriptionPeriod.yearly,
      priceLabel: '2 990 ₽ / год',
    ),
  ];

  final String id;
  final SubscriptionPeriod period;

  /// Display price; real stores provide localized prices.
  final String priceLabel;
}

enum SubscriptionStatus { active, expired, none }

class Subscription {
  const Subscription({
    required this.planId,
    required this.status,
    this.expiresAt,
  });

  final String planId;
  final SubscriptionStatus status;
  final DateTime? expiresAt;

  bool get isActive => status == SubscriptionStatus.active;
}

class CoinPack {
  const CoinPack({
    required this.id,
    required this.coins,
    required this.priceLabel,
  });

  static const List<CoinPack> defaults = [
    CoinPack(id: 'coins_100', coins: 100, priceLabel: '99 ₽'),
    CoinPack(id: 'coins_500', coins: 500, priceLabel: '399 ₽'),
  ];

  final String id;
  final int coins;
  final String priceLabel;
}

enum PurchaseStatus { success, cancelled, failed, nothingToRestore }

class PurchaseResult {
  const PurchaseResult(this.status, {this.subscription, this.coinsGranted = 0});

  final PurchaseStatus status;
  final Subscription? subscription;
  final int coinsGranted;

  bool get isSuccess => status == PurchaseStatus.success;
}

/// Ads + in-app purchases port. Store / ad SDKs plug in as adapters.
abstract interface class MonetizationService {
  /// Returns true when the user watched the ad to the end (reward earned).
  Future<bool> showRewardedAd();

  Future<void> showInterstitial();

  Future<PurchaseResult> purchasePremium(SubscriptionPlan plan);

  Future<PurchaseResult> restorePurchases();

  Future<PurchaseResult> purchaseCoins(CoinPack pack);
}
