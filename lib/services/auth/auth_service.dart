class AuthUser {
  const AuthUser({required this.id, required this.isAnonymous, this.email});

  final String id;
  final bool isAnonymous;
  final String? email;
}

/// Account port. MVP is fully anonymous/local; a Firebase Auth (or own
/// backend) adapter will link the local user id to a real account.
abstract interface class AuthService {
  Future<AuthUser> currentUser();

  Future<AuthUser> linkAccount({required String email});

  Future<void> signOut();
}

class LocalAnonymousAuthService implements AuthService {
  LocalAnonymousAuthService(this._userIdProvider);

  final Future<String> Function() _userIdProvider;

  @override
  Future<AuthUser> currentUser() async =>
      AuthUser(id: await _userIdProvider(), isAnonymous: true);

  @override
  Future<AuthUser> linkAccount({required String email}) async =>
      throw UnsupportedError('Account linking requires the backend');

  @override
  Future<void> signOut() async {}
}
