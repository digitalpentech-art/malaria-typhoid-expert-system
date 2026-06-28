import sys
import os

# Add the project directory to sys.path so imports work correctly
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app import create_app, db
from app.models import Symptom, Rule, Diagnosis
from app.services.inference_engine import InferenceEngine

app = create_app()

def test_inference():
    with app.app_context():
        print("--- Starting Verification ---")
        
        # 1. Verify Data Loading
        symptoms_count = Symptom.query.count()
        rules_count = Rule.query.count()
        print(f"Symptoms loaded: {symptoms_count}")
        print(f"Rules loaded: {rules_count}")
        
        if symptoms_count == 0 or rules_count == 0:
            print("FAILED: Data not loaded correctly.")
            return

        # 2. Test Malaria Case
        # Malaria symptoms: Fever, Chills, Sweating, Headache, Muscle Pain
        # We'll provide: Fever, Chills, Sweating
        fever = Symptom.query.filter_by(name='Fever').first()
        chills = Symptom.query.filter_by(name='Chills').first()
        sweating = Symptom.query.filter_by(name='Sweating').first()
        
        print("\nTesting Malaria Case (Fever, Chills, Sweating)...")
        engine = InferenceEngine([fever.id, chills.id, sweating.id])
        result, explanation, matches = engine.evaluate()
        print(f"Result: {result}")
        print(f"Explanation: {explanation}")
        
        if result == 'Malaria':
            print("SUCCESS: Malaria case correctly identified.")
        else:
            print(f"FAILED: Expected Malaria, got {result}")

        # 3. Test Typhoid Case
        # Typhoid symptoms: Fever, Abdominal Pain, Loss of Appetite, Weakness, Diarrhea
        # We'll provide: Fever, Abdominal Pain, Loss of Appetite
        abdominal_pain = Symptom.query.filter_by(name='Abdominal Pain').first()
        loss_appetite = Symptom.query.filter_by(name='Loss of Appetite').first()
        
        print("\nTesting Typhoid Case (Fever, Abdominal Pain, Loss of Appetite)...")
        engine = InferenceEngine([fever.id, abdominal_pain.id, loss_appetite.id])
        result, explanation, matches = engine.evaluate()
        print(f"Result: {result}")
        print(f"Explanation: {explanation}")
        
        if result == 'Typhoid':
            print("SUCCESS: Typhoid case correctly identified.")
        else:
            print(f"FAILED: Expected Typhoid, got {result}")

        # 4. Test Co-infection Case
        # Combination: Malaria symptoms + Typhoid symptoms
        # Malaria: Fever, Chills, Sweating, Headache, Muscle Pain
        # Typhoid: Fever, Abdominal Pain, Loss of Appetite, Weakness, Diarrhea
        # Total unique: Fever, Chills, Sweating, Headache, Muscle Pain, Abdominal Pain, Loss of Appetite, Weakness, Diarrhea (9)
        # Rule requires 6
        all_malaria = [fever.id, chills.id, sweating.id, Symptom.query.filter_by(name='Headache').first().id, Symptom.query.filter_by(name='Muscle Pain').first().id]
        all_typhoid = [fever.id, abdominal_pain.id, loss_appetite.id, Symptom.query.filter_by(name='Weakness').first().id, Symptom.query.filter_by(name='Diarrhea').first().id]
        combined_ids = list(set(all_malaria + all_typhoid))

        print("\nTesting Co-infection Case (Combined symptoms)...")
        engine = InferenceEngine(combined_ids)
        result, explanation, matches = engine.evaluate()
        print(f"Result: {result}")
        print(f"Explanation: {explanation}")

        if result == 'Co-infection':
            print("SUCCESS: Co-infection case correctly identified.")
        else:
            print(f"FAILED: Expected Co-infection, got {result}")

        print("\n--- Verification Finished ---")

if __name__ == '__main__':
    test_inference()
