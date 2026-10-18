import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../app/di/providers.dart';
import '../domain/world_hearts.dart';
import 'world_controller.dart';
import 'world_ui.dart';

/// Mounted on the hub and in Run; refreshes immediately when returning to the app.
class WorldHeartsPanel extends ConsumerStatefulWidget {
  const WorldHeartsPanel({this.compact = false, super.key});
  final bool compact;

  @override
  ConsumerState<WorldHeartsPanel> createState() => _WorldHeartsPanelState();
}

class _WorldHeartsPanelState extends ConsumerState<WorldHeartsPanel>
    with WidgetsBindingObserver {
  Timer? _timer;
  bool _busy = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    _timer = Timer.periodic(const Duration(seconds: 1), (_) => _tick());
    WidgetsBinding.instance.addPostFrameCallback((_) => _tick());
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (state == AppLifecycleState.resumed) _tick();
  }

  Future<void> _tick() async {
    if (!mounted || _busy) return;
    _busy = true;
    try {
      await ref.read(worldControllerProvider.notifier).refreshHearts();
      if (mounted) setState(() => _error = null);
    } catch (_) {
      if (mounted) setState(() => _error = 'Не удалось сохранить жизни. Повторяем…');
    } finally {
      _busy = false;
    }
  }

  @override
  void dispose() {
    _timer?.cancel();
    WidgetsBinding.instance.removeObserver(this);
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final saved = ref.watch(worldControllerProvider).value;
    if (saved == null) return const SizedBox.shrink();
    final now = ref.read(clockProvider).now();
    final s = WorldHearts.regenerate(saved, now);
    final wait = WorldHearts.nextIn(s, now);
    final full = wait == null;
    if (widget.compact) {
      return WorldPanel(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        onTap: () => showModalBottomSheet<void>(
          context: context, isScrollControlled: true,
          backgroundColor: WorldPalette.bg,
          builder: (_) => const SafeArea(child: SingleChildScrollView(
            child: Padding(padding: EdgeInsets.all(16), child: WorldHeartsPanel())))),
        child: Row(children: [
          const Icon(Icons.favorite_rounded, color: WorldPalette.red, size: 22),
          const SizedBox(width: 8),
          Expanded(child: Text('Жизни забега: ${s.hearts}/${s.maxHearts}',
            key: const ValueKey('world-hearts-count'),
            style: const TextStyle(color: WorldPalette.text, fontWeight: FontWeight.w800))),
          Text(full ? 'Полные' : '+1 ${WorldHearts.countdown(wait)}',
            style: const TextStyle(color: WorldPalette.cyan, fontSize: 12)),
          const SizedBox(width: 4),
          const Icon(Icons.chevron_right, color: WorldPalette.muted, size: 20),
        ]),
      );
    }
    return WorldPanel(
      glow: WorldPalette.red,
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text('Жизни забега: ${s.hearts}/${s.maxHearts}',
          key: const ValueKey('world-hearts-count'),
          style: const TextStyle(color: WorldPalette.text, fontWeight: FontWeight.w800)),
        const SizedBox(height: 8),
        Wrap(spacing: 6, children: List.generate(s.maxHearts, (i) => Icon(
          i < s.hearts ? Icons.favorite_rounded : Icons.favorite_border_rounded,
          color: i < s.hearts ? WorldPalette.red : WorldPalette.muted, size: 24))),
        const SizedBox(height: 8),
        Text(full ? 'Все жизни восстановлены' : 'Следующая жизнь через ${WorldHearts.countdown(wait)}',
          key: const ValueKey('world-hearts-timer'),
          style: const TextStyle(color: WorldPalette.cyan)),
        if (!full) ...[
          const SizedBox(height: 8),
          LinearProgressIndicator(value: (1 - wait.inMilliseconds / WorldHearts.interval.inMilliseconds).clamp(0.0, 1.0),
            color: WorldPalette.red, backgroundColor: WorldPalette.border),
          const SizedBox(height: 8),
        ],
        const Text('Одна жизнь каждые 30 минут, даже когда игра закрыта. Ошибка в бесконечном забеге отнимает одну жизнь. Серверная увеличивает максимум.',
          style: TextStyle(color: WorldPalette.muted, fontSize: 12)),
        if (!full) ...[
          const SizedBox(height: 10),
          WorldButton(
            label: 'Восстановить все за 1 💎 · у тебя ${s.gems}',
            icon: Icons.favorite,
            onPressed: s.gems < 1 || _busy ? null : () async {
              setState(() => _busy = true);
              try {
                await ref.read(worldControllerProvider.notifier).reviveInfinite();
                if (mounted) setState(() => _error = null);
              } catch (_) {
                if (mounted) setState(() => _error = 'Не удалось восстановить жизни. Попробуй ещё раз.');
              } finally {
                if (mounted) setState(() => _busy = false);
              }
            }),
          if (s.gems < 1) const Text('Нет алмазов — дождись бесплатного восстановления. Алмазы дают сундук экспедиции и каждый третий уровень сезона.',
            style: TextStyle(color: WorldPalette.muted, fontSize: 12)),
        ],
        if (_error != null) Text(_error!, style: const TextStyle(color: WorldPalette.orange)),
      ]),
    );
  }
}
