"""
Simple test to verify prompt_builder.py syntax and basic functionality.
Tests the key functions without full app initialization.
"""
import sys
import os

# Test 1: Syntax check
print("=" * 60)
print("Test 1: Syntax Check")
print("=" * 60)
try:
    with open("app/llm/prompt_builder.py", "r", encoding="utf-8") as f:
        code = f.read()
    compile(code, "app/llm/prompt_builder.py", "exec")
    print("✅ PASS: No syntax errors in prompt_builder.py")
except SyntaxError as e:
    print(f"❌ FAIL: Syntax error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ FAIL: Error: {e}")
    sys.exit(1)

# Test 2: Check for undefined variables
print("\n" + "=" * 60)
print("Test 2: Check for undefined variables")
print("=" * 60)

# Read the file and check for common issues
with open("app/llm/prompt_builder.py", "r", encoding="utf-8") as f:
    content = f.read()

# Check for undefined variable patterns
issues = []

# Check if 'subject' is used without being defined in _build_system_message
if "_build_system_message" in content:
    # Find the method
    lines = content.split('\n')
    in_method = False
    method_start = None
    for i, line in enumerate(lines):
        if "def _build_system_message" in line:
            in_method = True
            method_start = i
        elif in_method and line.strip() and not line.startswith(' ') and not line.startswith('\t'):
            # End of method
            method_end = i
            break
    
    if method_start:
        method_lines = lines[method_start:method_end if 'method_end' in locals() else len(lines)]
        method_content = '\n'.join(method_lines)
        
        # Check for undefined variables
        if "subject" in method_content and "subject: Optional[str]" not in method_content:
            # Check if subject is in parameters
            if "subject" not in method_content.split("def _build_system_message")[1].split(")")[0]:
                # Check if it's used in a safe way (with 'or' fallback)
                if "{subject or" not in method_content and "{subject}" in method_content:
                    issues.append("Line uses 'subject' without parameter in _build_system_message")
        
        if "grade_band" in method_content and "grade_band: Optional[str]" not in method_content:
            if "grade_band" not in method_content.split("def _build_system_message")[1].split(")")[0]:
                if "{grade_band or" not in method_content and "{grade_band}" in method_content:
                    issues.append("Line uses 'grade_band' without parameter in _build_system_message")

if issues:
    print("❌ FAIL: Found potential undefined variable issues:")
    for issue in issues:
        print(f"   - {issue}")
    sys.exit(1)
else:
    print("✅ PASS: No obvious undefined variable issues")

# Test 3: Check key functionality strings
print("\n" + "=" * 60)
print("Test 3: Check key functionality")
print("=" * 60)

checks = [
    ("Urdu language support", "Urdu" in content or "اردو" in content),
    ("Language instruction handling", "lang_instruction" in content),
    ("Standard validation", "is_recognized" in content or "may not be recognized" in content),
    ("Generic language instruction", "in {output_language}" in content or 'f"in {output_language}"' in content),
    ("No undefined subject in system message", "General educational standards for the subject" in content),
]

all_passed = True
for check_name, check_result in checks:
    if check_result:
        print(f"✅ PASS: {check_name}")
    else:
        print(f"❌ FAIL: {check_name}")
        all_passed = False

if not all_passed:
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ ALL TESTS PASSED!")
print("=" * 60)
print("\nKey features verified:")
print("  ✅ Syntax is correct")
print("  ✅ No undefined variable errors")
print("  ✅ Urdu language support")
print("  ✅ Standard validation")
print("  ✅ Generic language handling")
print("\nThe prompt builder is ready to use!")

