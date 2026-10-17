import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../features/playground/presentation/python_host.dart';
import '../../features/world/presentation/world_ui.dart';

class MainShell extends StatelessWidget {
  const MainShell({super.key, required this.shell});

  final StatefulNavigationShell shell;

  @override
  Widget build(BuildContext context) => Scaffold(
        backgroundColor: WorldPalette.bg,
        body: Stack(
          fit: StackFit.expand,
          children: [
            shell,
            const PythonHost(),
          ],
        ),
        bottomNavigationBar: _WorldTabBar(
          currentIndex: shell.currentIndex,
          onSelect: (index) => shell.goBranch(
            index,
            initialLocation: index == shell.currentIndex,
          ),
        ),
      );
}

class _WorldTabBar extends StatelessWidget {
  const _WorldTabBar({required this.currentIndex, required this.onSelect});

  final int currentIndex;
  final ValueChanged<int> onSelect;

  static const tabs = [
    (Icons.public_outlined, Icons.public_rounded, 'Мир'),
    (Icons.school_outlined, Icons.school_rounded, 'Учёба'),
    (Icons.biotech_outlined, Icons.biotech_rounded, 'DNA'),
    (Icons.terminal_outlined, Icons.terminal_rounded, 'Код'),
    (Icons.person_outline_rounded, Icons.person_rounded, 'Профиль'),
  ];

  @override
  Widget build(BuildContext context) => Container(
        decoration: const BoxDecoration(
          color: Color(0xFF08111F),
          border: Border(
            top: BorderSide(color: WorldPalette.border),
          ),
          boxShadow: [
            BoxShadow(
              color: Color(0x66000000),
              blurRadius: 20,
              offset: Offset(0, -5),
            ),
          ],
        ),
        child: SafeArea(
          top: false,
          child: SizedBox(
            height: 70,
            child: Row(
              children: [
                for (var i = 0; i < tabs.length; i++)
                  Expanded(
                    child: InkWell(
                      onTap: () => onSelect(i),
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(
                            i == currentIndex ? tabs[i].$2 : tabs[i].$1,
                            color: i == currentIndex
                                ? WorldPalette.purple
                                : WorldPalette.muted,
                          ),
                          const SizedBox(height: 4),
                          Text(
                            tabs[i].$3,
                            style: TextStyle(
                              color: i == currentIndex
                                  ? WorldPalette.text
                                  : WorldPalette.muted,
                              fontSize: 10,
                              fontWeight: i == currentIndex
                                  ? FontWeight.w900
                                  : FontWeight.w600,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
              ],
            ),
          ),
        ),
      );
}
