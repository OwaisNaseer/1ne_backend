"""
Seeder for chatbots, model assignments, and capabilities.
"""
from sqlalchemy.orm import Session
from decimal import Decimal

from app.core.logging import get_logger
from app.domains.chatbots.models import (
    Chatbot,
    ChatbotModelAssignment,
    ChatbotCapability,
)
from app.llm.config import llm_settings

logger = get_logger(__name__)


def seed_chatbots(db: Session, force: bool = False) -> dict:
    """Seed chatbots, model assignments, and capabilities."""
    chatbots_created = 0
    chatbots_skipped = 0
    models_created = 0
    capabilities_created = 0

    # Get default provider and model from config
    default_provider = llm_settings.DEFAULT_MODEL_PROVIDER
    default_model = llm_settings.DEFAULT_MODEL

    chatbot_data = [
        {
            "slug": "general-teaching-assistant",
            "name": "General Teaching Assistant",
            "description": "A versatile AI assistant for general teaching support, lesson planning, and educational guidance.",
            "category": "free",
            "subject": None,
            "access_level": "free",
            "system_prompt": "You are a helpful and knowledgeable teaching assistant. Provide clear, practical, and engaging educational guidance. Adapt your communication style to be approachable yet professional.",
            "models": [
                {"provider": default_provider, "model_name": default_model, "priority": 0, "is_primary": True},
            ],
            "capabilities": [],
        },
        {
            "slug": "literacy-lab-coach",
            "name": "Literacy Lab Coach",
            "description": "Comprehensive literacy support with text complexity analysis, guided reading strategies, writing feedback, and vocabulary development tools.",
            "category": "subject",
            "subject": "English",
            "access_level": "premium",
            "system_prompt": "You are an expert literacy coach specializing in text complexity analysis, guided reading strategies, writing feedback, and vocabulary development. Provide detailed, actionable guidance to help improve reading and writing skills.",
            "models": [
                {"provider": default_provider, "model_name": default_model, "priority": 0, "is_primary": True},
            ],
            "capabilities": [
                {
                    "capability_key": "text_complexity",
                    "capability_name": "Text Complexity Analysis",
                    "capability_description": "Analyze text complexity, readability scores, and provide insights for instructional leveling.",
                    "capability_category": "analysis",
                    "icon_name": "FileText",
                    "display_order": 1,
                    "is_primary": True,
                    "requires_input_type": "text",
                    "system_prompt_template": """You are a text complexity analysis expert. Analyze the provided text and respond with ONLY a JSON object in this exact format:

{
  "readingLevel": "Beginner|Intermediate|Advanced",
  "complexity": "Simple|Moderate|Complex",
  "wordCount": <number>,
  "sentenceCount": <number>,
  "avgWordsPerSentence": <number>,
  "vocabularyLevel": "Grade X-Y",
  "gradeLevel": "<grade_number>",
  "readabilityScore": <0-100>
}

Calculate readability using standard metrics. Return ONLY the JSON, no other text.""",
                    "processing_mode": "structured",
                },
                {
                    "capability_key": "guided_reading",
                    "capability_name": "Guided Reading Strategies",
                    "capability_description": "Generate guided reading questions, discussion prompts, and comprehension activities.",
                    "capability_category": "instruction",
                    "icon_name": "BookOpen",
                    "display_order": 2,
                    "is_primary": True,
                    "requires_input_type": "text",
                    "system_prompt_template": """You are a guided reading specialist. Create guided reading strategies and respond with ONLY a JSON object:

{
  "beforeReading": ["strategy1", "strategy2", "strategy3"],
  "duringReading": ["strategy1", "strategy2", "strategy3"],
  "afterReading": ["strategy1", "strategy2", "strategy3"],
  "vocabulary": ["term - definition", "term2 - definition2"],
  "comprehensionQuestions": {
    "literal": ["question1?", "question2?"],
    "inferential": ["question1?", "question2?"],
    "evaluative": ["question1?", "question2?"]
  }
}

Provide 3-5 items per category. Return ONLY the JSON, no other text.""",
                    "processing_mode": "structured",
                },
                {
                    "capability_key": "writing_feedback",
                    "capability_name": "Writing Feedback & Rubrics",
                    "capability_description": "Provide detailed writing feedback with rubrics and improvement suggestions.",
                    "capability_category": "feedback",
                    "icon_name": "PenTool",
                    "display_order": 3,
                    "is_primary": True,
                    "requires_input_type": "text",
                    "system_prompt_template": """You are an expert writing coach. Provide writing feedback as ONLY a JSON object:

{
  "strengths": ["strength1", "strength2", "strength3"],
  "areasForImprovement": ["area1", "area2"],
  "suggestions": ["suggestion1", "suggestion2", "suggestion3"],
  "rubricScore": {
    "content": <1-5>,
    "organization": <1-5>,
    "language": <1-5>,
    "conventions": <1-5>
  }
}

Be specific and constructive. Return ONLY the JSON, no other text.""",
                    "processing_mode": "structured",
                },
                {
                    "capability_key": "progress_tracking",
                    "capability_name": "Progress Tracking",
                    "capability_description": "Track student progress and generate progress reports.",
                    "capability_category": "tracking",
                    "icon_name": "ClipboardCheck",
                    "display_order": 4,
                    "is_primary": False,
                    "requires_input_type": "conversation",
                    "system_prompt_template": "You are a progress tracking specialist. Analyze conversation history and provide: 1) Progress summary, 2) Skill development areas, 3) Achievement milestones, 4) Next steps recommendations.",
                    "processing_mode": "structured",
                },
            ],
        },
        {
            "slug": "stem-inquiry-mentor",
            "name": "STEM Inquiry Mentor",
            "description": "NGSS-aligned investigations, engineering design challenges, and scientific method guidance for inquiry-based STEM learning.",
            "category": "subject",
            "subject": "Science",
            "access_level": "premium",
            "system_prompt": "You are an expert STEM inquiry mentor specializing in NGSS-aligned investigations, engineering design challenges, and scientific inquiry guidance. Provide detailed, actionable guidance for inquiry-based STEM learning.",
            "models": [
                {"provider": default_provider, "model_name": default_model, "priority": 0, "is_primary": True},
            ],
            "capabilities": [
                {
                    "capability_key": "ngss_investigation",
                    "capability_name": "NGSS Investigations",
                    "capability_description": "Generate NGSS-aligned investigation plans with phenomena, performance expectations, and assessment strategies.",
                    "capability_category": "investigation",
                    "icon_name": "FlaskConical",
                    "display_order": 1,
                    "is_primary": True,
                    "requires_input_type": "text",
                    "system_prompt_template": """You are an NGSS investigation specialist. Generate a complete NGSS-aligned investigation plan and respond with ONLY a JSON object:

{
  "phenomenon": "<observable phenomenon description>",
  "performanceExpectation": "<NGSS performance expectation code and description>",
  "dci": "<Disciplinary Core Idea description>",
  "sep": ["<Science & Engineering Practice 1>", "<SEP 2>", "<SEP 3>"],
  "ccc": ["<Crosscutting Concept 1>", "<CCC 2>", "<CCC 3>"],
  "investigationPlan": {
    "question": "<research question>",
    "hypothesis": "<testable hypothesis>",
    "materials": ["<material1>", "<material2>", "<material3>"],
    "procedure": ["<step1>", "<step2>", "<step3>", "<step4>", "<step5>"],
    "dataCollection": "<description of how to collect and record data>",
    "analysis": "<description of how to analyze the data>"
  },
  "assessment": {
    "formative": ["<formative assessment 1>", "<formative assessment 2>", "<formative assessment 3>"],
    "summative": "<summative assessment description>"
  }
}

Provide 3-5 items for arrays. Return ONLY the JSON, no other text.""",
                    "processing_mode": "structured",
                },
                {
                    "capability_key": "engineering_design",
                    "capability_name": "Engineering Design",
                    "capability_description": "Create engineering design challenges with constraints, criteria, and design cycle guidance.",
                    "capability_category": "engineering",
                    "icon_name": "Wrench",
                    "display_order": 2,
                    "is_primary": True,
                    "requires_input_type": "text",
                    "system_prompt_template": """You are an engineering design specialist. Generate a complete engineering design challenge and respond with ONLY a JSON object:

{
  "problem": "<engineering problem description>",
  "constraints": ["<constraint1>", "<constraint2>", "<constraint3>", "<constraint4>"],
  "criteria": ["<success criterion1>", "<criterion2>", "<criterion3>", "<criterion4>"],
  "designCycle": {
    "ask": ["<question1>", "<question2>", "<question3>", "<question4>"],
    "imagine": ["<idea1>", "<idea2>", "<idea3>", "<idea4>"],
    "plan": ["<plan step1>", "<plan step2>", "<plan step3>", "<plan step4>"],
    "create": ["<creation step1>", "<creation step2>", "<creation step3>", "<creation step4>"],
    "improve": ["<improvement step1>", "<improvement step2>", "<improvement step3>", "<improvement step4>", "<improvement step5>"]
  },
  "realWorldContext": "<real-world context and connections>",
  "ngssAlignment": ["<NGSS standard 1>", "<NGSS standard 2>", "<NGSS standard 3>", "<NGSS standard 4>"]
}

Provide 4-5 items per design cycle stage. Return ONLY the JSON, no other text.""",
                    "processing_mode": "structured",
                },
                {
                    "capability_key": "inquiry_guidance",
                    "capability_name": "Inquiry Guidance",
                    "capability_description": "Provide inquiry-based learning guidance with questions, hypothesis frameworks, and experimental design.",
                    "capability_category": "guidance",
                    "icon_name": "Brain",
                    "display_order": 3,
                    "is_primary": True,
                    "requires_input_type": "text",
                    "system_prompt_template": """You are an inquiry-based learning specialist. Generate comprehensive inquiry guidance and respond with ONLY a JSON object:

{
  "topic": "<topic name>",
  "questions": [
    {
      "level": "exploratory",
      "question": "<exploratory question>",
      "guidance": "<guidance for this question>"
    },
    {
      "level": "investigative",
      "question": "<investigative question>",
      "guidance": "<guidance for this question>"
    },
    {
      "level": "evaluative",
      "question": "<evaluative question>",
      "guidance": "<guidance for this question>"
    }
  ],
  "hypothesisFramework": {
    "template": "<hypothesis template>",
    "examples": ["<example1>", "<example2>"]
  },
  "experimentalDesign": {
    "variables": "<description of independent, dependent, and controlled variables>",
    "controls": "<description of control groups>",
    "procedure": "<step-by-step procedure>"
  },
  "dataAnalysis": {
    "methods": ["<method1>", "<method2>", "<method3>", "<method4>"],
    "tools": ["<tool1>", "<tool2>", "<tool3>"],
    "interpretation": "<guidance for interpreting results>"
  }
}

Return ONLY the JSON, no other text.""",
                    "processing_mode": "structured",
                },
            ],
        },
    ]

    for chatbot_info in chatbot_data:
        slug = chatbot_info["slug"]
        
        # Check if chatbot exists
        existing_chatbot = db.query(Chatbot).filter(Chatbot.slug == slug).first()

        if existing_chatbot and not force:
            logger.info(f"Chatbot '{slug}' already exists, skipping")
            chatbots_skipped += 1
            chatbot_obj = existing_chatbot
        else:
            if existing_chatbot and force:
                # Delete existing data
                db.query(ChatbotCapability).filter(
                    ChatbotCapability.chatbot_id == existing_chatbot.id
                ).delete()
                db.query(ChatbotModelAssignment).filter(
                    ChatbotModelAssignment.chatbot_id == existing_chatbot.id
                ).delete()
                db.delete(existing_chatbot)
                db.flush()

            # Create chatbot
            chatbot_obj = Chatbot(
                slug=slug,
                name=chatbot_info["name"],
                description=chatbot_info["description"],
                category=chatbot_info["category"],
                subject=chatbot_info["subject"],
                access_level=chatbot_info["access_level"],
                system_prompt=chatbot_info["system_prompt"],
                is_active=True,
            )
            db.add(chatbot_obj)
            db.flush()
            chatbots_created += 1
            logger.info(f"Created chatbot: {slug}")

        # Create model assignments
        for model_info in chatbot_info["models"]:
            existing_model = db.query(ChatbotModelAssignment).filter(
                ChatbotModelAssignment.chatbot_id == chatbot_obj.id,
                ChatbotModelAssignment.provider == model_info["provider"],
                ChatbotModelAssignment.model_name == model_info["model_name"],
            ).first()

            if existing_model and not force:
                continue

            if existing_model and force:
                db.delete(existing_model)
                db.flush()

            assignment = ChatbotModelAssignment(
                chatbot_id=chatbot_obj.id,
                provider=model_info["provider"],
                model_name=model_info["model_name"],
                priority=model_info["priority"],
                is_primary=model_info["is_primary"],
                temperature=Decimal("0.7"),
                max_tokens=2000,
                is_enabled=True,
            )
            db.add(assignment)
            models_created += 1

        # Create capabilities
        for capability_info in chatbot_info["capabilities"]:
            existing_capability = db.query(ChatbotCapability).filter(
                ChatbotCapability.chatbot_id == chatbot_obj.id,
                ChatbotCapability.capability_key == capability_info["capability_key"],
            ).first()

            if existing_capability and not force:
                continue

            if existing_capability and force:
                db.delete(existing_capability)
                db.flush()

            capability = ChatbotCapability(
                chatbot_id=chatbot_obj.id,
                capability_key=capability_info["capability_key"],
                capability_name=capability_info["capability_name"],
                capability_description=capability_info["capability_description"],
                capability_category=capability_info["capability_category"],
                icon_name=capability_info["icon_name"],
                display_order=capability_info["display_order"],
                is_primary=capability_info["is_primary"],
                requires_input_type=capability_info["requires_input_type"],
                system_prompt_template=capability_info["system_prompt_template"],
                processing_mode=capability_info["processing_mode"],
                is_active=True,
            )
            db.add(capability)
            capabilities_created += 1

    db.commit()
    logger.info(
        f"Chatbot seeding complete: {chatbots_created} chatbots created, "
        f"{chatbots_skipped} skipped, {models_created} models assigned, "
        f"{capabilities_created} capabilities created"
    )

    return {
        "chatbots_created": chatbots_created,
        "chatbots_skipped": chatbots_skipped,
        "models_created": models_created,
        "capabilities_created": capabilities_created,
    }
