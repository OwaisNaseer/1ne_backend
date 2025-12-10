"""
Test script to verify prompt_builder.py works correctly with all recent changes.
Tests:
1. Language handling (including Urdu and unrecognized languages)
2. Standard validation
3. No undefined variable errors
"""
import sys
import os

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.llm.prompt_builder import TOONPromptBuilder
from app.llm.toon_handler import TOONHandler
from app.schemas.template import TemplateCategory

def test_prompt_builder():
    """Test prompt builder with various scenarios."""
    print("=" * 60)
    print("Testing Prompt Builder")
    print("=" * 60)
    
    # Initialize builder
    toon_handler = TOONHandler()
    builder = TOONPromptBuilder(toon_handler)
    
    # Test 1: English language (standard)
    print("\n[Test 1] English language (standard)")
    print("-" * 60)
    try:
        input_data = {
            "subject": "Science",
            "grade_band": "5",
            "topic": "Earth's Rotation",
            "learning_objective": "Students will understand rotation",
            "time_duration_minutes": 45,
            "bloom_level": "Understand",
            "output_language": "English"
        }
        system_msg, user_msg = builder.build_prompt(
            template_category=TemplateCategory.LESSON_DESIGN,
            input_data=input_data,
            prompt_definition={}
        )
        print("✅ PASS: English language prompt built successfully")
        print(f"   System message length: {len(system_msg)} chars")
        print(f"   User message length: {len(user_msg)} chars")
    except Exception as e:
        print(f"❌ FAIL: {e}")
        return False
    
    # Test 2: Urdu language (unrecognized but should work)
    print("\n[Test 2] Urdu language (unrecognized)")
    print("-" * 60)
    try:
        input_data = {
            "subject": "Science",
            "grade_band": "5",
            "topic": "Earth's Rotation",
            "learning_objective": "Students will understand rotation",
            "time_duration_minutes": 45,
            "bloom_level": "Understand",
            "output_language": "Other",
            "language": "Urdu"
        }
        system_msg, user_msg = builder.build_prompt(
            template_category=TemplateCategory.LESSON_DESIGN,
            input_data=input_data,
            prompt_definition={}
        )
        print("✅ PASS: Urdu language prompt built successfully")
        assert "Urdu" in system_msg or "اردو" in system_msg or "in Urdu" in system_msg
        print("   ✅ Urdu language instruction found in prompt")
    except Exception as e:
        print(f"❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 3: Unrecognized language (should still work)
    print("\n[Test 3] Unrecognized language (e.g., 'Klingon')")
    print("-" * 60)
    try:
        input_data = {
            "subject": "Science",
            "grade_band": "5",
            "topic": "Earth's Rotation",
            "learning_objective": "Students will understand rotation",
            "time_duration_minutes": 45,
            "bloom_level": "Understand",
            "output_language": "Other",
            "language": "Klingon"
        }
        system_msg, user_msg = builder.build_prompt(
            template_category=TemplateCategory.LESSON_DESIGN,
            input_data=input_data,
            prompt_definition={}
        )
        print("✅ PASS: Unrecognized language prompt built successfully")
        assert "Klingon" in system_msg or "in Klingon" in system_msg
        print("   ✅ Klingon language instruction found in prompt")
    except Exception as e:
        print(f"❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 4: Recognized standard
    print("\n[Test 4] Recognized standard (CCSS)")
    print("-" * 60)
    try:
        input_data = {
            "subject": "Science",
            "grade_band": "5",
            "topic": "Earth's Rotation",
            "learning_objective": "Students will understand rotation",
            "time_duration_minutes": 45,
            "bloom_level": "Understand",
            "output_language": "English",
            "standard": "CCSS.MATH.5.NBT.1"
        }
        system_msg, user_msg = builder.build_prompt(
            template_category=TemplateCategory.LESSON_DESIGN,
            input_data=input_data,
            prompt_definition={}
        )
        print("✅ PASS: Recognized standard prompt built successfully")
        assert "CCSS" in system_msg or "CCSS" in user_msg
        print("   ✅ Standard found in prompt")
    except Exception as e:
        print(f"❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 5: Unrecognized standard (should show message)
    print("\n[Test 5] Unrecognized standard")
    print("-" * 60)
    try:
        input_data = {
            "subject": "Science",
            "grade_band": "5",
            "topic": "Earth's Rotation",
            "learning_objective": "Students will understand rotation",
            "time_duration_minutes": 45,
            "bloom_level": "Understand",
            "output_language": "English",
            "standard": "CUSTOM_STANDARD_XYZ"
        }
        system_msg, user_msg = builder.build_prompt(
            template_category=TemplateCategory.LESSON_DESIGN,
            input_data=input_data,
            prompt_definition={}
        )
        print("✅ PASS: Unrecognized standard prompt built successfully")
        assert "may not be recognized" in system_msg or "may not be recognized" in user_msg
        print("   ✅ Unrecognized standard message found in prompt")
    except Exception as e:
        print(f"❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 6: No undefined variable errors
    print("\n[Test 6] No undefined variable errors")
    print("-" * 60)
    try:
        input_data = {
            "subject": "Math",
            "grade_band": "3",
            "topic": "Addition",
            "learning_objective": "Students will add numbers",
            "time_duration_minutes": 30,
            "bloom_level": "Apply",
            "output_language": "Spanish",
            "standard": "UNKNOWN_STANDARD"
        }
        system_msg, user_msg = builder.build_prompt(
            template_category=TemplateCategory.LESSON_DESIGN,
            input_data=input_data,
            prompt_definition={}
        )
        print("✅ PASS: No undefined variable errors")
        print(f"   System message length: {len(system_msg)} chars")
        print(f"   User message length: {len(user_msg)} chars")
    except NameError as e:
        print(f"❌ FAIL: Undefined variable error: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = test_prompt_builder()
    sys.exit(0 if success else 1)

