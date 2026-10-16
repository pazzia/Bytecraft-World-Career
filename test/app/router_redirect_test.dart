import 'package:bytecraft/app/router/app_router.dart';
import 'package:bytecraft/app/router/routes.dart';
import 'package:bytecraft/features/settings/domain/app_settings.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  final fresh = AppSettings.initial('python');
  final onboarded = fresh.copyWith(onboardingCompleted: true);

  test('stays on splash until startup is ready', () {
    expect(
      resolveRedirect(location: Routes.home, isReady: false, settings: null),
      Routes.splash,
    );
    expect(
      resolveRedirect(location: Routes.splash, isReady: false, settings: null),
      isNull,
    );
  });

  test('new users go to onboarding', () {
    expect(
      resolveRedirect(location: Routes.splash, isReady: true, settings: fresh),
      Routes.onboarding,
    );
    expect(
      resolveRedirect(
        location: Routes.onboardingCourse,
        isReady: true,
        settings: fresh,
      ),
      isNull,
    );
  });

  test('onboarded users skip splash/onboarding and can open any page', () {
    expect(
      resolveRedirect(
        location: Routes.onboarding,
        isReady: true,
        settings: onboarded,
      ),
      Routes.home,
    );
    expect(
      resolveRedirect(
        location: Routes.level('python', 'py_var_001'),
        isReady: true,
        settings: onboarded,
      ),
      isNull,
    );
  });
}
