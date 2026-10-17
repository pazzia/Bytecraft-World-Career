import 'package:dio/dio.dart';

import '../domain/github_portfolio.dart';

class DioGitHubPortfolioRepository implements GitHubPortfolioRepository {
  DioGitHubPortfolioRepository(this._dio);

  final Dio _dio;

  @override
  Future<GitHubPortfolio> load(String username) async {
    final clean = username.trim().replaceFirst(RegExp(r'^@'), '');
    if (clean.isEmpty) return GitHubPortfolio.disconnected();

    try {
      final response = await _dio.get<List<dynamic>>(
        '/users/${Uri.encodeComponent(clean)}/repos',
        queryParameters: const {
          'per_page': 40,
          'sort': 'pushed',
          'direction': 'desc',
        },
      );
      final raw = response.data ?? const <dynamic>[];
      final repositories = raw
          .whereType<Map<String, dynamic>>()
          .where((repo) => repo['fork'] != true && repo['archived'] != true)
          .take(8)
          .toList(growable: false);

      final projects = await Future.wait(
        repositories.map((repo) => _project(clean, repo)),
      );
      return GitHubPortfolio(
        username: clean,
        status: GitHubPortfolioStatus.connected,
        projects: List.unmodifiable(projects),
      );
    } on DioException catch (error) {
      final code = error.response?.statusCode;
      if (code == 404) {
        return GitHubPortfolio.unavailable(
          clean,
          'Пользователь @$clean не найден на GitHub.',
        );
      }
      if (code == 403 || code == 429) {
        return GitHubPortfolio.unavailable(
          clean,
          'GitHub временно ограничил запросы. Попробуй обновить позже.',
        );
      }
      return GitHubPortfolio.unavailable(
        clean,
        'Не удалось обновить GitHub-портфолио.',
      );
    } catch (_) {
      return GitHubPortfolio.unavailable(
        clean,
        'Не удалось разобрать данные GitHub.',
      );
    }
  }

  Future<GitHubProjectEvidence> _project(
    String owner,
    Map<String, dynamic> repo,
  ) async {
    final name = repo['name'] as String? ?? 'repository';
    final rootNames = await _rootNames(owner, name);
    final topics = (repo['topics'] as List<dynamic>? ?? const <dynamic>[])
        .whereType<String>()
        .toList(growable: false);
    final updated = DateTime.tryParse(repo['pushed_at'] as String? ?? '');

    return GitHubProjectEvidence(
      name: name,
      description: repo['description'] as String? ?? '',
      primaryLanguage: repo['language'] as String? ?? '',
      topics: topics,
      stars: (repo['stargazers_count'] as num?)?.toInt() ?? 0,
      forks: (repo['forks_count'] as num?)?.toInt() ?? 0,
      hasTests: rootNames.contains('tests') || rootNames.contains('test'),
      hasCi: rootNames.contains('.github'),
      hasDocker: rootNames.contains('dockerfile') ||
          rootNames.contains('docker-compose.yml') ||
          rootNames.contains('docker-compose.yaml'),
      hasPackageConfig: rootNames.contains('pyproject.toml') ||
          rootNames.contains('setup.py') ||
          rootNames.contains('requirements.txt') ||
          rootNames.contains('poetry.lock'),
      updatedAt: updated,
    );
  }

  Future<Set<String>> _rootNames(String owner, String repository) async {
    try {
      final response = await _dio.get<dynamic>(
        '/repos/${Uri.encodeComponent(owner)}/${Uri.encodeComponent(repository)}/contents',
      );
      final data = response.data;
      if (data is! List<dynamic>) return const <String>{};
      return data
          .whereType<Map<String, dynamic>>()
          .map((item) => (item['name'] as String? ?? '').toLowerCase())
          .where((name) => name.isNotEmpty)
          .toSet();
    } on DioException {
      return const <String>{};
    }
  }
}
