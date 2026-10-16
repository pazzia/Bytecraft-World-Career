import '../../../core/time/clock.dart';
import '../domain/leaderboard.dart';

/// Static league for UI development until the backend exists.
class MockLeaderboardRepository implements LeaderboardRepository {
  const MockLeaderboardRepository(this._clock);

  static const Duration _leagueLength = Duration(days: 7);

  final Clock _clock;

  @override
  Future<League?> currentLeague(String userId) async => League(
        id: 'bronze',
        title: 'Бронзовая лига',
        endsAt: _clock.now().add(_leagueLength),
        entries: [
          const LeaderboardEntry(
            userId: 'bot_1',
            displayName: 'Ada',
            weeklyXp: 420,
            rank: 1,
          ),
          const LeaderboardEntry(
            userId: 'bot_2',
            displayName: 'Linus',
            weeklyXp: 310,
            rank: 2,
          ),
          LeaderboardEntry(
            userId: userId,
            displayName: 'Вы',
            weeklyXp: 0,
            rank: 3,
          ),
        ],
      );
}
