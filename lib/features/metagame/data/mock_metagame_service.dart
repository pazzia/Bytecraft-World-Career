import '../domain/metagame.dart';

class MockMetaGameService implements MetaGameService {
  const MockMetaGameService();

  static const Map<String, CompanyDepartment> _mapping = {
    'python': CompanyDepartment.backend,
    'sql': CompanyDepartment.database,
    'javascript': CompanyDepartment.frontend,
    'algorithms': CompanyDepartment.performance,
    'ai': CompanyDepartment.ai,
  };

  @override
  CompanyDepartment departmentFor(String courseId) =>
      _mapping[courseId] ?? CompanyDepartment.backend;

  @override
  Future<CompanyState> loadCompany() async => CompanyState(
        name: 'My Startup',
        departments: [
          for (final department in CompanyDepartment.values)
            DepartmentState(department: department, level: 0),
        ],
      );
}
