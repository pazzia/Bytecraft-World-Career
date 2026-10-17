import 'package:bytecraft/features/career/domain/career_dashboard.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('readiness is zero without skills', () {
    expect(CareerDashboardCalculator.readinessFor(const []), 0);
  });

  test('readiness reaches 100 when every target is met', () {
    const skills = [
      CareerSkill(
        id: CareerSkillId.pythonCore,
        title: 'Python Core',
        score: 85,
        target: 85,
      ),
      CareerSkill(
        id: CareerSkillId.testing,
        title: 'Testing',
        score: 90,
        target: 75,
      ),
    ];

    expect(CareerDashboardCalculator.readinessFor(skills), 100);
  });

  test('readiness reflects the average share of role requirements', () {
    const skills = [
      CareerSkill(
        id: CareerSkillId.pythonCore,
        title: 'Python Core',
        score: 42,
        target: 84,
      ),
      CareerSkill(
        id: CareerSkillId.testing,
        title: 'Testing',
        score: 75,
        target: 75,
      ),
    ];

    expect(CareerDashboardCalculator.readinessFor(skills), 75);
    expect(skills.first.gap, 42);
    expect(skills.last.readyForAssessment, isTrue);
  });
}
