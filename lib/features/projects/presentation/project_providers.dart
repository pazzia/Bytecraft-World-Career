import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../app/di/providers.dart';
import '../../playground/presentation/playground_providers.dart';
import '../domain/calculator_project.dart';
import '../domain/project_service.dart';

final projectServiceProvider = Provider<ProjectService>(
  (ref) => ProjectService(
    ref.watch(documentStoreProvider),
    ref.watch(gameSaveStoreProvider),
    ref.watch(worldRepositoryProvider),
    ref.watch(pythonRunnerProvider),
    ref.watch(textAssetLoaderProvider),
    ref.watch(clockProvider),
  ),
);
final calculatorProjectProvider = FutureProvider<CalculatorProject>((
  ref,
) async {
  ref.watch(gameSaveChangesProvider);
  return ref.watch(projectServiceProvider).load();
});
