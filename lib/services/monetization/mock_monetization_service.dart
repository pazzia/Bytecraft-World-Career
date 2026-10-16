import 'monetization_service.dart';

/// Simulates store and ad network behaviour for development builds.
class MockMonetizationService implements MonetizationService {
  MockMonetizationService({this.latency = const Duration(milliseconds: 400)});

  final Duration latency;
  Subscription? _subscription;

  Future<void> _wait() => Future<void>.delayed(latency);

  @override
  Future<bool> showRewardedAd() async {
    await _wait();
    return true;
  }

  @override
  Future<void> showInterstitial() => _wait();

  @override
  Future<PurchaseResult> purchasePremium(SubscriptionPlan plan) async {
    await _wait();
    final subscription = Subscription(
      planId: plan.id,
      status: SubscriptionStatus.active,
    );
    _subscription = subscription;
    return PurchaseResult(PurchaseStatus.success, subscription: subscription);
  }

  @override
  Future<PurchaseResult> restorePurchases() async {
    await _wait();
    final subscription = _subscription;
    if (subscription == null) {
      return const PurchaseResult(PurchaseStatus.nothingToRestore);
    }
    return PurchaseResult(PurchaseStatus.success, subscription: subscription);
  }

  @override
  Future<PurchaseResult> purchaseCoins(CoinPack pack) async {
    await _wait();
    return PurchaseResult(PurchaseStatus.success, coinsGranted: pack.coins);
  }
}
