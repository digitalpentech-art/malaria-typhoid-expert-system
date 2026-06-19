from app.models import Rule, Symptom, Recommendation

class InferenceEngine:
    def __init__(self, user_symptom_ids):
        self.user_symptom_ids = set(user_symptom_ids)
        self.rules = Rule.query.order_by(Rule.priority.desc()).all()

    def evaluate(self):
        """
        Perform forward chaining to find the best matching rule.
        Returns (conclusion, explanation, matching_symptoms)
        """
        best_match = None
        max_overlap = 0
        explanation = ""
        matching_symptoms = []

        for rule in self.rules:
            conditions = rule.get_conditions()
            required_symptom_ids = set(conditions.get('symptom_ids', []))
            min_count = conditions.get('min_count', len(required_symptom_ids))

            # Intersection of user symptoms and rule's required symptoms
            overlap_ids = self.user_symptom_ids.intersection(required_symptom_ids)
            overlap_count = len(overlap_ids)

            if overlap_count >= min_count:
                # Rule fires
                if overlap_count > max_overlap:
                    max_overlap = overlap_count
                    best_match = rule
                    matching_symptoms = list(overlap_ids)

        if best_match:
            symptom_names = [Symptom.query.get(sid).name for sid in matching_symptoms]
            explanation = f"Diagnosis '{best_match.conclusion}' was reached because you reported the following symptoms: {', '.join(symptom_names)}. "
            explanation += f"This matches the rule '{best_match.rule_name}' which requires at least {best_match.get_conditions().get('min_count')} matching symptoms."
            return best_match.conclusion, explanation, matching_symptoms

        return "Unknown", "No specific diagnosis could be determined from the provided symptoms. Please consult a medical professional.", []

    @staticmethod
    def get_advice(diagnosis_result):
        recommendation = Recommendation.query.filter_by(diagnosis_result=diagnosis_result).first()
        if recommendation:
            return recommendation.advice_text
        return "Please visit the nearest hospital for a proper medical examination."
