"""
Seed script for 12 core system templates with detailed input/output specifications.
"""
from datetime import datetime
from typing import Dict, Any

from sqlalchemy.orm import Session

from app.models.template import Template, TemplateCategory
from app.models.template_version import TemplateVersion, TemplateVersionStatus


def get_base_input_schema() -> Dict[str, Any]:
    """Get base input schema with universal fields - enhanced for international schools."""
    return {
        "type": "object",
        "properties": {
            "subject": {
                "type": "string",
                "enum": ["english", "math", "science", "social_studies", "steam", "other"],
                "title": "Subject Area",
                "description": "Select the subject area for this lesson/activity. Choose the primary academic discipline that aligns with international curriculum standards (e.g., English Language Arts, Mathematics, Science, Social Studies, or STEAM)."
            },
            "grade": {
                "type": "integer",
                "minimum": 0,
                "maximum": 12,
                "title": "Grade Level",
                "description": "Enter the grade level (0 for Kindergarten/K, 1-12 for grades 1-12). This ensures content is age-appropriate and aligns with international grade-level expectations (e.g., USA Common Core, UK National Curriculum, IB PYP/MYP/DP)."
            },
            "grade_band": {
                "type": "string",
                "enum": ["K-2", "3-5", "6-8", "9-12"],
                "title": "Grade Band (Optional)",
                "description": "Optional: Select a grade band for broader age-group alignment. Useful for multi-grade classrooms or when targeting developmental stages rather than specific grades."
            },
            "topic": {
                "type": "string",
                "title": "Topic or Learning Theme",
                "description": "Enter the specific topic, concept, or theme for this lesson/activity. Be specific and clear (e.g., 'Fractions and Decimals', 'The Water Cycle', 'Persuasive Writing', 'World War II'). This will be the central focus of the generated content."
            },
            "learning_objective": {
                "type": "string",
                "title": "Learning Objective",
                "description": "State the learning objective using SMART criteria (Specific, Measurable, Achievable, Relevant, Time-bound). Example: 'Students will be able to solve multi-step word problems involving fractions and decimals with 80% accuracy.' This should align with international curriculum standards and Bloom's Taxonomy levels."
            },
            "time_duration": {
                "type": "string",
                "title": "Time Duration",
                "description": "Specify the duration for this lesson/activity. Use clear formats like '45 minutes', '1 hour', '2 weeks', '90 minutes'. This helps ensure the generated content is appropriately paced for the available time."
            },
            "time_duration_minutes": {
                "type": "integer",
                "minimum": 5,
                "maximum": 480,
                "title": "Duration in Minutes (Optional)",
                "description": "Optional: Enter the duration in minutes for more precise time allocation. This helps generate content with accurate time estimates for each section."
            },
            "bloom_level": {
                "type": "string",
                "enum": ["Remember", "Understand", "Apply", "Analyze", "Evaluate", "Create", "Understand → Apply", "Analyze → Evaluate"],
                "title": "Bloom's Taxonomy Level",
                "description": "Select the cognitive level(s) from Bloom's Taxonomy that students will engage with. This ensures the content promotes appropriate levels of thinking: Remember (recall facts), Understand (comprehend meaning), Apply (use in new situations), Analyze (examine relationships), Evaluate (make judgments), Create (produce new work). You can select a progression (e.g., 'Understand → Apply') for lessons that build complexity."
            },
            "standard": {
                "type": "string",
                "title": "Educational Standard (Optional)",
                "description": "Optional: Enter specific educational standards to align with (e.g., 'CCSS.MATH.CONTENT.6.EE.A.2', 'UK National Curriculum Year 7', 'IB MYP Criterion A', 'NGSS MS-LS1-1'). This ensures the generated content aligns with recognized international curriculum frameworks."
            },
            "standards_framework": {
                "type": "string",
                "enum": ["CCSS", "UK_NATIONAL", "IB", "NGSS", "CAMBRIDGE", "EDEXCEL", "AQA", "AUSTRALIAN", "CANADIAN", "SINGAPORE", "OTHER"],
                "title": "Standards Framework (Optional)",
                "description": "Optional: Select the primary educational standards framework. This helps ensure content aligns with the appropriate international curriculum system (Common Core State Standards, UK National Curriculum, International Baccalaureate, Next Generation Science Standards, etc.)."
            },
            "output_language": {
                "type": "string",
                "enum": ["English", "Spanish", "French", "German", "Italian", "Portuguese", "Chinese", "Japanese", "Korean", "Russian", "Arabic", "Hindi", "Urdu", "Other"],
                "title": "Output Language",
                "description": "Select the language for the generated content. All headings, instructions, and content will be generated in this language. Choose 'Other' if you need a language not listed and specify it in the 'Language' field below."
            },
            "language": {
                "type": "string",
                "title": "Custom Language (if 'Other' selected)",
                "description": "If you selected 'Other' for Output Language, specify the language here. The system will attempt to generate content in this language."
            },
            "differentiation_needs": {
                "type": "boolean",
                "title": "Include Differentiation Strategies",
                "description": "Check this box if you need specific differentiation strategies included in the generated content. This will add support for struggling learners, advanced learners, English Language Learners, and students with diverse learning styles - essential for international classrooms with diverse student populations."
            },
            "differentiation_notes": {
                "type": "string",
                "title": "Differentiation Notes (Optional)",
                "description": "Optional: Provide specific information about student needs, learning differences, or accommodations required. This helps generate more targeted differentiation strategies (e.g., '3 ELL students at intermediate level', '2 students with ADHD need movement breaks', 'Advanced learners need extension activities')."
            },
            "materials": {
                "type": "string",
                "title": "Available Materials (Optional)",
                "description": "Optional: List the materials, resources, or equipment available for this lesson/activity. Be specific (e.g., 'Whiteboards, markers, calculators, graph paper, access to tablets'). This ensures the generated content uses realistic, available resources."
            },
            "available_materials": {
                "type": "array",
                "items": {"type": "string"},
                "title": "Materials List (Optional)",
                "description": "Optional: Provide a list of available materials as separate items. This is useful when you have a specific inventory of resources."
            },
            "constraints": {
                "type": "string",
                "title": "Constraints or Special Considerations (Optional)",
                "description": "Optional: Note any constraints, limitations, or special considerations for this lesson (e.g., 'No internet access', 'Limited space', 'Students must work in pairs', 'Cultural sensitivity required for diverse backgrounds'). This helps generate content that is practical and appropriate for your specific context."
            }
        }
    }


def get_output_schema_placeholder() -> Dict[str, Any]:
    """Get placeholder output schema describing universal output container."""
    return {
        "type": "object",
        "description": "Universal output container with overview, learning_goals, materials, steps, differentiation, assessment, teacher_notes, bloom_alignment, and optional questions (for assessments) or communication (for communication templates)"
    }


def get_default_model_config() -> Dict[str, Any]:
    """Get default model configuration."""
    return {
        "provider": "openai",
        "model": "gpt-4o-mini",
        "temperature": 0.7,
        "max_tokens": 2000
    }


def get_template_data() -> list[Dict[str, Any]]:
    """Get all 12 template definitions with their versions matching detailed criteria."""
    return [
        {
            # TEMPLATE 1: General Lesson Planner
            "template": {
                "slug": "lesson_planner",
                "name": "General Lesson Planner",
                "description": "Generate comprehensive lesson plans with 4-stage flow, learning intentions, success criteria, and Bloom alignment.",
                "category": "lesson_design",
                "subject_default": None,
                "grade_bands_supported": ["K-2", "3-5", "6-8", "9-12"],
            },
            "version": {
                "input_schema": {
                    **get_base_input_schema(),
                    "properties": {
                        **get_base_input_schema()["properties"],
                    },
                    "required": ["subject", "grade", "topic", "time_duration", "learning_objective", "bloom_level"]
                },
                "prompt_definition": {
                    "description": "Generate a comprehensive, internationally-aligned lesson plan suitable for high-level schools (USA, UK, IB, etc.) with: Lesson Overview, Learning Intentions, Success Criteria, Materials, Lesson Steps (Warmup → Instruction → Activity → Closure), Differentiation, Formative Assessment, Teacher Notes, and Bloom Mapping. Map topic to subject-specific instructional model, align steps with Bloom levels, auto-generate learning intentions and success criteria, build 4-stage lesson flow, add differentiation and exit ticket. Ensure content meets international quality standards, uses research-based pedagogy, and is culturally appropriate for diverse student populations.",
                    "context": "This lesson plan will be used in international schools and high-performing institutions. Content must be academically rigorous, pedagogically sound, and aligned with best practices from leading educational systems worldwide."
                }
            }
        },
        {
            # TEMPLATE 2: Activity Suggestion / Engagement Builder
            "template": {
                "slug": "learning_activity",
                "name": "Activity Suggestion / Engagement Builder",
                "description": "Create quick, engaging learning activities (15 min) with hands-on, discussion, creative, or game options.",
                "category": "lesson_design",
                "subject_default": None,
                "grade_bands_supported": ["K-2", "3-5", "6-8", "9-12"],
            },
            "version": {
                "input_schema": {
                    **get_base_input_schema(),
                    "properties": {
                        **get_base_input_schema()["properties"],
                        "activity_type": {
                            "type": "string",
                            "enum": ["hands_on", "discussion", "creative", "game"],
                            "title": "Activity Type",
                            "description": "Select the type of engagement activity. Hands-on: Physical manipulation and experimentation. Discussion: Collaborative dialogue and debate. Creative: Artistic expression and innovation. Game: Interactive, rule-based learning. Choose the format that best supports your learning objective and student engagement needs."
                        },
                        "materials_available": {
                            "type": "array",
                            "items": {"type": "string"},
                            "title": "Available Materials",
                            "description": "List the specific materials, resources, or equipment available for this activity. Be detailed and specific (e.g., 'Construction paper', 'Markers', 'Scissors', 'Digital tablets with internet access'). This ensures the generated activity uses realistic, available resources suitable for international school contexts."
                        }
                    },
                    "required": ["subject", "grade", "topic", "time_duration", "activity_type", "bloom_level"]
                },
                "prompt_definition": {
                    "description": "Generate a quick, engaging activity suitable for international classrooms with: Activity Title, Learning Goal, Materials Needed, Steps (simple and fast), Differentiation, Assessment Prompt, and Teacher Notes. Ensure the activity promotes active learning, critical thinking, and is appropriate for diverse student populations. Use research-based engagement strategies and align with international pedagogical best practices.",
                    "context": "This activity will be used in international schools. It should be engaging, pedagogically sound, and culturally sensitive."
                }
            }
        },
        {
            # TEMPLATE 3: Multi-Lesson Unit Planner
            "template": {
                "slug": "unit_planner",
                "name": "Multi-Lesson Unit Planner",
                "description": "Design comprehensive unit plans with weekly breakdown, multiple lessons, and assessments.",
                "category": "lesson_design",
                "subject_default": None,
                "grade_bands_supported": ["K-2", "3-5", "6-8", "9-12"],
            },
            "version": {
                "input_schema": {
                    **get_base_input_schema(),
                    "properties": {
                        **get_base_input_schema()["properties"],
                        "duration_weeks": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 12,
                            "title": "Unit Duration (Weeks)",
                            "description": "Enter the number of weeks for this unit plan. This helps structure the learning progression, allocate time for each lesson, and plan assessments appropriately. Typical units range from 2-6 weeks, but can extend to 12 weeks for comprehensive units in international curricula."
                        }
                    },
                    "required": ["subject", "grade", "topic", "duration_weeks", "learning_objective", "bloom_level"]
                },
                "prompt_definition": {
                    "description": "Generate a comprehensive, internationally-aligned unit plan suitable for high-level schools with: Unit Overview, Weekly Breakdown, Learning Intentions, Success Criteria, Activities Weekly Planner, Assessments (Formative + Summative), Differentiation across unit, and Resources Needed. Ensure the unit plan demonstrates coherent learning progression, integrates multiple assessment strategies, and provides opportunities for deep understanding. Align with international curriculum standards and use evidence-based instructional design principles.",
                    "context": "This unit plan will be used in international schools. It must demonstrate academic rigor, coherent learning progression, and alignment with international educational standards."
                }
            }
        },
        {
            # TEMPLATE 4: Formative Assessment Generator
            "template": {
                "slug": "formative_assessment",
                "name": "Formative Assessment Generator",
                "description": "Create quick formative assessments (5 min) with exit tickets, mini quizzes, or discussion checks.",
                "category": "assessment",
                "subject_default": None,
                "grade_bands_supported": ["K-2", "3-5", "6-8", "9-12"],
            },
            "version": {
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "subject": get_base_input_schema()["properties"]["subject"],
                        "grade": get_base_input_schema()["properties"]["grade"],
                        "grade_band": get_base_input_schema()["properties"]["grade_band"],
                        "topic": get_base_input_schema()["properties"]["topic"],
                        "learning_objective": get_base_input_schema()["properties"]["learning_objective"],
                        "bloom_level": get_base_input_schema()["properties"]["bloom_level"],
                        "standard": get_base_input_schema()["properties"]["standard"],
                        "standards_framework": get_base_input_schema()["properties"]["standards_framework"],
                        "output_language": get_base_input_schema()["properties"]["output_language"],
                        "language": get_base_input_schema()["properties"]["language"],
                        "time_duration": get_base_input_schema()["properties"]["time_duration"],
                        "time_duration_minutes": get_base_input_schema()["properties"]["time_duration_minutes"],
                        "assessment_type": {
                            "type": "string",
                            "enum": ["exit_ticket", "mini_quiz", "discussion_check"],
                            "title": "Formative Assessment Type",
                            "description": "Select the type of quick formative assessment. Exit Ticket: Brief end-of-lesson check (1-2 questions, typically 2-3 minutes). Mini Quiz: Short assessment with 3-5 questions (typically 5-10 minutes). Discussion Check: Oral or written response to prompt questions (typically 5-15 minutes). Choose the format that best fits your time constraints and assessment goals for international classroom contexts."
                        },
                        "differentiation_needs": get_base_input_schema()["properties"]["differentiation_needs"],
                        "differentiation_notes": get_base_input_schema()["properties"]["differentiation_notes"]
                    },
                    "required": ["subject", "grade", "topic", "assessment_type", "bloom_level", "time_duration"]
                },
                "prompt_definition": {
                    "description": "Generate a high-quality formative assessment suitable for international classrooms with: Assessment Type, Learning Target, 3-5 Quick Questions, Answer Key, Common Misconceptions, and Differentiation Prompt. Ensure questions assess deep understanding, not just surface knowledge. Include questions at various Bloom's Taxonomy levels. Provide clear answer keys with explanations. Address common misconceptions with pedagogical guidance.",
                    "context": "This assessment will be used in international schools. Questions must be academically rigorous and assess genuine understanding."
                }
            }
        },
        {
            # TEMPLATE 5: Summative Assessment / Test Builder
            "template": {
                "slug": "summative_assessment",
                "name": "Summative Assessment / Test Builder",
                "description": "Generate comprehensive summative assessments and tests with multiple question types.",
                "category": "assessment",
                "subject_default": None,
                "grade_bands_supported": ["K-2", "3-5", "6-8", "9-12"],
            },
            "version": {
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "subject": get_base_input_schema()["properties"]["subject"],
                        "grade": get_base_input_schema()["properties"]["grade"],
                        "grade_band": get_base_input_schema()["properties"]["grade_band"],
                        "topic": get_base_input_schema()["properties"]["topic"],
                        "learning_objective": get_base_input_schema()["properties"]["learning_objective"],
                        "bloom_level": get_base_input_schema()["properties"]["bloom_level"],
                        "standard": get_base_input_schema()["properties"]["standard"],
                        "standards_framework": get_base_input_schema()["properties"]["standards_framework"],
                        "output_language": get_base_input_schema()["properties"]["output_language"],
                        "language": get_base_input_schema()["properties"]["language"],
                        "question_types": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": ["MCQ", "short_answer", "diagram", "essay", "matching"]
                            },
                            "title": "Question Types",
                            "description": "Select the types of questions to include in this summative assessment. MCQ: Multiple choice questions for standardized assessment. Short Answer: Brief written responses requiring specific knowledge. Diagram: Visual representation, labeling, or drawing tasks. Essay: Extended written responses requiring analysis, synthesis, and evaluation. Matching: Pairing related concepts or items. Include multiple types to assess different cognitive skills and align with international assessment standards (e.g., GCSE, A-Level, IB, AP exams)."
                        },
                        "difficulty": {
                            "type": "string",
                            "enum": ["easy", "medium", "hard", "mixed"],
                            "title": "Difficulty Level",
                            "description": "Select the difficulty level for this assessment. Easy: Basic recall and understanding (foundational knowledge). Medium: Application and analysis (intermediate skills). Hard: Evaluation and synthesis (advanced critical thinking). Mixed: Combination of all levels for comprehensive assessment that mirrors international exam formats. Choose based on your learning objectives and international curriculum expectations."
                        },
                        "num_questions": {
                            "type": "integer",
                            "minimum": 5,
                            "maximum": 50,
                            "title": "Number of Questions (Optional)",
                            "description": "Optional: Specify the total number of questions for this assessment. If not specified, the system will generate an appropriate number based on question types and difficulty level. Typical summative assessments range from 10-30 questions depending on question complexity and time allocation."
                        },
                        "time_allocation_minutes": {
                            "type": "integer",
                            "minimum": 15,
                            "maximum": 180,
                            "title": "Time Allocation (Minutes) (Optional)",
                            "description": "Optional: Specify the total time allocated for this assessment in minutes. This helps ensure questions are appropriately scoped and students have adequate time to demonstrate their understanding. Typical summative assessments range from 45-90 minutes, with extended assessments up to 180 minutes for comprehensive exams."
                        }
                    },
                    "required": ["subject", "grade", "topic", "question_types", "bloom_level", "difficulty", "learning_objective"]
                },
                "prompt_definition": {
                    "description": "Generate a comprehensive, internationally-aligned summative assessment suitable for high-level schools with: Test Overview, Questions by Type, Rubric / Marking Guide, Answer Key, and Bloom Categorization. Ensure questions are academically rigorous, assess deep understanding, and align with international assessment standards. Include a detailed marking rubric that clearly distinguishes between performance levels. Questions should cover various cognitive levels and require critical thinking, not just recall.",
                    "context": "This assessment will be used in international schools. It must meet high academic standards and provide clear, fair evaluation criteria."
                }
            }
        },
        {
            # TEMPLATE 6: Behavior / SEL Activity Builder
            "template": {
                "slug": "sel_activity",
                "name": "Behavior / SEL Activity Builder",
                "description": "Create social-emotional learning activities with circle time, reflection, or discussion formats.",
                "category": "behavior",
                "subject_default": None,
                "grade_bands_supported": ["K-2", "3-5", "6-8", "9-12"],
            },
            "version": {
                "input_schema": {
                    **get_base_input_schema(),
                    "properties": {
                        "grade": get_base_input_schema()["properties"]["grade"],
                        "topic": get_base_input_schema()["properties"]["topic"],
                        "activity_type": {
                            "type": "string",
                            "enum": ["circle_time", "reflection", "discussion"],
                            "title": "SEL Activity Type",
                            "description": "Select the format for this social-emotional learning activity. Circle Time: Structured group sharing and community building (common in K-8). Reflection: Individual or small-group introspection and self-awareness. Discussion: Guided dialogue about emotions, relationships, or social situations. Choose the format appropriate for your grade level and cultural context in international schools."
                        },
                        "time_duration": get_base_input_schema()["properties"]["time_duration"],
                        "bloom_level": get_base_input_schema()["properties"]["bloom_level"]
                    },
                    "required": ["grade", "topic", "activity_type", "time_duration", "bloom_level"]
                },
                "prompt_definition": {
                    "description": "Generate a culturally-sensitive SEL activity suitable for international, diverse classrooms with: SEL Activity Title, Purpose, Materials (if needed), Steps, Reflection Questions, and Teacher Notes. Ensure the activity promotes social-emotional learning, cultural awareness, empathy, and inclusivity. Activities should be appropriate for diverse student populations and respect different cultural perspectives.",
                    "context": "This SEL activity will be used in international schools with diverse student populations. It must be culturally sensitive and promote inclusivity."
                }
            }
        },
        {
            # TEMPLATE 7: Classroom Management Plan Generator
            "template": {
                "slug": "classroom_management_plan",
                "name": "Classroom Management Plan Generator",
                "description": "Develop classroom management strategies and behavior intervention plans.",
                "category": "behavior",
                "subject_default": None,
                "grade_bands_supported": ["K-2", "3-5", "6-8", "9-12"],
            },
            "version": {
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "grade": {
                            "type": "integer",
                            "minimum": 0,
                            "maximum": 12,
                            "title": "Grade Level",
                            "description": "Enter the grade level (0 for Kindergarten/K, 1-12 for grades 1-12). This ensures the management strategies are developmentally appropriate and align with international school expectations for student behavior and classroom culture."
                        },
                        "class_size": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 50,
                            "title": "Class Size",
                            "description": "Enter the number of students in your class. This helps generate realistic management strategies, grouping suggestions, and intervention approaches suitable for your specific classroom context in international schools."
                        },
                        "behavior_focus": {
                            "type": "string",
                            "enum": ["low_attention", "noise", "routine"],
                            "title": "Primary Behavior Focus Area",
                            "description": "Select the primary behavior management challenge you want to address. Low Attention: Students struggle to focus or maintain engagement. Noise: Excessive talking or disruptive sounds. Routine: Difficulty following procedures or transitions. This helps generate targeted, evidence-based management strategies appropriate for international, diverse classrooms."
                        },
                        "differentiation_needs": {
                            "type": "boolean",
                            "title": "Include Differentiation Strategies",
                            "description": "Check this box if you need behavior management strategies that account for diverse student needs, cultural differences, and individual learning styles - essential for international classrooms with diverse populations."
                        }
                    },
                    "required": ["grade", "class_size", "behavior_focus"]
                },
                "prompt_definition": {
                    "description": "Generate a comprehensive classroom management plan suitable for international schools with: Classroom Rules, Daily Routines, Reinforcement Strategies, Tiered Interventions, and Parent Communication Note. Ensure the plan is culturally sensitive, promotes positive behavior, and uses evidence-based strategies. Include tiered intervention approaches that respect diverse student needs and cultural backgrounds.",
                    "context": "This management plan will be used in international schools. It must be culturally appropriate and use research-based behavior management strategies."
                }
            }
        },
        {
            # TEMPLATE 8: English Skills Builder (Reading/Writing)
            "template": {
                "slug": "english_task",
                "name": "English Skills Builder (Reading/Writing)",
                "description": "Create English Language Arts tasks focusing on writing, reading, or vocabulary skills.",
                "category": "subject_specific",
                "subject_default": "english",
                "grade_bands_supported": ["K-2", "3-5", "6-8", "9-12"],
            },
            "version": {
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "grade": get_base_input_schema()["properties"]["grade"],
                        "grade_band": get_base_input_schema()["properties"]["grade_band"],
                        "topic": get_base_input_schema()["properties"]["topic"],
                        "learning_objective": get_base_input_schema()["properties"]["learning_objective"],
                        "focus": {
                            "type": "string",
                            "enum": ["writing", "reading", "vocabulary"],
                            "title": "ELA Focus Area",
                            "description": "Select the primary English Language Arts skill focus. Writing: Composition, grammar, and written expression aligned with international literacy standards (CCSS, UK National Curriculum, IB). Reading: Comprehension, analysis, and interpretation of texts (close reading, literary analysis). Vocabulary: Word knowledge, etymology, and language development (academic vocabulary, word roots). Choose based on your learning objectives and international curriculum alignment needs."
                        },
                        "bloom_level": get_base_input_schema()["properties"]["bloom_level"],
                        "standard": get_base_input_schema()["properties"]["standard"],
                        "standards_framework": get_base_input_schema()["properties"]["standards_framework"],
                        "output_language": get_base_input_schema()["properties"]["output_language"],
                        "language": get_base_input_schema()["properties"]["language"],
                        "differentiation_needs": get_base_input_schema()["properties"]["differentiation_needs"],
                        "differentiation_notes": get_base_input_schema()["properties"]["differentiation_notes"],
                        "materials": get_base_input_schema()["properties"]["materials"]
                    },
                    "required": ["grade", "topic", "focus", "bloom_level"]
                },
                "prompt_definition": {
                    "description": "Generate a rigorous English/ELA task aligned with international standards (CCSS, UK National Curriculum, IB, etc.) with: Mini-Lesson Goal, Skill Practice Activity, Guided Examples, Sentence Starters, Student Task, and Assessment Criteria. Ensure the task develops reading, writing, speaking, and listening skills. Include authentic texts and real-world applications. Provide clear assessment criteria that measure genuine literacy skills.",
                    "context": "This ELA task will be used in international schools. It must align with international literacy standards and promote authentic language learning."
                }
            }
        },
        {
            # TEMPLATE 9: Math Problem / Activity Builder
            "template": {
                "slug": "math_task",
                "name": "Math Problem / Activity Builder",
                "description": "Generate math problems and activities with real-world, game, or visual problem types.",
                "category": "subject_specific",
                "subject_default": "math",
                "grade_bands_supported": ["K-2", "3-5", "6-8", "9-12"],
            },
            "version": {
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "grade": get_base_input_schema()["properties"]["grade"],
                        "grade_band": get_base_input_schema()["properties"]["grade_band"],
                        "topic": get_base_input_schema()["properties"]["topic"],
                        "learning_objective": get_base_input_schema()["properties"]["learning_objective"],
                        "problem_type": {
                            "type": "string",
                            "enum": ["real_world", "game", "visual"],
                            "title": "Math Problem Type",
                            "description": "Select the type of mathematical problem or activity. Real World: Authentic, contextual problems that connect math to everyday situations (promotes application and relevance, aligns with international problem-solving standards). Game: Interactive, rule-based mathematical challenges (promotes engagement and strategic thinking). Visual: Problems involving diagrams, graphs, or spatial reasoning (promotes visual-spatial intelligence and geometric thinking). Choose based on your learning objectives and alignment with international mathematics standards (CCSS, UK National Curriculum, IB, Singapore Math, etc.)."
                        },
                        "bloom_level": get_base_input_schema()["properties"]["bloom_level"],
                        "standard": get_base_input_schema()["properties"]["standard"],
                        "standards_framework": get_base_input_schema()["properties"]["standards_framework"],
                        "output_language": get_base_input_schema()["properties"]["output_language"],
                        "language": get_base_input_schema()["properties"]["language"],
                        "differentiation_needs": get_base_input_schema()["properties"]["differentiation_needs"],
                        "differentiation_notes": get_base_input_schema()["properties"]["differentiation_notes"],
                        "materials": get_base_input_schema()["properties"]["materials"]
                    },
                    "required": ["grade", "topic", "problem_type", "bloom_level"]
                },
                "prompt_definition": {
                    "description": "Generate a rigorous math problem/activity aligned with international standards (CCSS, UK National Curriculum, IB, etc.) with: Problem/Activity Title, Student Task, Steps / Game Instructions, Worked Example, and Extension Task. Ensure problems promote mathematical reasoning, problem-solving, and conceptual understanding. Include real-world applications and multiple solution strategies. Provide clear worked examples that demonstrate mathematical thinking processes.",
                    "context": "This math task will be used in international schools. It must align with international mathematics standards and promote deep mathematical understanding."
                }
            }
        },
        {
            # TEMPLATE 10: Science Experiment / Observation
            "template": {
                "slug": "science_investigation",
                "name": "Science Experiment / Observation",
                "description": "Design science experiments and observation activities with materials lists and safety notes.",
                "category": "subject_specific",
                "subject_default": "science",
                "grade_bands_supported": ["K-2", "3-5", "6-8", "9-12"],
            },
            "version": {
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "grade": get_base_input_schema()["properties"]["grade"],
                        "grade_band": get_base_input_schema()["properties"]["grade_band"],
                        "topic": get_base_input_schema()["properties"]["topic"],
                        "learning_objective": get_base_input_schema()["properties"]["learning_objective"],
                        "materials": {
                            "type": "array",
                            "items": {"type": "string"},
                            "title": "Required Materials",
                            "description": "List all materials, equipment, and resources needed for this science experiment or observation. Be specific and include quantities where relevant (e.g., 'Beakers (250ml) - 6', 'Safety goggles - 12 pairs', 'pH test strips - 1 pack', 'Digital microscope', 'Bunsen burner with safety equipment'). Include safety equipment and any special considerations for international school laboratory contexts. Ensure all materials meet international safety standards."
                        },
                        "bloom_level": get_base_input_schema()["properties"]["bloom_level"],
                        "standard": get_base_input_schema()["properties"]["standard"],
                        "standards_framework": get_base_input_schema()["properties"]["standards_framework"],
                        "output_language": get_base_input_schema()["properties"]["output_language"],
                        "language": get_base_input_schema()["properties"]["language"],
                        "time_duration": get_base_input_schema()["properties"]["time_duration"],
                        "time_duration_minutes": get_base_input_schema()["properties"]["time_duration_minutes"],
                        "constraints": get_base_input_schema()["properties"]["constraints"]
                    },
                    "required": ["grade", "topic", "materials", "bloom_level"]
                },
                "prompt_definition": {
                    "description": "Generate a rigorous science experiment/observation aligned with international standards (NGSS, UK National Curriculum, IB, etc.) with: Experiment Title, Aim, Hypothesis, Materials, Procedure, Observation Table, Conclusion Prompt, and Safety Notes. Ensure the experiment promotes scientific inquiry, critical thinking, and authentic scientific practices. Include clear safety considerations and opportunities for students to develop scientific reasoning skills.",
                    "context": "This science experiment will be used in international schools. It must align with international science standards and promote authentic scientific inquiry."
                }
            }
        },
        {
            # TEMPLATE 11: STEAM Maker Activity
            "template": {
                "slug": "steam_project",
                "name": "STEAM Maker Activity",
                "description": "Create STEAM (Science, Technology, Engineering, Arts, Math) maker challenges and projects.",
                "category": "subject_specific",
                "subject_default": "steam",
                "grade_bands_supported": ["K-2", "3-5", "6-8", "9-12"],
            },
            "version": {
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "grade": get_base_input_schema()["properties"]["grade"],
                        "grade_band": get_base_input_schema()["properties"]["grade_band"],
                        "topic": get_base_input_schema()["properties"]["topic"],
                        "learning_objective": get_base_input_schema()["properties"]["learning_objective"],
                        "materials": {
                            "type": "array",
                            "items": {"type": "string"},
                            "title": "Available Materials",
                            "description": "List the materials, tools, and resources available for this STEAM maker activity. Be specific about quantities and capabilities (e.g., 'Cardboard sheets - 20', 'Hot glue guns - 4', 'Arduino kits - 6', '3D printer access', 'Craft supplies assortment', 'Microcontrollers', 'Sensors and actuators'). This ensures the generated challenge is realistic and achievable with your available resources in international school maker spaces, fab labs, or innovation centers."
                        },
                        "bloom_level": get_base_input_schema()["properties"]["bloom_level"],
                        "standard": get_base_input_schema()["properties"]["standard"],
                        "standards_framework": get_base_input_schema()["properties"]["standards_framework"],
                        "output_language": get_base_input_schema()["properties"]["output_language"],
                        "language": get_base_input_schema()["properties"]["language"],
                        "time_duration": get_base_input_schema()["properties"]["time_duration"],
                        "time_duration_minutes": get_base_input_schema()["properties"]["time_duration_minutes"],
                        "differentiation_needs": get_base_input_schema()["properties"]["differentiation_needs"],
                        "differentiation_notes": get_base_input_schema()["properties"]["differentiation_notes"],
                        "constraints": get_base_input_schema()["properties"]["constraints"]
                    },
                    "required": ["grade", "topic", "materials", "bloom_level"]
                },
                "prompt_definition": {
                    "description": "Generate a rigorous STEAM maker activity suitable for international schools with: Challenge Statement, Build Instructions, Constraints, Testing Method, and Reflection. Ensure the activity integrates Science, Technology, Engineering, Arts, and Mathematics authentically. Promote design thinking, creativity, problem-solving, and collaboration. Include clear success criteria and opportunities for iterative improvement.",
                    "context": "This STEAM activity will be used in international schools. It must authentically integrate multiple disciplines and promote 21st-century skills."
                }
            }
        },
        {
            # TEMPLATE 12: Communication Generator
            "template": {
                "slug": "parent_communication",
                "name": "Communication Generator",
                "description": "Generate professional communications for parents, guardians, or other stakeholders.",
                "category": "communication",
                "subject_default": None,
                "grade_bands_supported": ["K-2", "3-5", "6-8", "9-12"],
            },
            "version": {
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "audience": {
                            "type": "string",
                            "enum": ["parents", "guardians", "administrators", "colleagues"],
                            "title": "Target Audience",
                            "description": "Select the primary audience for this communication. Parents/Guardians: Home-school communication requiring clarity and cultural sensitivity for diverse international families. Administrators: Professional updates requiring formal tone and data. Colleagues: Collaborative communication requiring professional but collegial tone. Choose based on your communication purpose and international school context."
                        },
                        "tone": {
                            "type": "string",
                            "enum": ["formal", "friendly", "supportive", "informative"],
                            "title": "Communication Tone",
                            "description": "Select the appropriate tone for this communication. Formal: Professional, structured language for official communications. Friendly: Warm, approachable language while maintaining professionalism. Supportive: Empathetic, encouraging language for sensitive topics. Informative: Clear, factual language for updates and announcements. Consider cultural communication styles in international school contexts."
                        },
                        "topic": {
                            "type": "string",
                            "title": "Communication Topic",
                            "description": "Enter the main topic or subject of this communication. Be clear and specific (e.g., 'Upcoming Science Fair', 'Student Progress Update', 'Field Trip Permission', 'Curriculum Changes'). This helps generate focused, appropriate content for your international school audience."
                        },
                        "grade": {
                            "type": "integer",
                            "minimum": 0,
                            "maximum": 12,
                            "title": "Grade Level",
                            "description": "Enter the grade level (0 for Kindergarten/K, 1-12 for grades 1-12) relevant to this communication. This ensures the language and content are age-appropriate and relevant for the target audience in international school contexts."
                        }
                    },
                    "required": ["audience", "tone", "topic", "grade"]
                },
                "prompt_definition": {
                    "description": "Generate a professional, culturally-sensitive communication suitable for international school contexts with: Subject Line, Message Body, Key Details, Call to Action, and Optional Attachments note. Ensure the communication is clear, respectful, and appropriate for diverse parent/guardian populations. Use professional tone while remaining accessible. Consider cultural differences in communication styles.",
                    "context": "This communication will be used in international schools with diverse parent/guardian populations. It must be professional, clear, and culturally sensitive."
                }
            }
        },
    ]


def seed_templates(db: Session, force: bool = False) -> Dict[str, int]:
    """
    Seed the 12 core system templates.
    
    Args:
        db: Database session
        force: If True, update existing templates. If False, skip existing ones (idempotent).
    
    Returns:
        Dictionary with counts of created/updated templates and versions
    """
    templates_data = get_template_data()
    created_templates = 0
    created_versions = 0
    skipped_templates = 0
    skipped_versions = 0
    
    for item in templates_data:
        template_data = item["template"]
        version_data = item["version"]
        
        # Check if template exists
        existing_template = db.query(Template).filter(Template.slug == template_data["slug"]).first()
        
        if existing_template:
            if force:
                # Update existing template
                for key, value in template_data.items():
                    # Convert enum to value if needed
                    if hasattr(value, 'value') and hasattr(value, 'name'):
                        value = value.value
                    setattr(existing_template, key, value)
                existing_template.is_system_template = True
                existing_template.is_active = True
                db.flush()
                template = existing_template
            else:
                # Skip existing template (idempotent)
                skipped_templates += 1
                template = existing_template
        else:
            # Create new template
            # Convert enum values to their string values for SQLAlchemy
            template_dict = {}
            for key, value in template_data.items():
                # Check if it's an enum by checking for 'value' and 'name' attributes
                if hasattr(value, 'value') and hasattr(value, 'name') and not isinstance(value, str):
                    template_dict[key] = value.value
                else:
                    template_dict[key] = value
            # Debug: print category value
            if 'category' in template_dict:
                from app.core.logging import get_logger
                logger = get_logger(__name__)
                logger.debug(f"Category value being set: {template_dict['category']} (type: {type(template_dict['category'])})")
            
            template = Template(
                **template_dict,
                is_system_template=True,
                is_active=True
            )
            db.add(template)
            db.flush()
            created_templates += 1
        
        # Check if version exists
        existing_version = db.query(TemplateVersion).filter(
            TemplateVersion.template_id == template.id,
            TemplateVersion.version == 1
        ).first()
        
        if existing_version:
            if force:
                # Update existing version
                for key, value in version_data.items():
                    if key == "input_schema":
                        existing_version.input_schema = value
                    elif key == "prompt_definition":
                        existing_version.prompt_definition = value
                existing_version.status = TemplateVersionStatus.PUBLISHED.value
                existing_version.output_schema = get_output_schema_placeholder()
                existing_version.model_config = get_default_model_config()
                if not existing_version.published_at:
                    existing_version.published_at = datetime.utcnow()
                db.flush()
            else:
                skipped_versions += 1
        else:
            # Create new version
            version = TemplateVersion(
                template_id=template.id,
                version=1,
                status=TemplateVersionStatus.PUBLISHED.value,
                input_schema=version_data["input_schema"],
                output_schema=get_output_schema_placeholder(),
                prompt_definition=version_data["prompt_definition"],
                model_config=get_default_model_config(),
                published_at=datetime.utcnow()
            )
            db.add(version)
            created_versions += 1
    
    db.commit()
    
    return {
        "templates_created": created_templates,
        "templates_skipped": skipped_templates,
        "versions_created": created_versions,
        "versions_skipped": skipped_versions
    }
