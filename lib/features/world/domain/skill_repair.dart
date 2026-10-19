/// A concrete learning gap, with independent examples already seen and a
/// durable proof. Broad historical counters never fabricate this evidence.
class SkillRepair {
  const SkillRepair({
    required this.skillId,
    required this.title,
    required this.category,
    this.openErrors = 0,
    this.assessmentRequested = false,
    this.generation = 0,
    this.attempts = 0,
    this.sources = const [],
    this.seen = const [],
    this.proofs = const [],
  });
  final String skillId, title, category;
  final bool assessmentRequested;
  final int openErrors, generation, attempts;
  final List<String> sources, seen;
  final List<Map<String, String>> proofs;
  bool get pending => openErrors > 0 || assessmentRequested;
  int get wrongAnswers => (attempts - proofs.length).clamp(0, 1 << 30);
  static String signature(String code, [String stdin = '']) =>
      '${code.replaceAll(RegExp(r'\s+'), '')}\u0000${stdin.trim()}';
  SkillRepair mistake(String source, {String stdin = ''}) => SkillRepair(
    skillId: skillId,
    title: title,
    category: category,
    openErrors: openErrors + 1,
    assessmentRequested: assessmentRequested,
    generation: generation + 1,
    attempts: attempts,
    sources: {...sources, signature(source, stdin)}.toList(),
    seen: seen,
    proofs: proofs,
  );
  SkillRepair review(
    String id, {
    required bool passed,
    required String code,
    required String stdin,
    required DateTime now,
  }) => SkillRepair(
    skillId: skillId,
    title: title,
    category: category,
    openErrors: passed ? 0 : openErrors,
    assessmentRequested: !passed && assessmentRequested,
    generation: generation + 1,
    attempts: attempts + 1,
    sources: sources,
    seen: [...seen, id],
    proofs: passed
        ? [
            ...proofs,
            {
              'exampleId': id,
              'signature': signature(code, stdin),
              'verifiedAt': now.toIso8601String(),
            },
          ]
        : proofs,
  );
  Map<String, dynamic> toJson() => {
    'skillId': skillId,
    'title': title,
    'category': category,
    'openErrors': openErrors,
    'assessmentRequested': assessmentRequested,
    'generation': generation,
    'attempts': attempts,
    'sources': sources,
    'seen': seen,
    'proofs': proofs,
  };
  factory SkillRepair.fromJson(Map<String, dynamic> json) => SkillRepair(
    skillId: json['skillId'] as String,
    title: json['title'] as String,
    category: json['category'] as String,
    openErrors: json['openErrors'] as int? ?? 0,
    assessmentRequested: json['assessmentRequested'] == true,
    generation: json['generation'] as int? ?? 0,
    attempts: json['attempts'] as int? ?? 0,
    sources: List<String>.from(json['sources'] as List? ?? []),
    seen: List<String>.from(json['seen'] as List? ?? []),
    proofs: [
      for (final proof in json['proofs'] as List? ?? [])
        Map<String, String>.from(proof as Map),
    ],
  );
}
