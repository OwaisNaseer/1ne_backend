"""
Seed script for core system templates with detailed input/output specifications.
"""
from datetime import datetime
from typing import Dict, Any

from sqlalchemy.orm import Session

from app.models.template import Template, TemplateCategory
from app.models.template_version import TemplateVersion, TemplateVersionStatus


def get_default_model_config() -> Dict[str, Any]:
    """Get default model configuration."""
    return {
        "provider": "openai",
        "model": "gpt-4o-mini",
        "temperature": 0.7,
        "max_tokens": 2000
    }


def get_template_data() -> list[Dict[str, Any]]:
    """Get all template definitions with their versions matching detailed criteria."""
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
                    "type": "object",
                    "properties": {
                        "subject": {
                            "type": "string",
                            "enum": ["english", "math", "science", "social_studies", "steam", "other"],
                            "title": "Subject",
                            "description": "Primary subject for this lesson (e.g. english, math, science)."
                        },
                        "grade": {
                            "type": "integer",
                            "minimum": 0,
                            "maximum": 12,
                            "title": "Grade",
                            "description": "Numeric grade level (0 for Kindergarten, 1–12 for grades 1–12)."
                        },
                        "topic": {
                            "type": "string",
                            "title": "Topic",
                            "description": "Short description of the lesson topic or focus."
                        },
                        "learning_objective": {
                            "type": "string",
                            "title": "Learning Objective",
                            "description": "Single clear objective for what students will know or be able to do."
                        },
                        "time_duration_minutes": {
                            "type": "integer",
                            "minimum": 5,
                            "maximum": 480,
                            "title": "Duration (minutes)",
                            "description": "Total lesson time in minutes."
                        },
                        "bloom_level": {
                            "type": "string",
                            "title": "Bloom Level",
                            "description": "Primary Bloom level for the lesson (e.g. Analyze, Apply, Create)."
                        },
                        "standard": {
                            "type": "string",
                            "title": "Standard",
                            "description": "Optional curriculum standard identifier (e.g. RL.8.2)."
                        },
                        "differentiation_needs": {
                            "type": "boolean",
                            "title": "Include Differentiation",
                            "description": "Whether to include specific differentiation suggestions."
                        },
                        "materials": {
                            "type": "string",
                            "title": "Materials",
                            "description": "Brief description of key materials (e.g. 'Printed short story, projector')."
                        },
                        "constraints": {
                            "type": "string",
                            "title": "Constraints",
                            "description": "Any important constraints or special considerations (e.g. mixed reading levels)."
                        }
                    },
                    "required": [
                        "subject",
                        "grade",
                        "topic",
                        "learning_objective",
                        "time_duration_minutes",
                        "bloom_level"
                    ]
                },
                "output_schema": {
                    "type": "object",
                    "title": "LessonPlannerOutput",
                    "required": [
                        "title",
                        "overview",
                        "learning_objectives",
                        "lesson_flow",
                        "assessment",
                        "bloom_alignment"
                    ],
                    "properties": {
                        "title": {"type": "string", "title": "Lesson Title"},
                        "overview": {"type": "string", "title": "Overview"},
                        "learning_objectives": {
                            "type": "array",
                            "title": "Learning Objectives",
                            "items": {"type": "string"}
                        },
                        "lesson_flow": {
                            "type": "array",
                            "title": "Lesson Flow",
                            "items": {
                                "type": "object",
                                "title": "LessonPhase",
                                "required": ["phase", "minutes", "activity"],
                                "properties": {
                                    "phase": {"type": "string", "title": "Phase"},
                                    "minutes": {"type": "integer", "title": "Minutes"},
                                    "activity": {"type": "string", "title": "Activity"}
                                }
                            }
                        },
                        "assessment": {
                            "type": "object",
                            "title": "Assessment",
                            "required": ["type", "description"],
                            "properties": {
                                "type": {"type": "string", "title": "Assessment Type"},
                                "description": {"type": "string", "title": "Assessment Description"}
                            }
                        },
                        "differentiation": {
                            "type": "object",
                            "title": "Differentiation",
                            "properties": {
                                "support": {
                                    "type": "array",
                                    "title": "Support Strategies",
                                    "items": {"type": "string"}
                                },
                                "extension": {
                                    "type": "array",
                                    "title": "Extension Opportunities",
                                    "items": {"type": "string"}
                                }
                            }
                        },
                        "bloom_alignment": {
                            "type": "object",
                            "title": "Bloom Alignment",
                            "required": ["level", "note"],
                            "properties": {
                                "level": {"type": "string", "title": "Bloom Level"},
                                "note": {"type": "string", "title": "Alignment Note"}
                            }
                        },
                        "standards_alignment": {
                            "type": "string",
                            "title": "Standards Alignment"
                        }
                    }
                },
                "stub_config": {
                    "title_template": "Finding the Theme",
                    "overview_template": "Students analyze how authors develop theme through details in {topic}.",
                    "learning_objectives_template": [
                        "Identify the theme of a short story.",
                        "Support theme with textual evidence."
                    ],
                    "lesson_flow": [
                        {"phase": "Hook", "minutes": 5, "activity": "Quote discussion related to {topic}."},
                        {"phase": "Instruction", "minutes": 10, "activity": "Model identifying theme in a short story."},
                        {"phase": "Guided Practice", "minutes": 15, "activity": "Whole-class analysis of a short story."},
                        {"phase": "Independent Practice", "minutes": 15, "activity": "Students identify theme and evidence in a new text."},
                        {"phase": "Closure", "minutes": 5, "activity": "Exit ticket: state the theme and one supporting quote."}
                    ],
                    "assessment": {
                        "type": "exit_ticket",
                        "description_template": "Students identify the theme and provide 2 supporting quotes from the text."
                    },
                    "differentiation": {
                        "support": [
                            "Provide highlighted or annotated versions of the text.",
                            "Offer sentence stems for stating theme and evidence."
                        ],
                        "extension": [
                            "Ask students to compare two possible themes and justify which is stronger using evidence."
                        ]
                    },
                    "bloom_alignment": {
                        "level": "Analyze",
                        "note_template": "Students interpret and justify theme using textual evidence in {topic}."
                    },
                    "standards_alignment_template": "Aligned to {standard}"
                },
                "prompt_definition": {
                    "description": "Generate a comprehensive, internationally-aligned lesson plan suitable for high-level schools (USA, UK, IB, etc.) with: Lesson Overview, Learning Intentions, Success Criteria, Materials, Lesson Steps (Warmup → Instruction → Activity → Closure), Differentiation, Formative Assessment, Teacher Notes, and Bloom Mapping. Map topic to subject-specific instructional model, align steps with Bloom levels, auto-generate learning intentions and success criteria, build 4-stage lesson flow, add differentiation and exit ticket. Ensure content meets international quality standards, uses research-based pedagogy, and is culturally appropriate for diverse student populations.",
                    "context": "This lesson plan will be used in international schools and high-performing institutions. Content must be academically rigorous, pedagogically sound, and aligned with best practices from leading educational systems worldwide."
                }
            }
        },
        {
            # TEMPLATE 25: GIS Mapping & Spatial Analysis Activity Builder
            "template": {
                "slug": "gis_mapping_spatial_analysis",
                "name": "GIS Mapping & Spatial Analysis Activity Builder",
                "description": "Helps teachers design GIS-style activities where students analyze geographic patterns using layers, maps, and spatial relationships.",
                "category": "subject_specific",
                "subject_default": "social_studies",
                "grade_bands_supported": ["6-8", "9-12"],
            },
            "version": {
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "grade_level": {
                            "type": "string",
                            "title": "Grade level",
                            "description": "e.g. Year 10"
                        },
                        "map_layers": {
                            "type": "array",
                            "title": "Map layers",
                            "description": "List of geographic layers students will analyze (e.g. Population Density, Transportation Networks).",
                            "items": {"type": "string"}
                        },
                        "region": {
                            "type": "string",
                            "title": "Region",
                            "description": "Geographic focus region, e.g. South-East Asia."
                        },
                        "learning_objective": {
                            "type": "string",
                            "title": "Learning objective",
                            "description": "e.g. Students analyze how infrastructure influences economic development."
                        },
                        "bloom_level": {
                            "type": "string",
                            "title": "Bloom level",
                            "description": "e.g. Analyze / Evaluate."
                        },
                        "assessment_type": {
                            "type": "string",
                            "title": "Assessment type",
                            "description": "e.g. Spatial Analysis Report."
                        }
                    },
                    "required": ["grade_level", "map_layers", "region", "learning_objective", "bloom_level"]
                },
                "output_schema": {
                    "type": "object",
                    "title": "GISMappingSpatialAnalysisOutput",
                    "required": [
                        "activity_overview",
                        "map_layer_analysis",
                        "spatial_pattern_questions",
                        "comparative_task",
                        "student_output",
                        "assessment_rubric",
                        "bloom_alignment"
                    ],
                    "properties": {
                        "activity_overview": {"type": "string", "title": "Activity overview"},
                        "map_layer_analysis": {
                            "type": "array",
                            "title": "Map layer analysis focus points",
                            "items": {"type": "string"}
                        },
                        "spatial_pattern_questions": {
                            "type": "array",
                            "title": "Spatial pattern questions",
                            "items": {"type": "string"}
                        },
                        "comparative_task": {"type": "string", "title": "Comparative task"},
                        "student_output": {"type": "string", "title": "Student output requirement"},
                        "assessment_rubric": {
                            "type": "array",
                            "title": "Assessment rubric (criteria + description)",
                            "items": {
                                "type": "object",
                                "required": ["criteria", "description"],
                                "properties": {
                                    "criteria": {"type": "string", "title": "Criteria"},
                                    "description": {"type": "string", "title": "Description"}
                                }
                            }
                        },
                        "bloom_alignment": {
                            "type": "object",
                            "title": "Bloom alignment",
                            "required": ["level", "description"],
                            "properties": {
                                "level": {"type": "string", "title": "Bloom level"},
                                "description": {"type": "string", "title": "Bloom alignment description"}
                            }
                        }
                    }
                },
                "stub_config": {
                    "activity_overview_template": "Students explore how geographic layers such as {map_layers} interact in {region} to influence economic development.",
                    "map_layer_analysis": [
                        "Population distribution",
                        "Major transportation routes",
                        "Economic activity centers"
                    ],
                    "spatial_pattern_questions": [
                        "Where do economic centers cluster?",
                        "How do transportation networks influence development?"
                    ],
                    "comparative_task_template": "Students compare two cities in {region} and explain their geographic advantages using map evidence.",
                    "student_output_template": "Write a 500-word spatial analysis report explaining key geographic relationships in {region}.",
                    "assessment_rubric": [
                        {"criteria": "Spatial interpretation", "description": "Identifies and describes spatial patterns using map layers."},
                        {"criteria": "Geographic reasoning", "description": "Explains relationships between layers such as infrastructure and development."},
                        {"criteria": "Evidence use", "description": "Supports conclusions with specific map-based evidence."}
                    ],
                    "bloom_alignment": {
                        "level": "Analyze / Evaluate",
                        "description_template": "Students analyze spatial relationships and evaluate development patterns in {region} using {map_layers}."
                    }
                },
                "prompt_definition": {
                    "description": "Generate a GIS-style mapping activity where students analyze how multiple map layers interact in a specific region. Output must include: Activity overview, Map layer analysis focus points, Spatial pattern questions, Comparative task, Student output requirement, Assessment rubric (criteria + description), and Bloom alignment.",
                    "context": "This template supports geography and global studies classes that introduce GIS thinking and spatial analysis. Ensure tasks require students to interpret patterns, justify claims with map evidence, and work at the requested Bloom level."
                }
            }
        },
        {
            # TEMPLATE 26: Sustainable Cities Planning Studio
            "template": {
                "slug": "sustainable_cities_planning_studio",
                "name": "Sustainable Cities Planning Studio",
                "description": "Engages students in urban planning challenges focused on sustainability, transport, housing, and green design.",
                "category": "subject_specific",
                "subject_default": "social_studies",
                "grade_bands_supported": ["6-8", "9-12"],
            },
            "version": {
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "grade_level": {
                            "type": "string",
                            "title": "Grade level",
                            "description": "e.g. Year 10"
                        },
                        "city_focus": {
                            "type": "string",
                            "title": "City focus",
                            "description": "e.g. Future Sustainable City."
                        },
                        "urban_issues": {
                            "type": "array",
                            "title": "Urban issues",
                            "description": "Key challenges such as traffic congestion, air pollution, housing.",
                            "items": {"type": "string"}
                        },
                        "project_duration": {
                            "type": "string",
                            "title": "Project duration",
                            "description": "e.g. 1 week."
                        },
                        "bloom_level": {
                            "type": "string",
                            "title": "Bloom level",
                            "description": "e.g. Create."
                        },
                        "team_size": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 20,
                            "title": "Team size"
                        }
                    },
                    "required": ["grade_level", "city_focus", "urban_issues", "project_duration", "bloom_level"]
                },
                "output_schema": {
                    "type": "object",
                    "title": "SustainableCitiesPlanningStudioOutput",
                    "required": [
                        "planning_challenge_brief",
                        "urban_planning_components",
                        "design_process",
                        "project_deliverables",
                        "evaluation_rubric",
                        "bloom_alignment"
                    ],
                    "properties": {
                        "planning_challenge_brief": {"type": "string", "title": "Planning challenge brief"},
                        "urban_planning_components": {
                            "type": "array",
                            "title": "Urban planning components",
                            "items": {"type": "string"}
                        },
                        "design_process": {
                            "type": "array",
                            "title": "Design process steps",
                            "items": {"type": "string"}
                        },
                        "project_deliverables": {
                            "type": "array",
                            "title": "Project deliverables",
                            "items": {"type": "string"}
                        },
                        "evaluation_rubric": {
                            "type": "array",
                            "title": "Evaluation rubric (criteria + description)",
                            "items": {
                                "type": "object",
                                "required": ["criteria", "description"],
                                "properties": {
                                    "criteria": {"type": "string", "title": "Criteria"},
                                    "description": {"type": "string", "title": "Description"}
                                }
                            }
                        },
                        "bloom_alignment": {
                            "type": "object",
                            "title": "Bloom alignment",
                            "required": ["level", "description"],
                            "properties": {
                                "level": {"type": "string", "title": "Bloom level"},
                                "description": {"type": "string", "title": "Bloom alignment description"}
                            }
                        }
                    }
                },
                "stub_config": {
                    "planning_challenge_brief_template": "Students design a {city_focus} addressing key issues such as {urban_issues} over {project_duration}.",
                    "urban_planning_components": [
                        "Transportation systems",
                        "Green spaces",
                        "Housing development",
                        "Waste management"
                    ],
                    "design_process": [
                        "Research urban challenges",
                        "Develop city layout",
                        "Propose sustainability solutions"
                    ],
                    "project_deliverables": [
                        "City design map",
                        "Written proposal",
                        "Class presentation"
                    ],
                    "evaluation_rubric": [
                        {"criteria": "Innovation", "description": "Proposes creative and original sustainability solutions."},
                        {"criteria": "Feasibility", "description": "Design is realistic and implementable within constraints."},
                        {"criteria": "Environmental impact", "description": "Demonstrates strong focus on sustainability and ecological outcomes."}
                    ],
                    "bloom_alignment": {
                        "level": "Create",
                        "description_template": "Students create a sustainable urban plan that integrates research, design, and evaluation for {city_focus}."
                    }
                },
                "prompt_definition": {
                    "description": "Generate a Sustainable Cities Planning Studio project where students act as urban planners. Output must include: Planning challenge brief, Urban planning components, Design process steps, Project deliverables, Evaluation rubric (criteria + description), and Bloom alignment.",
                    "context": "This template supports project-based learning in geography, civics, and sustainability. Ensure tasks encourage collaborative design, creative problem solving, and systems thinking about urban environments."
                }
            }
        },
        {
            # TEMPLATE 27: Global Trade Network Analysis
            "template": {
                "slug": "global_trade_network_analysis",
                "name": "Global Trade Network Analysis",
                "description": "Helps students understand global supply chains, trade patterns, and economic geography.",
                "category": "subject_specific",
                "subject_default": "social_studies",
                "grade_bands_supported": ["9-12"],
            },
            "version": {
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "grade_level": {
                            "type": "string",
                            "title": "Grade level",
                            "description": "e.g. Year 11"
                        },
                        "trade_focus": {
                            "type": "string",
                            "title": "Trade focus",
                            "description": "e.g. Global Supply Chains."
                        },
                        "products": {
                            "type": "array",
                            "title": "Products",
                            "description": "Key products whose supply chains students will trace (e.g. Electronics, Clothing).",
                            "items": {"type": "string"}
                        },
                        "regions": {
                            "type": "array",
                            "title": "Regions",
                            "description": "Regions involved in trade (e.g. Asia, Europe, North America).",
                            "items": {"type": "string"}
                        },
                        "bloom_level": {
                            "type": "string",
                            "title": "Bloom level",
                            "description": "e.g. Analyze / Evaluate."
                        },
                        "assessment_type": {
                            "type": "string",
                            "title": "Assessment type",
                            "description": "e.g. Trade Analysis Report."
                        }
                    },
                    "required": ["grade_level", "trade_focus", "products", "regions", "bloom_level"]
                },
                "output_schema": {
                    "type": "object",
                    "title": "GlobalTradeNetworkAnalysisOutput",
                    "required": [
                        "global_trade_overview",
                        "supply_chain_mapping_activity",
                        "trade_pattern_questions",
                        "economic_impact_analysis",
                        "student_task",
                        "assessment_rubric",
                        "bloom_alignment"
                    ],
                    "properties": {
                        "global_trade_overview": {"type": "string", "title": "Global trade overview"},
                        "supply_chain_mapping_activity": {
                            "type": "array",
                            "title": "Supply chain mapping steps",
                            "items": {"type": "string"}
                        },
                        "trade_pattern_questions": {
                            "type": "array",
                            "title": "Trade pattern questions",
                            "items": {"type": "string"}
                        },
                        "economic_impact_analysis": {
                            "type": "array",
                            "title": "Economic impact analysis focus points",
                            "items": {"type": "string"}
                        },
                        "student_task": {"type": "string", "title": "Student task"},
                        "assessment_rubric": {
                            "type": "array",
                            "title": "Assessment rubric (criteria + description)",
                            "items": {
                                "type": "object",
                                "required": ["criteria", "description"],
                                "properties": {
                                    "criteria": {"type": "string", "title": "Criteria"},
                                    "description": {"type": "string", "title": "Description"}
                                }
                            }
                        },
                        "bloom_alignment": {
                            "type": "object",
                            "title": "Bloom alignment",
                            "required": ["level", "description"],
                            "properties": {
                                "level": {"type": "string", "title": "Bloom level"},
                                "description": {"type": "string", "title": "Bloom alignment description"}
                            }
                        }
                    }
                },
                "stub_config": {
                    "global_trade_overview_template": "Explanation of how {products} move through global supply chains connecting {regions}.",
                    "supply_chain_mapping_activity": [
                        "Select a product.",
                        "Trace its journey from factory to consumer (Factory → Port → Shipping Route → Retail Market).",
                        "Annotate each stage with location and value added."
                    ],
                    "trade_pattern_questions": [
                        "Why are certain regions manufacturing hubs?",
                        "How do transportation routes influence trade flows?"
                    ],
                    "economic_impact_analysis": [
                        "Job creation in different regions.",
                        "Environmental costs of production and transport.",
                        "Economic dependency on global markets."
                    ],
                    "student_task_template": "Write a trade analysis report explaining how global trade networks function for {products} within {trade_focus}.",
                    "assessment_rubric": [
                        {"criteria": "Geographic analysis", "description": "Explains trade patterns across regions using spatial reasoning."},
                        {"criteria": "Economic reasoning", "description": "Accurately interprets supply chains and economic relationships."},
                        {"criteria": "Critical evaluation", "description": "Assesses social, environmental, and economic impacts with balance."}
                    ],
                    "bloom_alignment": {
                        "level": "Analyze / Evaluate",
                        "description_template": "Students analyze global trade networks and evaluate economic implications for {trade_focus} and {products}."
                    }
                },
                "prompt_definition": {
                    "description": "Generate a Global Trade Network Analysis activity where students trace products through international supply chains. Output must include: Global trade overview, Supply chain mapping activity, Trade pattern questions, Economic impact analysis focus points, Student task, Assessment rubric, and Bloom alignment.",
                    "context": "This template supports senior geography and economics classes studying globalization and trade. Ensure students interpret maps/diagrams, reason about supply chains, and critically evaluate impacts."
                }
            }
        },
        {
            # TEMPLATE 28: Interdisciplinary English Project Builder
            "template": {
                "slug": "interdisciplinary_english_project",
                "name": "Interdisciplinary English Project Builder",
                "description": "Connects English with science, history, or social studies for project-based learning and persuasive communication.",
                "category": "subject_specific",
                "subject_default": "english",
                "grade_bands_supported": ["6-8", "9-12"],
            },
            "version": {
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "grade_level": {
                            "type": "string",
                            "title": "Grade level",
                            "description": "e.g. Year 9"
                        },
                        "project_theme": {
                            "type": "string",
                            "title": "Project theme",
                            "description": "e.g. Environmental Sustainability."
                        },
                        "connected_subject": {
                            "type": "string",
                            "title": "Connected subject",
                            "description": "e.g. Science, History, Social Studies."
                        },
                        "learning_objective": {
                            "type": "string",
                            "title": "Learning objective",
                            "description": "e.g. Communicate scientific ideas through persuasive writing."
                        },
                        "project_duration": {
                            "type": "string",
                            "title": "Project duration",
                            "description": "e.g. 1 week."
                        },
                        "bloom_level": {
                            "type": "string",
                            "title": "Bloom level",
                            "description": "e.g. Create."
                        }
                    },
                    "required": ["grade_level", "project_theme", "connected_subject", "learning_objective", "project_duration", "bloom_level"]
                },
                "output_schema": {
                    "type": "object",
                    "title": "InterdisciplinaryEnglishProjectOutput",
                    "required": [
                        "project_overview",
                        "research_task",
                        "writing_task",
                        "presentation_component",
                        "assessment_rubric",
                        "bloom_alignment"
                    ],
                    "properties": {
                        "project_overview": {"type": "string", "title": "Project overview"},
                        "research_task": {
                            "type": "array",
                            "title": "Research task focus areas",
                            "items": {"type": "string"}
                        },
                        "writing_task": {
                            "type": "array",
                            "title": "Writing task outputs",
                            "items": {"type": "string"}
                        },
                        "presentation_component": {"type": "string", "title": "Presentation component"},
                        "assessment_rubric": {
                            "type": "array",
                            "title": "Assessment rubric (criteria + description)",
                            "items": {
                                "type": "object",
                                "required": ["criteria", "description"],
                                "properties": {
                                    "criteria": {"type": "string", "title": "Criteria"},
                                    "description": {"type": "string", "title": "Description"}
                                }
                            }
                        },
                        "bloom_alignment": {
                            "type": "object",
                            "title": "Bloom alignment",
                            "required": ["level", "description"],
                            "properties": {
                                "level": {"type": "string", "title": "Bloom level"},
                                "description": {"type": "string", "title": "Bloom alignment description"}
                            }
                        }
                    }
                },
                "stub_config": {
                    "project_overview_template": "Students explore {project_theme} in {connected_subject} and communicate findings through persuasive English writing.",
                    "research_task": [
                        "Investigate pollution impacts.",
                        "Explore renewable energy solutions.",
                        "Examine biodiversity loss and conservation."
                    ],
                    "writing_task": [
                        "Persuasive article",
                        "Awareness campaign message"
                    ],
                    "presentation_component_template": "Students present their argument to the class, explaining key ideas about {project_theme}.",
                    "assessment_rubric": [
                        {"criteria": "Research quality", "description": "Information is accurate, relevant, and well-sourced from {connected_subject}."},
                        {"criteria": "Writing clarity", "description": "Argument is clearly structured with strong persuasive techniques."},
                        {"criteria": "Creativity", "description": "Presentation and writing are engaging and original."}
                    ],
                    "bloom_alignment": {
                        "level": "Create",
                        "description_template": "Students create interdisciplinary communication products that synthesize research on {project_theme}."
                    }
                },
                "prompt_definition": {
                    "description": "Generate an interdisciplinary English project linking English with another subject such as science or history. Output must include: Project overview, Research task focus areas, Writing task outputs, Presentation component, Assessment rubric, and Bloom alignment.",
                    "context": "This template supports IB-style and modern curricula that emphasize interdisciplinary, project-based learning. Ensure tasks require both content understanding and advanced communication skills."
                }
            }
        },
        {
            # TEMPLATE 29: Literary Analysis Essay Architect (Advanced Literature)
            "template": {
                "slug": "literary_analysis_essay_architect",
                "name": "Literary Analysis Essay Architect (Advanced Literature)",
                "description": "Guides students in writing high-level literary analysis essays for IB, AP, Cambridge, and GCSE English Literature.",
                "category": "subject_specific",
                "subject_default": "english",
                "grade_bands_supported": ["9-12"],
            },
            "version": {
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "grade_level": {
                            "type": "string",
                            "title": "Grade level",
                            "description": "e.g. Year 11"
                        },
                        "literary_text": {
                            "type": "string",
                            "title": "Literary text",
                            "description": "Title and author, e.g. Macbeth by William Shakespeare."
                        },
                        "analysis_focus": {
                            "type": "string",
                            "title": "Analysis focus",
                            "description": "e.g. Ambition and Moral Corruption."
                        },
                        "essay_type": {
                            "type": "string",
                            "title": "Essay type",
                            "description": "e.g. Literary Analysis."
                        },
                        "learning_objective": {
                            "type": "string",
                            "title": "Learning objective",
                            "description": "e.g. Analyze how the author develops a theme through character and symbolism."
                        },
                        "essay_length": {
                            "type": "string",
                            "title": "Essay length",
                            "description": "e.g. 1000 words."
                        },
                        "bloom_level": {
                            "type": "string",
                            "title": "Bloom level",
                            "description": "e.g. Analyze → Evaluate."
                        },
                        "standards_framework": {
                            "type": "string",
                            "title": "Standards framework",
                            "description": "Optional curriculum framework (e.g. IB Literature)."
                        }
                    },
                    "required": ["grade_level", "literary_text", "analysis_focus", "essay_type", "learning_objective", "essay_length", "bloom_level"]
                },
                "output_schema": {
                    "type": "object",
                    "title": "LiteraryAnalysisEssayArchitectOutput",
                    "required": [
                        "literary_context_overview",
                        "analytical_essay_prompt",
                        "evidence_exploration_activity",
                        "essay_structure_guide",
                        "assessment_rubric",
                        "bloom_alignment"
                    ],
                    "properties": {
                        "literary_context_overview": {"type": "string", "title": "Literary context overview"},
                        "analytical_essay_prompt": {"type": "string", "title": "Analytical essay prompt"},
                        "evidence_exploration_activity": {
                            "type": "array",
                            "title": "Evidence exploration focus areas",
                            "items": {"type": "string"}
                        },
                        "essay_structure_guide": {
                            "type": "object",
                            "title": "Essay structure guide",
                            "properties": {
                                "introduction": {"type": "array", "title": "Introduction elements", "items": {"type": "string"}},
                                "body_paragraphs": {"type": "array", "title": "Body paragraph elements", "items": {"type": "string"}},
                                "conclusion": {"type": "array", "title": "Conclusion elements", "items": {"type": "string"}}
                            },
                            "required": ["introduction", "body_paragraphs", "conclusion"]
                        },
                        "assessment_rubric": {
                            "type": "array",
                            "title": "Assessment rubric (criteria + description)",
                            "items": {
                                "type": "object",
                                "required": ["criteria", "description"],
                                "properties": {
                                    "criteria": {"type": "string", "title": "Criteria"},
                                    "description": {"type": "string", "title": "Description"}
                                }
                            }
                        },
                        "bloom_alignment": {
                            "type": "object",
                            "title": "Bloom alignment",
                            "required": ["level", "description"],
                            "properties": {
                                "level": {"type": "string", "title": "Bloom level"},
                                "description": {"type": "string", "title": "Bloom alignment description"}
                            }
                        }
                    }
                },
                "stub_config": {
                    "literary_context_overview_template": "Brief explanation of how {analysis_focus} operates in {literary_text}, e.g. ambition drives the protagonist's rise to power but leads to psychological destruction.",
                    "analytical_essay_prompt_template": "How does the author use symbolism and character development to explore {analysis_focus} in {literary_text}?",
                    "evidence_exploration_activity": [
                        "Key character soliloquies or internal monologues.",
                        "Persuasive dialogue from pivotal scenes.",
                        "Symbolic motifs (e.g. blood, weather, light/dark)."
                    ],
                    "essay_structure_guide": {
                        "introduction": [
                            "Context for text and theme.",
                            "Clear thesis statement addressing {analysis_focus}."
                        ],
                        "body_paragraphs": [
                            "Analytical claim.",
                            "Embedded evidence (quotation).",
                            "Explanation and close analysis of language.",
                            "Comment on broader thematic implications."
                        ],
                        "conclusion": [
                            "Synthesis of main points.",
                            "Connection of theme to broader human or social questions."
                        ]
                    },
                    "assessment_rubric": [
                        {"criteria": "Interpretation", "description": "Shows insightful understanding of {analysis_focus} in {literary_text}."},
                        {"criteria": "Evidence", "description": "Selects accurate, well-integrated textual evidence."},
                        {"criteria": "Analysis", "description": "Offers detailed explanation of literary techniques and their effects."},
                        {"criteria": "Organization", "description": "Essay is logically structured with coherent paragraphs and transitions."}
                    ],
                    "bloom_alignment": {
                        "level": "Analyze → Evaluate",
                        "description_template": "Students analyze literary devices and evaluate thematic meaning in {literary_text} at an advanced level."
                    }
                },
                "prompt_definition": {
                    "description": "Generate a high-level literary analysis essay task suitable for IB, AP, Cambridge, or GCSE. Output must include: Literary context overview, Analytical essay prompt, Evidence exploration activity, Essay structure guide, Assessment rubric, and Bloom alignment.",
                    "context": "This template is for advanced literature classes. Ensure prompts demand close textual analysis, conceptual sophistication, and evaluative thinking."
                }
            }
        },
        {
            # TEMPLATE 30: Media Literacy & Bias Analysis Builder
            "template": {
                "slug": "media_literacy_bias_analysis",
                "name": "Media Literacy & Bias Analysis Builder",
                "description": "Helps teachers design activities where students analyze media bias, credibility, and perspective.",
                "category": "subject_specific",
                "subject_default": "social_studies",
                "grade_bands_supported": ["9-12"],
            },
            "version": {
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "grade_level": {
                            "type": "string",
                            "title": "Grade level",
                            "description": "e.g. Year 10"
                        },
                        "media_topic": {
                            "type": "string",
                            "title": "Media topic",
                            "description": "e.g. Climate Change Reporting."
                        },
                        "source_types": {
                            "type": "array",
                            "title": "Source types",
                            "description": "Types of sources to compare (e.g. News Article, Social Media Post).",
                            "items": {"type": "string"}
                        },
                        "learning_objective": {
                            "type": "string",
                            "title": "Learning objective",
                            "description": "e.g. Analyze bias and evaluate credibility of media sources."
                        },
                        "bloom_level": {
                            "type": "string",
                            "title": "Bloom level",
                            "description": "e.g. Analyze / Evaluate."
                        },
                        "assessment_type": {
                            "type": "string",
                            "title": "Assessment type",
                            "description": "e.g. Media Analysis Report."
                        }
                    },
                    "required": ["grade_level", "media_topic", "source_types", "learning_objective", "bloom_level"]
                },
                "output_schema": {
                    "type": "object",
                    "title": "MediaLiteracyBiasAnalysisOutput",
                    "required": [
                        "media_literacy_objective",
                        "source_comparison_task",
                        "bias_detection_questions",
                        "credibility_evaluation_framework",
                        "student_task",
                        "assessment_rubric",
                        "bloom_alignment"
                    ],
                    "properties": {
                        "media_literacy_objective": {"type": "string", "title": "Media literacy objective"},
                        "source_comparison_task": {
                            "type": "object",
                            "title": "Source comparison task",
                            "properties": {
                                "sources_to_compare": {"type": "array", "title": "Sources to compare", "items": {"type": "string"}},
                                "focus_areas": {"type": "array", "title": "Focus areas", "items": {"type": "string"}}
                            },
                            "required": ["sources_to_compare", "focus_areas"]
                        },
                        "bias_detection_questions": {
                            "type": "array",
                            "title": "Bias detection questions",
                            "items": {"type": "string"}
                        },
                        "credibility_evaluation_framework": {
                            "type": "array",
                            "title": "Credibility evaluation framework",
                            "items": {"type": "string"}
                        },
                        "student_task": {"type": "string", "title": "Student task"},
                        "assessment_rubric": {
                            "type": "array",
                            "title": "Assessment rubric (criteria + description)",
                            "items": {
                                "type": "object",
                                "required": ["criteria", "description"],
                                "properties": {
                                    "criteria": {"type": "string", "title": "Criteria"},
                                    "description": {"type": "string", "title": "Description"}
                                }
                            }
                        },
                        "bloom_alignment": {
                            "type": "object",
                            "title": "Bloom alignment",
                            "required": ["level", "description"],
                            "properties": {
                                "level": {"type": "string", "title": "Bloom level"},
                                "description": {"type": "string", "title": "Bloom alignment description"}
                            }
                        }
                    }
                },
                "stub_config": {
                    "media_literacy_objective_template": "Students analyze how information about {media_topic} is presented across different media sources and detect bias.",
                    "source_comparison_task": {
                        "sources_to_compare": [
                            "News article",
                            "Social media post"
                        ],
                        "focus_areas": [
                            "Language tone",
                            "Evidence used",
                            "Emotional framing"
                        ]
                    },
                    "bias_detection_questions": [
                        "What perspective does the author represent?",
                        "What information might be missing?",
                        "Is the language neutral, biased, or persuasive?"
                    ],
                    "credibility_evaluation_framework": [
                        "Author expertise and background.",
                        "Evidence reliability and sourcing.",
                        "Publication or platform credibility."
                    ],
                    "student_task_template": "Write a 500-word media analysis explaining which source on {media_topic} is more reliable and why.",
                    "assessment_rubric": [
                        {"criteria": "Source evaluation", "description": "Accurately identifies and evaluates source credibility."},
                        {"criteria": "Bias analysis", "description": "Clearly detects and explains perspectives and biases."},
                        {"criteria": "Reasoning", "description": "Builds a logical argument supported by specific examples."}
                    ],
                    "bloom_alignment": {
                        "level": "Analyze / Evaluate",
                        "description_template": "Students analyze media bias and evaluate credibility of sources about {media_topic}."
                    }
                },
                "prompt_definition": {
                    "description": "Generate a media literacy activity comparing at least two contrasting source types on a given topic. Output must include: Media literacy objective, Source comparison task (sources and focus areas), Bias detection questions, Credibility evaluation framework, Student task, Assessment rubric, and Bloom alignment.",
                    "context": "This template supports critical media literacy in secondary classrooms. Ensure tasks are age-appropriate and encourage skepticism, evidence-based evaluation, and ethical media consumption."
                }
            }
        },
        {
            # TEMPLATE 31: Scientific Controversy Debate Framework
            "template": {
                "slug": "scientific_controversy_debate",
                "name": "Scientific Controversy Debate Framework",
                "description": "Helps students debate scientific issues with conflicting perspectives, improving scientific literacy and argument evaluation.",
                "category": "subject_specific",
                "subject_default": "science",
                "grade_bands_supported": ["9-12"],
            },
            "version": {
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "grade_level": {
                            "type": "string",
                            "title": "Grade level",
                            "description": "e.g. Year 10"
                        },
                        "scientific_issue": {
                            "type": "string",
                            "title": "Scientific issue",
                            "description": "e.g. Should genetically modified crops be widely adopted?"
                        },
                        "roles": {
                            "type": "array",
                            "title": "Stakeholder roles",
                            "description": "List of roles students will play (e.g. Scientist, Environmental Activist).",
                            "items": {"type": "string"}
                        },
                        "debate_format": {
                            "type": "string",
                            "title": "Debate format",
                            "description": "e.g. Scientific Evidence Debate."
                        },
                        "bloom_level": {
                            "type": "string",
                            "title": "Bloom level",
                            "description": "e.g. Analyze / Evaluate."
                        },
                        "duration": {
                            "type": "string",
                            "title": "Duration",
                            "description": "e.g. 45 minutes."
                        }
                    },
                    "required": ["grade_level", "scientific_issue", "roles", "debate_format", "bloom_level", "duration"]
                },
                "output_schema": {
                    "type": "object",
                    "title": "ScientificControversyDebateOutput",
                    "required": [
                        "scientific_context_overview",
                        "stakeholder_role_profiles",
                        "evidence_analysis_task",
                        "debate_structure",
                        "reflection_questions",
                        "assessment_rubric",
                        "bloom_alignment"
                    ],
                    "properties": {
                        "scientific_context_overview": {"type": "string", "title": "Scientific context overview"},
                        "stakeholder_role_profiles": {
                            "type": "array",
                            "title": "Stakeholder role profiles",
                            "items": {
                                "type": "object",
                                "required": ["role", "focus"],
                                "properties": {
                                    "role": {"type": "string", "title": "Role"},
                                    "focus": {"type": "string", "title": "Focus"}
                                }
                            }
                        },
                        "evidence_analysis_task": {
                            "type": "string",
                            "title": "Evidence analysis task"
                        },
                        "debate_structure": {
                            "type": "array",
                            "title": "Debate structure steps",
                            "items": {"type": "string"}
                        },
                        "reflection_questions": {
                            "type": "array",
                            "title": "Reflection questions",
                            "items": {"type": "string"}
                        },
                        "assessment_rubric": {
                            "type": "array",
                            "title": "Assessment rubric (skill + criteria)",
                            "items": {
                                "type": "object",
                                "required": ["skill", "criteria"],
                                "properties": {
                                    "skill": {"type": "string", "title": "Skill"},
                                    "criteria": {"type": "string", "title": "Criteria"}
                                }
                            }
                        },
                        "bloom_alignment": {
                            "type": "object",
                            "title": "Bloom alignment",
                            "required": ["level", "description"],
                            "properties": {
                                "level": {"type": "string", "title": "Bloom level"},
                                "description": {"type": "string", "title": "Bloom alignment description"}
                            }
                        }
                    }
                },
                "stub_config": {
                    "scientific_context_overview_template": "Students explore the benefits and risks of {scientific_issue}, drawing on current scientific research.",
                    "stakeholder_role_profiles": [
                        {"role": "Biotechnology Scientist", "focus": "Agricultural innovation and increased yields."},
                        {"role": "Environmental Activist", "focus": "Ecological concerns and biodiversity impacts."},
                        {"role": "Farmer", "focus": "Productivity, economic stability, and livelihood."},
                        {"role": "Public Health Expert", "focus": "Food safety, regulation, and long-term health outcomes."}
                    ],
                    "evidence_analysis_task_template": "Students analyze scientific studies and popular articles about {scientific_issue}, identifying key findings and uncertainties.",
                    "debate_structure": [
                        "Evidence presentation",
                        "Argument development",
                        "Counterargument responses",
                        "Final evaluation vote"
                    ],
                    "reflection_questions": [
                        "How should scientific uncertainty influence decision-making?",
                        "Which evidence was most persuasive and why?"
                    ],
                    "assessment_rubric": [
                        {"skill": "Evidence interpretation", "criteria": "Accurately uses and explains scientific data."},
                        {"skill": "Argument logic", "criteria": "Presents clear, coherent reasoning supported by evidence."},
                        {"skill": "Critical thinking", "criteria": "Evaluates opposing viewpoints and limitations of evidence."}
                    ],
                    "bloom_alignment": {
                        "level": "Analyze / Evaluate",
                        "description_template": "Students analyze scientific evidence on {scientific_issue} and evaluate competing claims during debate."
                    }
                },
                "prompt_definition": {
                    "description": "Generate a scientific debate activity around a controversial issue. Output must include: Scientific context overview, Stakeholder role profiles, Evidence analysis task, Debate structure, Reflection questions, Assessment rubric, and Bloom alignment.",
                    "context": "This template is for science and interdisciplinary courses that teach evidence-based argumentation. Ensure roles are balanced and encourage respectful, critical discussion."
                }
            }
        },
        {
            # TEMPLATE 32: Policy Debate & Decision-Making Simulation
            "template": {
                "slug": "policy_debate_decision_simulation",
                "name": "Policy Debate & Decision-Making Simulation",
                "description": "Teaches students how to debate real-world policy decisions and evaluate trade-offs between competing solutions.",
                "category": "subject_specific",
                "subject_default": "social_studies",
                "grade_bands_supported": ["9-12"],
            },
            "version": {
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "grade_level": {
                            "type": "string",
                            "title": "Grade level",
                            "description": "e.g. Year 10"
                        },
                        "policy_issue": {
                            "type": "string",
                            "title": "Policy issue",
                            "description": "e.g. Should governments ban single-use plastics?"
                        },
                        "debate_roles": {
                            "type": "array",
                            "title": "Debate roles",
                            "description": "Roles such as Government, Environmental Activists, Business Owners, Consumers.",
                            "items": {"type": "string"}
                        },
                        "bloom_level": {
                            "type": "string",
                            "title": "Bloom level",
                            "description": "e.g. Analyze → Evaluate."
                        },
                        "activity_format": {
                            "type": "string",
                            "title": "Activity format",
                            "description": "e.g. Policy Simulation."
                        },
                        "duration": {
                            "type": "string",
                            "title": "Duration",
                            "description": "e.g. 50 minutes."
                        }
                    },
                    "required": ["grade_level", "policy_issue", "debate_roles", "bloom_level", "activity_format", "duration"]
                },
                "output_schema": {
                    "type": "object",
                    "title": "PolicyDebateDecisionSimulationOutput",
                    "required": [
                        "policy_issue_overview",
                        "role_assignment_sheets",
                        "debate_structure",
                        "critical_thinking_prompts",
                        "student_task",
                        "assessment_rubric",
                        "bloom_alignment"
                    ],
                    "properties": {
                        "policy_issue_overview": {"type": "string", "title": "Policy issue overview"},
                        "role_assignment_sheets": {
                            "type": "array",
                            "title": "Role assignment sheets",
                            "items": {
                                "type": "object",
                                "required": ["role", "goal"],
                                "properties": {
                                    "role": {"type": "string", "title": "Role"},
                                    "goal": {"type": "string", "title": "Goal"}
                                }
                            }
                        },
                        "debate_structure": {
                            "type": "array",
                            "title": "Debate structure steps",
                            "items": {"type": "string"}
                        },
                        "critical_thinking_prompts": {
                            "type": "array",
                            "title": "Critical thinking prompts",
                            "items": {"type": "string"}
                        },
                        "student_task": {"type": "string", "title": "Student task"},
                        "assessment_rubric": {
                            "type": "array",
                            "title": "Assessment rubric (skill + criteria)",
                            "items": {
                                "type": "object",
                                "required": ["skill", "criteria"],
                                "properties": {
                                    "skill": {"type": "string", "title": "Skill"},
                                    "criteria": {"type": "string", "title": "Criteria"}
                                }
                            }
                        },
                        "bloom_alignment": {
                            "type": "object",
                            "title": "Bloom alignment",
                            "required": ["level", "description"],
                            "properties": {
                                "level": {"type": "string", "title": "Bloom level"},
                                "description": {"type": "string", "title": "Bloom alignment description"}
                            }
                        }
                    }
                },
                "stub_config": {
                    "policy_issue_overview_template": "Students explore environmental, economic, and social perspectives on {policy_issue}, considering trade-offs between different policy options.",
                    "role_assignment_sheets": [
                        {"role": "Government", "goal": "Reduce environmental damage while maintaining political and economic stability."},
                        {"role": "Environmental Activists", "goal": "Advocate for strong sustainability policies and ambitious targets."},
                        {"role": "Business Owners", "goal": "Protect economic interests, jobs, and business viability."},
                        {"role": "Consumers", "goal": "Balance convenience, cost, and sustainability."}
                    ],
                    "debate_structure": [
                        "Stakeholder opening arguments",
                        "Evidence presentation",
                        "Cross-examination questions",
                        "Policy negotiation",
                        "Final decision vote"
                    ],
                    "critical_thinking_prompts": [
                        "What trade-offs exist between economic growth and environmental protection?",
                        "Which policy solution seems most balanced, and for whom?"
                    ],
                    "student_task_template": "Students write a short policy recommendation explaining their final position on {policy_issue} and justifying it with evidence.",
                    "assessment_rubric": [
                        {"skill": "Argument reasoning", "criteria": "Provides logical justification and recognizes trade-offs."},
                        {"skill": "Evidence use", "criteria": "Uses credible, relevant examples and data."},
                        {"skill": "Perspective awareness", "criteria": "Considers multiple stakeholder viewpoints fairly."}
                    ],
                    "bloom_alignment": {
                        "level": "Analyze → Evaluate",
                        "description_template": "Students analyze policy trade-offs and evaluate competing solutions related to {policy_issue}."
                    }
                },
                "prompt_definition": {
                    "description": "Generate a policy debate and decision-making simulation for a real-world issue. Output must include: Policy issue overview, Role assignment sheets, Debate structure, Critical thinking prompts, Student task, Assessment rubric, and Bloom alignment.",
                    "context": "This template is for civics, social studies, and interdisciplinary humanities courses. Ensure the simulation highlights trade-offs, multiple perspectives, and evidence-based decision-making."
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
                    "type": "object",
                    "properties": {
                        "subject": {
                            "type": "string",
                            "enum": ["english", "math", "science", "social_studies", "steam", "other"],
                            "title": "Subject",
                            "description": "Primary subject for this activity."
                        },
                        "grade": {
                            "type": "integer",
                            "minimum": 0,
                            "maximum": 12,
                            "title": "Grade",
                            "description": "Numeric grade level (0 for Kindergarten, 1–12 for grades 1–12)."
                        },
                        "topic": {
                            "type": "string",
                            "title": "Topic",
                            "description": "Short description of the activity topic or concept (e.g. 'Food Chains')."
                        },
                        "time_duration_minutes": {
                            "type": "integer",
                            "minimum": 5,
                            "maximum": 480,
                            "title": "Duration (minutes)",
                            "description": "Total time needed for the activity."
                        },
                        "bloom_level": {
                            "type": "string",
                            "title": "Bloom Level",
                            "description": "Primary Bloom level for the activity (e.g. Analyze, Apply, Create)."
                        },
                        "activity_type": {
                            "type": "string",
                            "enum": ["hands_on", "discussion", "creative", "game"],
                            "title": "Activity Type",
                            "description": "Type of engagement: hands_on, discussion, creative, or game."
                        },
                        "materials": {
                            "type": "array",
                            "items": {"type": "string"},
                            "title": "Materials",
                            "description": "List of materials available for the activity."
                        },
                        "constraints": {
                            "type": "string",
                            "title": "Constraints",
                            "description": "Any important constraints (e.g. 'No internet')."
                        }
                    },
                    "required": [
                        "subject",
                        "grade",
                        "topic",
                        "time_duration_minutes",
                        "bloom_level",
                        "activity_type",
                        "materials"
                    ]
                },
                "output_schema": {
                    "type": "object",
                    "title": "ActivitySuggestionOutput",
                    "required": [
                        "title",
                        "time_needed",
                        "learning_goal",
                        "materials",
                        "steps",
                        "assessment",
                        "bloom_alignment"
                    ],
                    "properties": {
                        "title": {"type": "string", "title": "Activity Title"},
                        "time_needed": {"type": "integer", "title": "Time Needed (minutes)"},
                        "learning_goal": {"type": "string", "title": "Learning Goal"},
                        "materials": {
                            "type": "array",
                            "title": "Materials",
                            "items": {"type": "string"}
                        },
                        "steps": {
                            "type": "array",
                            "title": "Steps",
                            "items": {"type": "string"}
                        },
                        "assessment": {"type": "string", "title": "Assessment Prompt"},
                        "differentiation": {
                            "type": "object",
                            "title": "Differentiation",
                            "properties": {
                                "support": {
                                    "type": "array",
                                    "title": "Support Strategies",
                                    "items": {"type": "string"}
                                },
                                "extension": {
                                    "type": "array",
                                    "title": "Extension Ideas",
                                    "items": {"type": "string"}
                                }
                            }
                        },
                        "bloom_alignment": {
                            "type": "object",
                            "title": "Bloom Alignment",
                            "required": ["level", "note"],
                            "properties": {
                                "level": {"type": "string", "title": "Bloom Level"},
                                "note": {"type": "string", "title": "Alignment Note"}
                            }
                        }
                    }
                },
                "stub_config": {
                    "title_template": "Food Web Disruption Game",
                    "time_needed": 30,
                    "learning_goal_template": "Analyze relationships in a food web.",
                    "materials": [
                        "Chart paper",
                        "Markers"
                    ],
                    "steps_template": [
                        "Draw a food web.",
                        "Assign one organism to each group.",
                        "Remove an organism and predict the impact on the food web."
                    ],
                    "assessment_template": "Students explain how removal of one organism affects the ecosystem.",
                    "differentiation": {
                        "support": [
                            "Provide sentence starters for describing cause and effect.",
                            "Offer a partially completed food web for students who need more scaffolding."
                        ],
                        "extension": [
                            "Ask students to add a climate change variable and predict additional impacts.",
                            "Have students design a new organism and place it in the food web."
                        ]
                    },
                    "bloom_alignment": {
                        "level": "Analyze",
                        "note_template": "Students examine cause-effect relationships in the food web for {topic}."
                    }
                },
                "prompt_definition": {
                    "description": "Generate a quick, engaging activity suitable for international classrooms with: Activity Title, Learning Goal, Materials Needed, Steps (simple and fast), Differentiation, Assessment Prompt, and Teacher Notes. Ensure the activity promotes active learning, critical thinking, and is appropriate for diverse student populations. Use research-based engagement strategies and align with international pedagogical best practices.",
                    "context": "This activity will be used in international schools. It should be engaging, pedagogically sound, and culturally sensitive."
                }
            }
        },
        {
            # TEMPLATE 3: Inquiry-Based Lesson Planner
            "template": {
                "slug": "inquiry_lesson_planner",
                "name": "Inquiry-Based Lesson Planner",
                "description": "Create inquiry-based lesson plans with driving question, 5E phases (Engage → Explore → Explain → Elaborate → Evaluate), and claim-evidence-reasoning assessment.",
                "category": "lesson_design",
                "subject_default": None,
                "grade_bands_supported": ["K-2", "3-5", "6-8", "9-12"],
            },
            "version": {
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "subject": {
                            "type": "string",
                            "enum": ["english", "math", "science", "social_studies", "steam", "other"],
                            "title": "Subject"
                        },
                        "grade": {"type": "integer", "minimum": 0, "maximum": 12, "title": "Grade"},
                        "topic": {"type": "string", "title": "Topic"},
                        "learning_objective": {"type": "string", "title": "Learning objective"},
                        "time_duration_minutes": {"type": "integer", "minimum": 5, "maximum": 480, "title": "Time (minutes)"},
                        "bloom_level": {"type": "string", "title": "Bloom level", "description": "Often Analyze or Evaluate"},
                        "standards_framework": {"type": "string", "title": "Standards framework (optional)"},
                        "standard": {"type": "string", "title": "Standard code (optional)"},
                        "differentiation_needs": {"type": "boolean", "title": "Differentiation toggle"},
                        "differentiation_notes": {"type": "string", "title": "Differentiation notes (optional)"},
                        "materials": {"type": "string", "title": "Materials (optional)"},
                        "constraints": {"type": "string", "title": "Constraints (optional)"}
                    },
                    "required": ["subject", "grade", "topic", "learning_objective", "time_duration_minutes", "bloom_level"]
                },
                "output_schema": {
                    "type": "object",
                    "title": "InquiryLessonPlannerOutput",
                    "required": [
                        "title",
                        "driving_question",
                        "overview",
                        "lesson_flow",
                        "assessment",
                        "differentiation",
                        "bloom_alignment",
                        "teacher_notes"
                    ],
                    "properties": {
                        "title": {"type": "string", "title": "Title"},
                        "driving_question": {"type": "string", "title": "Driving question"},
                        "overview": {"type": "string", "title": "Overview"},
                        "lesson_flow": {
                            "type": "array",
                            "title": "Lesson phases",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "phase": {"type": "string", "title": "Phase"},
                                    "minutes": {"type": "integer", "title": "Minutes"},
                                    "teacher_role": {"type": "string", "title": "Teacher facilitation"},
                                    "student_role": {"type": "string", "title": "Student actions"}
                                },
                                "required": ["phase", "minutes", "teacher_role", "student_role"]
                            }
                        },
                        "assessment": {
                            "type": "object",
                            "title": "Evidence of learning (CER)",
                            "properties": {
                                "type": {"type": "string", "title": "Type"},
                                "prompt": {"type": "string", "title": "Prompt"},
                                "success_criteria": {"type": "array", "title": "Success criteria", "items": {"type": "string"}}
                            },
                            "required": ["type", "prompt", "success_criteria"]
                        },
                        "differentiation": {
                            "type": "object",
                            "title": "Differentiation",
                            "properties": {
                                "support": {"type": "array", "items": {"type": "string"}},
                                "extension": {"type": "array", "items": {"type": "string"}}
                            },
                            "required": ["support", "extension"]
                        },
                        "bloom_alignment": {
                            "type": "object",
                            "title": "Bloom alignment",
                            "properties": {"level": {"type": "string"}, "note": {"type": "string"}},
                            "required": ["level", "note"]
                        },
                        "standards_alignment": {
                            "type": "object",
                            "title": "Standards alignment (optional)",
                            "properties": {
                                "framework": {"type": "string"},
                                "code": {"type": "string"},
                                "note": {"type": "string"}
                            }
                        },
                        "teacher_notes": {"type": "array", "title": "Teacher notes", "items": {"type": "string"}}
                    }
                },
                "stub_config": {
                    "title_template": "How Do Humans Change Ecosystems?",
                    "driving_question_template": "How can one human activity disrupt an ecosystem, and what should be done about it?",
                    "overview_template": "Students investigate case studies and produce a claim supported by evidence and reasoning for {topic}.",
                    "lesson_flow": [
                        {"phase": "Engage", "minutes": 10, "teacher_role": "Show two contrasting ecosystem photos and ask students what changed.", "student_role": "Make observations and generate questions."},
                        {"phase": "Explore", "minutes": 20, "teacher_role": "Assign case studies: deforestation, overfishing, pollution.", "student_role": "Extract evidence: what changed, what species are affected, what chain reactions occur."},
                        {"phase": "Explain", "minutes": 10, "teacher_role": "Model cause-effect mapping and define 'biodiversity' and 'stability'.", "student_role": "Build a cause-effect map from their case."},
                        {"phase": "Elaborate", "minutes": 15, "teacher_role": "Prompt evaluation: 'Which intervention is most realistic and why?'", "student_role": "Propose one solution and justify it using evidence and trade-offs."},
                        {"phase": "Evaluate", "minutes": 5, "teacher_role": "Collect CER exit ticket.", "student_role": "Submit claim-evidence-reasoning response."}
                    ],
                    "assessment": {
                        "type": "CER_exit_ticket",
                        "prompt_template": "Make a claim about the impact of your human activity, provide 2 pieces of evidence from the case study, and explain your reasoning. Then recommend one solution and justify it.",
                        "success_criteria": [
                            "Claim is clear",
                            "Evidence is relevant and accurate",
                            "Reasoning explains cause-effect",
                            "Solution is justified with trade-offs"
                        ]
                    },
                    "differentiation": {
                        "support": [
                            "Provide CER sentence frames",
                            "Use simplified case study versions for readers who need it"
                        ],
                        "extension": [
                            "Compare two interventions and argue which is better",
                            "Add a second variable (climate change, invasive species) and predict combined impacts"
                        ]
                    },
                    "bloom_alignment": {
                        "level": "Analyze → Evaluate",
                        "note_template": "Students analyze cause-effect relationships and evaluate solutions with justification for {topic}."
                    },
                    "standards_alignment": {
                        "framework_template": "{standards_framework}",
                        "code_template": "{standard}",
                        "note_template": "Students construct arguments supported by evidence about ecosystem interactions."
                    },
                    "teacher_notes": [
                        "Push students past opinions: require evidence cited from the case study.",
                        "Trade-offs must be explicit (cost, feasibility, unintended effects)."
                    ]
                },
                "prompt_definition": {
                    "description": "Generate an inquiry-based lesson plan with a driving question, 5E phases (Engage, Explore, Explain, Elaborate, Evaluate), clear student and teacher roles per phase, and claim-evidence-reasoning (CER) assessment. Include differentiation and Bloom/standards alignment.",
                    "context": "This inquiry lesson will be used in international schools. It must promote investigation, evidence-based reasoning, and authentic scientific or disciplinary practices."
                }
            }
        },
        {
            # TEMPLATE 4: Multi-Lesson Unit Planner
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
                    "type": "object",
                    "properties": {
                        "subject": {"type": "string", "enum": ["english", "math", "science", "social_studies", "steam", "other"], "title": "Subject Area", "description": "Select the subject area for this lesson/activity. Choose the primary academic discipline that aligns with international curriculum standards (e.g., English Language Arts, Mathematics, Science, Social Studies, or STEAM)."},
                        "grade": {"type": "integer", "minimum": 0, "maximum": 12, "title": "Grade Level", "description": "Enter the grade level (0 for Kindergarten/K, 1-12 for grades 1-12). This ensures content is age-appropriate and aligns with international grade-level expectations (e.g., USA Common Core, UK National Curriculum, IB PYP/MYP/DP)."},
                        "grade_band": {"type": "string", "enum": ["K-2", "3-5", "6-8", "9-12"], "title": "Grade Band (Optional)", "description": "Optional: Select a grade band for broader age-group alignment. Useful for multi-grade classrooms or when targeting developmental stages rather than specific grades."},
                        "topic": {"type": "string", "title": "Topic or Learning Theme", "description": "Enter the specific topic, concept, or theme for this lesson/activity. Be specific and clear (e.g., 'Fractions and Decimals', 'The Water Cycle', 'Persuasive Writing', 'World War II'). This will be the central focus of the generated content."},
                        "learning_objective": {"type": "string", "title": "Learning Objective", "description": "State the learning objective using SMART criteria (Specific, Measurable, Achievable, Relevant, Time-bound). Example: 'Students will be able to solve multi-step word problems involving fractions and decimals with 80% accuracy.' This should align with international curriculum standards and Bloom's Taxonomy levels."},
                        "time_duration": {"type": "string", "title": "Time Duration", "description": "Specify the duration for this lesson/activity. Use clear formats like '45 minutes', '1 hour', '2 weeks', '90 minutes'. This helps ensure the generated content is appropriately paced for the available time."},
                        "time_duration_minutes": {"type": "integer", "minimum": 5, "maximum": 480, "title": "Duration in Minutes (Optional)", "description": "Optional: Enter the duration in minutes for more precise time allocation. This helps generate content with accurate time estimates for each section."},
                        "bloom_level": {"type": "string", "enum": ["Remember", "Understand", "Apply", "Analyze", "Evaluate", "Create", "Understand → Apply", "Analyze → Evaluate"], "title": "Bloom's Taxonomy Level", "description": "Select the cognitive level(s) from Bloom's Taxonomy that students will engage with. This ensures the content promotes appropriate levels of thinking: Remember (recall facts), Understand (comprehend meaning), Apply (use in new situations), Analyze (examine relationships), Evaluate (make judgments), Create (produce new work). You can select a progression (e.g., 'Understand → Apply') for lessons that build complexity."},
                        "standard": {"type": "string", "title": "Educational Standard (Optional)", "description": "Optional: Enter specific educational standards to align with (e.g., 'CCSS.MATH.CONTENT.6.EE.A.2', 'UK National Curriculum Year 7', 'IB MYP Criterion A', 'NGSS MS-LS1-1'). This ensures the generated content aligns with recognized international curriculum frameworks."},
                        "standards_framework": {"type": "string", "enum": ["CCSS", "UK_NATIONAL", "IB", "NGSS", "CAMBRIDGE", "EDEXCEL", "AQA", "AUSTRALIAN", "CANADIAN", "SINGAPORE", "OTHER"], "title": "Standards Framework (Optional)", "description": "Optional: Select the primary educational standards framework. This helps ensure content aligns with the appropriate international curriculum system (Common Core State Standards, UK National Curriculum, International Baccalaureate, Next Generation Science Standards, etc.)."},
                        "output_language": {"type": "string", "enum": ["English", "Spanish", "French", "German", "Italian", "Portuguese", "Chinese", "Japanese", "Korean", "Russian", "Arabic", "Hindi", "Urdu", "Other"], "title": "Output Language", "description": "Select the language for the generated content. All headings, instructions, and content will be generated in this language. Choose 'Other' if you need a language not listed and specify it in the 'Language' field below."},
                        "language": {"type": "string", "title": "Custom Language (if 'Other' selected)", "description": "If you selected 'Other' for Output Language, specify the language here. The system will attempt to generate content in this language."},
                        "differentiation_needs": {"type": "boolean", "title": "Include Differentiation Strategies", "description": "Check this box if you need specific differentiation strategies included in the generated content. This will add support for struggling learners, advanced learners, English Language Learners, and students with diverse learning styles - essential for international classrooms with diverse student populations."},
                        "differentiation_notes": {"type": "string", "title": "Differentiation Notes (Optional)", "description": "Optional: Provide specific information about student needs, learning differences, or accommodations required. This helps generate more targeted differentiation strategies (e.g., '3 ELL students at intermediate level', '2 students with ADHD need movement breaks', 'Advanced learners need extension activities')."},
                        "materials": {"type": "string", "title": "Available Materials (Optional)", "description": "Optional: List the materials, resources, or equipment available for this lesson/activity. Be specific (e.g., 'Whiteboards, markers, calculators, graph paper, access to tablets'). This ensures the generated content uses realistic, available resources."},
                        "available_materials": {"type": "array", "items": {"type": "string"}, "title": "Materials List (Optional)", "description": "Optional: Provide a list of available materials as separate items. This is useful when you have a specific inventory of resources."},
                        "constraints": {"type": "string", "title": "Constraints or Special Considerations (Optional)", "description": "Optional: Note any constraints, limitations, or special considerations for this lesson (e.g., 'No internet access', 'Limited space', 'Students must work in pairs', 'Cultural sensitivity required for diverse backgrounds'). This helps generate content that is practical and appropriate for your specific context."},
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
                "output_schema": {
                    "type": "object",
                    "title": "UniversalTemplateOutput",
                    "required": ["overview", "learning_goals", "materials", "steps"],
                    "properties": {
                        "overview": {"type": "string", "title": "Overview"},
                        "learning_goals": {"type": "array", "title": "Learning Goals", "items": {"type": "string"}},
                        "materials": {"type": "array", "title": "Materials", "items": {"type": "string"}},
                        "steps": {
                            "type": "array",
                            "title": "Steps",
                            "items": {
                                "type": "object",
                                "title": "LessonStep",
                                "required": ["title", "description"],
                                "properties": {"title": {"type": "string", "title": "Title"}, "description": {"type": "string", "title": "Description"}},
                            },
                        },
                        "differentiation": {"type": "array", "title": "Differentiation", "items": {"type": "string"}},
                        "assessment": {
                            "type": ["object", "null"],
                            "title": "AssessmentSection",
                            "properties": {
                                "checks_for_understanding": {"type": "array", "items": {"type": "string"}},
                                "rubric": {"type": ["object", "null"]},
                            },
                            "required": ["checks_for_understanding"],
                        },
                        "teacher_notes": {"type": "array", "title": "Teacher Notes", "items": {"type": "string"}},
                        "bloom_alignment": {
                            "type": "array",
                            "title": "Bloom Alignment",
                            "items": {
                                "type": "object",
                                "title": "BloomAlignmentItem",
                                "required": ["level", "description"],
                                "properties": {
                                    "level": {"type": "string", "enum": ["remember", "understand", "apply", "analyze", "evaluate", "create"]},
                                    "description": {"type": "string", "title": "Description"},
                                },
                            },
                        },
                        "questions": {
                            "type": ["array", "null"],
                            "title": "Questions",
                            "items": {
                                "type": "object",
                                "title": "AssessmentQuestion",
                                "required": ["question_text", "type"],
                                "properties": {
                                    "question_text": {"type": "string", "title": "Question Text"},
                                    "type": {"type": "string", "title": "Type"},
                                    "answer_key": {"type": ["string", "null"]},
                                    "difficulty": {"type": ["string", "null"]},
                                },
                            },
                        },
                        "communication": {
                            "type": ["object", "null"],
                            "title": "CommunicationSection",
                            "properties": {
                                "subject_line": {"type": ["string", "null"]},
                                "message_body": {"type": ["string", "null"]},
                                "key_details": {"type": ["array", "null"], "items": {"type": "string"}},
                                "call_to_action": {"type": ["string", "null"]},
                            },
                        },
                    },
                },
                "stub_config": {
                    "overview_template": "{template_name} for {subject}: {topic}",
                    "learning_goals_template": ["{learning_objective}", "Help students engage deeply with {topic}."],
                    "materials": ["Whiteboard or digital board", "Student notebooks or devices"],
                    "step_titles": ["Introduction & Activation of Prior Knowledge", "Guided Practice", "Independent or Small-Group Practice"],
                    "step_descriptions_template": "Briefly introduce {topic} and ask students what they already know.",
                    "differentiation": ["Offer sentence stems or visual supports for students who need additional scaffolding.", "Provide extension tasks for students who are ready for enrichment."],
                    "teacher_notes": ["Adjust pacing based on student responses and check-ins.", "Capture examples of strong student thinking to highlight during debrief."],
                    "assessment_checks": ["Cold-call a few students to explain the concept.", "Use exit tickets asking students to solve a short problem or respond to a prompt."],
                },
                "prompt_definition": {
                    "description": "Generate a comprehensive, internationally-aligned unit plan suitable for high-level schools with: Unit Overview, Weekly Breakdown, Learning Intentions, Success Criteria, Activities Weekly Planner, Assessments (Formative + Summative), Differentiation across unit, and Resources Needed. Ensure the unit plan demonstrates coherent learning progression, integrates multiple assessment strategies, and provides opportunities for deep understanding. Align with international curriculum standards and use evidence-based instructional design principles.",
                    "context": "This unit plan will be used in international schools. It must demonstrate academic rigor, coherent learning progression, and alignment with international educational standards."
                }
            }
        },
        {
            # TEMPLATE 5: Formative Assessment Generator
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
                        "subject": {"type": "string", "enum": ["english", "math", "science", "social_studies", "steam", "other"], "title": "Subject Area", "description": "Select the subject area for this lesson/activity. Choose the primary academic discipline that aligns with international curriculum standards (e.g., English Language Arts, Mathematics, Science, Social Studies, or STEAM)."},
                        "grade": {"type": "integer", "minimum": 0, "maximum": 12, "title": "Grade Level", "description": "Enter the grade level (0 for Kindergarten/K, 1-12 for grades 1-12). This ensures content is age-appropriate and aligns with international grade-level expectations (e.g., USA Common Core, UK National Curriculum, IB PYP/MYP/DP)."},
                        "grade_band": {"type": "string", "enum": ["K-2", "3-5", "6-8", "9-12"], "title": "Grade Band (Optional)", "description": "Optional: Select a grade band for broader age-group alignment. Useful for multi-grade classrooms or when targeting developmental stages rather than specific grades."},
                        "topic": {"type": "string", "title": "Topic or Learning Theme", "description": "Enter the specific topic, concept, or theme for this lesson/activity. Be specific and clear (e.g., 'Fractions and Decimals', 'The Water Cycle', 'Persuasive Writing', 'World War II'). This will be the central focus of the generated content."},
                        "learning_objective": {"type": "string", "title": "Learning Objective", "description": "State the learning objective using SMART criteria (Specific, Measurable, Achievable, Relevant, Time-bound). Example: 'Students will be able to solve multi-step word problems involving fractions and decimals with 80% accuracy.' This should align with international curriculum standards and Bloom's Taxonomy levels."},
                        "bloom_level": {"type": "string", "enum": ["Remember", "Understand", "Apply", "Analyze", "Evaluate", "Create", "Understand → Apply", "Analyze → Evaluate"], "title": "Bloom's Taxonomy Level", "description": "Select the cognitive level(s) from Bloom's Taxonomy that students will engage with. This ensures the content promotes appropriate levels of thinking: Remember (recall facts), Understand (comprehend meaning), Apply (use in new situations), Analyze (examine relationships), Evaluate (make judgments), Create (produce new work). You can select a progression (e.g., 'Understand → Apply') for lessons that build complexity."},
                        "standard": {"type": "string", "title": "Educational Standard (Optional)", "description": "Optional: Enter specific educational standards to align with (e.g., 'CCSS.MATH.CONTENT.6.EE.A.2', 'UK National Curriculum Year 7', 'IB MYP Criterion A', 'NGSS MS-LS1-1'). This ensures the generated content aligns with recognized international curriculum frameworks."},
                        "standards_framework": {"type": "string", "enum": ["CCSS", "UK_NATIONAL", "IB", "NGSS", "CAMBRIDGE", "EDEXCEL", "AQA", "AUSTRALIAN", "CANADIAN", "SINGAPORE", "OTHER"], "title": "Standards Framework (Optional)", "description": "Optional: Select the primary educational standards framework. This helps ensure content aligns with the appropriate international curriculum system (Common Core State Standards, UK National Curriculum, International Baccalaureate, Next Generation Science Standards, etc.)."},
                        "output_language": {"type": "string", "enum": ["English", "Spanish", "French", "German", "Italian", "Portuguese", "Chinese", "Japanese", "Korean", "Russian", "Arabic", "Hindi", "Urdu", "Other"], "title": "Output Language", "description": "Select the language for the generated content. All headings, instructions, and content will be generated in this language. Choose 'Other' if you need a language not listed and specify it in the 'Language' field below."},
                        "language": {"type": "string", "title": "Custom Language (if 'Other' selected)", "description": "If you selected 'Other' for Output Language, specify the language here. The system will attempt to generate content in this language."},
                        "time_duration": {"type": "string", "title": "Time Duration", "description": "Specify the duration for this lesson/activity. Use clear formats like '45 minutes', '1 hour', '2 weeks', '90 minutes'. This helps ensure the generated content is appropriately paced for the available time."},
                        "time_duration_minutes": {"type": "integer", "minimum": 5, "maximum": 480, "title": "Duration in Minutes (Optional)", "description": "Optional: Enter the duration in minutes for more precise time allocation. This helps generate content with accurate time estimates for each section."},
                        "assessment_type": {
                            "type": "string",
                            "enum": ["exit_ticket", "mini_quiz", "discussion_check"],
                            "title": "Formative Assessment Type",
                            "description": "Select the type of quick formative assessment. Exit Ticket: Brief end-of-lesson check (1-2 questions, typically 2-3 minutes). Mini Quiz: Short assessment with 3-5 questions (typically 5-10 minutes). Discussion Check: Oral or written response to prompt questions (typically 5-15 minutes). Choose the format that best fits your time constraints and assessment goals for international classroom contexts."
                        },
                        "differentiation_needs": {"type": "boolean", "title": "Include Differentiation Strategies", "description": "Check this box if you need specific differentiation strategies included in the generated content. This will add support for struggling learners, advanced learners, English Language Learners, and students with diverse learning styles - essential for international classrooms with diverse student populations."},
                        "differentiation_notes": {"type": "string", "title": "Differentiation Notes (Optional)", "description": "Optional: Provide specific information about student needs, learning differences, or accommodations required. This helps generate more targeted differentiation strategies (e.g., '3 ELL students at intermediate level', '2 students with ADHD need movement breaks', 'Advanced learners need extension activities')."}
                    },
                    "required": ["subject", "grade", "topic", "assessment_type", "bloom_level", "time_duration"]
                },
                "output_schema": {
                    "type": "object",
                    "title": "UniversalTemplateOutput",
                    "required": ["overview", "learning_goals", "materials", "steps"],
                    "properties": {
                        "overview": {"type": "string", "title": "Overview"},
                        "learning_goals": {"type": "array", "title": "Learning Goals", "items": {"type": "string"}},
                        "materials": {"type": "array", "title": "Materials", "items": {"type": "string"}},
                        "steps": {
                            "type": "array",
                            "title": "Steps",
                            "items": {
                                "type": "object",
                                "title": "LessonStep",
                                "required": ["title", "description"],
                                "properties": {"title": {"type": "string", "title": "Title"}, "description": {"type": "string", "title": "Description"}},
                            },
                        },
                        "differentiation": {"type": "array", "title": "Differentiation", "items": {"type": "string"}},
                        "assessment": {
                            "type": ["object", "null"],
                            "title": "AssessmentSection",
                            "properties": {
                                "checks_for_understanding": {"type": "array", "items": {"type": "string"}},
                                "rubric": {"type": ["object", "null"]},
                            },
                            "required": ["checks_for_understanding"],
                        },
                        "teacher_notes": {"type": "array", "title": "Teacher Notes", "items": {"type": "string"}},
                        "bloom_alignment": {
                            "type": "array",
                            "title": "Bloom Alignment",
                            "items": {
                                "type": "object",
                                "title": "BloomAlignmentItem",
                                "required": ["level", "description"],
                                "properties": {
                                    "level": {"type": "string", "enum": ["remember", "understand", "apply", "analyze", "evaluate", "create"]},
                                    "description": {"type": "string", "title": "Description"},
                                },
                            },
                        },
                        "questions": {
                            "type": ["array", "null"],
                            "title": "Questions",
                            "items": {
                                "type": "object",
                                "title": "AssessmentQuestion",
                                "required": ["question_text", "type"],
                                "properties": {
                                    "question_text": {"type": "string", "title": "Question Text"},
                                    "type": {"type": "string", "title": "Type"},
                                    "answer_key": {"type": ["string", "null"]},
                                    "difficulty": {"type": ["string", "null"]},
                                },
                            },
                        },
                        "communication": {
                            "type": ["object", "null"],
                            "title": "CommunicationSection",
                            "properties": {
                                "subject_line": {"type": ["string", "null"]},
                                "message_body": {"type": ["string", "null"]},
                                "key_details": {"type": ["array", "null"], "items": {"type": "string"}},
                                "call_to_action": {"type": ["string", "null"]},
                            },
                        },
                    },
                },
                "stub_config": {
                    "overview_template": "{template_name} for {subject}: {topic}",
                    "learning_goals_template": ["{learning_objective}", "Help students engage deeply with {topic}."],
                    "materials": ["Whiteboard or digital board", "Student notebooks or devices"],
                    "step_titles": ["Introduction & Activation of Prior Knowledge", "Guided Practice", "Independent or Small-Group Practice"],
                    "step_descriptions_template": "Briefly introduce {topic} and ask students what they already know.",
                    "differentiation": ["Offer sentence stems or visual supports for students who need additional scaffolding.", "Provide extension tasks for students who are ready for enrichment."],
                    "teacher_notes": ["Adjust pacing based on student responses and check-ins.", "Capture examples of strong student thinking to highlight during debrief."],
                    "assessment_checks": ["Cold-call a few students to explain the concept.", "Use exit tickets asking students to solve a short problem or respond to a prompt."],
                },
                "prompt_definition": {
                    "description": "Generate a high-quality formative assessment suitable for international classrooms with: Assessment Type, Learning Target, 3-5 Quick Questions, Answer Key, Common Misconceptions, and Differentiation Prompt. Ensure questions assess deep understanding, not just surface knowledge. Include questions at various Bloom's Taxonomy levels. Provide clear answer keys with explanations. Address common misconceptions with pedagogical guidance.",
                    "context": "This assessment will be used in international schools. Questions must be academically rigorous and assess genuine understanding."
                }
            }
        },
        {
            # TEMPLATE 6: Summative Assessment / Test Builder
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
                        "subject": {"type": "string", "enum": ["english", "math", "science", "social_studies", "steam", "other"], "title": "Subject Area", "description": "Select the subject area for this lesson/activity. Choose the primary academic discipline that aligns with international curriculum standards (e.g., English Language Arts, Mathematics, Science, Social Studies, or STEAM)."},
                        "grade": {"type": "integer", "minimum": 0, "maximum": 12, "title": "Grade Level", "description": "Enter the grade level (0 for Kindergarten/K, 1-12 for grades 1-12). This ensures content is age-appropriate and aligns with international grade-level expectations (e.g., USA Common Core, UK National Curriculum, IB PYP/MYP/DP)."},
                        "grade_band": {"type": "string", "enum": ["K-2", "3-5", "6-8", "9-12"], "title": "Grade Band (Optional)", "description": "Optional: Select a grade band for broader age-group alignment. Useful for multi-grade classrooms or when targeting developmental stages rather than specific grades."},
                        "topic": {"type": "string", "title": "Topic or Learning Theme", "description": "Enter the specific topic, concept, or theme for this lesson/activity. Be specific and clear (e.g., 'Fractions and Decimals', 'The Water Cycle', 'Persuasive Writing', 'World War II'). This will be the central focus of the generated content."},
                        "learning_objective": {"type": "string", "title": "Learning Objective", "description": "State the learning objective using SMART criteria (Specific, Measurable, Achievable, Relevant, Time-bound). Example: 'Students will be able to solve multi-step word problems involving fractions and decimals with 80% accuracy.' This should align with international curriculum standards and Bloom's Taxonomy levels."},
                        "bloom_level": {"type": "string", "enum": ["Remember", "Understand", "Apply", "Analyze", "Evaluate", "Create", "Understand → Apply", "Analyze → Evaluate"], "title": "Bloom's Taxonomy Level", "description": "Select the cognitive level(s) from Bloom's Taxonomy that students will engage with. This ensures the content promotes appropriate levels of thinking: Remember (recall facts), Understand (comprehend meaning), Apply (use in new situations), Analyze (examine relationships), Evaluate (make judgments), Create (produce new work). You can select a progression (e.g., 'Understand → Apply') for lessons that build complexity."},
                        "standard": {"type": "string", "title": "Educational Standard (Optional)", "description": "Optional: Enter specific educational standards to align with (e.g., 'CCSS.MATH.CONTENT.6.EE.A.2', 'UK National Curriculum Year 7', 'IB MYP Criterion A', 'NGSS MS-LS1-1'). This ensures the generated content aligns with recognized international curriculum frameworks."},
                        "standards_framework": {"type": "string", "enum": ["CCSS", "UK_NATIONAL", "IB", "NGSS", "CAMBRIDGE", "EDEXCEL", "AQA", "AUSTRALIAN", "CANADIAN", "SINGAPORE", "OTHER"], "title": "Standards Framework (Optional)", "description": "Optional: Select the primary educational standards framework. This helps ensure content aligns with the appropriate international curriculum system (Common Core State Standards, UK National Curriculum, International Baccalaureate, Next Generation Science Standards, etc.)."},
                        "output_language": {"type": "string", "enum": ["English", "Spanish", "French", "German", "Italian", "Portuguese", "Chinese", "Japanese", "Korean", "Russian", "Arabic", "Hindi", "Urdu", "Other"], "title": "Output Language", "description": "Select the language for the generated content. All headings, instructions, and content will be generated in this language. Choose 'Other' if you need a language not listed and specify it in the 'Language' field below."},
                        "language": {"type": "string", "title": "Custom Language (if 'Other' selected)", "description": "If you selected 'Other' for Output Language, specify the language here. The system will attempt to generate content in this language."},
                        "question_types": {
                            "type": "array",
                            "items": {"type": "string", "enum": ["MCQ", "short_answer", "diagram", "essay", "matching"]},
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
                "output_schema": {
                    "type": "object",
                    "title": "SummativeAssessmentOutput",
                    "required": [
                        "test_overview",
                        "learning_goals",
                        "instructions",
                        "rubric",
                        "questions_section",
                        "answer_key",
                        "bloom_categorization",
                    ],
                    "properties": {
                        "test_overview": {"type": "string", "title": "Test Overview", "description": "Brief overview of the assessment: purpose, format, and what is being assessed."},
                        "learning_goals": {"type": "array", "title": "Learning Goals", "items": {"type": "string"}, "description": "Learning objectives this assessment measures."},
                        "instructions": {"type": "string", "title": "Instructions", "description": "Clear instructions for students: time allowed, how to answer, formatting rules."},
                        "rubric": {"type": "string", "title": "Rubric / Marking Guide", "description": "Marking rubric in readable form: performance levels (e.g. Beginning, Developing, Proficient, Advanced) with clear criteria for each. Use prose or bullet points, not raw JSON."},
                        "questions_section": {"type": "string", "title": "Questions", "description": "All questions by type. Number each question (1., 2., 3.). For MCQ list options A, B, C, D only — do NOT give the correct answer here; correct answers go only in Answer Key."},
                        "answer_key": {"type": "string", "title": "Answer Key", "description": "Numbered list matching each question: e.g. '1. B', '2. D', '3. A' for MCQ, or brief marking points for open questions. Must correspond one-to-one with question numbers. Do not write unrelated text."},
                        "bloom_categorization": {"type": "string", "title": "Bloom Categorization", "description": "One short line per question (e.g. '1. Apply; 2. Understand; 3. Analyze') or a short summary. No long paragraphs."},
                    },
                },
                "stub_config": {
                    "test_overview": "Summative assessment for {topic} at grade {grade}. Assesses {learning_objective}.",
                    "learning_goals": ["{learning_objective}", "Demonstrate understanding of {topic}."],
                    "instructions": "Answer all questions. Short answer: write in full sentences. Essay: plan before writing. Time: as specified per section.",
                    "rubric": "Proficient: Meets all criteria with clear evidence. Developing: Partial understanding. Beginning: Limited evidence. Advanced: Exceeds expectations with depth.",
                    "questions_section": "Short Answer: 3 questions. Essay: 1 extended response. See rubric for marking.",
                    "answer_key": "Answers and marking points will be provided in the full assessment.",
                    "bloom_categorization": "Questions align with {bloom_level} level(s) as specified.",
                },
                "prompt_definition": {
                    "description": "Generate a summative assessment with exactly these sections in order. (1) Test Overview — brief purpose and format. (2) Learning Goals — bullet list of what the test measures. (3) Instructions — clear student-facing rules and timing. (4) Rubric / Marking Guide — performance levels (Beginning, Developing, Proficient, Advanced) with criteria in prose or bullets. (5) Questions — number each question (1., 2., 3.); for MCQ show only question text and options A, B, C, D; do NOT reveal the correct answer in this section. (6) Answer Key — a numbered list that exactly matches the questions: for MCQ write '1. B', '2. D', etc.; for short answer/essay write brief marking points. The Answer Key must be the correct answer for each question number only; no unrelated sentences. (7) Bloom Categorization — one short line per question (e.g. '1. Apply; 2. Understand') or a brief summary. Write all sections in clear, human-readable form. No raw JSON. Match the question types and difficulty the user requested.",
                    "context": "This assessment is for international schools. The Answer Key must correspond one-to-one with question numbers. Do not put correct answers inline under each question; put them only in the Answer Key section."
                }
            }
        },
        {
            # TEMPLATE 7: Behavior / SEL Activity Builder
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
                    "type": "object",
                    "properties": {
                        "grade": {"type": "integer", "minimum": 0, "maximum": 12, "title": "Grade"},
                        "topic": {"type": "string", "title": "Topic", "description": "e.g. Start-of-year community building"},
                        "goal": {
                            "type": "string",
                            "enum": ["community building", "teamwork", "getting to know each other"],
                            "title": "Goal (optional)"
                        },
                        "time_duration_minutes": {"type": "integer", "minimum": 5, "maximum": 120, "title": "Time (minutes)"},
                        "class_size": {"type": "integer", "minimum": 1, "maximum": 500, "title": "Class size (optional)"},
                        "constraints": {"type": "string", "title": "Constraints (optional)", "description": "e.g. shy students, new class, no movement"},
                        "bloom_level": {"type": "string", "title": "Bloom level (optional)", "description": "Usually Understand or Apply"},
                        "standards_framework": {"type": "string", "title": "Standards framework (optional)", "description": "SEL frameworks if provided"},
                        "standard": {"type": "string", "title": "Standard code (optional)"},
                        "differentiation_needs": {"type": "boolean", "title": "Include differentiation"},
                        "differentiation_notes": {"type": "string", "title": "Differentiation notes (optional)"},
                        "materials": {"type": "string", "title": "Materials (optional)"}
                    },
                    "required": ["grade", "topic", "time_duration_minutes"]
                },
                "output_schema": {
                    "type": "object",
                    "title": "ClassroomIcebreakerOutput",
                    "required": [
                        "title",
                        "purpose",
                        "time_needed",
                        "grouping",
                        "materials",
                        "steps",
                        "reflection_prompts",
                        "differentiation",
                        "bloom_alignment",
                        "teacher_notes"
                    ],
                    "properties": {
                        "title": {"type": "string", "title": "Title"},
                        "purpose": {"type": "string", "title": "Purpose"},
                        "time_needed": {"type": "integer", "title": "Time needed (minutes)"},
                        "grouping": {"type": "string", "title": "Grouping"},
                        "materials": {"type": "array", "title": "Materials", "items": {"type": "string"}},
                        "steps": {"type": "array", "title": "Steps", "items": {"type": "string"}},
                        "reflection_prompts": {"type": "array", "title": "Debrief/reflection prompts", "items": {"type": "string"}},
                        "differentiation": {
                            "type": "object",
                            "title": "Differentiation",
                            "properties": {
                                "support": {"type": "array", "title": "Support", "items": {"type": "string"}},
                                "extension": {"type": "array", "title": "Extension", "items": {"type": "string"}}
                            },
                            "required": ["support", "extension"]
                        },
                        "bloom_alignment": {
                            "type": "object",
                            "title": "Bloom alignment",
                            "properties": {"level": {"type": "string"}, "note": {"type": "string"}},
                            "required": ["level", "note"]
                        },
                        "teacher_notes": {"type": "array", "title": "Teacher notes", "items": {"type": "string"}}
                    }
                },
                "stub_config": {
                    "title_template": "Find Your Common Ground",
                    "purpose_template": "Students discover shared interests safely and build early trust for {topic}.",
                    "time_needed": 20,
                    "grouping_template": "Small groups of 4",
                    "materials": ["Sticky notes", "Markers"],
                    "steps_template": [
                        "Each student writes 3 low-risk facts (e.g., favorite food, hobby, music genre) on sticky notes.",
                        "In groups, students place notes on a table and sort them into 'shared' vs 'unique'.",
                        "Groups create one 'We are the kind of group that...' statement based on what they share.",
                        "Each group shares their statement with the class."
                    ],
                    "reflection_prompts": [
                        "What did you learn about your classmates that surprised you?",
                        "How can shared interests help teamwork this year?"
                    ],
                    "differentiation": {
                        "support": [
                            "Provide a list of safe prompts to choose from",
                            "Allow students to write instead of speak"
                        ],
                        "extension": [
                            "Have groups set one teamwork norm based on what they learned",
                            "Connect shared interests to a group goal for the semester"
                        ]
                    },
                    "bloom_alignment": {
                        "level": "Understand",
                        "note_template": "Students explain meaning and connections rather than just listing facts for {topic}."
                    },
                    "teacher_notes": [
                        "Keep prompts low-risk to protect privacy and cultural comfort.",
                        "Model examples that are appropriate and inclusive."
                    ]
                },
                "prompt_definition": {
                    "description": "Generate a culturally-sensitive SEL activity suitable for international, diverse classrooms with: SEL Activity Title, Purpose, Materials (if needed), Steps, Reflection Questions, and Teacher Notes. Ensure the activity promotes social-emotional learning, cultural awareness, empathy, and inclusivity. Activities should be appropriate for diverse student populations and respect different cultural perspectives.",
                    "context": "This SEL activity will be used in international schools with diverse student populations. It must be culturally sensitive and promote inclusivity."
                }
            }
        },
        {
            # TEMPLATE 8: Classroom Management Plan Generator
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
                            "title": "Grade",
                            "description": "Numeric grade level (0 for Kindergarten, 1–12 for grades 1–12)."
                        },
                        "class_size": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 50,
                            "title": "Class Size",
                            "description": "Number of students in the class."
                        },
                        "behavior_focus": {
                            "type": "string",
                            "enum": ["noise", "low_attention", "routine"],
                            "title": "Behavior Focus",
                            "description": "Primary behavior focus (e.g. noise, low attention, routines)."
                        },
                        "teacher_style": {
                            "type": "string",
                            "enum": ["warm_strict", "authoritative", "student_led", "collaborative"],
                            "title": "Teacher Style",
                            "description": "Overall classroom management style (e.g. warm_strict)."
                        },
                        "differentiation_needs": {
                            "type": "boolean",
                            "title": "Include Differentiation",
                            "description": "Whether to include specific differentiation supports in the plan."
                        }
                    },
                    "required": ["grade", "class_size", "behavior_focus", "teacher_style"]
                },
                "output_schema": {
                    "type": "object",
                    "title": "ClassroomManagementPlanOutput",
                    "required": [
                        "classroom_philosophy",
                        "rules",
                        "routines",
                        "reinforcement",
                        "correction_ladder",
                        "scripts",
                        "differentiation"
                    ],
                    "properties": {
                        "classroom_philosophy": {"type": "string", "title": "Classroom Philosophy"},
                        "rules": {
                            "type": "array",
                            "title": "Rules",
                            "items": {"type": "string"}
                        },
                        "routines": {
                            "type": "object",
                            "title": "Routines",
                            "properties": {
                                "entry": {"type": "string", "title": "Entry Routine"},
                                "transition": {"type": "string", "title": "Transition Routine"}
                            }
                        },
                        "reinforcement": {
                            "type": "array",
                            "title": "Reinforcement Strategies",
                            "items": {"type": "string"}
                        },
                        "correction_ladder": {
                            "type": "array",
                            "title": "Correction Ladder",
                            "items": {"type": "string"}
                        },
                        "scripts": {
                            "type": "object",
                            "title": "Teacher Scripts",
                            "properties": {
                                "redirect": {"type": "string", "title": "Redirect Script"},
                                "choice": {"type": "string", "title": "Choice Script"}
                            }
                        },
                        "differentiation": {
                            "type": "object",
                            "title": "Differentiation Supports",
                            "properties": {
                                "support": {
                                    "type": "array",
                                    "title": "Support Strategies",
                                    "items": {"type": "string"}
                                }
                            }
                        }
                    }
                },
                "stub_config": {
                    "classroom_philosophy_template": "Clear expectations with consistent reinforcement, tailored to grade {grade} and a {teacher_style} style.",
                    "rules": [
                        "Raise hand to speak",
                        "Respect classmates",
                        "Follow directions the first time"
                    ],
                    "routines": {
                        "entry_template": "Enter quietly and begin Do Now immediately.",
                        "transition_template": "Teacher uses a 5-second countdown signal and visual cue."
                    },
                    "reinforcement": [
                        "Specific, labeled praise for meeting expectations.",
                        "Positive call or email home for consistent effort."
                    ],
                    "correction_ladder": [
                        "Non-verbal cue (proximity, eye contact, gesture).",
                        "Private reminder naming the expectation.",
                        "Logical consequence connected to the behavior."
                    ],
                    "scripts": {
                        "redirect_template": "Please show me you're ready to learn by following our class rule: {behavior_focus}.",
                        "choice_template": "You can choose to follow the expectation now or we will make up the time later."
                    },
                    "differentiation": {
                        "support": [
                            "Use a visual timer to support transitions.",
                            "Provide planned movement breaks for students who need them."
                        ]
                    }
                },
                "prompt_definition": {
                    "description": "Generate a comprehensive classroom management plan suitable for international schools with: Classroom Rules, Daily Routines, Reinforcement Strategies, Tiered Interventions, and Parent Communication Note. Ensure the plan is culturally sensitive, promotes positive behavior, and uses evidence-based strategies. Include tiered intervention approaches that respect diverse student needs and cultural backgrounds.",
                    "context": "This management plan will be used in international schools. It must be culturally appropriate and use research-based behavior management strategies."
                }
            }
        },
        {
            # TEMPLATE 9: English Skills Builder (Reading/Writing)
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
                        "grade": {"type": "integer", "minimum": 0, "maximum": 12, "title": "Grade"},
                        "focus": {
                            "type": "string",
                            "enum": ["reading", "writing", "vocabulary"],
                            "title": "Focus"
                        },
                        "topic": {"type": "string", "title": "Topic"},
                        "learning_objective": {"type": "string", "title": "Learning Objective"},
                        "time_duration_minutes": {"type": "integer", "minimum": 5, "maximum": 480, "title": "Time (minutes)"},
                        "bloom_level": {"type": "string", "title": "Bloom Level"},
                        "standards_framework": {"type": "string", "title": "Standards Framework (optional)"},
                        "standard": {"type": "string", "title": "Standard code (optional)"},
                        "differentiation_needs": {"type": "boolean", "title": "Differentiation on/off"},
                        "differentiation_notes": {"type": "string", "title": "Differentiation notes (optional)"},
                        "materials": {"type": "string", "title": "Materials (optional)"},
                        "constraints": {"type": "string", "title": "Constraints (optional)"},
                        "output_language": {"type": "string", "title": "Output language (optional)"},
                        "language": {"type": "string", "title": "Custom language if Other (optional)"}
                    },
                    "required": ["grade", "focus", "topic", "learning_objective", "time_duration_minutes", "bloom_level"]
                },
                "output_schema": {
                    "type": "object",
                    "title": "EnglishSkillsBuilderOutput",
                    "required": [
                        "title",
                        "overview",
                        "learning_objectives",
                        "success_criteria",
                        "mini_lesson",
                        "guided_practice",
                        "independent_task",
                        "assessment",
                        "differentiation",
                        "bloom_alignment",
                        "teacher_notes"
                    ],
                    "properties": {
                        "title": {"type": "string", "title": "Title"},
                        "overview": {"type": "string", "title": "Overview / Skill focus"},
                        "learning_objectives": {"type": "array", "title": "Learning objectives", "items": {"type": "string"}},
                        "success_criteria": {"type": "array", "title": "Success criteria", "items": {"type": "string"}},
                        "mini_lesson": {
                            "type": "object",
                            "title": "Mini-lesson",
                            "properties": {
                                "teacher_model": {"type": "string", "title": "Teacher script / model"},
                                "key_point": {"type": "string", "title": "Key point"}
                            },
                            "required": ["teacher_model", "key_point"]
                        },
                        "guided_practice": {
                            "type": "object",
                            "title": "Guided practice",
                            "properties": {
                                "activity": {"type": "string", "title": "Activity"},
                                "teacher_prompts": {"type": "array", "title": "Teacher prompts", "items": {"type": "string"}}
                            },
                            "required": ["activity", "teacher_prompts"]
                        },
                        "independent_task": {
                            "type": "object",
                            "title": "Independent task",
                            "properties": {
                                "task": {"type": "string", "title": "Task"},
                                "expected_answer_format": {"type": "string", "title": "Expected answer format"}
                            },
                            "required": ["task", "expected_answer_format"]
                        },
                        "assessment": {
                            "type": "object",
                            "title": "Assessment",
                            "properties": {
                                "type": {"type": "string", "title": "Type"},
                                "criteria": {"type": "array", "title": "Criteria", "items": {"type": "string"}}
                            },
                            "required": ["type", "criteria"]
                        },
                        "differentiation": {
                            "type": "object",
                            "title": "Differentiation",
                            "properties": {
                                "support": {"type": "array", "title": "Support", "items": {"type": "string"}},
                                "extension": {"type": "array", "title": "Extension", "items": {"type": "string"}}
                            },
                            "required": ["support", "extension"]
                        },
                        "bloom_alignment": {
                            "type": "object",
                            "title": "Bloom alignment",
                            "properties": {"level": {"type": "string"}, "note": {"type": "string"}},
                            "required": ["level", "note"]
                        },
                        "standards_alignment": {
                            "type": "object",
                            "title": "Standards alignment (if provided)",
                            "properties": {
                                "framework": {"type": "string"},
                                "code": {"type": "string"},
                                "note": {"type": "string"}
                            }
                        },
                        "teacher_notes": {"type": "array", "title": "Teacher notes", "items": {"type": "string"}}
                    }
                },
                "stub_config": {
                    "title_template": "Tracking Character Change With Evidence",
                    "overview_template": "Students read a short story excerpt and analyze how a main character changes from the beginning to the end for {topic}.",
                    "learning_objectives_template": [
                        "Identify key events that influence the character",
                        "Explain how the character changes over time",
                        "Support analysis with at least 2 direct quotes"
                    ],
                    "success_criteria": [
                        "I can describe the character at the beginning and end",
                        "I can include 2 accurate quotes",
                        "I can explain how the quotes show change"
                    ],
                    "mini_lesson": {
                        "teacher_model_template": "Read a short paragraph aloud and model thinking: 'At first, Jamal avoids responsibility... Later, he volunteers to help—this shows growth.' Focus on {topic}.",
                        "key_point_template": "Character change is shown through actions, choices, and responses to conflict."
                    },
                    "guided_practice": {
                        "activity_template": "Whole class completes a 'Beginning vs End' chart for the first half of the story.",
                        "teacher_prompts": [
                            "What action shows who the character is right now?",
                            "Which event pressures the character to change?"
                        ]
                    },
                    "independent_task": {
                        "task_template": "Complete the chart for the ending. Add 2 quotes (one from early, one from late) and write a 6–8 sentence explanation of the change.",
                        "expected_answer_format": "Chart + paragraph with evidence"
                    },
                    "assessment": {
                        "type": "quick_rubric",
                        "criteria": [
                            "Evidence is accurate and relevant",
                            "Explanation connects evidence to change",
                            "Writing is clear and mostly complete"
                        ]
                    },
                    "differentiation": {
                        "support": [
                            "Provide sentence starters: 'At the beginning, _ because _. Later, _ which shows _.'",
                            "Highlight 2–3 key paragraphs for ELL students"
                        ],
                        "extension": [
                            "Evaluate whether the change is believable and justify with evidence",
                            "Compare the main character's change to a secondary character"
                        ]
                    },
                    "bloom_alignment": {
                        "level": "Analyze",
                        "note_template": "Students examine relationships between events and character behavior, supported by evidence for {topic}."
                    },
                    "standards_alignment": {
                        "framework_template": "{standards_framework}",
                        "code_template": "{standard}",
                        "note_template": "Students analyze character development and cite textual evidence."
                    },
                    "teacher_notes": [
                        "Watch for summaries that don't explain change—require evidence + reasoning.",
                        "Common error: students pick quotes but don't connect them to character traits."
                    ]
                },
                "prompt_definition": {
                    "description": "Generate a rigorous English/ELA task aligned with international standards (CCSS, UK National Curriculum, IB, etc.) with: Mini-Lesson Goal, Skill Practice Activity, Guided Examples, Sentence Starters, Student Task, and Assessment Criteria. Ensure the task develops reading, writing, speaking, and listening skills. Include authentic texts and real-world applications. Provide clear assessment criteria that measure genuine literacy skills.",
                    "context": "This ELA task will be used in international schools. It must align with international literacy standards and promote authentic language learning."
                }
            }
        },
        {
            # TEMPLATE 10: Math Problem / Activity Builder
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
                        "grade": {"type": "integer", "minimum": 0, "maximum": 12, "title": "Grade"},
                        "topic": {"type": "string", "title": "Topic"},
                        "problem_type": {
                            "type": "string",
                            "enum": ["real_world", "game", "visual"],
                            "title": "Problem Type"
                        },
                        "bloom_level": {"type": "string", "title": "Bloom Level"},
                        "problem_count": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 50,
                            "title": "Problem Count"
                        },
                        "include_worked_solutions": {
                            "type": "boolean",
                            "title": "Include Worked Solutions"
                        }
                    },
                    "required": ["grade", "topic", "problem_type", "bloom_level", "problem_count"]
                },
                "output_schema": {
                    "type": "object",
                    "title": "MathTaskOutput",
                    "required": ["overview", "problems", "answer_key", "bloom_alignment"],
                    "properties": {
                        "overview": {"type": "string", "title": "Overview"},
                        "problems": {
                            "type": "array",
                            "title": "Problems",
                            "items": {
                                "type": "object",
                                "title": "MathProblem",
                                "required": ["question"],
                                "properties": {
                                    "question": {"type": "string", "title": "Question"},
                                    "expected_answer": {"type": "string", "title": "Expected Answer"},
                                    "worked_solution": {"type": "string", "title": "Worked Solution"}
                                }
                            }
                        },
                        "answer_key": {
                            "type": "array",
                            "title": "Answer Key",
                            "items": {
                                "type": "object",
                                "title": "AnswerKeyItem",
                                "required": ["problem", "answer"],
                                "properties": {
                                    "problem": {"type": "integer", "title": "Problem Number"},
                                    "answer": {"type": "string", "title": "Answer"}
                                }
                            }
                        },
                        "bloom_alignment": {
                            "type": "object",
                            "title": "Bloom Alignment",
                            "required": ["level", "note"],
                            "properties": {
                                "level": {"type": "string", "title": "Level"},
                                "note": {"type": "string", "title": "Note"}
                            }
                        }
                    }
                },
                "stub_config": {
                    "overview_template": "Practice solving proportional relationship problems for topic: {topic}.",
                    "problems": [
                        {
                            "question": "If 3 apples cost $6, how much do 5 apples cost?",
                            "expected_answer": "$10",
                            "worked_solution": "3/6 = 5/x → x = 10"
                        }
                    ],
                    "answer_key": [
                        {"problem": 1, "answer": "$10"}
                    ],
                    "bloom_alignment": {
                        "level": "Apply",
                        "note": "Students solve proportional equations correctly."
                    }
                },
                "prompt_definition": {
                    "description": "Generate a rigorous math problem/activity aligned with international standards (CCSS, UK National Curriculum, IB, etc.) with: Problem/Activity Title, Student Task, Steps / Game Instructions, Worked Example, and Extension Task. Ensure problems promote mathematical reasoning, problem-solving, and conceptual understanding. Include real-world applications and multiple solution strategies. Provide clear worked examples that demonstrate mathematical thinking processes.",
                    "context": "This math task will be used in international schools. It must align with international mathematics standards and promote deep mathematical understanding."
                }
            }
        },
        {
            # TEMPLATE 11: Science Experiment / Observation
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
                        "grade": {"type": "integer", "minimum": 0, "maximum": 12, "title": "Grade Level", "description": "Enter the grade level (0 for Kindergarten/K, 1-12 for grades 1-12). This ensures content is age-appropriate and aligns with international grade-level expectations (e.g., USA Common Core, UK National Curriculum, IB PYP/MYP/DP)."},
                        "grade_band": {"type": "string", "enum": ["K-2", "3-5", "6-8", "9-12"], "title": "Grade Band (Optional)", "description": "Optional: Select a grade band for broader age-group alignment. Useful for multi-grade classrooms or when targeting developmental stages rather than specific grades."},
                        "topic": {"type": "string", "title": "Topic or Learning Theme", "description": "Enter the specific topic, concept, or theme for this lesson/activity. Be specific and clear (e.g., 'Fractions and Decimals', 'The Water Cycle', 'Persuasive Writing', 'World War II'). This will be the central focus of the generated content."},
                        "learning_objective": {"type": "string", "title": "Learning Objective", "description": "State the learning objective using SMART criteria (Specific, Measurable, Achievable, Relevant, Time-bound). Example: 'Students will be able to solve multi-step word problems involving fractions and decimals with 80% accuracy.' This should align with international curriculum standards and Bloom's Taxonomy levels."},
                        "materials": {
                            "type": "array",
                            "items": {"type": "string"},
                            "title": "Required Materials",
                            "description": "List all materials, equipment, and resources needed for this science experiment or observation. Be specific and include quantities where relevant (e.g., 'Beakers (250ml) - 6', 'Safety goggles - 12 pairs', 'pH test strips - 1 pack', 'Digital microscope', 'Bunsen burner with safety equipment'). Include safety equipment and any special considerations for international school laboratory contexts. Ensure all materials meet international safety standards."
                        },
                        "bloom_level": {"type": "string", "enum": ["Remember", "Understand", "Apply", "Analyze", "Evaluate", "Create", "Understand → Apply", "Analyze → Evaluate"], "title": "Bloom's Taxonomy Level", "description": "Select the cognitive level(s) from Bloom's Taxonomy that students will engage with. This ensures the content promotes appropriate levels of thinking: Remember (recall facts), Understand (comprehend meaning), Apply (use in new situations), Analyze (examine relationships), Evaluate (make judgments), Create (produce new work). You can select a progression (e.g., 'Understand → Apply') for lessons that build complexity."},
                        "standard": {"type": "string", "title": "Educational Standard (Optional)", "description": "Optional: Enter specific educational standards to align with (e.g., 'CCSS.MATH.CONTENT.6.EE.A.2', 'UK National Curriculum Year 7', 'IB MYP Criterion A', 'NGSS MS-LS1-1'). This ensures the generated content aligns with recognized international curriculum frameworks."},
                        "standards_framework": {"type": "string", "enum": ["CCSS", "UK_NATIONAL", "IB", "NGSS", "CAMBRIDGE", "EDEXCEL", "AQA", "AUSTRALIAN", "CANADIAN", "SINGAPORE", "OTHER"], "title": "Standards Framework (Optional)", "description": "Optional: Select the primary educational standards framework. This helps ensure content aligns with the appropriate international curriculum system (Common Core State Standards, UK National Curriculum, International Baccalaureate, Next Generation Science Standards, etc.)."},
                        "output_language": {"type": "string", "enum": ["English", "Spanish", "French", "German", "Italian", "Portuguese", "Chinese", "Japanese", "Korean", "Russian", "Arabic", "Hindi", "Urdu", "Other"], "title": "Output Language", "description": "Select the language for the generated content. All headings, instructions, and content will be generated in this language. Choose 'Other' if you need a language not listed and specify it in the 'Language' field below."},
                        "language": {"type": "string", "title": "Custom Language (if 'Other' selected)", "description": "If you selected 'Other' for Output Language, specify the language here. The system will attempt to generate content in this language."},
                        "time_duration": {"type": "string", "title": "Time Duration", "description": "Specify the duration for this lesson/activity. Use clear formats like '45 minutes', '1 hour', '2 weeks', '90 minutes'. This helps ensure the generated content is appropriately paced for the available time."},
                        "time_duration_minutes": {"type": "integer", "minimum": 5, "maximum": 480, "title": "Duration in Minutes (Optional)", "description": "Optional: Enter the duration in minutes for more precise time allocation. This helps generate content with accurate time estimates for each section."},
                        "constraints": {"type": "string", "title": "Constraints or Special Considerations (Optional)", "description": "Optional: Note any constraints, limitations, or special considerations for this lesson (e.g., 'No internet access', 'Limited space', 'Students must work in pairs', 'Cultural sensitivity required for diverse backgrounds'). This helps generate content that is practical and appropriate for your specific context."}
                    },
                    "required": ["grade", "topic", "materials", "bloom_level"]
                },
                "output_schema": {
                    "type": "object",
                    "title": "UniversalTemplateOutput",
                    "required": ["overview", "learning_goals", "materials", "steps"],
                    "properties": {
                        "overview": {"type": "string", "title": "Overview"},
                        "learning_goals": {"type": "array", "title": "Learning Goals", "items": {"type": "string"}},
                        "materials": {"type": "array", "title": "Materials", "items": {"type": "string"}},
                        "steps": {
                            "type": "array",
                            "title": "Steps",
                            "items": {
                                "type": "object",
                                "title": "LessonStep",
                                "required": ["title", "description"],
                                "properties": {"title": {"type": "string", "title": "Title"}, "description": {"type": "string", "title": "Description"}},
                            },
                        },
                        "differentiation": {"type": "array", "title": "Differentiation", "items": {"type": "string"}},
                        "assessment": {
                            "type": ["object", "null"],
                            "title": "AssessmentSection",
                            "properties": {
                                "checks_for_understanding": {"type": "array", "items": {"type": "string"}},
                                "rubric": {"type": ["object", "null"]},
                            },
                            "required": ["checks_for_understanding"],
                        },
                        "teacher_notes": {"type": "array", "title": "Teacher Notes", "items": {"type": "string"}},
                        "bloom_alignment": {
                            "type": "array",
                            "title": "Bloom Alignment",
                            "items": {
                                "type": "object",
                                "title": "BloomAlignmentItem",
                                "required": ["level", "description"],
                                "properties": {
                                    "level": {"type": "string", "enum": ["remember", "understand", "apply", "analyze", "evaluate", "create"]},
                                    "description": {"type": "string", "title": "Description"},
                                },
                            },
                        },
                        "questions": {
                            "type": ["array", "null"],
                            "title": "Questions",
                            "items": {
                                "type": "object",
                                "title": "AssessmentQuestion",
                                "required": ["question_text", "type"],
                                "properties": {
                                    "question_text": {"type": "string", "title": "Question Text"},
                                    "type": {"type": "string", "title": "Type"},
                                    "answer_key": {"type": ["string", "null"]},
                                    "difficulty": {"type": ["string", "null"]},
                                },
                            },
                        },
                        "communication": {
                            "type": ["object", "null"],
                            "title": "CommunicationSection",
                            "properties": {
                                "subject_line": {"type": ["string", "null"]},
                                "message_body": {"type": ["string", "null"]},
                                "key_details": {"type": ["array", "null"], "items": {"type": "string"}},
                                "call_to_action": {"type": ["string", "null"]},
                            },
                        },
                    },
                },
                "stub_config": {
                    "overview_template": "{template_name} for {subject}: {topic}",
                    "learning_goals_template": ["{learning_objective}", "Help students engage deeply with {topic}."],
                    "materials": ["Whiteboard or digital board", "Student notebooks or devices"],
                    "step_titles": ["Introduction & Activation of Prior Knowledge", "Guided Practice", "Independent or Small-Group Practice"],
                    "step_descriptions_template": "Briefly introduce {topic} and ask students what they already know.",
                    "differentiation": ["Offer sentence stems or visual supports for students who need additional scaffolding.", "Provide extension tasks for students who are ready for enrichment."],
                    "teacher_notes": ["Adjust pacing based on student responses and check-ins.", "Capture examples of strong student thinking to highlight during debrief."],
                    "assessment_checks": ["Cold-call a few students to explain the concept.", "Use exit tickets asking students to solve a short problem or respond to a prompt."],
                },
                "prompt_definition": {
                    "description": "Generate a rigorous science experiment/observation aligned with international standards (NGSS, UK National Curriculum, IB, etc.) with: Experiment Title, Aim, Hypothesis, Materials, Procedure, Observation Table, Conclusion Prompt, and Safety Notes. Ensure the experiment promotes scientific inquiry, critical thinking, and authentic scientific practices. Include clear safety considerations and opportunities for students to develop scientific reasoning skills.",
                    "context": "This science experiment will be used in international schools. It must align with international science standards and promote authentic scientific inquiry."
                }
            }
        },
        {
            # TEMPLATE 12: STEAM Maker Activity
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
                        "grade": {"type": "integer", "minimum": 0, "maximum": 12, "title": "Grade"},
                        "topic": {"type": "string", "title": "Challenge Topic"},
                        "materials": {
                            "type": "array",
                            "items": {"type": "string"},
                            "title": "Materials"
                        },
                        "time_duration_minutes": {
                            "type": "integer",
                            "minimum": 5,
                            "maximum": 480,
                            "title": "Duration (minutes)"
                        },
                        "bloom_level": {"type": "string", "title": "Bloom Level"},
                        "constraints": {"type": "string", "title": "Constraints"}
                    },
                    "required": ["grade", "topic", "materials", "time_duration_minutes", "bloom_level"]
                },
                "output_schema": {
                    "type": "object",
                    "title": "SteamMakerActivityOutput",
                    "required": [
                        "challenge_title",
                        "challenge_brief",
                        "success_criteria",
                        "constraints",
                        "design_process",
                        "assessment",
                        "bloom_alignment"
                    ],
                    "properties": {
                        "challenge_title": {"type": "string", "title": "Challenge Title"},
                        "challenge_brief": {"type": "string", "title": "Challenge Brief"},
                        "success_criteria": {"type": "string", "title": "Success Criteria"},
                        "constraints": {
                            "type": "array",
                            "title": "Constraints",
                            "items": {"type": "string"}
                        },
                        "design_process": {
                            "type": "array",
                            "title": "Design Process",
                            "items": {"type": "string"}
                        },
                        "assessment": {
                            "type": "object",
                            "title": "Assessment",
                            "properties": {
                                "rubric": {
                                    "type": "array",
                                    "title": "Rubric",
                                    "items": {"type": "string"}
                                }
                            },
                            "required": ["rubric"]
                        },
                        "bloom_alignment": {
                            "type": "object",
                            "title": "Bloom Alignment",
                            "properties": {
                                "level": {"type": "string", "title": "Level"},
                                "note": {"type": "string", "title": "Note"}
                            },
                            "required": ["level", "note"]
                        }
                    }
                },
                "stub_config": {
                    "challenge_title_template": "Bridge Engineering Challenge",
                    "challenge_brief_template": "Design a bridge that holds the most coins.",
                    "success_criteria_template": "Holds at least 10 coins for 10 seconds.",
                    "constraints": ["Max 20 sticks"],
                    "design_process": [
                        "Sketch design",
                        "Build prototype",
                        "Test with coins",
                        "Improve design"
                    ],
                    "assessment": {
                        "rubric": [
                            "Meets constraints",
                            "Improves after testing"
                        ]
                    },
                    "bloom_alignment": {
                        "level": "Create",
                        "note": "Students design, test, and refine a solution."
                    }
                },
                "prompt_definition": {
                    "description": "Generate a rigorous STEAM maker activity suitable for international schools with: Challenge Statement, Build Instructions, Constraints, Testing Method, and Reflection. Ensure the activity integrates Science, Technology, Engineering, Arts, and Mathematics authentically. Promote design thinking, creativity, problem-solving, and collaboration. Include clear success criteria and opportunities for iterative improvement.",
                    "context": "This STEAM activity will be used in international schools. It must authentically integrate multiple disciplines and promote 21st-century skills."
                }
            }
        },
        {
            # TEMPLATE 13: Engineering Activity Suggestions
            "template": {
                "slug": "engineering_activity",
                "name": "Engineering Activity Suggestions",
                "description": "Create engineering-focused activities with challenge brief, build/test/iterate steps, and NGSS engineering practices alignment.",
                "category": "subject_specific",
                "subject_default": "steam",
                "grade_bands_supported": ["K-2", "3-5", "6-8", "9-12"],
            },
            "version": {
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "grade": {"type": "integer", "minimum": 0, "maximum": 12, "title": "Grade"},
                        "topic": {"type": "string", "title": "Engineering concept (topic)"},
                        "learning_objective": {"type": "string", "title": "Learning objective"},
                        "time_duration_minutes": {"type": "integer", "minimum": 5, "maximum": 480, "title": "Time (minutes)"},
                        "materials": {"type": "string", "title": "Materials available"},
                        "constraints": {"type": "string", "title": "Constraints (safety, time, space)"},
                        "bloom_level": {"type": "string", "title": "Bloom level", "description": "Often Apply or Create"},
                        "standards_framework": {"type": "string", "title": "Standards framework (optional)"},
                        "standard": {"type": "string", "title": "Standard code (optional)"},
                        "differentiation_needs": {"type": "boolean", "title": "Differentiation toggle"},
                        "differentiation_notes": {"type": "string", "title": "Differentiation notes (optional)"}
                    },
                    "required": ["grade", "topic", "time_duration_minutes", "bloom_level"]
                },
                "output_schema": {
                    "type": "object",
                    "title": "EngineeringActivityOutput",
                    "required": [
                        "title",
                        "concept_focus",
                        "challenge_brief",
                        "success_criteria",
                        "materials",
                        "steps",
                        "assessment",
                        "differentiation",
                        "bloom_alignment",
                        "teacher_notes"
                    ],
                    "properties": {
                        "title": {"type": "string", "title": "Activity title"},
                        "concept_focus": {"type": "string", "title": "Concept focus"},
                        "challenge_brief": {"type": "string", "title": "Challenge brief"},
                        "success_criteria": {"type": "array", "title": "Success criteria", "items": {"type": "string"}},
                        "materials": {"type": "array", "title": "Materials", "items": {"type": "string"}},
                        "steps": {"type": "array", "title": "Steps (build/test/iterate)", "items": {"type": "string"}},
                        "assessment": {
                            "type": "object",
                            "title": "Assessment rubric",
                            "properties": {
                                "type": {"type": "string", "title": "Type"},
                                "criteria": {"type": "array", "title": "Criteria", "items": {"type": "string"}}
                            },
                            "required": ["type", "criteria"]
                        },
                        "differentiation": {
                            "type": "object",
                            "title": "Differentiation",
                            "properties": {
                                "support": {"type": "array", "items": {"type": "string"}},
                                "extension": {"type": "array", "items": {"type": "string"}}
                            },
                            "required": ["support", "extension"]
                        },
                        "bloom_alignment": {
                            "type": "object",
                            "title": "Bloom alignment",
                            "properties": {"level": {"type": "string"}, "note": {"type": "string"}},
                            "required": ["level", "note"]
                        },
                        "standards_alignment": {
                            "type": "object",
                            "title": "Standards alignment (optional)",
                            "properties": {
                                "framework": {"type": "string"},
                                "code": {"type": "string"},
                                "note": {"type": "string"}
                            }
                        },
                        "teacher_notes": {"type": "array", "title": "Teacher notes", "items": {"type": "string"}}
                    }
                },
                "stub_config": {
                    "title_template": "Paper Truss Bridge Challenge",
                    "concept_focus_template": "Forces, load distribution, and structural stability using truss patterns for {topic}.",
                    "challenge_brief_template": "Build a paper bridge that spans 20 cm and holds the most coins before collapsing.",
                    "success_criteria": [
                        "Spans 20 cm without support in the middle",
                        "Holds coins for 10 seconds",
                        "Includes at least one truss pattern (triangle-based)"
                    ],
                    "materials": ["Paper", "Tape", "Scissors", "Coins"],
                    "steps": [
                        "Show 2 example truss patterns (simple triangles).",
                        "Teams sketch 2 designs and choose one with a reason.",
                        "Build prototype (15 minutes).",
                        "Test by adding coins one-by-one; record max load.",
                        "Improve ONE variable (add triangles, change width, reinforce joints).",
                        "Retest and compare results."
                    ],
                    "assessment": {
                        "type": "mini_rubric",
                        "criteria": [
                            "Meets constraints",
                            "Uses evidence from testing to improve design",
                            "Explains why the change increased/decreased strength"
                        ]
                    },
                    "differentiation": {
                        "support": [
                            "Provide a pre-made truss template students can fold",
                            "Assign clear roles (builder, recorder, tester)"
                        ],
                        "extension": [
                            "Optimize strength-to-material ratio (use less tape)",
                            "Explain failure points using force vocabulary (compression/tension)"
                        ]
                    },
                    "bloom_alignment": {
                        "level": "Create",
                        "note_template": "Students design, test, and iterate to produce an improved structure for {topic}."
                    },
                    "standards_alignment": {
                        "framework_template": "{standards_framework}",
                        "code_template": "{standard}",
                        "note_template": "Students evaluate solutions using systematic testing and constraints."
                    },
                    "teacher_notes": [
                        "Iteration is required—don't stop after one test.",
                        "Ensure groups record results to justify improvements."
                    ]
                },
                "prompt_definition": {
                    "description": "Generate an engineering-focused activity with: Activity title, Concept focus, Challenge brief, Success criteria, Materials, Steps (build/test/iterate), Assessment rubric, Differentiation, and Bloom/standards alignment. Align with NGSS engineering practices or local framework where provided.",
                    "context": "This engineering activity will be used in international schools. It must promote design thinking, safe testing, and iterative improvement with clear constraints."
                }
            }
        },
        {
            # TEMPLATE 14: Art Exploration
            "template": {
                "slug": "art_exploration",
                "name": "Art Exploration",
                "description": "Create art activities with theme, medium, warm-up → create → share/reflect steps, and optional artist reference.",
                "category": "subject_specific",
                "subject_default": "other",
                "grade_bands_supported": ["K-2", "3-5", "6-8", "9-12"],
            },
            "version": {
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "grade": {"type": "integer", "minimum": 0, "maximum": 12, "title": "Grade"},
                        "topic": {"type": "string", "title": "Art theme/topic"},
                        "learning_objective": {"type": "string", "title": "Learning objective"},
                        "medium": {
                            "type": "string",
                            "enum": ["drawing", "painting", "collage", "digital"],
                            "title": "Medium (optional)"
                        },
                        "time_duration_minutes": {"type": "integer", "minimum": 5, "maximum": 480, "title": "Time (minutes)"},
                        "bloom_level": {"type": "string", "title": "Bloom level", "description": "Understand/Create common; Evaluate optional for critique"},
                        "materials": {"type": "string", "title": "Materials"},
                        "constraints": {"type": "string", "title": "Constraints (mess, limited materials)"},
                        "differentiation_needs": {"type": "boolean", "title": "Differentiation toggle"},
                        "differentiation_notes": {"type": "string", "title": "Differentiation notes (optional)"},
                        "standards_framework": {"type": "string", "title": "Standards framework (optional)"},
                        "standard": {"type": "string", "title": "Standard code (optional)"}
                    },
                    "required": ["grade", "topic", "time_duration_minutes", "bloom_level"]
                },
                "output_schema": {
                    "type": "object",
                    "title": "ArtExplorationOutput",
                    "required": [
                        "title",
                        "overview",
                        "learning_goals",
                        "materials",
                        "steps",
                        "assessment",
                        "differentiation",
                        "bloom_alignment",
                        "teacher_notes"
                    ],
                    "properties": {
                        "title": {"type": "string", "title": "Activity title"},
                        "overview": {"type": "string", "title": "Theme + artist reference (optional)"},
                        "learning_goals": {"type": "array", "title": "Learning goals", "items": {"type": "string"}},
                        "materials": {"type": "array", "title": "Materials", "items": {"type": "string"}},
                        "steps": {"type": "array", "title": "Steps (warm-up → create → share/reflect)", "items": {"type": "string"}},
                        "assessment": {
                            "type": "object",
                            "title": "Assessment (rubric or checklist)",
                            "properties": {
                                "type": {"type": "string", "title": "Type"},
                                "criteria": {"type": "array", "title": "Criteria", "items": {"type": "string"}}
                            },
                            "required": ["type", "criteria"]
                        },
                        "differentiation": {
                            "type": "object",
                            "title": "Differentiation",
                            "properties": {
                                "support": {"type": "array", "items": {"type": "string"}},
                                "extension": {"type": "array", "items": {"type": "string"}}
                            },
                            "required": ["support", "extension"]
                        },
                        "bloom_alignment": {
                            "type": "object",
                            "title": "Bloom alignment",
                            "properties": {"level": {"type": "string"}, "note": {"type": "string"}},
                            "required": ["level", "note"]
                        },
                        "standards_alignment": {
                            "type": "object",
                            "title": "Standards alignment (if provided)",
                            "properties": {
                                "framework": {"type": "string"},
                                "code": {"type": "string"},
                                "note": {"type": "string"}
                            }
                        },
                        "teacher_notes": {"type": "array", "title": "Teacher notes", "items": {"type": "string"}}
                    }
                },
                "stub_config": {
                    "title_template": "Mood Landscapes: Warm vs Cool Colors",
                    "overview_template": "Students explore how color temperature affects mood by creating a simple landscape using warm or cool palettes for {topic}.",
                    "learning_goals": [
                        "Identify warm and cool colors",
                        "Choose colors intentionally to communicate mood",
                        "Explain artistic choices using art vocabulary"
                    ],
                    "materials": ["Crayons or colored pencils", "Paper"],
                    "steps": [
                        "Warm-up (5 min): Sort example colors into warm vs cool; discuss mood words (calm, excited, lonely, joyful).",
                        "Mini-demo (5 min): Teacher draws a simple landscape and shows how changing palette changes feeling.",
                        "Create (20 min): Students draw a landscape (real or imaginary) using mostly warm OR mostly cool colors to show a chosen mood.",
                        "Artist statement (5 min): Students write 3–4 sentences explaining mood + color choices.",
                        "Share (5 min): Gallery walk with 1 compliment + 1 question per artwork."
                    ],
                    "assessment": {
                        "type": "checklist",
                        "criteria": [
                            "Artwork uses mostly warm or mostly cool colors",
                            "Mood is clear",
                            "Artist statement explains choices"
                        ]
                    },
                    "differentiation": {
                        "support": [
                            "Provide landscape templates (horizon line + simple shapes)",
                            "Allow larger tools (thicker crayons) and reduced detail expectations"
                        ],
                        "extension": [
                            "Blend both palettes intentionally to show mood change",
                            "Add a short critique: what works best and why (using evidence from the piece)"
                        ]
                    },
                    "bloom_alignment": {
                        "level": "Create",
                        "note_template": "Students produce original artwork and justify choices using art vocabulary for {topic}."
                    },
                    "standards_alignment": {
                        "framework_template": "{standards_framework}",
                        "code_template": "{standard}",
                        "note_template": "Students apply color as an element of art to convey mood and explain intent."
                    },
                    "teacher_notes": [
                        "Keep vocabulary simple: warm/cool, mood, contrast.",
                        "Don't grade artistic talent—grade intentional choices and explanation."
                    ]
                },
                "prompt_definition": {
                    "description": "Generate an art exploration activity with: Activity title, Theme (optional artist reference), Learning goals, Materials, Steps (warm-up → create → share/reflect), Assessment (rubric or checklist), Differentiation, and Bloom/standards alignment. Support optional IB/UK/local arts standards when provided.",
                    "context": "This art activity will be used in international schools. It must be inclusive, respect constraints (mess, materials), and focus on intentional choices and explanation rather than artistic talent alone."
                }
            }
        },
        {
            # TEMPLATE 15: Concept Quest Adventure (Universal Subject Game)
            "template": {
                "slug": "concept_quest_adventure",
                "name": "Concept Quest Adventure",
                "description": "Story-driven concept game where students progress through mission levels to deepen understanding of core ideas across subjects.",
                "category": "lesson_design",
                "subject_default": None,
                "grade_bands_supported": ["K-2", "3-5", "6-8", "9-12"],
            },
            "version": {
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "grade_level": {
                            "type": "string",
                            "title": "Grade level",
                            "description": "e.g. Year 6, Grade 5"
                        },
                        "subject": {
                            "type": "string",
                            "title": "Subject",
                            "enum": ["science", "history", "geography", "literature", "economics", "other"],
                            "description": "Primary subject focus for the game."
                        },
                        "topic": {
                            "type": "string",
                            "title": "Topic",
                            "description": "Short description of the concept focus, e.g. Food Chains."
                        },
                        "bloom_level": {
                            "type": "string",
                            "title": "Bloom level",
                            "description": "e.g. Understand, Apply, Understand / Apply."
                        },
                        "game_duration": {
                            "type": "string",
                            "title": "Game duration",
                            "description": "Approximate time for the full game, e.g. 30 minutes."
                        },
                        "difficulty": {
                            "type": "string",
                            "title": "Difficulty",
                            "enum": ["Easy", "Medium", "Hard"],
                            "description": "Overall challenge level for the game."
                        },
                        "team_mode": {
                            "type": "boolean",
                            "title": "Team mode",
                            "description": "Whether students will play in teams (true) or individually (false)."
                        },
                        "standards_framework": {
                            "type": "string",
                            "title": "Standards framework (optional)",
                            "description": "Optional standards framework or curriculum label."
                        }
                    },
                    "required": [
                        "grade_level",
                        "subject",
                        "topic",
                        "bloom_level",
                        "game_duration",
                        "difficulty",
                        "team_mode"
                    ]
                },
                "output_schema": {
                    "type": "object",
                    "title": "ConceptQuestAdventureOutput",
                    "required": [
                        "title",
                        "story_scenario",
                        "mission_levels",
                        "game_mechanics",
                        "assessment",
                        "teacher_facilitation"
                    ],
                    "properties": {
                        "title": {
                            "type": "string",
                            "title": "Game title"
                        },
                        "story_scenario": {
                            "type": "string",
                            "title": "Story scenario",
                            "description": "Brief narrative hook that explains the problem or quest."
                        },
                        "mission_levels": {
                            "type": "array",
                            "title": "Mission levels",
                            "items": {
                                "type": "object",
                                "title": "Mission level",
                                "required": ["level_title", "description"],
                                "properties": {
                                    "level_title": {
                                        "type": "string",
                                        "title": "Level title"
                                    },
                                    "description": {
                                        "type": "string",
                                        "title": "Level description"
                                    },
                                    "student_task": {
                                        "type": "string",
                                        "title": "Student task",
                                        "description": "What students do to complete this level."
                                    }
                                }
                            }
                        },
                        "game_mechanics": {
                            "type": "array",
                            "title": "Game mechanics",
                            "items": {
                                "type": "string"
                            }
                        },
                        "assessment": {
                            "type": "array",
                            "title": "Assessment (skill + evidence)",
                            "items": {
                                "type": "object",
                                "required": ["skill", "evidence"],
                                "properties": {
                                    "skill": {
                                        "type": "string",
                                        "title": "Skill"
                                    },
                                    "evidence": {
                                        "type": "string",
                                        "title": "Evidence of learning"
                                    }
                                }
                            }
                        },
                        "teacher_facilitation": {
                            "type": "array",
                            "title": "Teacher facilitation steps",
                            "items": {
                                "type": "string"
                            }
                        }
                    }
                },
                "stub_config": {
                    "title_template": "The {topic} Quest",
                    "story_scenario_template": "The class has been transported into a {subject} world where the balance of {topic} has been disrupted. Students must complete concept missions to restore order for Grade {grade_level}.",
                    "mission_levels": [
                        {
                            "level_title": "Level 1 – Identify Key Concepts",
                            "description_template": "Students sort example items into correct categories related to {topic}.",
                            "student_task_template": "Select or classify items that correctly represent the core concept."
                        },
                        {
                            "level_title": "Level 2 – Build the Concept Model",
                            "description_template": "Students arrange cards or ideas to build a complete representation of {topic}.",
                            "student_task_template": "Assemble the model (diagram, sequence, or structure) in the correct order."
                        },
                        {
                            "level_title": "Level 3 – Challenge Scenario",
                            "description_template": "Students predict what happens if one part of the model changes or is removed.",
                            "student_task_template": "Explain the consequences and justify their reasoning using Bloom level {bloom_level}."
                        }
                    ],
                    "game_mechanics": [
                        "Teams earn quest points for correct answers and high-quality explanations.",
                        "Bonus points for creative reasoning or deep connections.",
                        "Time-based mini-challenges to keep energy high."
                    ],
                    "assessment": [
                        {
                            "skill": "Concept recognition",
                            "evidence_template": "Correctly identifies and classifies examples and non-examples of {topic}."
                        },
                        {
                            "skill": "Systems / relational thinking",
                            "evidence_template": "Accurately predicts how changes in one part of the concept affect the whole."
                        },
                        {
                            "skill": "Reasoning and explanation",
                            "evidence_template": "Provides clear verbal or written explanations using appropriate vocabulary."
                        }
                    ],
                    "teacher_facilitation": [
                        "Divide the class into teams or pairs based on {difficulty} and group dynamics.",
                        "Explain the story scenario and overall mission so students understand the stakes.",
                        "Distribute any cards, prompts, or digital resources needed for each mission level.",
                        "Run mission levels sequentially, pausing between levels to highlight key thinking moves.",
                        "Use questioning to push students from recall to {bloom_level} level reasoning.",
                        "Close with a brief reflection where students share the most important idea they learned about {topic}."
                    ]
                },
                "prompt_definition": {
                    "description": "Generate a concept quest game with: Game title, story scenario, mission levels (at least 3), game mechanics, assessment table (skill + evidence), and teacher facilitation steps. The game should be playable in a single lesson and adaptable across subjects.",
                    "context": "This template creates a story-driven concept game that can be used in science, history, geography, literature, or economics. The output must follow the provided output_schema exactly so the frontend can render sections for title, story, mission levels, game mechanics, assessment (skill/evidence), and teacher facilitation."
                }
            }
        },
        {
            # TEMPLATE 16: Sustainability Systems Thinking Lesson Builder
            "template": {
                "slug": "sustainability_systems_lesson",
                "name": "Sustainability Systems Thinking Lesson Builder",
                "description": "Build lessons on complex environmental systems (climate, biodiversity, water cycles) using systems mapping and causal reasoning.",
                "category": "subject_specific",
                "subject_default": "science",
                "grade_bands_supported": ["K-2", "3-5", "6-8", "9-12"],
            },
            "version": {
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "grade_level": {"type": "string", "title": "Grade level", "description": "e.g. Year 9, Grade 7"},
                        "topic": {"type": "string", "title": "Topic", "description": "e.g. Urban Heat Islands, biodiversity, water cycles"},
                        "bloom_level": {"type": "string", "title": "Bloom level", "description": "e.g. Analyze, Evaluate, Analyze / Evaluate"},
                        "lesson_duration": {"type": "string", "title": "Lesson duration", "description": "e.g. 60 minutes"},
                        "local_context": {"type": "string", "title": "Local context (optional)", "description": "e.g. Perth, Western Australia"},
                        "standards_framework": {"type": "string", "title": "Standards framework (optional)", "description": "e.g. Australian Curriculum Science"}
                    },
                    "required": ["grade_level", "topic", "bloom_level", "lesson_duration"]
                },
                "output_schema": {
                    "type": "object",
                    "title": "SustainabilitySystemsLessonOutput",
                    "required": [
                        "learning_objectives",
                        "systems_map_activity",
                        "guided_inquiry_questions",
                        "mini_case_study",
                        "assessment_rubric"
                    ],
                    "properties": {
                        "learning_objectives": {"type": "array", "title": "Learning objectives", "items": {"type": "string"}},
                        "systems_map_activity": {
                            "type": "object",
                            "title": "Systems map activity",
                            "properties": {
                                "description": {"type": "string", "title": "Activity description"},
                                "cause_effect_elements": {"type": "array", "title": "Cause-effect loop elements", "items": {"type": "string"}}
                            },
                            "required": ["description", "cause_effect_elements"]
                        },
                        "guided_inquiry_questions": {"type": "array", "title": "Guided inquiry questions", "items": {"type": "string"}},
                        "mini_case_study": {"type": "string", "title": "Mini-case study (localized)"},
                        "assessment_rubric": {
                            "type": "object",
                            "title": "Assessment rubric (aligned with Bloom)",
                            "properties": {
                                "type": {"type": "string", "title": "Type"},
                                "criteria": {"type": "array", "title": "Criteria", "items": {"type": "string"}}
                            },
                            "required": ["type", "criteria"]
                        }
                    }
                },
                "stub_config": {
                    "learning_objectives_template": [
                        "Analyze how urban materials affect temperature absorption.",
                        "Evaluate mitigation strategies for urban heat."
                    ],
                    "systems_map_activity": {
                        "description_template": "Students create a cause-effect loop diagram for {topic} including the following components and their relationships.",
                        "cause_effect_elements": [
                            "Concrete surfaces",
                            "Reduced vegetation",
                            "Heat absorption",
                            "Air temperature",
                            "Energy consumption"
                        ]
                    },
                    "guided_inquiry_questions": [
                        "How does replacing trees with asphalt affect thermal dynamics?",
                        "Which feedback loops amplify heat?"
                    ],
                    "mini_case_study_template": "Perth summer temperature data (provided). Localized context: {local_context}. Use this to ground the lesson in {topic}.",
                    "assessment_rubric": {
                        "type": "bloom_aligned",
                        "criteria": [
                            "Identifies system components (Analyze)",
                            "Explains feedback loops (Analyze)",
                            "Proposes justified intervention (Evaluate)"
                        ]
                    }
                },
                "prompt_definition": {
                    "description": "Generate a sustainability systems thinking lesson with: Learning objectives (Analyze/Evaluate), Systems map activity (cause-effect loop diagram with key components), Guided inquiry questions, Mini-case study localized to the given context, and Assessment rubric aligned with Bloom's level.",
                    "context": "This lesson will be used to teach complex environmental systems (climate, biodiversity, water cycles) using systems mapping and causal reasoning. Support optional curriculum standards when provided."
                }
            }
        },
        {
            # TEMPLATE 16: Field Investigation Planner (Outdoor / Environmental Study)
            "template": {
                "slug": "field_investigation_planner",
                "name": "Field Investigation Planner (Outdoor / Environmental Study)",
                "description": "Streamlines preparation for field-based ecological studies with protocol, data table, and reflection.",
                "category": "subject_specific",
                "subject_default": "science",
                "grade_bands_supported": ["K-2", "3-5", "6-8", "9-12"],
            },
            "version": {
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "grade_level": {"type": "string", "title": "Grade level", "description": "e.g. Year 7"},
                        "ecosystem_type": {"type": "string", "title": "Ecosystem type", "description": "e.g. Wetland, Forest"},
                        "investigation_focus": {"type": "string", "title": "Investigation focus", "description": "e.g. Water Quality, Biodiversity"},
                        "tools_available": {"type": "array", "items": {"type": "string"}, "title": "Tools available"},
                        "bloom_level": {"type": "string", "title": "Bloom level", "description": "e.g. Apply, Analyze"},
                        "risk_level": {"type": "string", "title": "Risk level", "description": "e.g. Low, Medium"}
                    },
                    "required": ["grade_level", "ecosystem_type", "investigation_focus", "bloom_level"]
                },
                "output_schema": {
                    "type": "object",
                    "title": "FieldInvestigationPlannerOutput",
                    "required": [
                        "fieldwork_objective",
                        "step_by_step_protocol",
                        "data_collection_table",
                        "data_analysis_prompts",
                        "reflection_systems_link"
                    ],
                    "properties": {
                        "fieldwork_objective": {"type": "string", "title": "Fieldwork objective"},
                        "step_by_step_protocol": {"type": "array", "title": "Step-by-step field protocol", "items": {"type": "string"}},
                        "data_collection_table": {
                            "type": "object",
                            "title": "Data collection table (printable)",
                            "properties": {
                                "headers": {"type": "array", "title": "Column headers", "items": {"type": "string"}},
                                "description": {"type": "string", "title": "Table description"}
                            },
                            "required": ["headers", "description"]
                        },
                        "data_analysis_prompts": {"type": "array", "title": "Data analysis prompts", "items": {"type": "string"}},
                        "reflection_systems_link": {"type": "string", "title": "Reflection + systems link"}
                    }
                },
                "stub_config": {
                    "fieldwork_objective_template": "Students measure abiotic factors and interpret ecosystem health for {ecosystem_type} ({investigation_focus}).",
                    "step_by_step_protocol": [
                        "Measure water temperature.",
                        "Test pH levels.",
                        "Record visible biodiversity."
                    ],
                    "data_collection_table": {
                        "headers": ["Sample Point", "Temp (°C)", "pH", "Observations"],
                        "description_template": "Printable data collection table for {investigation_focus} in {ecosystem_type}."
                    },
                    "data_analysis_prompts": [
                        "What patterns emerge across sample points?",
                        "Does pH suggest ecological stress?"
                    ],
                    "reflection_systems_link_template": "How might urban runoff impact this {ecosystem_type}?"
                },
                "prompt_definition": {
                    "description": "Generate a field investigation plan with: Fieldwork objective, Step-by-step field protocol, Printable data collection table, Data analysis prompts, and Reflection linking to systems (e.g. human impact). Tailor to ecosystem type, investigation focus, and tools available.",
                    "context": "This planner supports outdoor/environmental studies. Ensure protocol is safe for the given risk level and appropriate for the grade and tools available."
                }
            }
        },
        {
            # TEMPLATE 17: Climate Data Literacy Activity Generator
            "template": {
                "slug": "climate_data_literacy",
                "name": "Climate Data Literacy Activity Generator",
                "description": "Teaches students to interpret real climate or environmental datasets with graph interpretation, critical thinking, and evidence-based writing.",
                "category": "subject_specific",
                "subject_default": "science",
                "grade_bands_supported": ["K-2", "3-5", "6-8", "9-12"],
            },
            "version": {
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "grade_level": {"type": "string", "title": "Grade level", "description": "e.g. Year 10"},
                        "dataset_type": {"type": "string", "title": "Dataset type", "description": "e.g. Temperature Trends, Precipitation"},
                        "location": {"type": "string", "title": "Location", "description": "e.g. Western Australia"},
                        "years_range": {"type": "string", "title": "Years range", "description": "e.g. 1980-2020"},
                        "bloom_level": {"type": "string", "title": "Bloom level", "description": "e.g. Analyze, Evaluate"},
                        "assessment_type": {"type": "string", "title": "Assessment type", "description": "e.g. Short Report, Essay"}
                    },
                    "required": ["grade_level", "dataset_type", "location", "bloom_level"]
                },
                "output_schema": {
                    "type": "object",
                    "title": "ClimateDataLiteracyOutput",
                    "required": [
                        "dataset_summary",
                        "graph_interpretation_questions",
                        "critical_thinking_prompts",
                        "writing_task",
                        "rubric"
                    ],
                    "properties": {
                        "dataset_summary": {"type": "string", "title": "Dataset summary (auto-generated)"},
                        "graph_interpretation_questions": {"type": "array", "title": "Graph interpretation questions", "items": {"type": "string"}},
                        "critical_thinking_prompts": {"type": "array", "title": "Critical thinking prompts", "items": {"type": "string"}},
                        "writing_task": {"type": "string", "title": "Writing task"},
                        "rubric": {
                            "type": "object",
                            "title": "Rubric",
                            "properties": {
                                "criteria": {"type": "array", "title": "Criteria", "items": {"type": "string"}}
                            },
                            "required": ["criteria"]
                        }
                    }
                },
                "stub_config": {
                    "dataset_summary_template": "Overview of long-term temperature increase for {dataset_type} in {location} ({years_range}).",
                    "graph_interpretation_questions": [
                        "Identify the trend.",
                        "Calculate average increase per decade."
                    ],
                    "critical_thinking_prompts": [
                        "What factors might explain anomalies?",
                        "Is correlation equal to causation?"
                    ],
                    "writing_task_template": "Write a 400-word evidence-based analysis evaluating climate trends for {dataset_type} in {location}.",
                    "rubric": {
                        "criteria": [
                            "Accurate data interpretation",
                            "Logical reasoning",
                            "Evidence-based conclusion"
                        ]
                    }
                },
                "prompt_definition": {
                    "description": "Generate a climate data literacy activity with: Dataset summary (overview of the data), Graph interpretation questions, Critical thinking prompts (e.g. causation vs correlation), Writing task (evidence-based analysis), and Rubric. Tailor to dataset type, location, years range, and assessment type.",
                    "context": "This activity teaches students to interpret real climate or environmental datasets. Ensure questions and task align with Bloom level and assessment type."
                }
            }
        },
        {
            # TEMPLATE 18: Sustainability Design Challenge (Engineering + Environmental)
            "template": {
                "slug": "sustainability_design_challenge",
                "name": "Sustainability Design Challenge (Engineering + Environmental)",
                "description": "Project-based learning integrating science and engineering with design thinking stages and sustainability constraints.",
                "category": "subject_specific",
                "subject_default": "steam",
                "grade_bands_supported": ["K-2", "3-5", "6-8", "9-12"],
            },
            "version": {
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "grade_level": {"type": "string", "title": "Grade level", "description": "e.g. Year 8"},
                        "challenge_theme": {"type": "string", "title": "Challenge theme", "description": "e.g. Reduce Plastic Waste"},
                        "constraints": {"type": "array", "items": {"type": "string"}, "title": "Constraints"},
                        "duration": {"type": "string", "title": "Duration", "description": "e.g. 2 weeks"},
                        "bloom_level": {"type": "string", "title": "Bloom level", "description": "e.g. Create"},
                        "team_size": {"type": "integer", "minimum": 1, "maximum": 20, "title": "Team size"}
                    },
                    "required": ["grade_level", "challenge_theme", "bloom_level"]
                },
                "output_schema": {
                    "type": "object",
                    "title": "SustainabilityDesignChallengeOutput",
                    "required": [
                        "challenge_brief",
                        "design_thinking_stages",
                        "engineering_constraints",
                        "deliverables",
                        "evaluation_rubric"
                    ],
                    "properties": {
                        "challenge_brief": {"type": "string", "title": "Challenge brief"},
                        "design_thinking_stages": {
                            "type": "array",
                            "title": "Design thinking stages",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "stage": {"type": "string", "title": "Stage"},
                                    "description": {"type": "string", "title": "Description"}
                                },
                                "required": ["stage", "description"]
                            }
                        },
                        "engineering_constraints": {"type": "array", "title": "Engineering constraints", "items": {"type": "string"}},
                        "deliverables": {"type": "array", "title": "Deliverables", "items": {"type": "string"}},
                        "evaluation_rubric": {
                            "type": "object",
                            "title": "Evaluation rubric (creation level)",
                            "properties": {
                                "criteria": {"type": "array", "title": "Criteria", "items": {"type": "string"}}
                            },
                            "required": ["criteria"]
                        }
                    }
                },
                "stub_config": {
                    "challenge_brief_template": "Design a school-based solution to reduce single-use plastics for {challenge_theme}.",
                    "design_thinking_stages": [
                        {"stage": "Empathize", "description": "Survey students."},
                        {"stage": "Define", "description": "Identify biggest waste sources."},
                        {"stage": "Ideate", "description": "Brainstorm 10 ideas."},
                        {"stage": "Prototype", "description": "Model or presentation."},
                        {"stage": "Test", "description": "Peer feedback."}
                    ],
                    "engineering_constraints": [
                        "Budget under $100",
                        "Must be sustainable"
                    ],
                    "deliverables": [
                        "Proposal document",
                        "Prototype",
                        "5-minute pitch"
                    ],
                    "evaluation_rubric": {
                        "criteria": [
                            "Innovation",
                            "Feasibility",
                            "Environmental impact reasoning"
                        ]
                    }
                },
                "prompt_definition": {
                    "description": "Generate a sustainability design challenge with: Challenge brief, Design thinking stages (Empathize, Define, Ideate, Prototype, Test), Engineering constraints, Deliverables, and Evaluation rubric at Create level. Integrate science and engineering for project-based learning.",
                    "context": "This challenge is for project-based learning integrating science and engineering. Tailor to challenge theme, constraints, duration, and team size."
                }
            }
        },
        {
            # TEMPLATE 19: Biodiversity Impact Simulation & Role Play
            "template": {
                "slug": "biodiversity_role_play",
                "name": "Biodiversity Impact Simulation & Role Play",
                "description": "Helps students understand environmental trade-offs via role-play debate with stakeholder roles and structured debate format.",
                "category": "subject_specific",
                "subject_default": "science",
                "grade_bands_supported": ["K-2", "3-5", "6-8", "9-12"],
            },
            "version": {
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "grade_level": {"type": "string", "title": "Grade level", "description": "e.g. Year 9"},
                        "issue": {"type": "string", "title": "Issue", "description": "e.g. Coastal Development vs Marine Protection"},
                        "roles": {"type": "array", "items": {"type": "string"}, "title": "Roles", "description": "Stakeholder roles for the debate"},
                        "bloom_level": {"type": "string", "title": "Bloom level", "description": "e.g. Evaluate"},
                        "format": {"type": "string", "title": "Format", "description": "e.g. Structured Debate"}
                    },
                    "required": ["grade_level", "issue", "bloom_level"]
                },
                "output_schema": {
                    "type": "object",
                    "title": "BiodiversityRolePlayOutput",
                    "required": [
                        "background_brief",
                        "role_assignment_sheets",
                        "debate_structure",
                        "reflection_prompts",
                        "assessment"
                    ],
                    "properties": {
                        "background_brief": {"type": "string", "title": "Background brief"},
                        "role_assignment_sheets": {
                            "type": "array",
                            "title": "Role assignment sheets",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "role": {"type": "string", "title": "Role"},
                                    "stakeholder_goals": {"type": "string", "title": "Stakeholder goals"},
                                    "key_arguments": {"type": "array", "title": "Key arguments", "items": {"type": "string"}},
                                    "data_references": {"type": "array", "title": "Data references", "items": {"type": "string"}}
                                },
                                "required": ["role", "stakeholder_goals", "key_arguments", "data_references"]
                            }
                        },
                        "debate_structure": {"type": "array", "title": "Debate structure", "items": {"type": "string"}},
                        "reflection_prompts": {"type": "array", "title": "Reflection prompts", "items": {"type": "string"}},
                        "assessment": {
                            "type": "object",
                            "title": "Assessment",
                            "properties": {
                                "criteria": {"type": "array", "title": "Criteria", "items": {"type": "string"}}
                            },
                            "required": ["criteria"]
                        }
                    }
                },
                "stub_config": {
                    "background_brief_template": "Overview of coastal ecosystem importance and the tension between development and protection for {issue}.",
                    "role_assignment_sheets": [
                        {"role": "Developer", "stakeholder_goals": "Advocate for economic development and jobs.", "key_arguments": ["Job creation", "Local revenue"], "data_references": ["Employment projections", "Tax revenue estimates"]},
                        {"role": "Environmental Scientist", "stakeholder_goals": "Present evidence on biodiversity and ecosystem services.", "key_arguments": ["Habitat loss", "Species decline"], "data_references": ["Marine surveys", "IUCN data"]},
                        {"role": "Local Resident", "stakeholder_goals": "Represent community quality of life and access.", "key_arguments": ["Livelihoods", "Cultural value"], "data_references": ["Community surveys"]},
                        {"role": "Government", "stakeholder_goals": "Balance regulation and sustainable use.", "key_arguments": ["Policy options", "Compliance"], "data_references": ["Existing regulations", "Impact assessments"]}
                    ],
                    "debate_structure": [
                        "Opening statements",
                        "Rebuttals",
                        "Evidence round",
                        "Final vote"
                    ],
                    "reflection_prompts": [
                        "What trade-offs were most difficult?",
                        "How should policy balance economics and ecology?"
                    ],
                    "assessment": {
                        "criteria": [
                            "Reasoning",
                            "Evidence use",
                            "Ethical consideration"
                        ]
                    }
                },
                "prompt_definition": {
                    "description": "Generate a biodiversity impact simulation/role play with: Background brief (ecosystem context), Role assignment sheets (stakeholder goals, key arguments, data references per role), Debate structure, Reflection prompts, and Assessment (reasoning, evidence use, ethical consideration).",
                    "context": "This activity helps students understand environmental trade-offs via role-play debate. Tailor to the issue and roles provided; support structured debate format."
                }
            }
        },
        {
            # TEMPLATE 20: Communication Generator
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
                "output_schema": {
                    "type": "object",
                    "title": "UniversalTemplateOutput",
                    "required": ["overview", "learning_goals", "materials", "steps"],
                    "properties": {
                        "overview": {"type": "string", "title": "Overview"},
                        "learning_goals": {"type": "array", "title": "Learning Goals", "items": {"type": "string"}},
                        "materials": {"type": "array", "title": "Materials", "items": {"type": "string"}},
                        "steps": {
                            "type": "array",
                            "title": "Steps",
                            "items": {
                                "type": "object",
                                "title": "LessonStep",
                                "required": ["title", "description"],
                                "properties": {"title": {"type": "string", "title": "Title"}, "description": {"type": "string", "title": "Description"}},
                            },
                        },
                        "differentiation": {"type": "array", "title": "Differentiation", "items": {"type": "string"}},
                        "assessment": {
                            "type": ["object", "null"],
                            "title": "AssessmentSection",
                            "properties": {
                                "checks_for_understanding": {"type": "array", "items": {"type": "string"}},
                                "rubric": {"type": ["object", "null"]},
                            },
                            "required": ["checks_for_understanding"],
                        },
                        "teacher_notes": {"type": "array", "title": "Teacher Notes", "items": {"type": "string"}},
                        "bloom_alignment": {
                            "type": "array",
                            "title": "Bloom Alignment",
                            "items": {
                                "type": "object",
                                "title": "BloomAlignmentItem",
                                "required": ["level", "description"],
                                "properties": {
                                    "level": {"type": "string", "enum": ["remember", "understand", "apply", "analyze", "evaluate", "create"]},
                                    "description": {"type": "string", "title": "Description"},
                                },
                            },
                        },
                        "questions": {
                            "type": ["array", "null"],
                            "title": "Questions",
                            "items": {
                                "type": "object",
                                "title": "AssessmentQuestion",
                                "required": ["question_text", "type"],
                                "properties": {
                                    "question_text": {"type": "string", "title": "Question Text"},
                                    "type": {"type": "string", "title": "Type"},
                                    "answer_key": {"type": ["string", "null"]},
                                    "difficulty": {"type": ["string", "null"]},
                                },
                            },
                        },
                        "communication": {
                            "type": ["object", "null"],
                            "title": "CommunicationSection",
                            "properties": {
                                "subject_line": {"type": ["string", "null"]},
                                "message_body": {"type": ["string", "null"]},
                                "key_details": {"type": ["array", "null"], "items": {"type": "string"}},
                                "call_to_action": {"type": ["string", "null"]},
                            },
                        },
                    },
                },
                "stub_config": {
                    "overview_template": "{template_name} for {subject}: {topic}",
                    "learning_goals_template": ["{learning_objective}", "Help students engage deeply with {topic}."],
                    "materials": ["Whiteboard or digital board", "Student notebooks or devices"],
                    "step_titles": ["Introduction & Activation of Prior Knowledge", "Guided Practice", "Independent or Small-Group Practice"],
                    "step_descriptions_template": "Briefly introduce {topic} and ask students what they already know.",
                    "differentiation": ["Offer sentence stems or visual supports for students who need additional scaffolding.", "Provide extension tasks for students who are ready for enrichment."],
                    "teacher_notes": ["Adjust pacing based on student responses and check-ins.", "Capture examples of strong student thinking to highlight during debrief."],
                    "assessment_checks": ["Cold-call a few students to explain the concept.", "Use exit tickets asking students to solve a short problem or respond to a prompt."],
                },
                "prompt_definition": {
                    "description": "Generate a professional, culturally-sensitive communication suitable for international school contexts with: Subject Line, Message Body, Key Details, Call to Action, and Optional Attachments note. Ensure the communication is clear, respectful, and appropriate for diverse parent/guardian populations. Use professional tone while remaining accessible. Consider cultural differences in communication styles.",
                    "context": "This communication will be used in international schools with diverse parent/guardian populations. It must be professional, clear, and culturally sensitive."
                }
            }
        },
        {
            # TEMPLATE 21: Math City Builder Game
            "template": {
                "slug": "math_city_builder",
                "name": "Math City Builder Game",
                "description": "Students solve math problems to build and manage a virtual city. Teaches arithmetic, algebra, geometry, and financial literacy.",
                "category": "lesson_design",
                "subject_default": "math",
                "grade_bands_supported": ["K-2", "3-5", "6-8", "9-12"],
            },
            "version": {
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "grade_level": {
                            "type": "string",
                            "title": "Grade level",
                            "description": "e.g. Year 5, Grade 5"
                        },
                        "subject": {
                            "type": "string",
                            "title": "Subject",
                            "description": "Primary subject (e.g. Mathematics)."
                        },
                        "topic": {
                            "type": "string",
                            "title": "Topic",
                            "description": "Short description of the math focus, e.g. Area and Perimeter."
                        },
                        "bloom_level": {
                            "type": "string",
                            "title": "Bloom level",
                            "description": "e.g. Apply, Analyze."
                        },
                        "game_duration": {
                            "type": "string",
                            "title": "Game duration",
                            "description": "Approximate time for the full game, e.g. 40 minutes."
                        },
                        "city_theme": {
                            "type": "string",
                            "title": "City theme",
                            "description": "Theme for the virtual city, e.g. Eco City."
                        },
                        "team_mode": {
                            "type": "boolean",
                            "title": "Team mode",
                            "description": "Whether students play in teams (true) or individually (false)."
                        }
                    },
                    "required": [
                        "grade_level",
                        "subject",
                        "topic",
                        "bloom_level",
                        "game_duration",
                        "city_theme",
                        "team_mode"
                    ]
                },
                "output_schema": {
                    "type": "object",
                    "title": "MathCityBuilderOutput",
                    "required": [
                        "title",
                        "game_scenario",
                        "challenges",
                        "game_mechanics",
                        "assessment"
                    ],
                    "properties": {
                        "title": {"type": "string", "title": "Game title"},
                        "game_scenario": {"type": "string", "title": "Game scenario"},
                        "challenges": {
                            "type": "array",
                            "title": "Challenges",
                            "items": {
                                "type": "object",
                                "required": ["challenge_title", "description"],
                                "properties": {
                                    "challenge_title": {"type": "string", "title": "Challenge title"},
                                    "description": {"type": "string", "title": "Description"},
                                    "details": {"type": "string", "title": "Details (e.g. dimensions, constraints)"}
                                }
                            }
                        },
                        "game_mechanics": {
                            "type": "array",
                            "title": "Game mechanics",
                            "items": {"type": "string"}
                        },
                        "assessment": {
                            "type": "array",
                            "title": "Assessment (skill + evidence)",
                            "items": {
                                "type": "object",
                                "required": ["skill", "evidence"],
                                "properties": {
                                    "skill": {"type": "string", "title": "Skill"},
                                    "evidence": {"type": "string", "title": "Evidence"}
                                }
                            }
                        }
                    }
                },
                "stub_config": {
                    "title_template": "Build Your {city_theme}",
                    "game_scenario_template": "Students must design a sustainable city by calculating building spaces for {topic}.",
                    "challenges": [
                        {
                            "challenge_title": "Park Design",
                            "description_template": "Students calculate area given dimensions.",
                            "details_template": "Length = 20 m, Width = 15 m."
                        },
                        {
                            "challenge_title": "Solar Farm",
                            "description_template": "Students determine perimeter fencing needed.",
                            "details_template": "Perimeter calculation challenge."
                        },
                        {
                            "challenge_title": "Budget Constraint",
                            "description_template": "Students allocate funds to build houses.",
                            "details_template": "Financial literacy and allocation."
                        }
                    ],
                    "game_mechanics": [
                        "Points for correct calculations",
                        "Bonus for fastest solution",
                        "City upgrades unlocked"
                    ],
                    "assessment": [
                        {"skill": "Mathematical accuracy", "evidence_template": "Correct calculations"},
                        {"skill": "Problem solving", "evidence_template": "Efficient design choices"},
                        {"skill": "Real-world application", "evidence_template": "Budget allocation"}
                    ]
                },
                "prompt_definition": {
                    "description": "Generate a Math City Builder game with: Game title, game scenario, challenges (e.g. Park Design, Solar Farm, Budget Constraint) with dimensions/constraints, game mechanics, and assessment table (skill + evidence). Focus on arithmetic, algebra, geometry, and financial literacy as appropriate for the topic.",
                    "context": "This template creates a city-building game where students solve math problems to build and manage a virtual city. Output must include title, scenario, challenges, game mechanics, and assessment (skill/evidence)."
                }
            }
        },
        {
            # TEMPLATE 22: History Time Travel Simulation
            "template": {
                "slug": "history_time_travel_simulation",
                "name": "History Time Travel Simulation",
                "description": "Students become historical decision makers and experience consequences. Works for History, Civics, and Social Studies.",
                "category": "lesson_design",
                "subject_default": None,
                "grade_bands_supported": ["K-2", "3-5", "6-8", "9-12"],
            },
            "version": {
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "grade_level": {
                            "type": "string",
                            "title": "Grade level",
                            "description": "e.g. Year 8, Grade 8"
                        },
                        "subject": {
                            "type": "string",
                            "title": "Subject",
                            "description": "e.g. History, Civics, Social Studies."
                        },
                        "topic": {
                            "type": "string",
                            "title": "Topic",
                            "description": "Historical focus, e.g. Industrial Revolution."
                        },
                        "bloom_level": {
                            "type": "string",
                            "title": "Bloom level",
                            "description": "e.g. Analyze, Evaluate, Analyze / Evaluate."
                        },
                        "game_duration": {
                            "type": "string",
                            "title": "Game duration",
                            "description": "Approximate time, e.g. 45 minutes."
                        },
                        "roles": {
                            "type": "array",
                            "title": "Roles",
                            "items": {"type": "string"},
                            "description": "Stakeholder roles for the simulation, e.g. Factory Owner, Worker, Government, Inventor."
                        }
                    },
                    "required": [
                        "grade_level",
                        "subject",
                        "topic",
                        "bloom_level",
                        "game_duration",
                        "roles"
                    ]
                },
                "output_schema": {
                    "type": "object",
                    "title": "HistoryTimeTravelOutput",
                    "required": [
                        "title",
                        "scenario",
                        "game_rounds",
                        "game_mechanics",
                        "assessment"
                    ],
                    "properties": {
                        "title": {"type": "string", "title": "Game title"},
                        "scenario": {"type": "string", "title": "Scenario"},
                        "game_rounds": {
                            "type": "array",
                            "title": "Game rounds",
                            "items": {
                                "type": "object",
                                "required": ["round_title", "description"],
                                "properties": {
                                    "round_title": {"type": "string", "title": "Round title"},
                                    "description": {"type": "string", "title": "Description"},
                                    "choices": {
                                        "type": "array",
                                        "title": "Choices",
                                        "items": {"type": "string"}
                                    }
                                }
                            }
                        },
                        "game_mechanics": {
                            "type": "array",
                            "title": "Game mechanics",
                            "items": {"type": "string"}
                        },
                        "assessment": {
                            "type": "array",
                            "title": "Assessment (skill + evidence)",
                            "items": {
                                "type": "object",
                                "required": ["skill", "evidence"],
                                "properties": {
                                    "skill": {"type": "string", "title": "Skill"},
                                    "evidence": {"type": "string", "title": "Evidence"}
                                }
                            }
                        }
                    }
                },
                "stub_config": {
                    "title_template": "{topic} Simulator",
                    "scenario_template": "Students roleplay stakeholders during the {topic}.",
                    "game_rounds": [
                        {
                            "round_title": "Factory Expansion",
                            "description_template": "Factory owner chooses expansion strategy.",
                            "choices": ["Hire more workers", "Buy machines"]
                        },
                        {
                            "round_title": "Worker Conditions",
                            "description_template": "Workers demand improvements.",
                            "choices": ["Better wages", "Shorter hours"]
                        },
                        {
                            "round_title": "Government Policy",
                            "description_template": "Government decides policy direction.",
                            "choices": ["Introduce labor laws", "Allow free market"]
                        }
                    ],
                    "game_mechanics": [
                        "Each decision changes economy score",
                        "Each decision changes worker happiness",
                        "Each decision changes production output"
                    ],
                    "assessment": [
                        {"skill": "Historical understanding", "evidence_template": "Accurate reasoning"},
                        {"skill": "Critical thinking", "evidence_template": "Trade-off evaluation"},
                        {"skill": "Argumentation", "evidence_template": "Debate participation"}
                    ]
                },
                "prompt_definition": {
                    "description": "Generate a History Time Travel simulation with: Game title, scenario, game rounds (each with round title, description, and choices), game mechanics (how decisions affect economy score, worker happiness, production output, etc.), and assessment table (skill + evidence). Students roleplay the given roles and experience consequences of decisions.",
                    "context": "This template creates a role-play simulation for History, Civics, or Social Studies. Output must include title, scenario, game rounds with choices, game mechanics, and assessment (skill/evidence)."
                }
            }
        },
        {
            # TEMPLATE 23: Science Lab Mystery Game
            "template": {
                "slug": "science_lab_mystery",
                "name": "Science Lab Mystery Game",
                "description": "Students solve a scientific mystery using evidence. Teaches scientific method, hypothesis testing, and evidence analysis.",
                "category": "lesson_design",
                "subject_default": "science",
                "grade_bands_supported": ["K-2", "3-5", "6-8", "9-12"],
            },
            "version": {
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "grade_level": {
                            "type": "string",
                            "title": "Grade level",
                            "description": "e.g. Year 7, Grade 7"
                        },
                        "subject": {
                            "type": "string",
                            "title": "Subject",
                            "description": "e.g. Science."
                        },
                        "topic": {
                            "type": "string",
                            "title": "Topic",
                            "description": "Scientific focus, e.g. Chemical Reactions."
                        },
                        "bloom_level": {
                            "type": "string",
                            "title": "Bloom level",
                            "description": "e.g. Analyze."
                        },
                        "game_duration": {
                            "type": "string",
                            "title": "Game duration",
                            "description": "Approximate time, e.g. 35 minutes."
                        },
                        "mystery_type": {
                            "type": "string",
                            "title": "Mystery type",
                            "description": "Type of mystery scenario, e.g. Lab Accident."
                        }
                    },
                    "required": [
                        "grade_level",
                        "subject",
                        "topic",
                        "bloom_level",
                        "game_duration",
                        "mystery_type"
                    ]
                },
                "output_schema": {
                    "type": "object",
                    "title": "ScienceLabMysteryOutput",
                    "required": [
                        "title",
                        "scenario",
                        "evidence_cards",
                        "investigation_steps",
                        "game_mechanics",
                        "assessment"
                    ],
                    "properties": {
                        "title": {"type": "string", "title": "Game title"},
                        "scenario": {"type": "string", "title": "Scenario"},
                        "evidence_cards": {
                            "type": "array",
                            "title": "Evidence cards",
                            "items": {
                                "type": "object",
                                "required": ["label", "description"],
                                "properties": {
                                    "label": {"type": "string", "title": "Evidence label"},
                                    "description": {"type": "string", "title": "Description"}
                                }
                            }
                        },
                        "investigation_steps": {
                            "type": "array",
                            "title": "Investigation steps",
                            "items": {"type": "string"}
                        },
                        "game_mechanics": {
                            "type": "array",
                            "title": "Game mechanics",
                            "items": {"type": "string"}
                        },
                        "assessment": {
                            "type": "array",
                            "title": "Assessment (skill + evidence)",
                            "items": {
                                "type": "object",
                                "required": ["skill", "evidence"],
                                "properties": {
                                    "skill": {"type": "string", "title": "Skill"},
                                    "evidence": {"type": "string", "title": "Evidence"}
                                }
                            }
                        }
                    }
                },
                "stub_config": {
                    "title_template": "The {mystery_type} Mystery",
                    "scenario_template": "A {topic} incident occurred. Students must determine what happened using evidence.",
                    "evidence_cards": [
                        {"label": "Evidence A", "description_template": "Observable clue related to {topic}."},
                        {"label": "Evidence B", "description_template": "Second clue."},
                        {"label": "Evidence C", "description_template": "Third clue."}
                    ],
                    "investigation_steps": [
                        "Form hypothesis",
                        "Test reactions or gather data",
                        "Identify cause or conclusion"
                    ],
                    "game_mechanics": [
                        "Teams earn points for correct hypothesis",
                        "Points for logical reasoning",
                        "Points for evidence use"
                    ],
                    "assessment": [
                        {"skill": "Scientific reasoning", "evidence_template": "Hypothesis formation"},
                        {"skill": "Data interpretation", "evidence_template": "Evidence analysis"},
                        {"skill": "Problem solving", "evidence_template": "Correct conclusion"}
                    ]
                },
                "prompt_definition": {
                    "description": "Generate a Science Lab Mystery game with: Game title, scenario (e.g. lab accident or scientific mystery), evidence cards (label + description), investigation steps (e.g. form hypothesis, test reactions, identify conclusion), game mechanics, and assessment table (skill + evidence). Focus on scientific method, hypothesis testing, and evidence analysis.",
                    "context": "This template creates a mystery game where students solve a scientific puzzle using evidence. Output must include title, scenario, evidence cards, investigation steps, game mechanics, and assessment (skill/evidence)."
                }
            }
        },
        {
            # TEMPLATE 24: Global Geography Strategy Game
            "template": {
                "slug": "global_geography_strategy",
                "name": "Global Geography Strategy Game",
                "description": "Students manage global resources and environmental challenges. Teaches geography, climate science, and economics.",
                "category": "lesson_design",
                "subject_default": None,
                "grade_bands_supported": ["K-2", "3-5", "6-8", "9-12"],
            },
            "version": {
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "grade_level": {
                            "type": "string",
                            "title": "Grade level",
                            "description": "e.g. Year 9, Grade 9"
                        },
                        "subject": {
                            "type": "string",
                            "title": "Subject",
                            "description": "e.g. Geography."
                        },
                        "topic": {
                            "type": "string",
                            "title": "Topic",
                            "description": "Focus, e.g. Climate Change."
                        },
                        "bloom_level": {
                            "type": "string",
                            "title": "Bloom level",
                            "description": "e.g. Evaluate, Create, Evaluate / Create."
                        },
                        "game_duration": {
                            "type": "string",
                            "title": "Game duration",
                            "description": "Approximate time, e.g. 50 minutes."
                        },
                        "regions": {
                            "type": "array",
                            "title": "Regions",
                            "items": {"type": "string"},
                            "description": "World regions students represent, e.g. Asia, Europe, Africa, Americas."
                        }
                    },
                    "required": [
                        "grade_level",
                        "subject",
                        "topic",
                        "bloom_level",
                        "game_duration",
                        "regions"
                    ]
                },
                "output_schema": {
                    "type": "object",
                    "title": "GlobalGeographyStrategyOutput",
                    "required": [
                        "title",
                        "scenario",
                        "game_rounds",
                        "game_mechanics",
                        "assessment"
                    ],
                    "properties": {
                        "title": {"type": "string", "title": "Game title"},
                        "scenario": {"type": "string", "title": "Scenario"},
                        "game_rounds": {
                            "type": "array",
                            "title": "Game rounds",
                            "items": {
                                "type": "object",
                                "required": ["round_title", "description"],
                                "properties": {
                                    "round_title": {"type": "string", "title": "Round title"},
                                    "description": {"type": "string", "title": "Description"},
                                    "choices": {
                                        "type": "array",
                                        "title": "Choices",
                                        "items": {"type": "string"}
                                    }
                                }
                            }
                        },
                        "game_mechanics": {
                            "type": "array",
                            "title": "Game mechanics",
                            "items": {"type": "string"}
                        },
                        "assessment": {
                            "type": "array",
                            "title": "Assessment (skill + evidence)",
                            "items": {
                                "type": "object",
                                "required": ["skill", "evidence"],
                                "properties": {
                                    "skill": {"type": "string", "title": "Skill"},
                                    "evidence": {"type": "string", "title": "Evidence"}
                                }
                            }
                        }
                    }
                },
                "stub_config": {
                    "title_template": "Planet Earth Strategy Game",
                    "scenario_template": "Students represent world regions managing resources while addressing {topic}.",
                    "game_rounds": [
                        {
                            "round_title": "Energy Production",
                            "description_template": "Choose energy strategy.",
                            "choices": ["Coal", "Solar", "Wind"]
                        },
                        {
                            "round_title": "Economic Development",
                            "description_template": "Choose development path.",
                            "choices": ["Build factories", "Protect forests"]
                        },
                        {
                            "round_title": "Climate Disaster",
                            "description_template": "Students must allocate emergency resources.",
                            "choices": []
                        }
                    ],
                    "game_mechanics": [
                        "Players track economy score",
                        "Players track environmental health",
                        "Players track global cooperation"
                    ],
                    "assessment": [
                        {"skill": "Geographical understanding", "evidence_template": "Resource decisions"},
                        {"skill": "Systems thinking", "evidence_template": "Long-term planning"},
                        {"skill": "Ethical reasoning", "evidence_template": "Sustainability choices"}
                    ]
                },
                "prompt_definition": {
                    "description": "Generate a Global Geography Strategy game with: Game title, scenario (students represent world regions managing resources and addressing the topic), game rounds (e.g. Energy Production, Economic Development, Climate Disaster) with choices, game mechanics (economy score, environmental health, global cooperation), and assessment table (skill + evidence). Focus on geography, climate science, and economics.",
                    "context": "This template creates a strategy game for geography and sustainability. Output must include title, scenario, game rounds with choices, game mechanics, and assessment (skill/evidence)."
                }
            }
        },
    ]


def seed_templates(db: Session, force: bool = False) -> Dict[str, int]:
    """
    Seed the core system templates.
    
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
                    elif key == "output_schema":
                        existing_version.output_schema = value
                    elif key == "stub_config":
                        existing_version.stub_config = value
                    elif key == "prompt_definition":
                        existing_version.prompt_definition = value
                existing_version.status = TemplateVersionStatus.PUBLISHED.value
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
                output_schema=version_data.get("output_schema"),
                stub_config=version_data.get("stub_config"),
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
