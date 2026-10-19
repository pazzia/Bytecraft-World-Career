import 'skill_repair.dart';
import 'world_challenge.dart';

class RepairExample {
  const RepairExample({
    required this.id,
    required this.code,
    required this.stdin,
    required this.answer,
    this.prompt,
    this.options = const [],
  });
  final String id, code, stdin, answer;
  final String? prompt;
  final List<String> options;
  factory RepairExample.fromJson(Map<String, dynamic> json) => RepairExample(
    id: json['id'] as String,
    code: json['code'] as String,
    stdin: json['stdin'] as String? ?? '',
    answer: json['answer'] as String,
    prompt: json['prompt'] as String?,
    options: List<String>.from(json['options'] as List? ?? []),
  );
  WorldChallenge question(SkillRepair repair) => WorldChallenge(
    id: '${repair.skillId}:${repair.generation}:$id',
    title: 'Самостоятельная проверка',
    category: repair.category,
    code: code,
    prompt:
        prompt ??
        '${stdin.isEmpty ? '' : 'Данные ввода:\n$stdin\n'}Введи точный вывод программы без внешних кавычек.',
    options: options,
    answer: answer,
    explanation: 'Проверяемый ответ:\n$answer',
  );
}

class RepairCatalog {
  RepairCatalog(this.skills, {this.origins = const {}});
  final Map<String, Map<String, dynamic>> skills;
  final Map<String, Map<String, dynamic>> origins;
  factory RepairCatalog.fromJson(Map<String, dynamic> json) {
    if (json['schemaVersion'] != 1)
      throw StateError('Unsupported repair catalogue');
    return RepairCatalog(
      {
        for (final e in (json['skills'] as Map).entries)
          '${e.key}': Map<String, dynamic>.from(e.value as Map),
      },
      origins: {
        for (final e in (json['origins'] as Map? ?? {}).entries)
          '${e.key}': Map<String, dynamic>.from(e.value as Map),
      },
    );
  }
  String title(SkillRepair repair) => repair.skillId.startsWith('world:')
      ? repair.title
      : skills[repair.skillId]?['title'] as String? ?? repair.title;
  RepairExample? next(SkillRepair repair) {
    if (!repair.pending) return null;
    final examples = <RepairExample>[];
    for (final json in skills[repair.skillId]?['examples'] as List? ?? []) {
      final example = RepairExample.fromJson(
        Map<String, dynamic>.from(json as Map),
      );
      examples.add(example);
    }
    final disclosedAnswers = {
      for (final e in examples)
        if (repair.seen.contains(e.id)) e.answer,
    };
    final candidates = examples
        .where(
          (example) =>
              !repair.seen.contains(example.id) &&
              !repair.sources.contains(
                SkillRepair.signature(example.code, example.stdin),
              ),
        )
        .toList();
    for (final candidate in candidates) {
      if (!disclosedAnswers.contains(candidate.answer)) return candidate;
    }
    return candidates.isEmpty ? null : candidates.first;
  }
}
