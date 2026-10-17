import 'career_dashboard.dart';
import 'github_portfolio.dart';

class CvDraftBuilder {
  const CvDraftBuilder();

  String build(CareerDashboard dashboard) {
    final buffer = StringBuffer()
      ..writeln(dashboard.targetTitle)
      ..writeln()
      ..writeln('CAREER PROFILE')
      ..writeln('Career Readiness: ${dashboard.readiness}%')
      ..writeln('Career Score: ${dashboard.careerScore}/100')
      ..writeln('CV Readiness: ${dashboard.cvScore}/100')
      ..writeln()
      ..writeln('SKILLS');

    for (final skill in dashboard.skills) {
      final evidence = skill.portfolioBonus > 0
          ? ' · GitHub proof +${skill.portfolioBonus}'
          : '';
      buffer.writeln('- ${skill.title}: ${skill.score}/100$evidence');
    }

    buffer
      ..writeln()
      ..writeln('LEARNING EVIDENCE')
      ..writeln(
        '- Bytecraft: ${dashboard.completedLevels} из ${dashboard.totalLevels} уровней завершено.',
      );

    final portfolio = dashboard.portfolio;
    if (portfolio.connected) {
      buffer
        ..writeln()
        ..writeln('GITHUB PORTFOLIO')
        ..writeln('- @${portfolio.username}: ${portfolio.projects.length} релевантных публичных проектов');
      for (final project in portfolio.projects.take(5)) {
        buffer.writeln('- ${_projectLine(project)}');
      }
    }

    if (dashboard.actions.isNotEmpty) {
      buffer
        ..writeln()
        ..writeln('CURRENT DEVELOPMENT FOCUS');
      for (final action in dashboard.actions) {
        buffer.writeln('- ${action.title}: ${action.subtitle}');
      }
    }

    buffer
      ..writeln()
      ..writeln(
        'Примечание: это автоматически собранный черновик на основе прогресса Bytecraft и публичных GitHub-метаданных. Перед отправкой работодателю добавь опыт, компании, достижения и контакты.',
      );
    return buffer.toString().trim();
  }

  String _projectLine(GitHubProjectEvidence project) {
    final evidence = <String>[
      if (project.primaryLanguage.isNotEmpty) project.primaryLanguage,
      if (project.hasTests) 'tests',
      if (project.hasCi) 'CI',
      if (project.hasDocker) 'Docker',
      if (project.hasPackageConfig) 'package config',
    ];
    final suffix = evidence.isEmpty ? '' : ' — ${evidence.join(', ')}';
    return '${project.name}$suffix';
  }
}
