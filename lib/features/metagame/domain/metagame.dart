/// Departments of the player's virtual IT company.
enum CompanyDepartment {
  frontend,
  backend,
  database,
  ai,
  infrastructure,
  security,
  performance,
}

class DepartmentState {
  const DepartmentState({required this.department, required this.level});

  final CompanyDepartment department;
  final int level;
}

class CompanyState {
  const CompanyState({required this.name, required this.departments});

  final String name;
  final List<DepartmentState> departments;
}

/// Meta-game port: learning progress upgrades company departments.
/// Kept separate from the Level Engine; it only reads progress.
abstract interface class MetaGameService {
  /// Which department a course (or topic) upgrades.
  CompanyDepartment departmentFor(String courseId);

  Future<CompanyState> loadCompany();
}
