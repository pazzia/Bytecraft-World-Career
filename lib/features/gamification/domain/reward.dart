/// A bundle of currencies granted to the player.
class Reward {
  const Reward({this.xp = 0, this.coins = 0});

  static const Reward none = Reward();

  final int xp;
  final int coins;

  bool get isEmpty => xp == 0 && coins == 0;

  Reward operator +(Reward other) =>
      Reward(xp: xp + other.xp, coins: coins + other.coins);

  @override
  bool operator ==(Object other) =>
      other is Reward && other.xp == xp && other.coins == coins;

  @override
  int get hashCode => Object.hash(xp, coins);

  @override
  String toString() => 'Reward(xp: $xp, coins: $coins)';
}
