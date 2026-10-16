import 'package:flutter/material.dart';

import '../../../core/theme/app_spacing.dart';
import '../../../shared/widgets/app_card.dart';
import 'question_renderer.dart';

class UnsupportedRenderer extends QuestionRenderer {
  const UnsupportedRenderer();

  @override
  Widget build(BuildContext context, QuestionContext question) => const AppCard(
        child: Padding(
          padding: EdgeInsets.all(Spacing.sm),
          child: Text(
            'Этот тип задания появится в следующей версии приложения.',
            textAlign: TextAlign.center,
          ),
        ),
      );
}
