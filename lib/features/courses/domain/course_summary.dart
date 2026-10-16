enum CourseAvailability { available, comingSoon }

/// Catalog entry used on the language selection screen.
class CourseSummary {
  const CourseSummary({
    required this.id,
    required this.title,
    required this.language,
    required this.icon,
    required this.availability,
    this.description = '',
  });

  final String id;
  final String title;
  final String language;
  final String icon;
  final String description;
  final CourseAvailability availability;

  bool get isAvailable => availability == CourseAvailability.available;
}
