import 'package:flutter/material.dart';

import 'core/app_theme.dart';
import 'data/seed_levels.dart';
import 'models/level.dart';
import 'screens/home_screen.dart';
import 'screens/learning_map_screen.dart';
import 'screens/level_screen.dart';
import 'screens/onboarding_screen.dart';
import 'screens/profile_screen.dart';
import 'state/app_controller.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const CodeQuestApp());
}

class CodeQuestApp extends StatefulWidget {
  const CodeQuestApp({super.key});

  @override
  State<CodeQuestApp> createState() => _CodeQuestAppState();
}

class _CodeQuestAppState extends State<CodeQuestApp> {
  final AppController controller = AppController();

  @override
  void initState() {
    super.initState();
    controller.addListener(_refresh);
    controller.init();
  }

  @override
  void dispose() {
    controller.removeListener(_refresh);
    controller.dispose();
    super.dispose();
  }

  void _refresh() => setState(() {});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'CodeQuest',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.light(),
      home: !controller.initialized
          ? const _Splash()
          : controller.progress.onboardingDone
              ? _HomeFlow(controller: controller)
              : OnboardingScreen(onDone: controller.finishOnboarding),
    );
  }
}

class _Splash extends StatelessWidget {
  const _Splash();
  @override
  Widget build(BuildContext context) => const Scaffold(body: Center(child: CircularProgressIndicator()));
}

class _HomeFlow extends StatelessWidget {
  const _HomeFlow({required this.controller});
  final AppController controller;

  @override
  Widget build(BuildContext context) {
    return HomeScreen(
      progress: controller.progress,
      onHardcoreChanged: (enabled) => controller.setHardcoreMode(enabled, seedLevels),
      onProfile: () => Navigator.push(
        context,
        MaterialPageRoute(builder: (_) => ProfileScreen(progress: controller.progress)),
      ),
      onContinue: () => Navigator.push(
        context,
        MaterialPageRoute(
          builder: (_) => LearningMapScreen(
            levels: seedLevels,
            controller: controller,
            onLevel: (Level level) => Navigator.push(
              context,
              MaterialPageRoute(
                builder: (_) => LevelScreen(
                  level: level,
                  onSubmit: (answer, mistakes) => controller.submit(
                    level: level,
                    answer: answer,
                    mistakes: mistakes,
                    allLevels: seedLevels,
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}
