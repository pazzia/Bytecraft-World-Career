class LeaderboardEntry {
  const LeaderboardEntry({
    required this.userId,
    required this.displayName,
    required this.weeklyXp,
    required this.rank,
  });

  final String userId;
  final String displayName;
  final int weeklyXp;
  final int rank;
}

class League {
  const League({
    required this.id,
    required this.title,
    required this.entries,
    required this.endsAt,
  });

  final String id;
  final String title;
  final List<LeaderboardEntry> entries;
  final DateTime endsAt;
}

/// Weekly leagues live on the backend; the client only reads them and
/// reports XP through sync.
abstract interface class LeaderboardRepository {
  Future<League?> currentLeague(String userId);
}
