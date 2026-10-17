import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../app/di/providers.dart';
import '../../progress/presentation/progress_providers.dart';
import '../data/practice_repository.dart';
import '../data/pyodide_runner.dart';
import '../domain/practice_task.dart';
import '../domain/python_runner.dart';

/// One interpreter for the whole app: Pyodide loads once and stays warm.
final pythonRunnerProvider = Provider<PythonRunner>((ref) {
  final runner = PyodideRunner();
  ref.onDispose(runner.dispose);
  return runner;
});

final pythonRunnerStateProvider = StreamProvider<PythonRunnerState>((ref) async* {
  final runner = ref.watch(pythonRunnerProvider);
  yield runner.state;
  yield* runner.states;
});

final practiceRepositoryProvider = Provider<PracticeRepository>(
  (ref) => PracticeRepository(
    ref.watch(textAssetLoaderProvider),
    ref.watch(documentStoreProvider),
  ),
);

final practiceTasksProvider = FutureProvider<List<PracticeTask>>((ref) async {
  final courseId = await ref.watch(activeCourseIdProvider.future);
  return ref.watch(practiceRepositoryProvider).tasks(courseId);
});

final solvedPracticeProvider = FutureProvider<Set<String>>((ref) async {
  ref.watch(progressRevisionProvider);
  final courseId = await ref.watch(activeCourseIdProvider.future);
  return ref.watch(practiceRepositoryProvider).solved(courseId);
});

/// The sandbox editor's text survives tab switches (in memory).
final sandboxDraftProvider =
    NotifierProvider<SandboxDraft, ({String code, String stdin})>(SandboxDraft.new);

class SandboxDraft extends Notifier<({String code, String stdin})> {
  static const String sample = '''# Напишите любой код на Python и нажмите «Запустить»
name = input("Как вас зовут? ")
print(f"Привет, {name}!")

squares = [n * n for n in range(1, 6)]
print("Квадраты:", squares)
''';

  @override
  ({String code, String stdin}) build() => (code: sample, stdin: 'Ада');

  void setCode(String code) => state = (code: code, stdin: state.stdin);

  void setStdin(String stdin) => state = (code: state.code, stdin: stdin);
}
