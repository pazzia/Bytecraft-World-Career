import 'package:flutter/material.dart';

class CodeCard extends StatelessWidget {
  const CodeCard({super.key, required this.code});
  final String code;

  @override
  Widget build(BuildContext context) {
    if (code.isEmpty) return const SizedBox.shrink();
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(color: const Color(0xFF171820), borderRadius: BorderRadius.circular(16)),
      child: SelectableText(code, style: const TextStyle(color: Color(0xFFECECF1), fontFamily: 'monospace', fontSize: 17, height: 1.45)),
    );
  }
}
