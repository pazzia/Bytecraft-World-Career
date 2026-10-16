/// Remote-configurable switches for gradual rollout and A/B tests.
enum FeatureFlag {
  lives('lives_enabled', defaultValue: true),
  ads('ads_enabled', defaultValue: false),
  aiTutor('ai_tutor_enabled', defaultValue: false),
  dailyChallenge('daily_challenge_enabled', defaultValue: true),
  metagame('metagame_enabled', defaultValue: false),
  leaderboards('leaderboards_enabled', defaultValue: false);

  const FeatureFlag(this.key, {required this.defaultValue});

  final String key;
  final bool defaultValue;
}

abstract interface class FeatureFlagService {
  bool isEnabled(FeatureFlag flag);

  /// Fetches fresh values (remote config). Must not throw.
  Future<void> refresh();
}

/// Defaults + local overrides. Remote Config adapter can extend this later.
class LocalFeatureFlagService implements FeatureFlagService {
  LocalFeatureFlagService({Map<FeatureFlag, bool> overrides = const {}})
      : _overrides = {...overrides};

  final Map<FeatureFlag, bool> _overrides;

  @override
  bool isEnabled(FeatureFlag flag) => _overrides[flag] ?? flag.defaultValue;

  void setOverride(FeatureFlag flag, {required bool enabled}) =>
      _overrides[flag] = enabled;

  @override
  Future<void> refresh() async {}
}
