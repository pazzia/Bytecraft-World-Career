enum GitHubPortfolioStatus { disconnected, connected, unavailable }

class GitHubProjectEvidence {
  const GitHubProjectEvidence({
    required this.name,
    required this.description,
    required this.primaryLanguage,
    required this.topics,
    required this.stars,
    required this.forks,
    required this.hasTests,
    required this.hasCi,
    required this.hasDocker,
    required this.hasPackageConfig,
    this.updatedAt,
  });

  final String name;
  final String description;
  final String primaryLanguage;
  final List<String> topics;
  final int stars;
  final int forks;
  final bool hasTests;
  final bool hasCi;
  final bool hasDocker;
  final bool hasPackageConfig;
  final DateTime? updatedAt;

  bool get isPython => primaryLanguage.toLowerCase() == 'python';

  String get searchableText => [
        name,
        description,
        primaryLanguage,
        ...topics,
      ].join(' ').toLowerCase();
}

class GitHubPortfolio {
  const GitHubPortfolio({
    required this.username,
    required this.status,
    required this.projects,
    this.message,
  });

  factory GitHubPortfolio.disconnected() => const GitHubPortfolio(
        username: '',
        status: GitHubPortfolioStatus.disconnected,
        projects: <GitHubProjectEvidence>[],
      );

  factory GitHubPortfolio.unavailable(String username, String message) =>
      GitHubPortfolio(
        username: username,
        status: GitHubPortfolioStatus.unavailable,
        projects: const <GitHubProjectEvidence>[],
        message: message,
      );

  final String username;
  final GitHubPortfolioStatus status;
  final List<GitHubProjectEvidence> projects;
  final String? message;

  bool get connected => status == GitHubPortfolioStatus.connected;
  int get projectCount => projects.length;
}

abstract interface class GitHubPortfolioRepository {
  Future<GitHubPortfolio> load(String username);
}
