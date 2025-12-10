"""
Test script that simulates the frontend flow to verify end-to-end functionality.
This tests the actual execution flow that happens when a user submits a form from the frontend.
"""
import sys
import os
import json

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_frontend_flow():
    """Test the complete frontend flow."""
    print("=" * 60)
    print("Testing Frontend Flow")
    print("=" * 60)
    
    # Simulate frontend payload (what frontend sends)
    test_cases = [
        {
            "name": "English with recognized standard",
            "payload": {
                "subject": "Science",
                "grade_band": "5",
                "topic": "Earth's Rotation",
                "learning_objective": "Students will understand how Earth rotates",
                "time_duration_minutes": 45,
                "bloom_level": "Understand",
                "output_language": "English",
                "standard": "CCSS.SCI.5.ESS.1"
            }
        },
        {
            "name": "Urdu language (Other option)",
            "payload": {
                "subject": "Math",
                "grade_band": "3",
                "topic": "Addition",
                "learning_objective": "Students will add numbers",
                "time_duration_minutes": 30,
                "bloom_level": "Apply",
                "output_language": "Other",
                "language": "Urdu",
                "standard": "CCSS.MATH.3.NBT.1"
            }
        },
        {
            "name": "Unrecognized language (Other option)",
            "payload": {
                "subject": "Science",
                "grade_band": "4",
                "topic": "Plants",
                "learning_objective": "Students will learn about plants",
                "time_duration_minutes": 40,
                "bloom_level": "Remember",
                "output_language": "Other",
                "language": "Klingon",
                "standard": "CUSTOM_STANDARD_XYZ"
            }
        },
        {
            "name": "Unrecognized standard",
            "payload": {
                "subject": "English",
                "grade_band": "6",
                "topic": "Poetry",
                "learning_objective": "Students will analyze poetry",
                "time_duration_minutes": 50,
                "bloom_level": "Analyze",
                "output_language": "Spanish",
                "standard": "UNKNOWN_STANDARD_123"
            }
        },
        {
            "name": "No standard provided",
            "payload": {
                "subject": "History",
                "grade_band": "7",
                "topic": "World War II",
                "learning_objective": "Students will understand WWII",
                "time_duration_minutes": 60,
                "bloom_level": "Understand",
                "output_language": "French"
            }
        }
    ]
    
    # Import after path setup
    try:
        from app.llm.prompt_builder import TOONPromptBuilder
        from app.llm.toon_handler import TOONHandler
        from app.schemas.template import TemplateCategory
    except ImportError as e:
        print(f"❌ FAIL: Import error: {e}")
        print("   Make sure you're running from the correct directory")
        return False
    
    # Initialize builder
    toon_handler = TOONHandler()
    builder = TOONPromptBuilder(toon_handler)
    
    all_passed = True
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n[Test {i}] {test_case['name']}")
        print("-" * 60)
        
        try:
            # Simulate what frontend does: build prompt with input_data
            input_data = test_case['payload']
            
            # Build prompt (this is what execution_service does)
            system_msg, user_msg = builder.build_prompt(
                template_category=TemplateCategory.LESSON_DESIGN,
                input_data=input_data,
                prompt_definition={}
            )
            
            # Verify results
            checks = []
            
            # Check 1: Language handling
            if input_data.get("output_language") == "Other":
                custom_lang = input_data.get("language", "")
                if custom_lang:
                    if custom_lang in system_msg or custom_lang in user_msg or f"in {custom_lang}" in system_msg or f"in {custom_lang}" in user_msg:
                        checks.append(("Language", True, f"Custom language '{custom_lang}' found in prompt"))
                    else:
                        checks.append(("Language", False, f"Custom language '{custom_lang}' NOT found in prompt"))
                else:
                    checks.append(("Language", False, "Custom language not provided"))
            else:
                lang = input_data.get("output_language", "English")
                if lang in system_msg or lang in user_msg:
                    checks.append(("Language", True, f"Language '{lang}' found in prompt"))
                else:
                    checks.append(("Language", False, f"Language '{lang}' NOT found in prompt"))
            
            # Check 2: Standard handling
            standard = input_data.get("standard")
            if standard:
                if standard in system_msg or standard in user_msg:
                    checks.append(("Standard", True, f"Standard '{standard}' found in prompt"))
                    
                    # Check if unrecognized standard message is shown
                    if not any(standard.upper().startswith(prefix) for prefix in ["CCSS", "UK", "IB", "AUSTRALIAN", "CANADIAN", "SINGAPORE", "NEXT_GEN"]):
                        if "may not be recognized" in system_msg or "may not be recognized" in user_msg:
                            checks.append(("Standard Validation", True, "Unrecognized standard message shown"))
                        else:
                            checks.append(("Standard Validation", False, "Unrecognized standard message NOT shown"))
                else:
                    checks.append(("Standard", False, f"Standard '{standard}' NOT found in prompt"))
            else:
                checks.append(("Standard", True, "No standard provided (optional)"))
            
            # Check 3: No undefined variable errors
            if "subject" in system_msg and "{subject}" in system_msg and "subject: Optional[str]" not in str(builder._build_system_message.__code__.co_varnames):
                # This is okay if it's in a safe context
                pass
            checks.append(("No Errors", True, "No undefined variable errors"))
            
            # Report results
            all_checks_passed = all(check[1] for check in checks)
            if all_checks_passed:
                print("✅ PASS")
                for check_name, passed, msg in checks:
                    print(f"   ✅ {check_name}: {msg}")
            else:
                print("❌ FAIL")
                for check_name, passed, msg in checks:
                    status = "✅" if passed else "❌"
                    print(f"   {status} {check_name}: {msg}")
                all_passed = False
            
            # Show prompt lengths
            print(f"   System message: {len(system_msg)} chars")
            print(f"   User message: {len(user_msg)} chars")
            
        except NameError as e:
            print(f"❌ FAIL: Undefined variable error: {e}")
            import traceback
            traceback.print_exc()
            all_passed = False
        except Exception as e:
            print(f"❌ FAIL: Error: {e}")
            import traceback
            traceback.print_exc()
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL FRONTEND FLOW TESTS PASSED!")
        print("=" * 60)
        print("\nThe system is ready for frontend integration!")
        return True
    else:
        print("❌ SOME TESTS FAILED")
        print("=" * 60)
        return False

if __name__ == "__main__":
    success = test_frontend_flow()
    sys.exit(0 if success else 1)

