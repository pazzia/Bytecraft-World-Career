import 'dart:developer' as developer;

/// Product analytics events. Business logic depends only on this enum and
/// [AnalyticsService]; vendors (Firebase, Amplitude, ...) are adapters.
enum AnalyticsEvent {
  appOpen('app_open'),
  onboardingComplete('onboarding_complete'),
  courseStarted('course_started'),
  levelStarted('level_started'),
  answerSubmitted('answer_submitted'),
  wrongAnswer('wrong_answer'),
  levelCompleted('level_completed'),
  levelFailed('level_failed'),
  hintUsed('hint_used'),
  streakExtended('streak_extended'),
  dailyChallengeStarted('daily_challenge_started'),
  dailyChallengeCompleted('daily_challenge_completed'),
  premiumScreenOpened('premium_screen_opened'),
  subscriptionStarted('subscription_started'),
  adWatched('ad_watched');

  const AnalyticsEvent(this.eventName);

  final String eventName;
}

abstract interface class AnalyticsService {
  void track(AnalyticsEvent event, [Map<String, Object?> params = const {}]);

  void setUserId(String userId);
}

/// Development adapter: writes events to the debug log.
class LoggingAnalyticsService implements AnalyticsService {
  const LoggingAnalyticsService();

  @override
  void track(AnalyticsEvent event, [Map<String, Object?> params = const {}]) {
    developer.log('${event.eventName} $params', name: 'analytics');
  }

  @override
  void setUserId(String userId) {
    developer.log('user=$userId', name: 'analytics');
  }
}

/// Fans events out to several vendors.
class CompositeAnalyticsService implements AnalyticsService {
  const CompositeAnalyticsService(this._delegates);

  final List<AnalyticsService> _delegates;

  @override
  void track(AnalyticsEvent event, [Map<String, Object?> params = const {}]) {
    for (final delegate in _delegates) {
      delegate.track(event, params);
    }
  }

  @override
  void setUserId(String userId) {
    for (final delegate in _delegates) {
      delegate.setUserId(userId);
    }
  }
}

/// Keeps events in memory. Used by tests and debug screens.
class RecordingAnalyticsService implements AnalyticsService {
  final List<(AnalyticsEvent, Map<String, Object?>)> events = [];
  String? userId;

  Iterable<AnalyticsEvent> get names => events.map((entry) => entry.$1);

  @override
  void track(AnalyticsEvent event, [Map<String, Object?> params = const {}]) {
    events.add((event, params));
  }

  @override
  void setUserId(String userId) => this.userId = userId;
}
