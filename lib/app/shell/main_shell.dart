import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/theme/app_spacing.dart';
import '../../core/theme/app_theme.dart';
import '../../core/theme/game_colors.dart';
import '../../features/journal/presentation/journal_providers.dart';
import '../../features/learning_map/presentation/learning_map_providers.dart';
import '../../features/playground/presentation/python_host.dart';
import '../../services/feature_flags/feature_flag_service.dart';
import '../di/providers.dart';

/// Bottom navigation shell for the main tabs. Each tab keeps its own
/// navigation stack (StatefulShellRoute.indexedStack).
///
/// The map's "На время" tab switches the whole shell to the night palette.
class MainShell extends ConsumerWidget {
  const MainShell({super.key, required this.shell});

  static const int mapBranch = 1;

  final StatefulNavigationShell shell;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final timedEnabled =
        ref.watch(featureFlagsProvider).isEnabled(FeatureFlag.timedRuns);
    final isTimed = timedEnabled &&
        shell.currentIndex == mapBranch &&
        ref.watch(mapModeProvider) == MapMode.timed;
    final scaffold = Scaffold(
      body: Stack(
        children: [
          Positioned.fill(child: shell),
          const PythonHost(),
        ],
      ),
      bottomNavigationBar: _TabBar(
        dueReviews: ref.watch(dueReviewCountProvider).value ?? 0,
        currentIndex: shell.currentIndex,
        onSelect: (index) => shell.goBranch(
          index,
          initialLocation: index == shell.currentIndex,
        ),
      ),
    );
    return isTimed ? Theme(data: AppTheme.timed, child: scaffold) : scaffold;
  }
}

class _TabBar extends StatelessWidget {
  const _TabBar({
    required this.currentIndex,
    required this.onSelect,
    required this.dueReviews,
  });

  final int currentIndex;
  final ValueChanged<int> onSelect;

  /// Journal topics due for review: a badge on the journal tab.
  final int dueReviews;

  static const int _journalTab = 2;

  static const List<(IconData, IconData, String)> _tabs = [
    (Icons.home_outlined, Icons.home_rounded, 'Главная'),
    (Icons.map_outlined, Icons.map_rounded, 'Карта'),
    (Icons.menu_book_outlined, Icons.menu_book_rounded, 'Журнал'),
    (Icons.terminal_outlined, Icons.terminal_rounded, 'Код'),
    (Icons.person_outline_rounded, Icons.person_rounded, 'Профиль'),
  ];

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    final game = context.gameColors;
    final isDark = scheme.brightness == Brightness.dark;
    return Container(
      decoration: BoxDecoration(
        color: isDark ? game.track : scheme.surface,
        border: Border(top: BorderSide(color: scheme.outline)),
      ),
      child: SafeArea(
        top: false,
        child: SizedBox(
          height: 68,
          child: Row(
            children: [
              for (var i = 0; i < _tabs.length; i++)
                Expanded(
                  child: Semantics(
                    button: true,
                    selected: i == currentIndex,
                    label: i == _journalTab && dueReviews > 0
                        ? '${_tabs[i].$3}, к повторению: $dueReviews'
                        : _tabs[i].$3,
                    excludeSemantics: true,
                    child: InkWell(
                      onTap: () => onSelect(i),
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Badge(
                            isLabelVisible: i == _journalTab && dueReviews > 0,
                            label: Text('$dueReviews'),
                            backgroundColor: game.streak,
                            child: Icon(
                              i == currentIndex ? _tabs[i].$2 : _tabs[i].$1,
                              color: i == currentIndex
                                  ? scheme.primary
                                  : game.textMuted,
                            ),
                          ),
                          const SizedBox(height: Spacing.xs),
                          Text(
                            _tabs[i].$3,
                            style: Theme.of(context)
                                .textTheme
                                .labelSmall
                                ?.copyWith(
                                  color: i == currentIndex
                                      ? scheme.primary
                                      : game.textMuted,
                                  fontWeight: i == currentIndex
                                      ? FontWeight.w800
                                      : FontWeight.w600,
                                ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }
}
