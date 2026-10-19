import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../app/di/providers.dart';
import '../domain/repair_catalog.dart';
import '../domain/repair_service.dart';
import 'world_controller.dart';
import 'world_challenge_screens.dart';
import 'world_ui.dart';

final repairServiceProvider = Provider<RepairService>(
  (ref) => RepairService(
    ref.watch(gameSaveStoreProvider),
    ref.watch(worldRepositoryProvider),
    ref.watch(textAssetLoaderProvider),
    ref.watch(clockProvider),
  ),
);
final repairCatalogProvider = FutureProvider<RepairCatalog>(
  (ref) => ref.watch(repairServiceProvider).catalog(),
);

class RepairOverview extends ConsumerWidget {
  const RepairOverview({super.key});
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final records =
        ref.watch(worldControllerProvider).value?.repairs.values.toList() ?? [];
    final world = ref.watch(worldControllerProvider).value;
    final unattributed =
        ((world?.mistakes.values.fold<int>(0, (sum, n) => sum + n) ?? 0) -
                records.fold<int>(0, (sum, r) => sum + r.openErrors))
            .clamp(0, 1 << 30);
    final pending = records.where((r) => r.pending).toList();
    final confirmed = records
        .where((r) => !r.pending && r.proofs.isNotEmpty)
        .length;
    return ref
        .watch(repairCatalogProvider)
        .when(
          loading: () => const Text('Загрузка самостоятельных проверок…'),
          error: (_, __) => TextButton(
            onPressed: () => ref.invalidate(repairCatalogProvider),
            child: const Text('Повторить загрузку проверок'),
          ),
          data: (catalog) => WorldPanel(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                const Text(
                  'Закрепление по подтемам',
                  style: TextStyle(
                    color: WorldPalette.cyan,
                    fontWeight: FontWeight.w800,
                  ),
                ),
                Text(
                  'Ждут проверки: ${pending.length} · подтверждено: $confirmed',
                  style: const TextStyle(color: WorldPalette.text),
                ),
                const SizedBox(height: 8),
                const Text(
                  'Реши другой пример без разбора. Повторение показанного ответа не подтверждает навык.',
                  style: TextStyle(color: WorldPalette.muted),
                ),
                for (final repair in pending) ...[
                  const Divider(color: WorldPalette.border),
                  Text(
                    catalog.title(repair),
                    style: const TextStyle(
                      color: WorldPalette.text,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                  Text(
                    'Ошибок по подтеме: ${repair.openErrors}',
                    style: const TextStyle(color: WorldPalette.muted),
                  ),
                  TextButton(
                    onPressed: catalog.next(repair) == null
                        ? null
                        : () => Navigator.of(context).push(
                            MaterialPageRoute<void>(
                              builder: (_) =>
                                  RepairScreen(skillId: repair.skillId),
                            ),
                          ),
                    child: Text(
                      catalog.next(repair) == null
                          ? 'Нужны новые независимые примеры'
                          : 'Проверить на другом примере',
                    ),
                  ),
                ],
                for (final repair in records.where(
                  (r) => !r.pending && r.proofs.isNotEmpty,
                )) ...[
                  const Divider(color: WorldPalette.border),
                  Text(
                    '✓ ${catalog.title(repair)}',
                    style: const TextStyle(color: WorldPalette.green),
                  ),
                  Text(
                    'Самостоятельное решение сохранено · ${_proofDate(repair.proofs.last['verifiedAt'])}',
                    style: const TextStyle(
                      color: WorldPalette.muted,
                      fontSize: 12,
                    ),
                  ),
                ],
                if (unattributed > 0)
                  Text(
                    'Старых ошибок без известной подтемы: $unattributed. Они не засчитываются как подтверждённые навыки.',
                    style: const TextStyle(color: WorldPalette.muted),
                  ),
                if (pending.isEmpty)
                  const Text(
                    'Новых ошибок с известной подтемой нет. Старые общие счётчики не считаются доказательством навыка.',
                    style: TextStyle(color: WorldPalette.muted),
                  ),
              ],
            ),
          ),
        );
  }
}

String _proofDate(String? value) {
  final date = DateTime.tryParse(value ?? '')?.toLocal();
  if (date == null) return 'дата недоступна';
  String two(int n) => n.toString().padLeft(2, '0');
  return '${two(date.day)}.${two(date.month)}.${date.year} ${two(date.hour)}:${two(date.minute)}';
}

class RepairScreen extends ConsumerStatefulWidget {
  const RepairScreen({required this.skillId, super.key});
  final String skillId;
  @override
  ConsumerState<RepairScreen> createState() => _RepairScreenState();
}

class _RepairScreenState extends ConsumerState<RepairScreen> {
  RepairResult? _feedback;
  @override
  Widget build(BuildContext context) {
    final state = ref.watch(worldControllerProvider).value;
    final catalog = ref.watch(repairCatalogProvider).value;
    final repair = state?.repairs[widget.skillId];
    return WorldPage(
      title: 'Самостоятельная проверка',
      child: state == null || catalog == null
          ? const Center(child: CircularProgressIndicator())
          : ListView(
              padding: const EdgeInsets.all(16),
              children: [
                Text(
                  repair == null
                      ? 'Запись ошибки сброшена.'
                      : catalog.title(repair),
                  style: const TextStyle(
                    color: WorldPalette.text,
                    fontSize: 20,
                    fontWeight: FontWeight.w800,
                  ),
                ),
                const SizedBox(height: 10),
                if (_feedback != null)
                  WorldPanel(
                    glow: _feedback!.passed
                        ? WorldPalette.green
                        : WorldPalette.orange,
                    child: Text(
                      _feedback!.message,
                      style: const TextStyle(color: WorldPalette.text),
                    ),
                  ),
                const SizedBox(height: 10),
                if (repair != null &&
                    repair.pending &&
                    catalog.next(repair) != null)
                  WorldChallengeForm(
                    key: ValueKey('${repair.skillId}:${repair.generation}'),
                    task: catalog.next(repair)!.question(repair),
                    wrongAnswers: repair.attempts,
                    submit: (answer, _) async {
                      final result = await ref
                          .read(repairServiceProvider)
                          .submit(
                            repair.skillId,
                            repair.generation,
                            catalog.next(repair)!.id,
                            answer,
                          );
                      if (mounted) setState(() => _feedback = result);
                    },
                  )
                else ...[
                  Text(
                    repair != null && repair.pending
                        ? 'Незнакомые примеры этой подтемы закончились. Ошибка остаётся незакреплённой; повтор разобранного примера не даст подтверждения.'
                        : 'Подтверждение сохранено. Оно не является профессиональной аттестацией.',
                    style: const TextStyle(color: WorldPalette.text),
                  ),
                  TextButton(
                    onPressed: () => Navigator.of(context).pop(),
                    child: const Text('Вернуться к ошибкам'),
                  ),
                ],
              ],
            ),
    );
  }
}
