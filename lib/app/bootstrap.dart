import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../core/storage/shared_preferences_store.dart';
import 'app.dart';
import 'di/providers.dart';

/// Creates platform adapters that need async initialisation and starts
/// the app. Everything else is lazily built by providers.
Future<void> bootstrap() async {
  WidgetsFlutterBinding.ensureInitialized();
  final prefs = await SharedPreferences.getInstance();
  runApp(
    ProviderScope(
      overrides: [
        keyValueStoreProvider.overrideWithValue(SharedPreferencesStore(prefs)),
      ],
      child: const BytecraftApp(),
    ),
  );
}
