import 'package:bytecraft/features/career/domain/career_dashboard.dart';
import 'package:bytecraft/features/career/domain/cv_draft_builder.dart';
import 'package:bytecraft/features/career/domain/github_portfolio.dart';
import 'package:bytecraft/features/career/domain/vacancy_match.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('GitHub portfolio score rewards concrete engineering evidence', () {
    final portfolio = GitHubPortfolio(
      username: 'dev',
      status: GitHubPortfolioStatus.connected,
      projects: [
        GitHubProjectEvidence(
          name: 'backend-api',
          description: 'FastAPI service',
          primaryLanguage: 'Python',
          topics: const ['fastapi'],
          stars: 1,
          forks: 0,
          hasTests: true,
          hasCi: true,
          hasDocker: true,
          hasPackageConfig: true,
        ),
        const GitHubProjectEvidence(
          name: 'mobile',
          description: '',
          primaryLanguage: 'Dart',
          topics: [],
          stars: 0,
          forks: 0,
          hasTests: false,
          hasCi: false,
          hasDocker: false,
          hasPackageConfig: false,
        ),
      ],
    );

    expect(CareerDashboardCalculator.portfolioScoreFor(portfolio), 41);
    expect(
      CareerDashboardCalculator.portfolioScoreFor(GitHubPortfolio.disconnected()),
      0,
    );
  });

  test('vacancy matcher detects requirements and points to weakest gap', () {
    const skills = [
      CareerSkill(
        id: CareerSkillId.pythonCore,
        title: 'Python Core',
        score: 80,
        target: 85,
      ),
      CareerSkill(
        id: CareerSkillId.testing,
        title: 'Testing',
        score: 60,
        target: 75,
      ),
      CareerSkill(
        id: CareerSkillId.async,
        title: 'Async',
        score: 40,
        target: 70,
      ),
      CareerSkill(
        id: CareerSkillId.production,
        title: 'Production',
        score: 70,
        target: 70,
      ),
    ];

    final report = const VacancyMatcher().analyze(
      'Ищем Python разработчика: pytest, Docker, FastAPI и asyncio.',
      skills,
    );

    expect(report.hasRequirements, isTrue);
    expect(report.requirements, hasLength(4));
    expect(report.match, 63);
    expect(report.gaps.first.label, 'Async / concurrency');
  });

  test('CV draft includes GitHub proof and current skill score', () {
    const project = GitHubProjectEvidence(
      name: 'python-service',
      description: 'API',
      primaryLanguage: 'Python',
      topics: ['backend'],
      stars: 2,
      forks: 0,
      hasTests: true,
      hasCi: true,
      hasDocker: false,
      hasPackageConfig: true,
    );
    const portfolio = GitHubPortfolio(
      username: 'dev',
      status: GitHubPortfolioStatus.connected,
      projects: [project],
    );
    const skill = CareerSkill(
      id: CareerSkillId.pythonCore,
      title: 'Python Core',
      score: 82,
      target: 85,
      courseScore: 76,
      portfolioBonus: 6,
    );
    const dashboard = CareerDashboard(
      targetId: CareerTargetId.pythonBackend,
      targetTitle: 'Python Backend Developer',
      careerScore: 82,
      readiness: 88,
      cvScore: 75,
      skills: [skill],
      actions: [],
      roleMatches: [],
      completedLevels: 120,
      totalLevels: 367,
      portfolio: portfolio,
      portfolioScore: 30,
    );

    final draft = const CvDraftBuilder().build(dashboard);
    expect(draft, contains('Python Core: 82/100'));
    expect(draft, contains('GitHub proof +6'));
    expect(draft, contains('python-service'));
    expect(draft, contains('@dev'));
  });
}
