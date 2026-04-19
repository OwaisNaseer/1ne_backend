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
        {
            # TEMPLATE 25: Tool Recommendations
            "template": {
                "slug": "tool_recommendations",
                "name": "Tool Recommendations",
                "description": "Discover the best MagicSchool tools to use based on your specific needs.",
                "category": "communication",
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
                            "description": "Select the target grade level.",
                            "enum": [
                                "Kindergarten",
                                "1st grade",
                                "2nd grade",
                                "3rd grade",
                                "4th grade",
                                "5th grade",
                                "6th grade",
                                "7th grade",
                                "8th grade",
                                "9th grade",
                                "10th grade",
                                "11th grade",
                                "12th grade",
                            ],
                        },
                        "educator_description": {
                            "type": "string",
                            "title": "Describe Yourself as an Educator and/or Your Needs:",
                            "description": "Share your context and what support you need.",
                            "format": "textarea",
                            "maxLength": 75000,
                        },
                        "attachment_file_name": {
                            "type": "string",
                            "title": "Attached file (optional)",
                            "description": "Optional file name from Add File for context (no file parsing in this version).",
                        },
                    },
                    "required": ["grade_level", "educator_description"],
                },
                "output_schema": {
                    "type": "object",
                    "title": "ToolRecommendationsOutput",
                    "required": ["tool_recommendations"],
                    "properties": {
                        "tool_recommendations": {
                            "type": "string",
                            "title": "Tool Recommendations",
                            "description": "Markdown response with educator tools, student tools, and a short follow-up prompt.",
                        },
                    },
                },
                "stub_config": {
                    "tool_recommendations_template": (
                        "## MagicSchool for Educators Tool Recommendations\n\n"
                        "1. [Math Spiral Review](https://app.magicschool.ai/tools/math-spiral-review) - Generate targeted spiral review problem sets to reinforce algebra, geometry, and pre-calculus skills for {grade_level}; useful for bellringers, homework, or quick formative checks that align with secondary math pacing.\n"
                        "2. [5E Model Lesson Plan](https://app.magicschool.ai/tools/5e-model-lesson-plan) - Create Engage/Explore/Explain/Elaborate/Evaluate lesson plans for high school science labs and units; great for designing inquiry-based biology, chemistry, or physics lessons that meet rigor for {grade_level}.\n"
                        "3. [Science Labs](https://app.magicschool.ai/tools/science-labs) - Generate custom, standards-aware lab activities and materials (procedures, materials, safety notes) tailored to your topic and grade level.\n"
                        "4. [Multiple Explanations](https://app.magicschool.ai/tools/multiple-explanations) - Produce alternate explanations and scaffolds for challenging math/science concepts so you can reteach using different representations.\n"
                        "5. [Rubric Generator](https://app.magicschool.ai/tools/rubric-generator) - Build clear, standards-aligned rubrics for lab reports and projects to communicate expectations and speed up grading.\n\n"
                        "## MagicSchool for Students (MagicStudent) Tool Recommendations\n\n"
                        "1. [Math Review (Student)](https://app.magicschool.ai/magic-student/room/new?tool=math-review-s) - Student-facing practice and review questions for algebra and geometry topics.\n"
                        "2. [AI Tutor (Student)](https://app.magicschool.ai/magic-student/room/new?tool=tutor-me-s) - On-demand tutoring assistant for homework support and worked examples.\n"
                        "3. [Multiple Explanations (Student)](https://app.magicschool.ai/magic-student/room/new?tool=multiple-explanations-s) - Helps students who struggle with one explanation style by offering alternative concept explanations.\n"
                        "4. [Text Proofreader (Student)](https://app.magicschool.ai/magic-student/room/new?tool=proofreader-s) - Lets students check lab reports and written responses for clarity and correctness before submission.\n"
                        "5. [Quiz Me! (Student)](https://app.magicschool.ai/magic-student/room/new?tool=quiz-me-s) - Self-quizzing tool students can use to practice for tests or check mastery of standards.\n\n"
                        "Review these recommendations and tell me if you want the suggested teacher tools organized into a weekly workflow, or if you'd like sample outputs (a spiral review set, a 5E lesson outline, or a ready-to-run lab) created for a specific topic."
                    ),
                },
                "prompt_definition": {
                    "description": (
                        "Recommend the most relevant MagicSchool teacher and MagicStudent tools based on the educator's context."
                    ),
                    "context": (
                        "Return exactly one markdown field: tool_recommendations. "
                        "Structure it with a teacher tools section, a student tools section, numbered recommendations with links, and a concise follow-up offer."
                    ),
                    "exemplar_input": {
                        "grade_level": "9th grade",
                        "educator_description": (
                            "I'm a special education teacher who co-teaches math and science in high school. "
                            "What tools would be helpful for a frog dissection lab and teaching vocabulary?"
                        ),
                    },
                    "exemplar_output": {
                        "tool_recommendations": (
                            "## MagicSchool for Educators Tool Recommendations\n\n"
                            "1. [Math Spiral Review](https://app.magicschool.ai/tools/math-spiral-review) - Generate targeted spiral review problem sets to reinforce algebra, geometry, and pre-calculus skills for 9th grade.\n"
                            "2. [5E Model Lesson Plan](https://app.magicschool.ai/tools/5e-model-lesson-plan) - Create inquiry-based lesson plans for science labs and units with clearer structure and pacing.\n"
                            "3. [Science Labs](https://app.magicschool.ai/tools/science-labs) - Generate custom, standards-aware lab activities and materials (procedures, safety notes, and assessment checkpoints).\n"
                            "4. [Multiple Explanations](https://app.magicschool.ai/tools/multiple-explanations) - Offer differentiated explanations for complex terms and concepts so students can access content in multiple ways.\n"
                            "5. [Rubric Generator](https://app.magicschool.ai/tools/rubric-generator) - Build clear, standards-aligned rubrics for lab reports and projects.\n\n"
                            "## MagicSchool for Students (MagicStudent) Tool Recommendations\n\n"
                            "1. [Math Review (Student)](https://app.magicschool.ai/magic-student/room/new?tool=math-review-s) - Student-facing review and practice for algebra/geometry topics.\n"
                            "2. [AI Tutor (Student)](https://app.magicschool.ai/magic-student/room/new?tool=tutor-me-s) - On-demand support for homework, concept checks, and worked examples.\n"
                            "3. [Multiple Explanations (Student)](https://app.magicschool.ai/magic-student/room/new?tool=multiple-explanations-s) - Helps students revisit challenging ideas using alternative explanation styles.\n"
                            "4. [Text Proofreader (Student)](https://app.magicschool.ai/magic-student/room/new?tool=proofreader-s) - Improves clarity and correctness in student lab write-ups before submission.\n"
                            "5. [Quiz Me! (Student)](https://app.magicschool.ai/magic-student/room/new?tool=quiz-me-s) - Self-quizzing practice to build retention before tests.\n\n"
                            "Review these recommendations and tell me if you'd like a weekly workflow plan or sample outputs for your next biology/science unit."
                        ),
                    },
                },
            },
        },
        {
            # TEMPLATE 26: Feedback Writer
            "template": {
                "slug": "feedback_writer",
                "name": "Feedback Writer",
                "description": "Generate structured writing feedback with strengths, growth areas, and clear next steps.",
                "category": "communication",
                "subject_default": "english",
                "grade_bands_supported": ["3-5", "6-8", "9-12"],
            },
            "version": {
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "grade_level": {
                            "type": "string",
                            "title": "Grade level",
                            "description": "Select the target grade level.",
                            "enum": [
                                "3rd grade",
                                "4th grade",
                                "5th grade",
                                "6th grade",
                                "7th grade",
                                "8th grade",
                                "9th grade",
                                "10th grade",
                                "11th grade",
                                "12th grade",
                            ],
                        },
                        "assignment_description": {
                            "type": "string",
                            "title": "Describe the assignment",
                            "description": "Describe the writing task and success criteria.",
                            "format": "textarea",
                            "maxLength": 75000,
                        },
                        "feedback_rubric": {
                            "type": "string",
                            "title": "Type of feedback or rubric",
                            "description": "Paste rubric criteria, focus skills, or scoring guidance.",
                            "format": "textarea",
                            "maxLength": 75000,
                        },
                        "additional_instructions": {
                            "type": "string",
                            "title": "Additional instructions for the feedback (optional)",
                            "description": "Optional tone, focus, or grading constraints.",
                            "format": "textarea",
                            "maxLength": 75000,
                        },
                        "student_writing": {
                            "type": "string",
                            "title": "Insert the writing you want feedback on",
                            "description": "Paste student writing for targeted feedback.",
                            "format": "textarea",
                            "maxLength": 75000,
                        },
                    },
                    "required": [
                        "grade_level",
                        "assignment_description",
                        "feedback_rubric",
                        "student_writing",
                    ],
                },
                "output_schema": {
                    "type": "object",
                    "title": "FeedbackWriterOutput",
                    "required": [
                        "areas_of_strength",
                        "areas_for_growth",
                        "writing_mechanics_feedback",
                        "next_steps",
                        "encouraging_summary",
                    ],
                    "properties": {
                        "areas_of_strength": {
                            "type": "string",
                            "title": "Areas of Strength",
                            "description": "Specific strengths tied to evidence from the writing.",
                        },
                        "areas_for_growth": {
                            "type": "string",
                            "title": "Areas for Growth",
                            "description": "Actionable improvement points with examples.",
                        },
                        "writing_mechanics_feedback": {
                            "type": "string",
                            "title": "General Feedback on Writing Mechanics",
                            "description": "Mechanics notes such as grammar, punctuation, sentence flow, and clarity.",
                        },
                        "next_steps": {
                            "type": "string",
                            "title": "Suggested Revision Next Steps",
                            "description": "2-4 concrete revision steps the student can do next.",
                        },
                        "encouraging_summary": {
                            "type": "string",
                            "title": "Encouraging Summary",
                            "description": "A short supportive closing statement.",
                        },
                    },
                },
                "stub_config": {
                    "areas_of_strength_template": (
                        "- You clearly explain the core idea of the assignment and keep your response focused on the prompt.\n"
                        "- You include relevant text evidence and connect examples back to your analysis.\n"
                        "- Your writing shows strong effort and thoughtful interpretation for {grade_level} expectations."
                    ),
                    "areas_for_growth_template": (
                        "- Go deeper in your analysis by explaining why each example matters, not only what happens.\n"
                        "- Vary sentence openings to improve flow and reduce repeated phrasing.\n"
                        "- Add one additional example from another part of the text to strengthen your argument."
                    ),
                    "writing_mechanics_feedback_template": (
                        "- Improve formal tone in a few places by replacing conversational wording.\n"
                        "- Check punctuation and comma usage in longer sentences.\n"
                        "- Review transitions between paragraphs so each idea connects more smoothly."
                    ),
                    "next_steps_template": (
                        "1. Revise one paragraph by adding deeper explanation after your evidence.\n"
                        "2. Replace at least two informal phrases with academic wording.\n"
                        "3. Add one more supporting quote and explain its significance.\n"
                        "4. Re-read aloud once to catch clarity and punctuation issues."
                    ),
                    "encouraging_summary_template": (
                        "You are on the right track. With a bit more depth and polish, this can become a strong final piece."
                    ),
                },
                "prompt_definition": {
                    "description": (
                        "Generate clear, rubric-aligned writing feedback for student work."
                    ),
                    "context": (
                        "Return exactly these sections: areas_of_strength, areas_for_growth, "
                        "writing_mechanics_feedback, next_steps, encouraging_summary. "
                        "Use direct, supportive language; cite concrete evidence from the student writing; "
                        "keep feedback actionable and age-appropriate for the selected grade level."
                    ),
                    "exemplar_input": {
                        "grade_level": "8th grade",
                        "assignment_description": (
                            "Analyze imagery in 'Of Mice and Men' and include at least three textual examples."
                        ),
                        "feedback_rubric": (
                            "Accurate analysis of imagery, use of evidence, organization, and clear writing mechanics."
                        ),
                        "additional_instructions": (
                            "Focus on conventions and use of evidence. Keep tone supportive and specific."
                        ),
                        "student_writing": (
                            "In 'Of Mice and Men,' Steinbeck uses imagery to show the hard life during the Great Depression. "
                            "One example is George describing the dream ranch with Lennie. Another is the rabbits Lennie wants "
                            "to care for. These images help us feel the characters' hopes and struggles."
                        ),
                    },
                    "exemplar_output": {
                        "areas_of_strength": (
                            "- You identify multiple examples of imagery and connect them to the novel's themes.\n"
                            "- Your references to George's dream ranch and Lennie's rabbits show clear textual awareness.\n"
                            "- Your response stays focused on the prompt and presents a clear central idea."
                        ),
                        "areas_for_growth": (
                            "- Push your analysis further by explaining why each image is significant to character development.\n"
                            "- Add one additional example from a different scene to show range.\n"
                            "- Expand commentary after each example so your reasoning is more detailed."
                        ),
                        "writing_mechanics_feedback": (
                            "- Use more formal wording in place of conversational phrases.\n"
                            "- Combine short sentences where appropriate to improve flow.\n"
                            "- Check punctuation in compound sentences for clarity."
                        ),
                        "next_steps": (
                            "1. Add one new quotation with analysis.\n"
                            "2. Revise at least one paragraph to include deeper commentary.\n"
                            "3. Replace informal wording with academic language.\n"
                            "4. Proofread for punctuation and sentence variety."
                        ),
                        "encouraging_summary": (
                            "Great start. Your ideas are clear, and with deeper explanation your analysis will become much stronger."
                        ),
                    },
                },
            },
        },
        {
            # TEMPLATE 27: Text Rewriter
            "template": {
                "slug": "text_rewriter",
                "name": "Text Rewriter",
                "description": "Take any text and rewrite it with custom criteria.",
                "category": "communication",
                "subject_default": "english",
                "grade_bands_supported": ["6-8", "9-12"],
            },
            "version": {
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "original_text": {
                            "type": "string",
                            "title": "Original Text",
                            "description": "Paste the original text you want rewritten.",
                            "format": "textarea",
                            "maxLength": 75000,
                        },
                        "rewrite_instruction": {
                            "type": "string",
                            "title": "Rewrite so that",
                            "description": "Explain how the text should be rewritten (length, tone, style, clarity, or audience).",
                            "format": "textarea",
                            "maxLength": 75000,
                        },
                    },
                    "required": ["original_text", "rewrite_instruction"],
                },
                "output_schema": {
                    "type": "object",
                    "title": "TextRewriterOutput",
                    "required": ["rewritten_text"],
                    "properties": {
                        "rewritten_text": {
                            "type": "string",
                            "title": "Rewritten Text",
                            "description": "The rewritten version of the original text that follows the instruction.",
                        }
                    },
                },
                "stub_config": {
                    "rewritten_text_template": (
                        "Choose a work of fiction with a rebel character who disrupts societal, familial, or political affairs. "
                        "In a focused essay, analyze how the rebel's complex motivation shapes your interpretation of the work as a whole."
                    ),
                },
                "prompt_definition": {
                    "description": (
                        "Rewrite the provided text using the exact user instruction while preserving the original meaning unless instructed otherwise."
                    ),
                    "context": (
                        "Return exactly one field: rewritten_text. "
                        "Provide only the rewritten passage, ready to use. "
                        "Do not include explanations, labels, or extra commentary."
                    ),
                    "exemplar_input": {
                        "original_text": (
                            "Many works of literature feature a rebel character who changes or disrupts the existing state of societal, "
                            "familial, or political affairs in the text. They may break social norms, challenge long-held values, "
                            "subvert expectations, or participate in other forms of resistance. The character's motivation for this "
                            "rebellious behavior is often complex. Either from your own reading or from the list below, choose a work "
                            "of fiction in which a character changes or disrupts the existing state of societal, familial, or political "
                            "affairs. Then, in a well-written essay, analyze how the complex motivation of the rebel contributes to an "
                            "interpretation of the work as a whole."
                        ),
                        "rewrite_instruction": "it is half as long",
                    },
                    "exemplar_output": {
                        "rewritten_text": (
                            "Choose a work of fiction with a rebel character who disrupts societal, familial, or political affairs. "
                            "In a well-written essay, analyze how the rebel's complex motivation contributes to your interpretation "
                            "of the work as a whole."
                        ),
                    },
                },
            },
        },
        {
            # TEMPLATE 28: Multiple Choice Quiz / Assessment
            "template": {
                "slug": "mc_assessment",
                "name": "Multiple Choice Quiz / Assessment",
                "description": "Generate a multiple choice assessment, quiz, or test based on any topic, standard(s), or criteria.",
                "category": "assessment",
                "subject_default": None,
                "grade_bands_supported": ["3-5", "6-8", "9-12"],
            },
            "version": {
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "grade_level": {
                            "type": "string",
                            "title": "Grade level",
                            "description": "Select the target grade level.",
                            "enum": [
                                "3rd grade",
                                "4th grade",
                                "5th grade",
                                "6th grade",
                                "7th grade",
                                "8th grade",
                                "9th grade",
                                "10th grade",
                                "11th grade",
                                "12th grade",
                            ],
                        },
                        "number_of_questions": {
                            "type": "integer",
                            "title": "Number of Questions",
                            "description": "How many multiple choice questions to generate.",
                            "minimum": 3,
                            "maximum": 25,
                            "default": 5,
                        },
                        "options_per_question": {
                            "type": "integer",
                            "title": "Number of Options per Question",
                            "description": "How many answer options each question should have.",
                            "minimum": 3,
                            "maximum": 6,
                            "default": 4,
                        },
                        "topic_standard_text": {
                            "type": "string",
                            "title": "Topic, Standard, Text, or Description of the Assessment (be specific)",
                            "description": "Main topic and scope of the quiz/assessment.",
                            "format": "textarea",
                            "maxLength": 12000,
                        },
                        "standards_to_align": {
                            "type": "string",
                            "title": "Standards Set to Align to",
                            "description": "Optional standard set(s), e.g., CCSS, TEKS, NGSS, state standards.",
                            "format": "textarea",
                            "maxLength": 12000,
                        },
                        "attachment_file_name": {
                            "type": "string",
                            "title": "Attached file (optional)",
                            "description": "Optional Add File metadata only (no file parsing in this version).",
                        },
                    },
                    "required": [
                        "grade_level",
                        "number_of_questions",
                        "options_per_question",
                        "topic_standard_text",
                    ],
                },
                "output_schema": {
                    "type": "object",
                    "title": "MultipleChoiceAssessmentOutput",
                    "required": ["title", "questions", "answer_key_note", "answer_key"],
                    "properties": {
                        "title": {
                            "type": "string",
                            "title": "Assessment title",
                        },
                        "questions": {
                            "type": "array",
                            "title": "Questions",
                            "items": {
                                "type": "object",
                                "required": ["number", "question", "options"],
                                "properties": {
                                    "number": {"type": "integer", "title": "Question number"},
                                    "question": {"type": "string", "title": "Question stem"},
                                    "options": {
                                        "type": "array",
                                        "title": "Options",
                                        "items": {"type": "string"},
                                    },
                                },
                            },
                        },
                        "answer_key_note": {
                            "type": "string",
                            "title": "Answer key note",
                        },
                        "answer_key": {
                            "type": "array",
                            "title": "Answer key",
                            "items": {"type": "string"},
                        },
                        "standards_alignment": {
                            "type": "array",
                            "title": "Standards alignment",
                            "items": {"type": "string"},
                        },
                        "review_note": {
                            "type": "string",
                            "title": "Review note",
                        },
                    },
                },
                "stub_config": None,
                "prompt_definition": {
                    "description": "Generate a multiple choice quiz/assessment aligned to the requested grade level, topic, and standards. Return clear question stems with labeled options, answer key, and optional standards alignment.",
                    "context": "Output must match output_schema exactly with title, questions, answer_key_note, answer_key, optional standards_alignment, and optional review_note.",
                    "exemplar_input": {
                        "grade_level": "7th grade",
                        "number_of_questions": 5,
                        "options_per_question": 4,
                        "topic_standard_text": "Diagnostic assessment on the process of mitosis",
                        "standards_to_align": "Any standards worldwide (CCSS, TEKS, Ontario, Florida)",
                    },
                    "exemplar_output": {
                        "title": "Diagnostic Assessment on the Process of Mitosis",
                        "questions": [
                            {
                                "number": 1,
                                "question": "Which of the following best describes the process of mitosis?",
                                "options": [
                                    "a. The division of DNA into two identical daughter cells",
                                    "b. The exchange of genetic material between homologous chromosomes",
                                    "c. The joining of a sperm and egg cell to form a zygote",
                                    "d. The duplication of chromosomes followed by their separation into two identical nuclei",
                                ],
                            },
                            {
                                "number": 2,
                                "question": "What is the purpose of mitosis in the cell cycle?",
                                "options": [
                                    "a. To repair damaged DNA",
                                    "b. To produce gametes for sexual reproduction",
                                    "c. To create genetic diversity",
                                    "d. To generate two identical daughter cells",
                                ],
                            },
                            {
                                "number": 3,
                                "question": "During which phase of mitosis do the chromosomes line up at the equator of the cell?",
                                "options": [
                                    "a. Prophase",
                                    "b. Metaphase",
                                    "c. Anaphase",
                                    "d. Telophase",
                                ],
                            },
                            {
                                "number": 4,
                                "question": "What happens to the nuclear membrane during mitosis?",
                                "options": [
                                    "a. It disappears during prophase and reappears during telophase",
                                    "b. It remains intact throughout the entire process",
                                    "c. It dissolves during metaphase and reforms during anaphase",
                                    "d. It separates into two halves during telophase",
                                ],
                            },
                            {
                                "number": 5,
                                "question": "Which of the following is NOT a stage of mitosis?",
                                "options": [
                                    "a. Interphase",
                                    "b. Prophase",
                                    "c. Metaphase",
                                    "d. Telophase",
                                ],
                            },
                        ],
                        "answer_key_note": "Answer Key (Always review AI generated answers for accuracy - Math is more likely to be inaccurate):",
                        "answer_key": ["1. d", "2. d", "3. b", "4. a", "5. a"],
                        "standards_alignment": [
                            "MS-LS1-3: Use argument supported by evidence for how the body is a system of interacting subsystems composed of groups of cells.",
                            "MS-LS3-1: Develop and use a model to describe why structural changes to genes (mutations) located on chromosomes may affect proteins and may result in harmful, beneficial, or neutral effects to the structure and function of the organism.",
                        ],
                        "review_note": "Review this closely for accuracy, especially in math, as AI may have limitations.",
                    },
                },
            },
        },
        {
            # TEMPLATE 29: Academic Content Generator
            "template": {
                "slug": "academic_content_generator",
                "name": "Academic Content",
                "description": "Generate custom academic content based on the criteria of your choice.",
                "category": "lesson_design",
                "subject_default": None,
                "grade_bands_supported": ["3-5", "6-8", "9-12"],
            },
            "version": {
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "grade_level": {
                            "type": "string",
                            "title": "Grade level",
                            "description": "Select the target grade level.",
                            "enum": [
                                "3rd grade",
                                "4th grade",
                                "5th grade",
                                "6th grade",
                                "7th grade",
                                "8th grade",
                                "9th grade",
                                "10th grade",
                                "11th grade",
                                "12th grade",
                            ],
                        },
                        "topic_standard_objective": {
                            "type": "string",
                            "title": "Topic, standard, objective (be as specific as possible)",
                            "description": "Main objective/topic for the generated content.",
                            "format": "textarea",
                            "maxLength": 12000,
                        },
                        "text_length": {
                            "type": "string",
                            "title": "Text Length",
                            "description": "Requested approximate output length (e.g., 1 page exactly).",
                            "maxLength": 200,
                        },
                        "content_type": {
                            "type": "string",
                            "title": "Content Type",
                            "description": "Type of academic content (e.g., textbook page, reading passage, explainer notes).",
                            "maxLength": 200,
                        },
                        "additional_criteria": {
                            "type": "string",
                            "title": "Additional Criteria",
                            "description": "Any additional requirements to include.",
                            "format": "textarea",
                            "maxLength": 12000,
                        },
                        "attachment_file_name": {
                            "type": "string",
                            "title": "Attached file (optional)",
                            "description": "Optional Add File metadata only (no file parsing in this version).",
                        },
                    },
                    "required": [
                        "grade_level",
                        "topic_standard_objective",
                        "text_length",
                        "content_type",
                    ],
                },
                "output_schema": {
                    "type": "object",
                    "title": "AcademicContentOutput",
                    "required": ["academic_content"],
                    "properties": {
                        "academic_content": {
                            "type": "string",
                            "title": "Academic Content",
                            "description": "Main generated academic content with headings, bold sections, and bullet points.",
                        }
                    },
                },
                "stub_config": None,
                "prompt_definition": {
                    "description": "Generate academic content tailored to grade level, topic/objective, requested length, content type, and additional criteria. Keep the writing age-appropriate, factual, and instruction-ready.",
                    "context": "Output must match output_schema exactly with a single field academic_content. Inside that field, provide well-structured markdown with heading(s), bolded subheads, and bullets where helpful.",
                    "exemplar_input": {
                        "grade_level": "7th grade",
                        "topic_standard_objective": "SWBAT explain the differences between ethnic and religious groups - they are studying southern Africa",
                        "text_length": "1 Page exactly",
                        "content_type": "Textbook page",
                        "additional_criteria": "Make sure that it explicitly names several of the ethnic and religious groups in southern Africa",
                    },
                    "exemplar_output": {
                        "academic_content": (
                            "## Understanding Ethnic and Religious Diversity in Southern Africa\n\n"
                            "In Southern Africa, there is a rich tapestry of ethnic and religious groups that contribute to the region's cultural diversity.\n\n"
                            "One prominent ethnic group in Southern Africa is the Zulu people. Another significant ethnic group is the Xhosa people. The San people, also known as the Bushmen, are one of the oldest ethnic groups in the region.\n\n"
                            "Religiously, Southern Africa is diverse as well. Christianity is the dominant religion with denominations such as Catholicism, Anglicanism, and various independent churches. Islam is also practiced by a significant minority. Additionally, traditional African religions, such as ancestral worship and animism, continue to be practiced.\n\n"
                            "**What students will be able to do (SWBAT):** Explain the differences between ethnic groups and religious groups and identify several ethnic and religious groups found in southern Africa.\n\n"
                            "**What is an ethnic group?**\n"
                            "An ethnic group is a group of people who share a common cultural background, including language, ancestry, and traditions.\n\n"
                            "**What is a religious group?**\n"
                            "A religious group is a community of people who share beliefs about spirituality, rituals, sacred texts, and worship practices.\n\n"
                            "**Key differences (easy to remember):**\n"
                            "- Ethnicity is about culture, ancestry, and language.\n"
                            "- Religion is about beliefs, worship, and spiritual practices.\n"
                            "- A person can belong to one ethnic group and follow any religion (or no religion).\n"
                            "- Ethnic identity is usually inherited; religious identity can be chosen or changed.\n\n"
                            "**Examples in southern Africa - Ethnic groups (named):**\n"
                            "- Zulu\n"
                            "- Xhosa\n"
                            "- Shona\n"
                            "- Ndebele\n"
                            "- Tswana\n"
                            "- Venda\n\n"
                            "**Examples in southern Africa - Religious groups (named):**\n"
                            "- Christianity\n"
                            "- African Traditional Religions\n"
                            "- Islam\n"
                            "- Hinduism\n"
                            "- No religious affiliation / secular\n\n"
                            "**How ethnicity and religion interact in southern Africa:**\n"
                            "- Many ethnic groups practice Christianity alongside African Traditional Religions.\n"
                            "- Ethnic traditions often remain strong even when religious beliefs change.\n"
                            "- Historical migration and colonialism brought new religions and mixed cultures.\n\n"
                            "**Short classroom activity (1-2 minutes):**\n"
                            "Ask students to pick one ethnic group and one religious group named above and explain how these identities might shape a person's life.\n\n"
                            "**Summary:**\n"
                            "Ethnic groups are tied to shared culture and ancestry. Religious groups are tied to shared beliefs and worship."
                        )
                    },
                },
            },
        },
        {
            # TEMPLATE 30: Text Proofreader
            "template": {
                "slug": "text_proofreader",
                "name": "Text Proofreader",
                "description": "Proofread any text - correcting grammar, spelling, punctuation, and adding clarity.",
                "category": "communication",
                "subject_default": None,
                "grade_bands_supported": ["K-2", "3-5", "6-8", "9-12"],
            },
            "version": {
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "original_text": {
                            "type": "string",
                            "title": "Original Text",
                            "description": "Paste the source text you want to proofread.",
                            "format": "textarea",
                            "maxLength": 75000,
                        },
                        "attachment_file_name": {
                            "type": "string",
                            "title": "Attached file (optional)",
                            "description": "Optional file name from Add File for context (no file parsing in this version).",
                        },
                    },
                    "required": ["original_text"],
                },
                "output_schema": {
                    "type": "object",
                    "title": "TextProofreaderOutput",
                    "required": ["title", "rewritten_text", "applied_criteria"],
                    "properties": {
                        "title": { "type": "string", "title": "Response title" },
                        "rewritten_text": {
                            "type": "string",
                            "title": "Proofread text",
                            "description": "Primary proofread version of the original text.",
                        },
                        "applied_criteria": {
                            "type": "array",
                            "title": "Applied criteria",
                            "description": "Short bullets summarizing how proofreading improvements were applied.",
                            "items": {"type": "string"},
                        },
                        "optional_alternatives": {
                            "type": "array",
                            "title": "Optional alternatives",
                            "description": "Optional alternate proofreading versions.",
                            "items": {"type": "string"},
                        },
                    },
                },
                "stub_config": None,
                "prompt_definition": {
                    "description": "Proofread user-provided text, correcting grammar, spelling, punctuation, and adding clarity while preserving the original meaning.",
                    "context": "Output must match output_schema exactly with title, rewritten_text, applied_criteria, and optional optional_alternatives. If attachment_file_name is provided, treat it as context metadata only.",
                    "exemplar_input": {
                        "original_text": "In 'Of Mice and Men,' John Steinbeck uses lots of vivid descriptions to depict the hardships of life during the Great Depression. These descriptions help readers empathize with the characters and enhance the book's appeal. One prominent example is when George describes the dream ranch he envisions with Lennie.\n\nIn the book, George says, 'O.K. Someday—we're gonna get the jack together and we're gonna have a little house and a couple of acres an' a cow and some pigs...' This imagery creates a tranquil setting where they can live happily. The house, the acres, and the animals give us a good feeling. It's like a movie in our mind, and we can see it clearly.\n\nAnother image is when George talks about the rabbits Lennie wants to take care for. George says, 'We'll have a big vegetable patch and a rabbit hutch and chickens. And when it rains in the winter, we'll just say the hell with 'go' to work, and we'll build up a fire in the stove and set around it an' listen to the rain comin' down on the roof.' This description conjures an inviting space for relaxation. The rain, the fire, and the rabbits evoke a sense of warmth, creating a delightful mental image.",
                    },
                    "exemplar_output": {
                        "title": "Text Proofreader Result",
                        "rewritten_text": "In 'Of Mice and Men,' John Steinbeck uses lots of vivid descriptions to depict the hardships of life during the Great Depression. These descriptions help readers empathize with the characters and enhance the book's appeal. One prominent example is when George describes the dream ranch he envisions with Lennie.\n\nIn the book, George says, 'O.K. Someday—we're gonna get the jack together and we're gonna have a little house and a couple of acres an' a cow and some pigs...' This imagery creates a tranquil setting where they can live happily. The house, the acres, and the animals give readers a good feeling. It's like a movie in our minds—we can see it clearly.\n\nAnother image is when George talks about the rabbits Lennie wants to take care of. George says, 'We'll have a big vegetable patch and a rabbit hutch and chickens. And when it rains in the winter, we'll just say the hell with 'go' to work, and we'll build up a fire in the stove and set around it, an' listen to the rain comin' down on the roof.' This description conjures an inviting space for relaxation. The rain, the fire, and the rabbits evoke a sense of warmth, creating a delightful mental image.",
                        "applied_criteria": [
                            "Corrected grammar and word choice (for example, 'take care for' -> 'take care of' and improved phrasing for clarity).",
                            "Cleaned up punctuation and sentence boundaries, especially around the quoted dialogue and commas.",
                            "Improved readability by tightening a few transitions while preserving the original meaning and examples.",
                            "Maintained the structure of the explanation and ensured each paragraph connects back to the effect on readers.",
                        ],
                    },
                },
            },
        },
        {
            # TEMPLATE 31: Professional Email
            "template": {
                "slug": "professional_email",
                "name": "Professional Email",
                "description": "Generate a professional email communication.",
                "category": "communication",
                "subject_default": None,
                "grade_bands_supported": ["K-2", "3-5", "6-8", "9-12"],
            },
            "version": {
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "author_name": {
                            "type": "string",
                            "title": "Author Name",
                            "description": "Name to sign at the end of the email.",
                            "maxLength": 200,
                        },
                        "email_content": {
                            "type": "string",
                            "title": "Content to include in the email",
                            "description": "Paste the message details you want included in the email.",
                            "format": "textarea",
                            "maxLength": 75000,
                        },
                    },
                    "required": ["author_name", "email_content"],
                },
                "output_schema": {
                    "type": "object",
                    "title": "ProfessionalEmailOutput",
                    "required": ["subject:"],
                    "properties": {
                        "subject:": {
                            "type": "string",
                            "title": "Subject:",
                            "description": "Subject value followed by the email body content."
                        },
                    },
                },
                "stub_config": None,
                "prompt_definition": {
                    "description": "Write a professional, ready-to-send email. Use the provided email_content to create a clear subject and a polished message body. Keep the tone respectful and appropriate for educational stakeholders. Add a brief thank-you line and close with 'Best regards,' followed by the author_name as the signature.",
                    "context": "The output must be split into the section key: subject:. Write HUMAN-READABLE content only; no JSON inside the section. Put the subject value first, then a blank line, then the email body paragraphs, and end with the signature.",
                    "exemplar_input": {
                        "author_name": "Mrs. Smith",
                        "email_content": "Please see my earlier email regarding the changes to that basketball schedule for this season. We need to make sure that we have one administrator at each home game. I will start a google form where we can all sign up to be present at one or two games.",
                    },
                    "exemplar_output": {
                        "subject:": "Administrator Coverage for Home Basketball Games\n\nPlease see my earlier email about the changes to that basketball schedule for this season. We need to make sure that we have one administrator at each home game. I will start a Google Form where we can all sign up to be present at one or two games.\n\nThank you for your support — I appreciate your help in ensuring we have coverage.\n\nBest regards,\nMrs. Smith",
                    },
                },
            },
        },
        {
            # TEMPLATE 32: IEP Generator
            "template": {
                "slug": "iep_generator",
                "name": "IEP Generator",
                "description": "Generate an Individualized Education Program (IEP) draft.",
                "category": "behavior",
                "subject_default": None,
                "grade_bands_supported": ["K-2", "3-5", "6-8", "9-12"],
            },
            "version": {
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "student_name": {
                            "type": "string",
                            "title": "Student Name",
                            "description": "Name of the student for the IEP.",
                            "maxLength": 200,
                        },
                        "grade": {
                            "type": "string",
                            "title": "Grade",
                            "description": "Select the grade level for the student.",
                            "enum": [
                                "K",
                                "1st grade",
                                "2nd grade",
                                "3rd grade",
                                "4th grade",
                                "5th grade",
                                "6th grade",
                                "7th grade",
                                "8th grade",
                                "9th grade",
                                "10th grade",
                                "11th grade",
                                "12th grade",
                            ],
                        },
                        "abilities_needs_strengths": {
                            "type": "string",
                            "title": "Description of abilities, needs, and strengths",
                            "description": "Describe the student's abilities, needs, and strengths for the IEP.",
                            "format": "textarea",
                            "maxLength": 12000,
                        },
                        "sensory_strategies": {
                            "type": "string",
                            "title": "Description of sensory strategies, include the main needs",
                            "description": "Describe the student's sensory strategies and sensory-related needs.",
                            "format": "textarea",
                            "maxLength": 12000,
                        },
                        "sensory_balance_activities": {
                            "type": "string",
                            "title": "Can you suggest activities to help improve [Student Name]'s sensory balance?",
                            "description": "Suggest sensory balance activities that could be implemented in the classroom.",
                            "format": "textarea",
                            "maxLength": 12000,
                        },
                    },
                    "required": [
                        "student_name",
                        "grade",
                        "abilities_needs_strengths",
                        "sensory_strategies",
                        "sensory_balance_activities",
                    ],
                },
                "output_schema": {
                    "type": "object",
                    "title": "IEPGeneratorOutput",
                    "required": ["iep_draft"],
                    "properties": {
                        "iep_draft": {
                            "type": "string",
                            "title": "Student IEP Draft - Review closely before implementation",
                            "description": "Markdown IEP draft with clear headings, bold measurable goals, and bullet lists.",
                        }
                    },
                },
                "stub_config": None,
                "prompt_definition": {
                    "description": "Generate a complete IEP draft for the student using the provided abilities/needs/strengths and sensory information.",
                    "context": "Output must match output_schema exactly with a single field iep_draft. Write the IEP in HUMAN-READABLE markdown only. Include the following headings in order: Present Levels of Performance; Student Needs and Impact of Disability; Goals and Objectives; Accommodations and Modifications. Under Goals and Objectives, include multiple bold Measurable Goals and supporting Objectives as bullet lists. Under Accommodations and Modifications, include a bullet list of supports.",
                    "exemplar_input": {
                        "student_name": "Student Name",
                        "grade": "4th grade",
                        "abilities_needs_strengths": "Student Name is a 4th-grade learner with strong curiosity and a clear willingness to participate when routines are predictable. They benefit from structured transitions and visual supports. Sensory processing differences impact attention, engagement, and comfort during unstructured moments.",
                        "sensory_strategies": "Student Name benefits from predictable sensory supports including scheduled breaks, access to a sensory tool box, and calming input when overwhelmed (e.g., quiet space, reduced noise, movement opportunities). They may show sensory sensitivities during loud environments, crowded spaces, or when unexpected changes occur.",
                        "sensory_balance_activities": "Suggest classroom and movement activities that support sensory regulation. Examples include guided movement breaks, sensory-friendly work stations, structured sensory circuits, and planned opportunities for proprioceptive and vestibular input. Provide activities that can be implemented during transitions and short breaks."
                    },
                    "exemplar_output": {
                        "iep_draft": "## Present Levels of Performance\n\nStudent Name is a 4th-grade learner who demonstrates strengths in curiosity, participation, and effort when expectations are clear. Student Name may require additional support to manage sensory input and maintain attention during transitions and high-stimulation activities.\n\nStudent Name’s sensory processing needs affect how they experience classroom environments. Loud or unpredictable situations can reduce engagement and increase the likelihood of off-task behavior, withdrawal, or avoidance. With consistent routines and sensory supports, Student Name can participate more successfully and demonstrate improved readiness for learning.\n\n## Student Needs and Impact of Disability\n\n- Student Name needs structured routines and clear expectations to support self-regulation.\n- Student Name needs sensory strategies to manage overwhelm and support continued participation.\n- Student Name needs opportunities for movement and sensory input in predictable ways to improve focus and reduce stress.\n\n## Goals and Objectives\n\n**Measurable Goal: Enhancing Social Communication Skills**\n\n- **Objective:** During structured classroom discussions, Student Name will participate in a turn-taking routine (e.g., initiate and respond using a sentence starter) in 4 out of 5 opportunities across 3 consecutive sessions.\n- **Objective:** Student Name will use an appropriate communication strategy (request help, ask for a break, or express a need) when support is needed in 4 out of 5 observed opportunities.\n\n**Measurable Goal: Managing Sensory Sensitivities**\n\n- **Objective:** When exposed to a predictable classroom trigger (e.g., noisy transition), Student Name will use a taught regulation strategy (break card, quiet corner routine, or sensory tool) within 5 minutes in 4 out of 5 opportunities.\n- **Objective:** Student Name will remain engaged in assigned task activities for at least 10 minutes with no more than 2 redirections in 4 out of 5 opportunities.\n\n**Measurable Goal: Building Flexibility with Routines**\n\n- **Objective:** Student Name will transition using a visual schedule and transition script with successful completion in 4 out of 5 opportunities across 3 consecutive weeks.\n- **Objective:** Student Name will demonstrate coping behavior (breathing routine, coping statement, or request for support) after unexpected changes in 4 out of 5 opportunities.\n\n## Accommodations and Modifications\n\n- Provide a predictable daily schedule with visual cues and explicit transition warnings.\n- Offer scheduled sensory breaks (planned and signaled) and access to a sensory tool box.\n- Implement a quiet/calming area for regulation when Student Name becomes overwhelmed.\n- Allow movement breaks and sensory-friendly work options (e.g., alternative seating or short activity circuit).\n- Use sentence starters and communication supports to encourage appropriate social interaction and help-seeking.\n- Provide positive reinforcement for use of regulation and communication strategies.\n\n",
                    },
                },
            },
        },
        {
            # TEMPLATE 33: Report Card Comments
            "template": {
                "slug": "report_card_comments",
                "name": "Report Card Comments",
                "description": "Generate report card comments with a student's strengths and areas for growth.",
                "category": "communication",
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
                            "description": "Select the student's grade level.",
                            "enum": [
                                "K",
                                "1st grade",
                                "2nd grade",
                                "3rd grade",
                                "4th grade",
                                "5th grade",
                                "6th grade",
                                "7th grade",
                                "8th grade",
                                "9th grade",
                                "10th grade",
                                "11th grade",
                                "12th grade",
                            ],
                        },
                        "student_pronouns": {
                            "type": "string",
                            "title": "Student Pronouns",
                            "description": "e.g., he/she/they.",
                            "maxLength": 100,
                        },
                        "areas_of_strength": {
                            "type": "string",
                            "title": "Areas of Strength",
                            "description": "Areas to celebrate.",
                            "format": "textarea",
                            "maxLength": 12000,
                        },
                        "areas_for_growth": {
                            "type": "string",
                            "title": "Areas for Growth",
                            "description": "Areas to improve.",
                            "format": "textarea",
                            "maxLength": 12000,
                        },
                    },
                    "required": [
                        "grade_level",
                        "student_pronouns",
                        "areas_of_strength",
                        "areas_for_growth",
                    ],
                },
                "output_schema": {
                    "type": "object",
                    "title": "ReportCardCommentsOutput",
                    "required": ["comments"],
                    "properties": {
                        "comments": {
                            "type": "string",
                            "title": "Exemplar",
                            "description": "Final report card comments with strengths and opportunities for growth.",
                        }
                    },
                },
                "stub_config": None,
                "prompt_definition": {
                    "description": "Generate concise, professional report card comments using the student's strengths and growth areas.",
                    "context": "Output must match output_schema exactly with one field: comments. Write markdown-ready prose using this exact format: **Areas of Strength:** <paragraph> followed by a blank line then **Opportunities for Growth:** <paragraph>. Keep tone supportive, specific, and actionable for families.",
                    "exemplar_input": {
                        "grade_level": "8th grade",
                        "student_pronouns": "he",
                        "areas_of_strength": "Homework completion, good friend, punctual",
                        "areas_for_growth": "Distracted easily, struggles with independent work",
                    },
                    "exemplar_output": {
                        "comments": "**Areas of Strength:** The student consistently demonstrates his strength in completing homework assignments on time. He is a reliable and responsible student in this aspect. Additionally, he is known for being a good friend to his classmates, showing kindness and empathy towards others. Lastly, he is punctual and arrives to class promptly, demonstrating excellent time management skills.\n\n**Opportunities for Growth:** While the student possesses many strengths, he sometimes gets easily distracted during independent work. Encouraging him to stay focused and providing strategies to help him stay on task will support his growth in this area. While he may struggle with independent work, with guidance and practice, he can develop the skills necessary to work more independently and become a more self-sufficient learner.",
                    },
                },
            },
        },
        {
            # TEMPLATE 34: Informational Texts
            "template": {
                "slug": "informational_text_generator",
                "name": "Informational Texts",
                "description": "Generate original informational texts customized to the topic of your choice.",
                "category": "communication",
                "subject_default": None,
                "grade_bands_supported": ["3-5", "6-8", "9-12"],
            },
            "version": {
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "grade_level": {
                            "type": "string",
                            "title": "Grade level",
                            "description": "Select the target grade level.",
                            "enum": [
                                "3rd grade",
                                "4th grade",
                                "5th grade",
                                "6th grade",
                                "7th grade",
                                "8th grade",
                                "9th grade",
                                "10th grade",
                                "11th grade",
                                "12th grade",
                            ],
                        },
                        "text_length": {
                            "type": "string",
                            "title": "Text Length",
                            "description": "Choose the target length for the informational text.",
                            "enum": ["1 paragraph", "1 page", "2 pages"],
                        },
                        "informational_text_type": {
                            "type": "string",
                            "title": "Informational Text Type",
                            "description": "Select the style of informational writing.",
                            "enum": [
                                "Expository",
                                "Literary Nonfiction",
                                "How-To / Procedural",
                                "Cause and Effect",
                                "Compare and Contrast",
                                "Problem and Solution",
                            ],
                        },
                        "topic": {
                            "type": "string",
                            "title": "Topic (be as specific as possible)",
                            "description": "Provide the topic and any specific angle or focus to include.",
                            "format": "textarea",
                            "maxLength": 12000,
                        },
                    },
                    "required": [
                        "grade_level",
                        "text_length",
                        "informational_text_type",
                        "topic",
                    ],
                },
                "output_schema": {
                    "type": "object",
                    "title": "InformationalTextsOutput",
                    "required": ["informational_text"],
                    "properties": {
                        "informational_text": {
                            "type": "string",
                            "title": "Exemplar",
                            "description": "Final informational text in clean markdown format.",
                        }
                    },
                },
                "stub_config": None,
                "prompt_definition": {
                    "description": "Write an original informational text appropriate for the selected grade level, length, and text type.",
                    "context": "Output must match output_schema exactly with one field: informational_text. The informational_text should be markdown-ready prose with a clear title and organized paragraphs/subheadings when appropriate. Keep tone academic and age-appropriate.",
                    "exemplar_input": {
                        "grade_level": "9th grade",
                        "text_length": "1 page",
                        "informational_text_type": "Expository",
                        "topic": "Impacts of social media use on adolescents",
                    },
                    "exemplar_output": {
                        "informational_text": "# The Impacts of Social Media Use on Adolescents\n\nSocial media has become an integral part of daily life for many adolescents. Platforms such as Instagram, TikTok, Snapchat, and YouTube provide opportunities for connection, creativity, and learning. At the same time, heavy use can affect mental health, attention, and decision-making. Understanding both the benefits and the risks helps students make healthier choices online.\n\n## Mental Health and Self-Esteem\n\nOne major impact of social media is its influence on mental health and self-image. Positive online spaces can help teens feel included and supported. However, constant comparison to curated posts can lead to insecurity, anxiety, and low self-esteem. When teens measure themselves against unrealistic online standards, they may feel pressure to look or act a certain way.\n\n## Attention, Sleep, and Academic Performance\n\nFrequent notifications and endless scrolling can disrupt focus and reduce productivity. Many adolescents report spending more time online than intended, which can interfere with homework and studying. Late-night device use is also linked to poor sleep quality, and less sleep can negatively affect memory, mood, and classroom performance.\n\n## Relationships and Communication\n\nSocial media can strengthen friendships by helping teens stay connected outside of school. It can also create conflict when messages are misunderstood or when cyberbullying occurs. Because online communication lacks facial expressions and tone, small disagreements can quickly escalate. Learning respectful digital communication is essential.\n\n## Positive Uses of Social Media\n\nDespite the challenges, social media can be used in meaningful ways. Teens can follow educational creators, join academic communities, explore career interests, and share creative projects. Advocacy campaigns and peer support groups can also promote awareness of important social issues.\n\n## Strategies for Healthier Use\n\n- Set daily time limits and take regular screen breaks.\n- Turn off non-essential notifications during study time.\n- Follow accounts that inspire learning and well-being.\n- Avoid comparing your real life to curated online posts.\n- Prioritize sleep by avoiding screens before bedtime.\n- Talk to a trusted adult if online experiences feel harmful.\n\nIn conclusion, social media can be both helpful and harmful for adolescents. Its impact depends on how it is used. With thoughtful habits and digital awareness, teens can benefit from online opportunities while protecting their mental health, academic success, and relationships.",
                    },
                },
            },
        },
        {
            # TEMPLATE 35: Text Summarizer
            "template": {
                "slug": "summarizer",
                "name": "Text Summarizer",
                "description": "Summarize any text in whatever length you choose.",
                "category": "communication",
                "subject_default": None,
                "grade_bands_supported": ["3-5", "6-8", "9-12"],
            },
            "version": {
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "length_of_summary": {
                            "type": "string",
                            "title": "Length of summary",
                            "description": "Select the target summary length.",
                            "enum": ["1 paragraph", "2 paragraphs", "3 paragraphs", "1 page"],
                        },
                        "original_text": {
                            "type": "string",
                            "title": "Original Text",
                            "description": "Paste the original text you want summarized.",
                            "format": "textarea",
                            "maxLength": 75000,
                        },
                    },
                    "required": ["length_of_summary", "original_text"],
                },
                "output_schema": {
                    "type": "object",
                    "title": "TextSummarizerOutput",
                    "required": ["summary"],
                    "properties": {
                        "summary": {
                            "type": "string",
                            "title": "Exemplar",
                            "description": "Final summarized text in clear, readable markdown.",
                        }
                    },
                },
                "stub_config": None,
                "prompt_definition": {
                    "description": "Summarize the provided text according to the selected summary length.",
                    "context": "Output must match output_schema exactly with one field: summary. Write polished, human-readable prose. Preserve key ideas and sequence. Use a clear title when helpful and optional subheadings for readability.",
                    "exemplar_input": {
                        "length_of_summary": "3 paragraphs",
                        "original_text": "The Water Cycle: A Natural Marvel\n\nThe water cycle, also known as the hydrological cycle, is a continuous and vital process that governs the movement of water on Earth. This intricate system comprises several stages, ensuring a dynamic exchange of water between the atmosphere, land, and oceans.\n\n1. Evaporation:\nThe water cycle begins with evaporation, where the sun's radiant energy transforms liquid water from oceans, rivers, lakes, and even plants into water vapor. This invisible water vapor rises into the atmosphere, forming clouds.\n\n2. Condensation:\nAs warm, moist air rises, it encounters cooler temperatures at higher altitudes. This leads to condensation, during which the water vapor changes back into tiny water droplets that cluster together to form clouds.\n\n3. Precipitation:\nWhen the concentration of water droplets in clouds becomes too heavy, gravity takes over, and precipitation occurs. This can take various forms, including rain, snow, sleet, or hail.\n\n4. Infiltration and Runoff:\nAfter precipitation, water either infiltrates into the ground, replenishing groundwater and supporting plant life, or flows over the surface as runoff, eventually reaching rivers, lakes, and oceans.\n\n5. Transpiration:\nTranspiration is a lesser-known but equally significant component of the water cycle. In this stage, plants release water vapor through tiny pores in their leaves.\n\nIn conclusion, the water cycle is a fundamental natural process that sustains life on Earth.",
                    },
                    "exemplar_output": {
                        "summary": "# The Water Cycle: A Natural Marvel\n\nThe water cycle, also known as the hydrological cycle, is a continuous and vital process that governs the movement of water on Earth. This intricate system comprises several stages, ensuring a dynamic exchange of water between the atmosphere, land, and oceans.\n\nEvaporation begins the cycle as the sun's energy transforms liquid water from oceans, rivers, and lakes into water vapor that rises into the atmosphere. As this warm, moist air cools, condensation occurs, forming clouds from tiny droplets. When clouds become saturated, precipitation returns water to Earth's surface as rain, snow, sleet, or hail.\n\nAfter precipitation, water either infiltrates the ground to recharge groundwater or moves as runoff to streams, rivers, and oceans. Plants also contribute through transpiration, releasing water vapor back into the air. Together, these interconnected stages maintain Earth's water distribution and support ecosystems, weather systems, and life.",
                    },
                },
            },
        },
        {
            # TEMPLATE 36: Text Translator
            "template": {
                "slug": "translator",
                "name": "Text Translator",
                "description": "Translate any text or uploaded document into any language.",
                "category": "communication",
                "subject_default": None,
                "grade_bands_supported": ["K-2", "3-5", "6-8", "9-12"],
            },
            "version": {
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "language_to_translate_to": {
                            "type": "string",
                            "title": "Language to translate to",
                            "description": "Target language for translation.",
                            "enum": [
                                "Spanish",
                                "French",
                                "German",
                                "Italian",
                                "Portuguese",
                                "Arabic",
                                "Hindi",
                                "Chinese (Simplified)",
                                "Japanese",
                                "Korean",
                            ],
                        },
                        "original_text": {
                            "type": "string",
                            "title": "Original Text",
                            "description": "Paste the source text that should be translated.",
                            "format": "textarea",
                            "maxLength": 75000,
                        },
                    },
                    "required": ["language_to_translate_to", "original_text"],
                },
                "output_schema": {
                    "type": "object",
                    "title": "TextTranslatorOutput",
                    "required": ["translation"],
                    "properties": {
                        "translation": {
                            "type": "string",
                            "title": "Exemplar",
                            "description": "Final translated text in the requested language.",
                        }
                    },
                },
                "stub_config": None,
                "prompt_definition": {
                    "description": "Translate the provided text accurately into the requested target language while preserving meaning, tone, and structure.",
                    "context": "Output must match output_schema exactly with one field: translation. Return translated text only in readable prose/markdown. Keep names/placeholders (like [Parent's Name]) preserved and translated naturally where appropriate.",
                    "exemplar_input": {
                        "language_to_translate_to": "Spanish",
                        "original_text": "Dear [Parent's Name],\n\nI trust this email finds you well. I am writing to share some encouraging news regarding your child's performance in my math class.\n\nOver the past few weeks, I have had the opportunity to observe a significant improvement in your student's understanding and application of mathematical concepts. Their dedication to academic growth and consistent effort have truly stood out, and I wanted to take a moment to express my appreciation for their hard work.\n\nNot only has your child demonstrated a commendable grasp of challenging mathematical principles, but they have also shown a willingness to engage actively in class discussions and seek clarification when needed. Their enthusiasm for learning is both admirable and infectious, contributing positively to the overall classroom environment.\n\nI believe it is crucial to acknowledge and celebrate the achievements of our students, and your child's progress in math is certainly worthy of recognition. It is evident that they have been investing time and effort into their studies, and as a result, they are reaping the rewards of their commitment.\n\nI encourage you to continue providing support and encouragement to your child in their academic journey. Your involvement plays a vital role in fostering a positive attitude toward learning and contributes to their overall success. If you have any questions or would like to discuss your child's progress further, please feel free to reach out. I am more than happy to schedule a meeting or provide additional information as needed.\n\nThank you for your ongoing support, and I look forward to witnessing your child's continued growth and success in my math class.\n\nBest regards,",
                    },
                    "exemplar_output": {
                        "translation": "Ciertamente! Aquí está la traducción del texto al español:\n\nEstimado/a [Nombre del Padre/Madre],\n\nEspero que este correo electrónico le encuentre bien. Le escribo para compartir algunas noticias alentadoras sobre el desempeño de su hijo/a en mi clase de matemáticas.\n\nEn las últimas semanas, he tenido la oportunidad de observar una mejora significativa en la comprensión y aplicación de conceptos matemáticos por parte de su estudiante. Su dedicación al crecimiento académico y su esfuerzo constante realmente se han destacado, y quería tomar un momento para expresar mi agradecimiento por su arduo trabajo.\n\nNo solo su hijo/a ha demostrado un entendimiento encomiable de principios matemáticos desafiantes, sino que también ha mostrado disposición para participar activamente en las discusiones de clase y buscar aclaraciones cuando es necesario. Su entusiasmo por el aprendizaje es tanto admirable como contagioso, contribuyendo positivamente al ambiente general de la clase.\n\nCreo que es crucial reconocer y celebrar los logros de nuestros estudiantes, y el progreso de su hijo/a en matemáticas ciertamente merece reconocimiento. Es evidente que han estado invirtiendo tiempo y esfuerzo en sus estudios, y como resultado, están cosechando los frutos de su compromiso.\n\nLe animo a seguir brindando apoyo y estímulo a su hijo/a en su trayectoria académica. Su participación desempeña un papel vital en fomentar una actitud positiva hacia el aprendizaje y contribuye a su éxito general. Si tiene alguna pregunta o le gustaría discutir el progreso de su hijo/a en mayor detalle, no dude en ponerse en contacto. Estoy más que encantado de programar una reunión o proporcionar información adicional según sea necesario.\n\nGracias por su continuo apoyo, y espero con interés presenciar el crecimiento continuo y el éxito de su hijo/a en mi clase de matemáticas.\n\nSaludos cordiales,",
                    },
                },
            },
        },
        {
            # TEMPLATE 37: Email Responder
            "template": {
                "slug": "email-responder",
                "name": "Email Responder",
                "description": "Generate a custom professional email response to an email that you received.",
                "category": "communication",
                "subject_default": None,
                "grade_bands_supported": ["K-2", "3-5", "6-8", "9-12"],
            },
            "version": {
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "author_name": {
                            "type": "string",
                            "title": "Author Name",
                            "description": "Name to sign at the end of the response.",
                            "maxLength": 200,
                        },
                        "email_you_are_responding_to": {
                            "type": "string",
                            "title": "Email you're responding to",
                            "description": "Paste the email message you are replying to.",
                            "format": "textarea",
                            "maxLength": 75000,
                        },
                        "what_you_want_to_communicate_in_response": {
                            "type": "string",
                            "title": "What you want to communicate in response",
                            "description": "Key points you want included in your response email.",
                            "format": "textarea",
                            "maxLength": 12000,
                        },
                    },
                    "required": [
                        "email_you_are_responding_to",
                        "what_you_want_to_communicate_in_response",
                    ],
                },
                "output_schema": {
                    "type": "object",
                    "title": "EmailResponderOutput",
                    "required": ["email_response"],
                    "properties": {
                        "email_response": {
                            "type": "string",
                            "title": "Exemplar",
                            "description": "Final professional email response text.",
                        }
                    },
                },
                "stub_config": None,
                "prompt_definition": {
                    "description": "Write a professional email response based on the incoming email and the user's intended message.",
                    "context": "Output must match output_schema exactly with one field: email_response. Start with 'Email Response:' followed by the full response draft. Keep tone professional, concise, and friendly. Use the provided author_name as sign-off when available.",
                    "exemplar_input": {
                        "author_name": "Jane Smith",
                        "email_you_are_responding_to": "Hello Jane,\n\nI hope you are doing well. I am reaching out to see if your school would be open to partnering with us on a feasibility study for using MagicSchool AI in dissertation-level research. I would love to discuss this with you and explore possibilities.\n\nBest regards,\nAlex",
                        "what_you_want_to_communicate_in_response": "That sounds great lets set up time",
                    },
                    "exemplar_output": {
                        "email_response": "Email Response: Hi there,\n\nThank you for reaching out to us! We are thrilled at the prospect of partnering with you for your feasibility study using MagicSchool AI for your dissertation. Let's schedule a time to discuss this further and explore the possibilities. Please let me know your availability, and we can set up a meeting to delve into the details.\n\nLooking forward to connecting with you soon!\n\nBest regards,\n[Your Name]",
                    },
                },
            },
        },
        {
            # TEMPLATE 38: Text Dependent Questions
            "template": {
                "slug": "text-dependent-questions",
                "name": "Text Dependent Questions",
                "description": "Generate text-dependent questions based on any text.",
                "category": "assessment",
                "subject_default": None,
                "grade_bands_supported": ["3-5", "6-8", "9-12"],
            },
            "version": {
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "grade_level": {
                            "type": "string",
                            "title": "Grade level",
                            "description": "Select the target grade level.",
                            "enum": [
                                "3rd grade",
                                "4th grade",
                                "5th grade",
                                "6th grade",
                                "7th grade",
                                "8th grade",
                                "9th grade",
                                "10th grade",
                                "11th grade",
                                "12th grade",
                            ],
                        },
                        "number_of_questions": {
                            "type": "string",
                            "title": "Number of Questions",
                            "description": "Choose how many questions to generate.",
                            "enum": ["3", "5", "7", "10"],
                        },
                        "question_types": {
                            "type": "string",
                            "title": "Question Types",
                            "description": "Comprehension, Literary Devices, Theme, Mix of Literary Devices & Comprehension, etc.",
                            "format": "textarea",
                            "maxLength": 12000,
                        },
                        "text": {
                            "type": "string",
                            "title": "Text",
                            "description": "Insert the source text to generate text-dependent questions from.",
                            "format": "textarea",
                            "maxLength": 75000,
                        },
                    },
                    "required": ["grade_level", "number_of_questions", "question_types", "text"],
                },
                "output_schema": {
                    "type": "object",
                    "title": "TextDependentQuestionsOutput",
                    "required": ["questions_output"],
                    "properties": {
                        "questions_output": {
                            "type": "string",
                            "title": "Exemplar",
                            "description": "Final text-dependent questions output in markdown.",
                        }
                    },
                },
                "stub_config": None,
                "prompt_definition": {
                    "description": "Generate rigorous text-dependent questions from the provided text.",
                    "context": "Output must match output_schema exactly with one field: questions_output. Use markdown with a title line that includes topic and grade level, then a numbered list of questions. Questions must require evidence from the text. End with an 'Answer Key:' heading. If a true answer key cannot be confidently generated, write 'Answer key not provided for text-dependent questions.'",
                    "exemplar_input": {
                        "grade_level": "10th grade",
                        "number_of_questions": "10",
                        "question_types": "comprehension",
                        "text": "Cellular respiration is the process by which cells convert glucose into ATP energy. It includes glycolysis, the Krebs cycle, and the electron transport chain. Aerobic respiration uses oxygen and produces more ATP, while anaerobic respiration occurs without oxygen and produces less ATP.",
                    },
                    "exemplar_output": {
                        "questions_output": "# Text Dependent Questions on Cellular Respiration:\n\n1. What is cellular respiration, and what is its primary function?\n2. Explain the difference between aerobic and anaerobic respiration using evidence from the text.\n3. Which three stages of cellular respiration are listed in the passage?\n4. What does the passage say about oxygen's role in aerobic respiration?\n5. According to the text, why does anaerobic respiration produce less ATP?\n6. Identify the sentence that explains how glucose is used in this process.\n7. Which stage is named first, and what does that ordering suggest about sequence?\n8. What key product is formed by cellular respiration, and where is it mentioned?\n9. How does the passage contrast energy yield between aerobic and anaerobic pathways?\n10. Which words in the text signal a compare/contrast structure between respiration types?\n\n## Answer Key:\n\nAnswer key not provided for text-dependent questions.",
                    },
                },
            },
        },
        {
            # TEMPLATE 39: Text Leveler
            "template": {
                "slug": "text-leveler",
                "name": "Text Leveler",
                "description": "Level any text to adapt it to fit a student's reading level and skills.",
                "category": "communication",
                "subject_default": None,
                "grade_bands_supported": ["3-5", "6-8", "9-12"],
            },
            "version": {
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "grade_level": {
                            "type": "string",
                            "title": "Grade level",
                            "description": "Target grade level for the releveled text.",
                            "enum": [
                                "3rd grade",
                                "4th grade",
                                "5th grade",
                                "6th grade",
                                "7th grade",
                                "8th grade",
                                "9th grade",
                                "10th grade",
                                "11th grade",
                                "12th grade",
                            ],
                        },
                        "original_text": {
                            "type": "string",
                            "title": "Original Text",
                            "description": "Paste the original text to relevel.",
                            "format": "textarea",
                            "maxLength": 75000,
                        },
                    },
                    "required": ["grade_level", "original_text"],
                },
                "output_schema": {
                    "type": "object",
                    "title": "TextLevelerOutput",
                    "required": ["releveled_text"],
                    "properties": {
                        "releveled_text": {
                            "type": "string",
                            "title": "Exemplar",
                            "description": "Final text rewritten for the target grade level.",
                        }
                    },
                },
                "stub_config": None,
                "prompt_definition": {
                    "description": "Rewrite the source text for the selected grade level while preserving original meaning, sequence, and important details.",
                    "context": "Output must match output_schema exactly with one field: releveled_text. Start with a title in this style: 'The Great Gatsby — Releveled for 8th Grade' (adapt text and grade dynamically). Then provide polished paragraph prose only. Do not output JSON.",
                    "exemplar_input": {
                        "grade_level": "8th grade",
                        "original_text": "The Great Gatsby - Full Text\n\nChapter 1\n\nMy family have been prominent, well-to-do people in this middle-western city for three generations. The Carraways are something of a clan and we have a tradition that we're descended from the Dukes of Buccleuch, but the actual founder of my line was my grandfather's brother who came here in fifty-one, sent a substitute to the Civil War and started the wholesale hardware business that my father carries on today.",
                    },
                    "exemplar_output": {
                        "releveled_text": "## The Great Gatsby — Rewritten for 8th Grade\n\nMy family has been well-known and fairly rich in this Midwestern city for three generations. The Carraways are like a close family group, and we even say we are descended from the Dukes of Buccleuch. But the person who began my grandfather's branch came to America in 1851, paid someone else to fight in the Civil War for him, and started the wholesale hardware business my father now runs.\n\nI never met that great-uncle, but people say I look like him, especially in an old portrait in my father's office. I graduated from Yale in 1915, and after serving in what people called the Great War, I came home restless. I liked the center of the country, but it felt like the edge of everything, so I decided to move East and learn the bond business.\n\nEveryone I knew seemed to work in that business. My aunts and uncles talked about it as if they were choosing a prep school for me, and my father agreed to support me for a year. After some delays, I moved East in the spring of 1922, thinking I would return once I had learned enough.\n\nAt first, I tried to find rooms in the city, but it was warm out and I wanted open space and trees. A man in an office suggested we rent a house in a nearby town and commute. He found me a weathered bungalow for eighty dollars a month. At the last minute his company sent him to Washington, so I ended up moving there alone with an old Dodge and a Finnish woman who cooked my meals.",
                    },
                },
            },
        },
        {
            # TEMPLATE 40: Unit Plan Generator
            "template": {
                "slug": "unit-plan-generator",
                "name": "Unit Plan Generator",
                "description": "Generate a unit plan based on any topic and academic standards, with day-by-day lessons and assessments.",
                "category": "lesson_design",
                "subject_default": None,
                "grade_bands_supported": ["3-5", "6-8", "9-12"],
            },
            "version": {
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "grade_level": {
                            "type": "string",
                            "title": "Grade level",
                            "description": "Select the grade level for this unit.",
                            "enum": [
                                "3rd grade",
                                "4th grade",
                                "5th grade",
                                "6th grade",
                                "7th grade",
                                "8th grade",
                                "9th grade",
                                "10th grade",
                                "11th grade",
                                "12th grade",
                            ],
                        },
                        "length_of_unit": {
                            "type": "string",
                            "title": "Length of Unit",
                            "description": "How many school days this unit should span.",
                            "enum": [
                                "5 school days",
                                "10 school days",
                                "15 school days",
                                "20 school days",
                                "25 school days",
                                "30 school days",
                            ],
                        },
                        "unit_title_or_topics": {
                            "type": "string",
                            "title": "Unit Plan Title / Topic(s)",
                            "description": "The unit title and/or main topic(s) to cover.",
                            "format": "textarea",
                            "maxLength": 75000,
                        },
                        "context": {
                            "type": "string",
                            "title": "Context (Optional)",
                            "description": "Optional: audience, course, constraints, or instructional goals.",
                            "format": "textarea",
                            "maxLength": 75000,
                        },
                        "standards": {
                            "type": "string",
                            "title": "Standards Set to Align to (Optional)",
                            "description": "Optional: paste or describe standards (CCSS, TEKS, Ontario, Florida, IB, etc.).",
                            "format": "textarea",
                            "maxLength": 75000,
                        },
                    },
                    "required": ["grade_level", "length_of_unit", "unit_title_or_topics"],
                },
                "output_schema": {
                    "type": "object",
                    "title": "UnitPlanGeneratorOutput",
                    "required": ["unit_plan"],
                    "properties": {
                        "unit_plan": {
                            "type": "string",
                            "title": "Exemplar",
                            "description": "Full unit plan in markdown: overview, numbered lessons (objectives, assessments, key points, standards), culminating ideas, and standards summary.",
                        }
                    },
                },
                "stub_config": None,
                "prompt_definition": {
                    "description": "Create a practical, classroom-ready unit plan for the given grade, duration, and topic. Pace lessons across the stated number of school days.",
                    "context": "Output must match output_schema exactly with one field: unit_plan. Use markdown. Include: a clear unit title; a brief overview; numbered lessons that fit the unit length (group or split days logically); for each lesson: Objectives, Assessments, Key Points, and Standards (cite user-provided standards when supplied, otherwise infer plausible placeholders and label them clearly). Add Culminating Activities Suggestions and a Standards Addressed list. Do not output JSON.",
                    "exemplar_input": {
                        "grade_level": "8th grade",
                        "length_of_unit": "15 school days",
                        "unit_title_or_topics": "Overview of classical Japanese history.",
                        "context": "I am a world history teacher and I need to develop an introductory unit that explores classical Japanese history.",
                        "standards": "",
                    },
                    "exemplar_output": {
                        "unit_plan": "## Unit Title: Overview of Classical Japanese History\n\n### Overview\nThis fifteen-day introductory unit situates classical Japan (roughly late Yamato through early feudal transitions) for eighth-grade world history students. Students map geography and periodization, trace political and religious change, and analyze primary and secondary sources on court culture and society.\n\n---\n\n### Lesson 1 — Geography, Chronology, and Vocabulary\n\n**Objectives:** Students locate Japan’s major islands and neighboring regions; build a working timeline of classical periods; define key terms (e.g., *kami*, *Shotoku*, *Heian*).\n\n**Assessments:** Quick map check; exit ticket with three terms and one inference.\n\n**Key Points:** Physical geography and isolation; why period labels matter; how historians divide classical eras.\n\n**Standards:** *Placeholders — align to your framework:* cite specific reading, writing, and speaking standards for historical sources and geographic reasoning.\n\n---\n\n### Lesson 2 — Early State and Borrowing from China\n\n**Objectives:** Explain how early Japanese rulers consolidated power; describe Taika-style reforms and Chinese influence.\n\n**Assessments:** Short comparison chart (Japan vs. Chinese models); one-paragraph explanation.\n\n**Key Points:** Yamato legitimacy; missions to China; selective adaptation vs. copying.\n\n**Standards:** *Placeholders:* argument from evidence; comparing societies.\n\n---\n\n### Lesson 3 — Prince Shōtoku and Buddhist Foundations\n\n**Objectives:** Interpret the Seventeen-Article Constitution as a historical source; connect Buddhism to governance and culture.\n\n**Assessments:** Guided source questions; discussion participation rubric.\n\n**Key Points:** Ethics of rule; religion as political glue; limits of the text as “law.”\n\n**Standards:** *Placeholders:* analyzing point of view in foundational documents.\n\n---\n\n### Lesson 4 — Nara Period Institutions\n\n**Objectives:** Describe Nara capital planning and state Buddhism; evaluate benefits and tensions of centralized temple power.\n\n**Assessments:** Mini-debate prompt; brief written reflection.\n\n**Key Points:** *Heijō-kyō*; Great Buddha at Tōdai-ji; economic and labor demands of major projects.\n\n**Standards:** *Placeholders:* cause and effect; evaluating costs of centralization.\n\n---\n\n### Lesson 5 — Court Culture in the Heian Period\n\n**Objectives:** Characterize aristocratic life; connect literature and art to court values; identify cultural achievements of the Heian era.\n\n**Assessments:** Image analysis worksheet; two-level text-dependent questions on an excerpt from *The Tale of Genji* (abridged).\n\n**Key Points:** Fujiwara influence; aesthetics and gendered roles; poetry as political communication.\n\n**Standards:** *Placeholders:* integrating visual and literary evidence.\n\n---\n\n### Culminating Activities Suggestions\n- **Museum box:** Students curate 5 artifacts (images or descriptions) with captions explaining classical Japan’s politics, belief, and daily life.\n- **Document-based question:** Respond to a prompt comparing Nara state Buddhism with Heian court culture using two classroom sources.\n- **Presentation:** Small groups teach one subtopic (geography, reform, religion, court culture) with a guiding question and one primary-source quote.\n\n### Standards Addressed\n- *Reading/Writing:* evidence-based claims, summarizing sources, integrating visual information.\n- *Speaking/Listening:* structured discussion, collaborative presentation.\n- *Social Studies:* geographic reasoning, historical causation, comparison across societies, analysis of primary sources.\n\n*Replace placeholder standard lines with your district’s codes when you paste standards into the generator.*",
                    },
                },
            },
        },
        {
            # TEMPLATE 41: Letter of Recommendation
            "template": {
                "slug": "letter-of-recommendation",
                "name": "Letter of Recommendation",
                "description": "Generate a customized letter of recommendation to an institution for a student.",
                "category": "communication",
                "subject_default": None,
                "grade_bands_supported": ["6-8", "9-12"],
            },
            "version": {
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "institution": {
                            "type": "string",
                            "title": "Institution",
                            "description": "The college, university, program, or organization the letter is addressed to.",
                            "maxLength": 500,
                        },
                        "student_pronouns": {
                            "type": "string",
                            "title": "Student Pronouns",
                            "description": "Pronouns to use for the student (e.g., he/him, she/her, they/them).",
                            "maxLength": 120,
                        },
                        "relationship_to_student": {
                            "type": "string",
                            "title": "Relationship to Student",
                            "description": "Your role relative to the student (e.g., teacher, counselor, mentor).",
                            "maxLength": 300,
                        },
                        "important_information": {
                            "type": "string",
                            "title": "Important information to include",
                            "description": "Details about the student’s strengths, achievements, character, and why you recommend them.",
                            "format": "textarea",
                            "maxLength": 75000,
                        },
                    },
                    "required": [
                        "institution",
                        "student_pronouns",
                        "relationship_to_student",
                        "important_information",
                    ],
                },
                "output_schema": {
                    "type": "object",
                    "title": "LetterOfRecommendationOutput",
                    "required": ["letter"],
                    "properties": {
                        "letter": {
                            "type": "string",
                            "title": "Exemplar",
                            "description": "Full letter of recommendation in markdown.",
                        }
                    },
                },
                "stub_config": None,
                "prompt_definition": {
                    "description": "Write a polished, formal letter of recommendation suitable for admissions or selection committees. Address the specified institution. Use the given pronouns consistently. Reflect the writer’s relationship to the student. Weave in all important information naturally.",
                    "context": "Output must match output_schema exactly with one field: letter. Use markdown. Begin with a subject line such as **Letter of Recommendation:** followed by a blank line, then a professional salutation directed at the institution (e.g., “To the Admissions Committee at …”). Use placeholders where the user did not supply specifics: [Date], [Student Name], [Your Name], [Your Title], [School Name], [Contact Information]. Do not output JSON.",
                    "exemplar_input": {
                        "institution": "University of Denver",
                        "student_pronouns": "He",
                        "relationship_to_student": "Teacher",
                        "important_information": "Excellent student, top 5 in his class, two sport athlete (baseball and basketball), NGSS member and student body president",
                    },
                    "exemplar_output": {
                        "letter": "**Letter of Recommendation:**\n\n[Date]\n\nTo the Admissions Committee at the University of Denver:\n\nI am pleased to recommend [Student Name] for admission to the University of Denver. As his **Teacher**, I have had the opportunity to observe [Student Name] in the classroom and in school leadership settings, and I can say with confidence that he is an **excellent student** who will contribute both academically and to your campus community.\n\nAcademically, [Student Name] ranks in the **top five** of his class. He approaches assignments with care, asks insightful questions, and supports classmates in group work without overshadowing them. His work is consistently thorough, and he balances a demanding course load with maturity and organization.\n\nBeyond the classroom, [Student Name] is a **two-sport athlete**, competing in **baseball** and **basketball**. He practices with discipline, supports teammates, and models good sportsmanship. His ability to manage athletics alongside strong academics speaks to his time management and resilience.\n\n[Student Name] is also deeply engaged in school life. He is an active **NGSS** member and serves as **student body president**, where he has helped coordinate events and represent student voices thoughtfully. In these roles he listens well, communicates clearly, and follows through on commitments—qualities that will serve him well in college.\n\nI recommend [Student Name] to you without reservation. If you would like additional context, please contact me at the information below.\n\nSincerely,\n\n[Your Name]  \n[Your Title]  \n[School Name]  \n[Contact Information]",
                    },
                },
            },
        },
        {
            # TEMPLATE 42: 5E Model Lesson Plan
            "template": {
                "slug": "5e-model-lesson-plan",
                "name": "5E Model Lesson Plan",
                "description": "Generate a 5E model lesson plan - Engage, Explore, Explain, Elaborate, Evaluate.",
                "category": "lesson_design",
                "subject_default": None,
                "grade_bands_supported": ["3-5", "6-8", "9-12"],
            },
            "version": {
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "grade_level": {
                            "type": "string",
                            "title": "Grade level",
                            "description": "Select the grade level for this lesson.",
                            "enum": [
                                "3rd grade",
                                "4th grade",
                                "5th grade",
                                "6th grade",
                                "7th grade",
                                "8th grade",
                                "9th grade",
                                "10th grade",
                                "11th grade",
                                "12th grade",
                            ],
                        },
                        "topic_standard_or_objective": {
                            "type": "string",
                            "title": "Topic, Standard, or Objective",
                            "description": "Topic, standard code, or learning objective (any framework worldwide).",
                            "format": "textarea",
                            "maxLength": 75000,
                        },
                        "additional_customization": {
                            "type": "string",
                            "title": "Additional Customization (Optional)",
                            "description": "Optional: pacing, hands-on emphasis, grouping, language supports, etc.",
                            "format": "textarea",
                            "maxLength": 75000,
                        },
                        "standards": {
                            "type": "string",
                            "title": "Standards Set to Align to (Optional)",
                            "description": "Optional: paste or describe standards (CCSS, TEKS, Ontario, NGSS, etc.).",
                            "format": "textarea",
                            "maxLength": 75000,
                        },
                    },
                    "required": ["grade_level", "topic_standard_or_objective"],
                },
                "output_schema": {
                    "type": "object",
                    "title": "FiveEModelLessonOutput",
                    "required": ["lesson_plan"],
                    "properties": {
                        "lesson_plan": {
                            "type": "string",
                            "title": "Exemplar",
                            "description": "Full 5E lesson plan in markdown.",
                        }
                    },
                },
                "stub_config": None,
                "prompt_definition": {
                    "description": "Design one or more class sessions using the 5E model (Engage, Explore, Explain, Elaborate, Evaluate) for the stated grade and topic. Honor optional customization and align to user-provided standards when supplied.",
                    "context": "Output must match output_schema exactly with one field: lesson_plan. Use markdown. Start with a compelling unit/lesson title, then **Engage**, **Explore**, **Explain**, **Elaborate**, **Evaluate** as main headings. Within each phase include concrete timing, materials, student tasks, and teacher moves. For Engage: brief phenomenon/hook, think-pair-share, purpose. For Explore: hands-on stations (name each), safety, and a clear data-collection step. For Explain: student synthesis, teacher moves with sample guiding questions, and a short formal mini-lesson with key vocabulary. For Elaborate: an application activity (e.g., poster or skit) plus an extension/challenge (e.g., case study). For Evaluate: formative checks, summative options (item types such as diagram labeling and scenario questions), a self-assessment rubric, and a brief teacher note. End with **Aligned Standards** tied to user standards when provided. Do not output JSON.",
                    "exemplar_input": {
                        "grade_level": "8th grade",
                        "topic_standard_or_objective": "What role do muscles, tendons, ligaments and bones play in allowing a human to walk?",
                        "additional_customization": "We are exploring the musculoskeletal system and its functions. The guiding question for our lesson is how do bones, muscles, tendons and ligaments work together to allow humans to walk around their environment?",
                        "standards": "NGSS",
                    },
                    "exemplar_output": {
                        "lesson_plan": "## Walking Wonders: How Bones, Muscles, Tendons & Ligaments Work Together\n\n**Grade:** 8th grade · **Standards focus:** NGSS (user indicated NGSS; align codes to your district bundle).\n\n---\n\n## Engage (10–12 minutes)\n\n**Brief phenomenon:** Short video or live demo of walking—compare a normal stride with walking while wearing a soft ankle brace or tape that limits side-to-side motion at the ankle.\n\n**Think–pair–share prompt:** “Which body structures must cooperate for each step—and what job does each one do?” Pairs draft a one-sentence claim; share out to build a common list.\n\n**Purpose:** Activate prior knowledge and frame the investigative question: *How do bones, muscles, tendons, and ligaments work together to allow humans to walk safely and efficiently?*\n\n---\n\n## Explore (35–40 minutes) — Hands-on stations\n\nStudents rotate in small groups (~8–10 minutes per station). Post clear station cards and a **data collection** handout where students record observations and a short “So what?” inference for each station.\n\n1. **Bone & joint station** — Use arm/leg models or simple cardboard “bones” and brass fasteners as joints. Label lever, fulcrum (joint), and load; sketch one movement at the knee or ankle.\n2. **Muscle and tendon station** — Elastic bands represent muscle contraction; string “tendons” transfer force to a rigid “bone.” Demonstrate how shortening on one side changes joint angle.\n3. **Ligament & stability station** — Tape a hinge “joint” tightly vs. loosely; relate to limiting excessive motion and preventing dislocation. Connect to ankle/knee stability during walking.\n4. **Gait observation station** — Watch a slow-motion clip of walking; sketch heel strike → stance → toe-off and note which structures must stabilize vs. propel.\n\n**Safety:** Appropriate use of scissors/elastic; no sharp probes; maintain spacing during movement demos.\n\n---\n\n## Explain (20–25 minutes)\n\n**Student synthesis:** Groups transfer station notes into a four-column organizer (**Bone / Muscle / Tendon / Ligament**) and add one real-world example for each (e.g., Achilles tendon, ACL as a ligament example at high level).\n\n**Teacher moves (guiding questions):** “Where is the force generated?” “What transfers the force?” “What prevents the joint from moving the wrong way?” “When you step, which tissues are actively contracting vs. passively stabilizing?”\n\n**Formal mini-lesson (7–10 minutes):** Define *agonist/antagonist* pairs; *tendon* as force transmitter; *ligament* as passive stabilizer; *bone* as rigid lever. Clarify **sprain vs. strain** in student-friendly language.\n\n**Formative check:** Exit ticket—label a simple leg diagram and explain one injury scenario using the terms *tendon* and *ligament* correctly.\n\n---\n\n## Elaborate (20–25 minutes)\n\n**Application activity (student choice):**\n- **Option A — Safety poster:** Create a poster for a school hallway or gym explaining how warm-ups and proper footwear protect tendons and ligaments during sports that involve cutting and jumping.\n- **Option B — Public service skit:** 3–4 students act out a coach-led warm-up scene that names at least three structures and why they matter for walking/running.\n\n**Extension / challenge (advanced learners):** **Sprained ankle mini–case study** — Read a short scenario about an inversion ankle injury. Students annotate which structures are most likely stressed and propose two evidence-based prevention habits.\n\n**Supports:** Sentence frames for multilingual learners; optional sentence starters for the case study; challenge: add a labeled free-body style sketch for forces at the ankle during push-off.\n\n---\n\n## Evaluate\n\n**Formative checks:** Station worksheets, teacher observation checklist for vocabulary in context, peer feedback on posters/skits using a simple two-stars-and-a-wish protocol.\n\n**Summative assessment (homework or next class):** Mixed formats—(1) **label a diagram** of the lower leg showing bone, muscle belly, tendon, and ligament; (2) **scenario questions** (e.g., “Which tissue is primarily injured in an overstretched ligament?”); (3) short written explanation of how muscle contraction leads to movement at a joint.\n\n**Self-assessment rubric (student-facing):** I can name the roles of bone, muscle, tendon, and ligament (1–4); I can explain walking as a coordinated process (1–4); I use scientific vocabulary accurately (1–4); my diagram is labeled clearly (1–4).\n\n**Teacher note:** Emphasize that this lesson is a conceptual introduction—clinical diagnosis belongs to health professionals; keep examples school-appropriate and inclusive of diverse athletic backgrounds.\n\n---\n\n## Aligned Standards\n\n- **NGSS MS-LS1-3** — Use argument supported by evidence for how the body is a system of interacting subsystems composed of groups of cells (adapt wording to your state’s adopted version).\n- **NGSS MS-LS1-8** — Gather and synthesize information that sensory receptors respond to stimuli (e.g., stretch/pressure) and send messages to the brain that can result in behaviors like adjusting gait (adapt to your adopted MS bundle).\n\n*Cross-cutting concepts:* systems and system models; structure and function. *SEP:* developing and using models; engaging in argument from evidence.",
                    },
                },
            },
        },
        {
            # TEMPLATE 43: Math Story Word Problems
            "template": {
                "slug": "math-story-word-problems",
                "name": "Math Story Word Problems",
                "description": "Write custom math word problems based on what you're teaching and any story topic.",
                "category": "assessment",
                "subject_default": "math",
                "grade_bands_supported": ["3-5", "6-8", "9-12"],
            },
            "version": {
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "grade_level": {
                            "type": "string",
                            "title": "Grade level",
                            "description": "Select the grade level for reading level and difficulty.",
                            "enum": [
                                "3rd grade",
                                "4th grade",
                                "5th grade",
                                "6th grade",
                                "7th grade",
                                "8th grade",
                                "9th grade",
                                "10th grade",
                                "11th grade",
                                "12th grade",
                            ],
                        },
                        "number_of_questions": {
                            "type": "string",
                            "title": "Number of Questions",
                            "description": "How many word problems to generate.",
                            "enum": ["3", "5", "7", "10"],
                        },
                        "math_standard_objective_topic": {
                            "type": "string",
                            "title": "Math Standard / Objective / Topic",
                            "description": "The math skill, standard, or topic (e.g., volume of a cone, multiplying fractions).",
                            "format": "textarea",
                            "maxLength": 75000,
                        },
                        "story_topic": {
                            "type": "string",
                            "title": "Story Topic",
                            "description": "The story setting or theme to weave into each problem (e.g., a concert, stock market game, sports).",
                            "format": "textarea",
                            "maxLength": 75000,
                        },
                    },
                    "required": [
                        "grade_level",
                        "number_of_questions",
                        "math_standard_objective_topic",
                        "story_topic",
                    ],
                },
                "output_schema": {
                    "type": "object",
                    "title": "MathStoryWordProblemsOutput",
                    "required": ["word_problems"],
                    "properties": {
                        "word_problems": {
                            "type": "string",
                            "title": "Exemplar",
                            "description": "Numbered math story word problems in markdown.",
                        }
                    },
                },
                "stub_config": None,
                "prompt_definition": {
                    "description": "Generate engaging story-based math word problems that match the grade level, integrate the story topic naturally, and assess the stated math topic or standard.",
                    "context": "Output must match output_schema exactly with one field: word_problems. Use markdown: start with a short title line (## ...) that reflects the math topic and story theme, then a numbered list (1., 2., ...) with exactly as many problems as the user requested. Each problem should be a single coherent paragraph or two short sentences; include any necessary numbers and units; avoid duplicate setups. Do not output JSON.",
                    "exemplar_input": {
                        "grade_level": "7th grade",
                        "number_of_questions": "3",
                        "math_standard_objective_topic": "Volume of a Cone",
                        "story_topic": "Beyonce concert",
                    },
                    "exemplar_output": {
                        "word_problems": "## Volume at the Venue: Beyoncé Concert Cone Problems\n\n1. At the merch stand, limited-edition commemorative cones are sold as drink holders. Each holder is shaped like a right circular cone with a radius of 4 cm and a height of 15 cm. What is the volume of one holder? Use **V = (1/3)πr²h** and leave your answer in terms of **π**.\n\n2. During sound check, a stage prop is a solid foam cone used as a pedestal for a microphone. The cone has a radius of **0.5 m** and a height of **1.2 m**. The crew wants to know how much space the foam occupies so they can store it in a road case. Find the volume of the cone in cubic meters. Round to **two** decimal places and use **π ≈ 3.14**.\n\n3. Two fans compare souvenir snow-cone cups from different sections. **Fan A’s** cup is a cone with radius **3 in.** and height **8 in.** **Fan B’s** cup is a cone with radius **4 in.** and height **6 in.** Which cup holds more? Justify by finding both volumes (in terms of **π** or using **π ≈ 3.14**) and stating which is greater.",
                    },
                },
            },
        },
        {
            # TEMPLATE 44: Support Goals Creator
            "template": {
                "slug": "support-goals-creator",
                "name": "Support Goals Creator",
                "description": "Create a SMART goals tracker for students aligned to their needs. (Tier 2/3, MTSS, IEPs, etc.)",
                "category": "behavior",
                "subject_default": None,
                "grade_bands_supported": ["3-5", "6-8", "9-12"],
            },
            "version": {
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "grade_level": {
                            "type": "string",
                            "title": "Grade level",
                            "description": "Select the student's grade level for age-appropriate goal language.",
                            "enum": [
                                "3rd grade",
                                "4th grade",
                                "5th grade",
                                "6th grade",
                                "7th grade",
                                "8th grade",
                                "9th grade",
                                "10th grade",
                                "11th grade",
                                "12th grade",
                            ],
                        },
                        "number_of_goals": {
                            "type": "string",
                            "title": "Number of Goals",
                            "description": "How many SMART goals to include in the tracker.",
                            "enum": ["3", "4", "5", "6", "7", "10"],
                        },
                        "goals_accommodations_behaviors": {
                            "type": "string",
                            "title": "IEP / 504 Goals, Accommodations, or Behaviors to Track",
                            "description": "List goals, accommodations, or behaviors to turn into measurable SMART goals (e.g., self regulation, social interaction, homework completion).",
                            "format": "textarea",
                            "maxLength": 75000,
                        },
                    },
                    "required": ["grade_level", "number_of_goals", "goals_accommodations_behaviors"],
                },
                "output_schema": {
                    "type": "object",
                    "title": "SupportGoalsCreatorOutput",
                    "required": ["progress_tracker"],
                    "properties": {
                        "progress_tracker": {
                            "type": "string",
                            "title": "Exemplar",
                            "description": "Markdown: Progress Monitoring Tracker table with Goal, Frequency of Monitoring, Observation/Data, Progress, Notes.",
                        }
                    },
                },
                "stub_config": None,
                "prompt_definition": {
                    "description": "Create a progress-monitoring tracker with SMART goals tailored to the grade level and the IEP/504/MTSS focus areas the teacher listed.",
                    "context": "Output must match output_schema exactly with one field: progress_tracker. Use markdown. Start with ## Progress Monitoring Tracker, then a short intro line (grade level, context: Tier 2/3, MTSS, IEP as appropriate). Then output a GitHub-flavored markdown **table** with exactly these five columns in order: **Goal** | **Frequency of Monitoring** | **Observation/Data** | **Progress** | **Notes**. Include exactly the number of goal rows the user requested. Each Goal cell must be a full SMART-style sentence (specific, measurable criterion, time frame, measurement method when possible). Leave Observation/Data, Progress, and Notes cells empty or with a single em dash for manual entry. Use realistic monitoring frequencies (e.g., Daily, Weekly, Bi-weekly, Twice weekly). Do not output JSON.",
                    "exemplar_input": {
                        "grade_level": "9th grade",
                        "number_of_goals": "5",
                        "goals_accommodations_behaviors": "Self regulation when upset, positive social interaction, homework completion, classwork completion.",
                    },
                    "exemplar_output": {
                        "progress_tracker": "## Progress Monitoring Tracker\n\n**Context:** Grade 9 · Tier 2/3 or IEP-aligned support · Use this table for ongoing progress monitoring; record data in school-approved systems.\n\n| Goal | Frequency of Monitoring | Observation/Data | Progress | Notes |\n| --- | --- | --- | --- | --- |\n| By the end of the next 12 weeks, when feeling upset in class the student will use at least two taught self-regulation strategies (deep breathing, 5-4-3-2-1 grounding, or requesting a break) independently in 4 out of 5 opportunities as measured by teacher or para observation and a self-report checklist. | Twice weekly | — | — | — |\n| Within 10 weeks, the student will initiate or respond positively to peers in social situations (for example greeting, joining group work, offering help) in at least 3 out of 5 observed opportunities, as measured by teacher observation and a peer or social skills rubric. | Once weekly | — | — | — |\n| Over the next 9 weeks, the student will complete and turn in assigned homework on time for at least 80% of assignments each week, as measured by the teacher assignment log and student planner checks. | Weekly | — | — | — |\n| Within 9 weeks, the student will complete at least 85% of in-class assigned tasks during independent work periods across a week on average, as measured by teacher observation and classwork records. | Three times weekly | — | — | — |\n| By the end of the semester (approximately 16 weeks), the student will reduce escalation incidents requiring teacher intervention from the current baseline by 50% through use of self-monitoring and teacher-supported interventions, as measured by behavior incident log and self-monitoring data. | Ongoing; incident-based review weekly | — | — | — |",
                    },
                },
            },
        },
        {
            # TEMPLATE 45: DOK Questions
            "template": {
                "slug": "dok-questions",
                "name": "DOK Questions",
                "description": "Generate questions based on topic or standard for each of the 4 Depth of Knowledge (DOK) levels.",
                "category": "assessment",
                "subject_default": None,
                "grade_bands_supported": ["3-5", "6-8", "9-12"],
            },
            "version": {
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "grade_level": {
                            "type": "string",
                            "title": "Grade level",
                            "description": "Select the grade level for question complexity and vocabulary.",
                            "enum": [
                                "3rd grade",
                                "4th grade",
                                "5th grade",
                                "6th grade",
                                "7th grade",
                                "8th grade",
                                "9th grade",
                                "10th grade",
                                "11th grade",
                                "12th grade",
                            ],
                        },
                        "topic_standard_or_objective": {
                            "type": "string",
                            "title": "Topic, Standard, or Objective",
                            "description": "The topic, standard code, or learning objective (e.g., mitosis, forces and motion, literary devices).",
                            "format": "textarea",
                            "maxLength": 75000,
                        },
                        "standards": {
                            "type": "string",
                            "title": "Standards Set to Align to",
                            "description": "Optional: frameworks or codes (CCSS, TEKS, Ontario, NGSS, Florida, etc.).",
                            "format": "textarea",
                            "maxLength": 75000,
                        },
                    },
                    "required": ["grade_level", "topic_standard_or_objective"],
                },
                "output_schema": {
                    "type": "object",
                    "title": "DokQuestionsOutput",
                    "required": ["dok_questions"],
                    "properties": {
                        "dok_questions": {
                            "type": "string",
                            "title": "Exemplar",
                            "description": "Markdown: DOK Level 1–4 sections with leveled questions.",
                        }
                    },
                },
                "stub_config": None,
                "prompt_definition": {
                    "description": "Generate classroom-ready questions at all four Depth of Knowledge (DOK) levels for the given topic and grade.",
                    "context": "Output must match output_schema exactly with one field: dok_questions. Use markdown. Begin with a one-line intro naming grade and topic. Then four sections in order: ### DOK Level 1 - Recall (measure, recall, calculate, define, list, identify), ### DOK Level 2 - Skill/Concept (graph, classify, compare, estimate, summarize), ### DOK Level 3 - Strategic Thinking (assess, investigate, formulate, draw conclusions, construct), ### DOK Level 4 - Extended Thinking (analyze, critique, create, design, apply concepts). Under each heading provide a short bullet list of distinct questions (aim for 4–6 per level). Align wording to user-supplied standards when provided. Questions must map clearly to the topic. Do not output JSON.",
                    "exemplar_input": {
                        "grade_level": "7th grade",
                        "topic_standard_or_objective": "Forces and motion",
                        "standards": "NGSS MS-PS2 Motion and Stability: Forces and Interactions",
                    },
                    "exemplar_output": {
                        "dok_questions": "## DOK-leveled questions: Forces and motion (Grade 7)\n\n*Aligned to user-indicated NGSS MS-PS2-style performance expectations; adapt codes to your adopted standards.*\n\n### DOK Level 1 - Recall (measure, recall, calculate, define, list, identify)\n\n- Define **force** in your own words and give the SI unit used to measure it.\n- List three common types of forces students might observe in everyday life (for example gravity, friction, normal force).\n- Identify whether a given scenario describes a **balanced** or **unbalanced** net force on an object at rest.\n- What is **Newton's First Law** of motion, stated in student-friendly language?\n- Name the two measurements you would read from a force diagram if the scale shows newtons.\n\n### DOK Level 2 - Skill/Concept (graph, classify, compare, estimate, summarize)\n\n- Compare how a **heavier** object and a **lighter** object respond when the same push is applied on a smooth surface; reference friction and inertia in your comparison.\n- Classify examples as **contact** forces versus **non-contact** forces and justify each choice.\n- Interpret a simple distance–time or speed–time graph: summarize what constant speed versus acceleration looks like on the graph.\n- Estimate the net force direction when two opposing forces of different magnitudes act on the same object.\n- Summarize the relationship between **mass**, **acceleration**, and **net force** using a sentence and one numerical example.\n\n### DOK Level 3 - Strategic Thinking (assess, investigate, formulate, draw conclusions, construct)\n\n- Design an **investigation** to test how the mass of a cart affects the distance it travels when released from the same ramp height; identify variables, controls, and what you will measure.\n- A student claims heavier objects always fall faster. **Formulate** an argument using evidence from a classroom drop-tower or simulation to support or refute the claim.\n- **Construct** a free-body diagram for a book resting on a desk and explain how the forces balance.\n- Plan how you would **assess** whether a peer's experimental conclusion is supported by the data table they collected.\n- Draw conclusions from a provided data set (mass vs. acceleration): what pattern supports Newton's Second Law in qualitative terms?\n\n### DOK Level 4 - Extended Thinking (analyze, critique, create, design, apply concepts)\n\n- **Analyze** a complex scenario (for example a car braking on a wet road) by identifying multiple forces acting and predicting how reduced friction changes stopping distance.\n- **Design** a safety feature or rule for a school sports context (helmets, cleats, playground equipment) that reduces injury risk, and explain the physics reasoning.\n- **Critique** a flawed explanation of motion (such as \"objects stop because motion runs out\") and rewrite it using accurate force concepts.\n- **Create** a short public-service explanation for younger students about seat belts and inertia in a crash; use accurate vocabulary and avoid misconceptions.\n- **Apply** force and motion concepts to propose how engineers might test a new backpack design for comfort and stability while walking.",
                    },
                },
            },
        },
        {
            # TEMPLATE 46: Song Generator
            "template": {
                "slug": "song-generator",
                "name": "Song Generator",
                "description": "Write a custom song about any topic to the tune of the song of your choice!",
                "category": "communication",
                "subject_default": None,
                "grade_bands_supported": ["K-2", "3-5", "6-8", "9-12"],
            },
            "version": {
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "song_topic": {
                            "type": "string",
                            "title": "Song Topic",
                            "description": "Who or what the song is about (e.g., a teacher, a class, a school event).",
                            "maxLength": 2000,
                        },
                        "details_to_include": {
                            "type": "string",
                            "title": "Details to Include in the Song",
                            "description": "Facts, traits, hobbies, inside jokes, or occasion to weave into the lyrics.",
                            "format": "textarea",
                            "maxLength": 75000,
                        },
                        "artist_and_song_title": {
                            "type": "string",
                            "title": "Artist Name & Song Title",
                            "description": "The tune to match in mood, rhythm, and section structure (e.g., Artist - Song Title).",
                            "maxLength": 500,
                        },
                    },
                    "required": ["song_topic", "details_to_include", "artist_and_song_title"],
                },
                "output_schema": {
                    "type": "object",
                    "title": "SongGeneratorOutput",
                    "required": ["song_lyrics"],
                    "properties": {
                        "song_lyrics": {
                            "type": "string",
                            "title": "Exemplar",
                            "description": "Original school-appropriate song lyrics in markdown.",
                        }
                    },
                },
                "stub_config": None,
                "prompt_definition": {
                    "description": "Write original, school-appropriate song lyrics about the given topic, incorporating every detail the user listed. Match the named reference track in overall mood, energy, and typical song structure (verses, chorus, optional bridge and outro)—without copying copyrighted lyrics line-for-line.",
                    "context": "Output must match output_schema exactly with one field: song_lyrics. Use markdown. Start with ## and a creative title for the new song (not the original song title alone). Then labeled sections such as **Verse 1**, **Pre-Chorus** (if fitting), **Chorus**, **Verse 2**, **Bridge**, **Chorus** (repeat if appropriate), **Outro**. Keep language positive and inclusive; avoid slurs, profanity, and identifiable student privacy details. Credit line: mention the tune is *inspired by* the user-supplied artist and song for rhythm and structure only. Do not output JSON.",
                    "exemplar_input": {
                        "song_topic": "6th grade math teacher, Ms. Lynn",
                        "details_to_include": "She sponsors the math club, loves rock climbing on weekends, is vegetarian, and we are celebrating her birthday at school with a surprise party in the cafeteria.",
                        "artist_and_song_title": "Taylor Swift - Cruel Summer",
                    },
                    "exemplar_output": {
                        "song_lyrics": "## Number Crunchin' Queen\n\n*Original lyrics for a school celebration. Inspired by the energy and verse–chorus structure of the reference track you named; not a reproduction of any copyrighted song.*\n\n**Verse 1**  \nSixth grade hallway, bells are ringing loud,  \nMs. Lynn is walking in, we're a proud crowd.  \nWhiteboard markers, problems on the screen—  \nShe makes fractions feel like a winning team.\n\n**Pre-Chorus**  \nShe climbs on weekends, chalk dust on her hands,  \nVegetarian lunch, still the coolest in the land.\n\n**Chorus**  \nNumber crunchin' queen, we're singing happy birthday—  \nMath club after school, you show us the way!  \nNumber crunchin' queen, cafeteria lights up today—  \nSurprise in every smile, Ms. Lynn, hip hip hooray!\n\n**Verse 2**  \nGraph paper mountains, rise and run with pride,  \nYou spot our mistakes, then you stand by our side.  \nRock wall courage when the numbers get tough—  \nYou teach us *try again*; that's more than enough.\n\n**Chorus**  \nNumber crunchin' queen, we're singing happy birthday—  \nMath club after school, you show us the way!  \nNumber crunchin' queen, cafeteria lights up today—  \nSurprise in every smile, Ms. Lynn, hip hip hooray!\n\n**Bridge**  \nNo meat on your plate, but you've got all the heart—  \nWe plotted this party like it's function graph art.  \nStreamers, cupcakes, and a card we all signed:  \n*Thanks for the problems—thanks for sharpening our minds.*\n\n**Chorus**  \nNumber crunchin' queen, we're singing happy birthday—  \nMath club after school, you show us the way!  \nNumber crunchin' queen, cafeteria lights up today—  \nSurprise in every smile, Ms. Lynn, hip hip hooray!\n\n**Outro**  \nMs. Lynn—enjoy your day. One, two, three… **surprise!**",
                    },
                },
            },
        },
        {
            # TEMPLATE 47: Social Stories
            "template": {
                "slug": "social-stories",
                "name": "Social Stories",
                "description": "Generate a social story about a particular event to help a student understand what to expect in that situation.",
                "category": "behavior",
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
                            "description": "Select the student's grade for age-appropriate language and examples.",
                            "enum": [
                                "Kindergarten",
                                "1st grade",
                                "2nd grade",
                                "3rd grade",
                                "4th grade",
                                "5th grade",
                                "6th grade",
                                "7th grade",
                                "8th grade",
                                "9th grade",
                                "10th grade",
                                "11th grade",
                                "12th grade",
                            ],
                        },
                        "social_situation": {
                            "type": "string",
                            "title": "Social situation, event, or activity",
                            "description": "Describe the situation (e.g., getting ready for school, group work, gym class, dentist visit).",
                            "format": "textarea",
                            "maxLength": 75000,
                        },
                    },
                    "required": ["grade_level", "social_situation"],
                },
                "output_schema": {
                    "type": "object",
                    "title": "SocialStoriesOutput",
                    "required": ["social_story"],
                    "properties": {
                        "social_story": {
                            "type": "string",
                            "title": "Exemplar",
                            "description": "First-person social story in markdown with a clear title and supportive tone.",
                        }
                    },
                },
                "stub_config": None,
                "prompt_definition": {
                    "description": "Write a social story that prepares the student for the described situation using clear, reassuring, concrete language.",
                    "context": "Output must match output_schema exactly with one field: social_story. Use markdown. Start with ## and a short, positive title. Use first person (I/me) or a named student (one simple name) consistent with the grade level. Explain what will happen, what others might do, what the student can do, and that different feelings are okay. Include optional short bullet lists such as **Before…**, **During…**, **After…** when they help clarity. Avoid shaming, medical claims, or identifying real students. Keep length appropriate for the grade. Do not output JSON.",
                    "exemplar_input": {
                        "grade_level": "4th grade",
                        "social_situation": "Engaging in an activity in your gym class where students sometimes have very different experience levels with the activity",
                    },
                    "exemplar_output": {
                        "social_story": "## Learning Together in Gym Class\n\nMy name is Jordan. I am in fourth grade. Sometimes our gym class has an activity where some kids have done it a lot before and some kids are trying it for the first time. That is okay. Everyone learns at their own speed.\n\nWhen I walk into the gym, I will hear the teacher explain the activity. The teacher wants everyone to be safe and to try their best. My job is to listen, follow directions, and ask for help if I need it.\n\nSometimes I might feel nervous if other students seem really good at something. I can remind myself: *I am still learning.* Other times I might feel proud because I already know a skill. I can remind myself: *I can be kind and patient with classmates who are learning too.*\n\nIf I do not understand the rules, I can raise my hand or ask the teacher to show me again. If I need a break, I can use the signal my teacher taught us. If someone else needs extra time or a simpler version of the task, that does not mean I did anything wrong—it means we are all different people with different practice.\n\n**Before gym starts, I can:**\n- Take a slow breath and think one calm thought.\n- Tie my shoes and check that I am wearing the right shoes for the activity.\n- Tell a trusted adult if something hurts or feels unsafe.\n\n**During the activity, I will:**\n- Stay in my space and use equipment the way the teacher taught.\n- Cheer for myself for trying, even if I am not the fastest or strongest yet.\n- Use respectful words if I work with a partner or a team.\n\n**After the activity, I will:**\n- Put equipment away where the teacher says.\n- Notice one thing I tried that felt brave, even if it was small.\n- Remember that gym class is for learning skills, not for being perfect on the first day.\n\nWhen gym is over, I will line up with my class. I did my part by being safe, respectful, and willing to learn. That is what good teammates do.",
                    },
                },
            },
        },
        {
            # TEMPLATE 48: Choice Board (UDL)
            "template": {
                "slug": "choice-board-udl",
                "name": "Choice Board (UDL)",
                "description": "Create a choice board for a student assignment based on the principles of UDL.",
                "category": "lesson_design",
                "subject_default": None,
                "grade_bands_supported": ["3-5", "6-8", "9-12"],
            },
            "version": {
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "grade_level": {
                            "type": "string",
                            "title": "Grade level",
                            "description": "Select the grade level for task complexity and vocabulary.",
                            "enum": [
                                "3rd grade",
                                "4th grade",
                                "5th grade",
                                "6th grade",
                                "7th grade",
                                "8th grade",
                                "9th grade",
                                "10th grade",
                                "11th grade",
                                "12th grade",
                            ],
                        },
                        "learning_goal_standard_objective_topic": {
                            "type": "string",
                            "title": "Learning Goal, Standard, Objective, or Topic",
                            "description": "What students should demonstrate (topic, standard code, or objective).",
                            "format": "textarea",
                            "maxLength": 75000,
                        },
                        "additional_detail": {
                            "type": "string",
                            "title": "Additional detail for the choice board",
                            "description": "Optional: modalities to include, time limits, materials, grouping, or accessibility needs.",
                            "format": "textarea",
                            "maxLength": 75000,
                        },
                    },
                    "required": ["grade_level", "learning_goal_standard_objective_topic"],
                },
                "output_schema": {
                    "type": "object",
                    "title": "ChoiceBoardUdlOutput",
                    "required": ["choice_board"],
                    "properties": {
                        "choice_board": {
                            "type": "string",
                            "title": "Exemplar",
                            "description": "Markdown choice board: title plus UDL-aligned options table.",
                        }
                    },
                },
                "stub_config": None,
                "prompt_definition": {
                    "description": "Design a Universal Design for Learning (UDL) choice board so students can engage with the same learning goal through multiple means of representation, action and expression, and engagement.",
                    "context": "Output must match output_schema exactly with one field: choice_board. Use markdown. Start with ## and a short title that names the topic plus \"Choice Board\". Add one line naming the grade level. Then a markdown table with columns: **Option** | **Assignment Title** | **Assignment Description (≤1 sentence)**. Provide **9** numbered options (1–9) when possible, each a distinct modality (e.g., visual, kinesthetic, verbal, musical, technology, writing, discussion, game, quiz). Each description must be one sentence or shorter. Honor optional additional detail when provided. Keep tasks school-safe and feasible in a typical classroom. Do not output JSON.",
                    "exemplar_input": {
                        "grade_level": "7th grade",
                        "learning_goal_standard_objective_topic": "The phases of mitosis",
                        "additional_detail": "Include a lot of diverse activities across modalities (e.g., art, song, movement, writing, tech).",
                    },
                    "exemplar_output": {
                        "choice_board": "## Phases of Mitosis Choice Board\n\n**Grade:** 7th grade · **UDL focus:** multiple means of engagement, representation, and action & expression.\n\n| Option | Assignment Title | Assignment Description (≤1 sentence) |\n| --- | --- | --- |\n| 1 | Comic-Strip Mitosis | Draw a 6-panel comic showing each phase of mitosis with one short caption per panel. |\n| 2 | Stop-Motion Video | Create a 60–90 second stop-motion video using clay or paper models to show the phases of mitosis. |\n| 3 | Foldable Diagram | Make a 3-fold paper diagram that labels and briefly describes each phase of mitosis. |\n| 4 | Match-and-Explain Game | Build 8 cards (4 phase names, 4 pictures) and write one-sentence explanations linking each picture to its phase. |\n| 5 | Phases Song or Rap | Write and perform a 30–60 second song or rap that names and orders the phases of mitosis. |\n| 6 | Venn Comparison Chart | Create a two-column Venn chart comparing mitosis and meiosis with three key differences and one similarity. |\n| 7 | Microscope Sketchbook | View prepared cell-division images (or provided photos) and sketch one example of a phase, labeling two key features. |\n| 8 | Real-World Analogy Poster | Design a poster that uses a clear everyday analogy (e.g., copying a recipe) to explain the purpose and steps of mitosis. |\n| 9 | Quick Quiz & Reflection | Write 5 multiple-choice questions about the phases of mitosis and include one short paragraph explaining why mitosis is important. |",
                    },
                },
            },
        },
        {
            # TEMPLATE 49: Vocabulary List Generator
            "template": {
                "slug": "vocabulary-list-generator",
                "name": "Vocabulary List Generator",
                "description": "Generate a list of vocabulary words based on a subject, topic, or text.",
                "category": "lesson_design",
                "subject_default": None,
                "grade_bands_supported": ["3-5", "6-8", "9-12"],
            },
            "version": {
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "grade_level": {
                            "type": "string",
                            "title": "Grade level",
                            "description": "Select the grade level for definition complexity and reading level.",
                            "enum": [
                                "3rd grade",
                                "4th grade",
                                "5th grade",
                                "6th grade",
                                "7th grade",
                                "8th grade",
                                "9th grade",
                                "10th grade",
                                "11th grade",
                                "12th grade",
                            ],
                        },
                        "vocabulary_words_to_define": {
                            "type": "string",
                            "title": "Vocabulary Words to Define",
                            "description": "How many terms to include in the list.",
                            "enum": ["5", "8", "10", "12", "15", "20"],
                        },
                        "topic_or_text": {
                            "type": "string",
                            "title": "Topic or text",
                            "description": "A short topic (e.g., mitosis, forces and motion) or longer passage from which to extract or derive vocabulary.",
                            "format": "textarea",
                            "maxLength": 75000,
                        },
                    },
                    "required": ["grade_level", "vocabulary_words_to_define", "topic_or_text"],
                },
                "output_schema": {
                    "type": "object",
                    "title": "VocabularyListGeneratorOutput",
                    "required": ["vocabulary_list"],
                    "properties": {
                        "vocabulary_list": {
                            "type": "string",
                            "title": "Exemplar",
                            "description": "Markdown vocabulary list with bold terms and clear definitions.",
                        }
                    },
                },
                "stub_config": None,
                "prompt_definition": {
                    "description": "Produce a teaching-ready vocabulary list for the given grade, topic, or source text.",
                    "context": "Output must match output_schema exactly with one field: vocabulary_list. Use markdown. Start with ## and a title such as \"Vocabulary for [topic]\". Add one line noting the grade level. Then for each term use **Bold term** followed by a definition in plain language (one or two sentences). Include exactly the number of terms requested. If the user pasted a long passage, prioritize high-value academic or domain-specific words from that passage; if the input is a short topic, generate the most important terms for that topic. Definitions must be accurate and classroom-appropriate. Do not output JSON.",
                    "exemplar_input": {
                        "grade_level": "11th grade",
                        "vocabulary_words_to_define": "10",
                        "topic_or_text": "Stages of cellular respiration.",
                    },
                    "exemplar_output": {
                        "vocabulary_list": "## Vocabulary for Stages of Cellular Respiration\n\n**Grade:** 11th grade · *Cellular respiration* is the overall process these terms help explain.\n\n**Glycolysis** — A series of reactions in the cytoplasm that splits glucose into pyruvate and yields a small net gain of ATP and reduced electron carriers.\n\n**Pyruvate oxidation** — The step that converts pyruvate into acetyl groups attached to coenzyme A, releasing carbon dioxide and generating NADH for later stages.\n\n**Acetyl-CoA** — A two-carbon carrier molecule that delivers acetyl units into the citric acid cycle after pyruvate processing.\n\n**Citric acid cycle** — A cyclic pathway in the mitochondrial matrix that oxidizes acetyl groups, releases CO₂, and transfers electrons to NADH and FADH₂.\n\n**Electron transport chain** — A series of membrane proteins that pass electrons from donors to oxygen, pumping protons to build an electrochemical gradient.\n\n**Oxidative phosphorylation** — ATP production driven by the proton gradient across the inner mitochondrial membrane, coupled to electron transport.\n\n**ATP synthase** — The enzyme complex that uses the proton gradient to phosphorylate ADP, forming ATP.\n\n**NADH and FADH₂** — Reduced coenzymes that carry high-energy electrons from glycolysis and the citric acid cycle to the electron transport chain.\n\n**Proton gradient** — An unequal distribution of hydrogen ions across a membrane that stores potential energy used by ATP synthase.\n\n**Substrate-level phosphorylation** — Direct transfer of a phosphate group to ADP from a phosphorylated substrate, producing ATP without using the proton gradient.",
                    },
                },
            },
        },
        {
            # TEMPLATE 50: Project Based Learning (PBL)
            "template": {
                "slug": "project-based-learning-pbl",
                "name": "Project Based Learning (PBL)",
                "description": "Generate a lesson plan based on the principles of Project Based Learning (PBL).",
                "category": "lesson_design",
                "subject_default": None,
                "grade_bands_supported": ["6-8", "9-12"],
            },
            "version": {
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "grade_level": {
                            "type": "string",
                            "title": "Grade level",
                            "description": "Select the grade level for cognitive demand and independence.",
                            "enum": [
                                "3rd grade",
                                "4th grade",
                                "5th grade",
                                "6th grade",
                                "7th grade",
                                "8th grade",
                                "9th grade",
                                "10th grade",
                                "11th grade",
                                "12th grade",
                            ],
                        },
                        "topic_or_project_description": {
                            "type": "string",
                            "title": "Topic or Title / Description of Project",
                            "description": "Project title, driving idea, or full description students will investigate.",
                            "format": "textarea",
                            "maxLength": 75000,
                        },
                        "additional_detail_considerations": {
                            "type": "string",
                            "title": "Additional detail / considerations (Optional)",
                            "description": "Optional: community partners, field sites, materials, grouping, pacing, or constraints.",
                            "format": "textarea",
                            "maxLength": 75000,
                        },
                        "standards": {
                            "type": "string",
                            "title": "Standards Set to Align to (Optional)",
                            "description": "Optional: frameworks or codes (CCSS, TEKS, NGSS, Ontario, etc.).",
                            "format": "textarea",
                            "maxLength": 75000,
                        },
                    },
                    "required": ["grade_level", "topic_or_project_description"],
                },
                "output_schema": {
                    "type": "object",
                    "title": "ProjectBasedLearningOutput",
                    "required": ["pbl_lesson_plan"],
                    "properties": {
                        "pbl_lesson_plan": {
                            "type": "string",
                            "title": "Exemplar",
                            "description": "Full PBL unit outline in markdown with Gold Standard PBL-style sections.",
                        }
                    },
                },
                "stub_config": None,
                "prompt_definition": {
                    "description": "Design a project-based learning experience with a sustained inquiry, authentic context, student voice and choice, critique and revision, and a public product.",
                    "context": "Output must match output_schema exactly with one field: pbl_lesson_plan. Use markdown. Include these section headings in order (use ### for each): **Driving Question or Challenge**, **Real-world Context**, **In-depth Inquiry**, **Student Voice and Choice**, **Reflection**, **Critique and Revision**, **Public Product**, **Collaboration**, **Teacher Facilitation**, **Interdisciplinary Connection** (bulleted list across subjects), **Assessment** (subheadings Formative and Summative), **Aligned Standards**. Start with ## project title. Name the grade level once near the top. Ground every section in the user's topic and optional details. When standards are provided, cite them explicitly; otherwise suggest plausible placeholder standards labeled as examples. Do not output JSON.",
                    "exemplar_input": {
                        "grade_level": "11th grade",
                        "topic_or_project_description": "Explore the impacts of urban development on the heat island effect that certain areas in Denver experience during our hottest days of the year.",
                        "additional_detail_considerations": "There are various open spaces in and around Denver where students can monitor air temperatures. There are also urban spaces where students can go to monitor air temperatures.",
                        "standards": "NGSS",
                    },
                    "exemplar_output": {
                        "pbl_lesson_plan": "## Explore Denver's Urban Heat Islands\n\n**Grade:** 11th grade · **Project type:** interdisciplinary field investigation with a public product.\n\n### Driving Question or Challenge\nHow does urban development in Denver influence local temperature patterns during the hottest days of the year, and what evidence-based design or policy recommendations could reduce harmful heat effects in affected neighborhoods?\n\n### Real-world Context\nUrban heat islands occur when built surfaces absorb and re-radiate heat, raising temperatures where people live, learn, and play. Students connect daily weather experiences to equity questions about who is most exposed to extreme heat and why it matters for health and learning.\n\n### In-depth Inquiry\nTeams develop investigable sub-questions (for example comparing park, parking lot, and tree-shaded sites), plan repeated temperature and surface observations using school-safe protocols, log metadata (time of day, cloud cover), and analyze patterns with graphs and maps. Students justify claims with evidence and consider uncertainty and sampling limitations.\n\n### Student Voice and Choice\nStudents choose monitoring locations from an approved list, decide roles (field lead, data manager, communications), select visualization formats, and pick the public product format (policy brief, community infographic series, recorded podcast, or city council-style presentation).\n\n### Reflection\nWeekly reflection prompts connect findings to personal experience and to science practices: *What surprised us? What would we measure differently next time? How does our evidence support our recommendation?*\n\n### Critique and Revision\nStructured peer review using a rubric aligned to claim-evidence-reasoning; one revision cycle after feedback from peers and a teacher conference; optional review from a community partner if available.\n\n### Public Product\nA concise heat-mitigation recommendation for a chosen Denver neighborhood, supported by data visuals and at least three feasible actions (for example tree canopy, cool surfaces, shade planning, or transit-oriented cooling strategies).\n\n### Collaboration\nHeterogeneous teams of 3–4 with rotating roles; norms for respectful disagreement; shared digital lab notebook; whole-class gallery walk to compare conclusions across sites.\n\n### Teacher Facilitation\nLaunch with a phenomenon anchor; model data ethics and field safety; provide checkpoints for data quality; coach argumentation without taking over student conclusions; coordinate permissions for off-campus or partner sites per district policy.\n\n### Interdisciplinary Connection\n- **Science / Earth systems:** heat transfer, weather variables, human impacts on Earth systems.  \n- **Mathematics:** descriptive statistics, graphing, rates of change, error and variability.  \n- **Social studies / Civics:** land use, environmental justice, local policy levers.  \n- **English / ELA:** informational writing, audience analysis, oral presentation.  \n- **Art / Design:** visual communication for public audiences.\n\n### Assessment\n**Formative:** field logs, peer critique sheets, checkpoint quizzes on vocabulary and graph reading, teacher conferencing notes.  \n**Summative:** public product rubric (accuracy of science content, use of evidence, feasibility of recommendations, collaboration, and communication).\n\n### Aligned Standards\n*Examples when aligning to NGSS-style high school performance expectations (adapt codes to your state adoption):* **HS-ESS3-4** — Evaluate or refine a technological solution that reduces impacts of human activities on Earth systems. **HS-ESS2-4** — Use a model to describe how variations in the flow of energy into and out of Earth’s systems result in changes in climate. Add SEP emphasis on **Analyzing and interpreting data** and **Engaging in argument from evidence**.",
                    },
                },
            },
        },
        {
            # TEMPLATE 51: Standards Unpacker
            "template": {
                "slug": "standards-unpacker",
                "name": "Standards Unpacker",
                "description": "Unpack any standard into component parts to understand what students need to learn.",
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
                            "description": "The grade band the standard is intended for (select the closest match).",
                            "enum": [
                                "Kindergarten",
                                "1st grade",
                                "2nd grade",
                                "3rd grade",
                                "4th grade",
                                "5th grade",
                                "6th grade",
                                "7th grade",
                                "8th grade",
                                "9th grade",
                                "10th grade",
                                "11th grade",
                                "12th grade",
                            ],
                        },
                        "standard_to_unpack": {
                            "type": "string",
                            "title": "Standard to Unpack",
                            "description": "Paste the full standard text, code, and strand (any framework worldwide).",
                            "format": "textarea",
                            "maxLength": 75000,
                        },
                    },
                    "required": ["grade_level", "standard_to_unpack"],
                },
                "output_schema": {
                    "type": "object",
                    "title": "StandardsUnpackerOutput",
                    "required": ["unpacked_standard"],
                    "properties": {
                        "unpacked_standard": {
                            "type": "string",
                            "title": "Exemplar",
                            "description": "Markdown unpack: components, expectations, targets, strategies, assessments, summary.",
                        }
                    },
                },
                "stub_config": None,
                "prompt_definition": {
                    "description": "Unpack the provided standard for the selected grade into teachable parts: knowledge, skills, concepts, expectations, measurable targets, instruction, and assessment.",
                    "context": "Output must match output_schema exactly with one field: unpacked_standard. Use markdown. Begin with one line quoting or naming the standard and the grade. Then use ### headings in this order: **Break Down Standard — key components** (sub-bullets for Skills, Knowledge, and Concepts), **Define Expectations — what students should learn**, **Learning Targets — specific, measurable** (use clear \"I can …\" statements), **Instruction strategies**, **Assessment ideas**, **Summary** (short paragraph). Keep content accurate to the standard text the user supplied. Do not output JSON.",
                    "exemplar_input": {
                        "grade_level": "6th grade",
                        "standard_to_unpack": "CCSS.Math.Content.6.EE.B.5 — Understand solving an equation or inequality as a process of answering a question: which values from a specified set, if any, make the equation or inequality true? Use substitution to determine whether a given number in a specified set makes an equation or inequality true.",
                    },
                    "exemplar_output": {
                        "unpacked_standard": "**Standard:** CCSS.Math.Content.6.EE.B.5 · **Grade focus:** 6th grade\n\n### Break Down Standard — key components\n\n- **Skills:** Substitute values into equations and inequalities; test truth values; compare solution sets; represent reasoning in words and symbols.\n- **Knowledge:** Meaning of *solution* and *solution set* for an equation or inequality in one variable; role of a specified replacement set; use of equality and inequality symbols.\n- **Concepts:** Equations and inequalities as questions about unknown values; substitution as an efficient check; relationship between arithmetic structure and truth (e.g., when adding the same amount to both sides preserves truth for equations—preview only if your unit sequence includes it).\n\n### Define Expectations — what students should learn\n\n- Students understand that solving starts with clarifying which values are allowed to be tested (the specified set).\n- Students can explain *why* a value does or does not work using substitution, not only *whether* it works.\n- Students distinguish between **one**, **several**, **all**, or **no** values in the set that satisfy the equation or inequality.\n\n### Learning Targets — specific, measurable\n\n- I can substitute a value from a given set into an equation or inequality and compute each side correctly.\n- I can decide if the value makes the statement true and justify my decision with arithmetic evidence.\n- I can list all solutions from a finite specified set or explain that none work.\n- I can translate a short word problem into an equation or inequality and test candidate values from a set.\n\n### Instruction strategies\n\n- **Concrete–representational–abstract:** use balances, tables, or number lines before symbolic-only work.\n- **Think-aloud modeling** for substitution with careful annotation of each side.\n- **Partner checks** with a “claim–evidence” sentence frame: *I claim x = … works because when I substitute…*\n- **Error analysis** tasks with common mistakes (sign errors, order of operations).\n\n### Assessment ideas\n\n- **Quick check:** Which of {2, 5, 8} makes \\(2x + 1 = 11\\) true? Show substitution work.\n- **Exit ticket:** Write one value that does **not** solve \\(y - 4 \\leq 10\\) from {10, 14, 16} and explain.\n- **Short performance:** Given a specified set, sort cards into “solution / not a solution” with a one-sentence rationale.\n\n### Summary\nThis standard centers **reasoning about equality and inequality** through substitution within a bounded set—ideal for building procedural fluency *with* conceptual understanding before formal solution techniques. Instruction should keep the “question the equation is asking” visible so students connect symbols to meaning.",
                    },
                },
            },
        },
        {
            # TEMPLATE 52: Group Work Generator
            "template": {
                "slug": "group-work-generator",
                "name": "Group Work Generator",
                "description": "Generate group work activity for students based on a topic, standard, or objective.",
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
                            "description": "Select the grade level for task complexity and independence.",
                            "enum": [
                                "Kindergarten",
                                "1st grade",
                                "2nd grade",
                                "3rd grade",
                                "4th grade",
                                "5th grade",
                                "6th grade",
                                "7th grade",
                                "8th grade",
                                "9th grade",
                                "10th grade",
                                "11th grade",
                                "12th grade",
                            ],
                        },
                        "time_for_group_work": {
                            "type": "string",
                            "title": "Time for Group Work",
                            "description": "How long the collaborative task should run.",
                            "enum": [
                                "5 minutes",
                                "10 minutes",
                                "15 minutes",
                                "20 minutes",
                                "25 minutes",
                                "30 minutes",
                                "40 minutes",
                                "45 minutes",
                            ],
                        },
                        "topic_objective_or_standard": {
                            "type": "string",
                            "title": "Topic, objective, or standard",
                            "description": "Paste a standard with description, a unit objective, or a short topic prompt.",
                            "format": "textarea",
                            "maxLength": 75000,
                        },
                        "number_of_students_participating": {
                            "type": "string",
                            "title": "Number of Students Participating",
                            "description": "Typical group size for this activity (per group).",
                            "enum": ["2", "3", "4", "5", "6"],
                        },
                    },
                    "required": [
                        "grade_level",
                        "time_for_group_work",
                        "topic_objective_or_standard",
                        "number_of_students_participating",
                    ],
                },
                "output_schema": {
                    "type": "object",
                    "title": "GroupWorkGeneratorOutput",
                    "required": ["group_work_plan"],
                    "properties": {
                        "group_work_plan": {
                            "type": "string",
                            "title": "Exemplar",
                            "description": "Markdown group-work task with roles, procedure, and teacher notes.",
                        }
                    },
                },
                "stub_config": None,
                "prompt_definition": {
                    "description": "Design a focused group task that fits the time limit, group size, and standard or topic, with clear roles and accountability.",
                    "context": "Output must match output_schema exactly with one field: group_work_plan. Use markdown. Start with ## and a short engaging task title. Include a metadata line (**Grade**, **Duration**, **Group size**, **Topic / Standard**). Then sections: ### Learning objective, ### Materials (per group), ### Role structure (bullets), ### Procedure (timed steps that fit the chosen duration), ### Guiding prompts, ### Facilitator notes, ### Reflection questions, ### Assessment / success criteria, ### Differentiation (Support and Challenge). Keep language inclusive and school-safe. Do not output JSON.",
                    "exemplar_input": {
                        "grade_level": "5th grade",
                        "time_for_group_work": "20 minutes",
                        "topic_objective_or_standard": "Human-Environment Interaction: Place, Regions, and Culture. SS.G.1.5: Investigate how the cultural and environmental characteristics of places within the United States change over time.",
                        "number_of_students_participating": "2",
                    },
                    "exemplar_output": {
                        "group_work_plan": "## Group Work Task: Then & Now — How People and Places Change\n\n**Grade:** 5 · **Duration:** 20 minutes · **Group size:** 2 students · **Topic / Standard:** Human-Environment Interaction: Place, Regions, and Culture · **SS.G.1.5** — Investigate how the cultural and environmental characteristics of places within the United States change over time.\n\n### Learning objective\nStudents will **compare** how a U.S. place has changed over time and **explain** at least one cultural or environmental reason using evidence from provided sources.\n\n### Materials (per pair)\n- Two teacher-vetted source cards (one labeled **Then**, one **Now**) or short approved excerpts\n- One **planning worksheet** with prompts: What was the place like before? What is it like now? What changed? Who was affected?\n- Pencil; optional colored pencils; classroom timer\n\n### Role structure\n- **Researcher:** reads closely, pulls evidence, writes first draft of notes on the worksheet\n- **Communicator:** checks that both agree on claims, keeps time for each step, shares out if the teacher calls on the pair\n\n### Procedure (20 minutes)\n- **0:00–1:00** — Read the objective together; confirm roles; skim both cards for headings and visuals.\n- **1:00–8:00** — Annotate **Then** (Researcher leads) and **Now** (Communicator leads); switch halfway so both touch each source.\n- **8:00–14:00** — Complete the worksheet: at least **two** evidence notes for *change* and **one** inference about *effect on people*.\n- **14:00–18:00** — Co-write a **two-sentence headline** that states their main claim about change.\n- **18:00–20:00** — Rehearse a 20-second summary; quick self-check against the success criteria.\n\n### Guiding prompts\n- What stayed the same and what changed—physically, culturally, or economically?\n- Who might benefit from the change, and who might face challenges?\n- What is one responsible action people took—or could take—in response?\n\n### Facilitator notes\n- With **pairs**, use **timed turns** so participation stays balanced; signal a 30-second “switch speaker” halfway through discussions.\n- Circulate with a simple checklist: both names on the worksheet, evidence cited, headline matches evidence.\n- If pairs finish early, ask them to add a **respectful** “So what?” sentence for their community.\n\n### Reflection questions (pairs turn in)\n- What is one concrete way our place changed?\n- Which detail from the sources best supports our headline—and why?\n- What is one question we would ask a local historian or elder?\n\n### Assessment / success criteria\n- Worksheet shows **then**, **now**, **change**, and **effect** with source-based notes.\n- Headline matches the evidence (no contradictions).\n- Each student can paraphrase the pair’s claim without reading the paper word-for-word.\n\n### Differentiation\n- **Support:** sentence frames (“One change we noticed is ___ because the source says ___”).\n- **Challenge:** add a third lens (for example **transportation** or **economy**) with one extra evidence bullet.\n\n### Answer-key exemplar (teacher-only)\n- **Then:** small river town with mills and local river trade.\n- **Now:** same town adds recreation trails and small businesses serving visitors.\n- **Change:** economy shifts toward services and tourism alongside older industries.\n- **Effect on people:** new opportunities for some workers; possible concerns about housing or traffic—keep student language respectful and evidence-based.",
                    },
                },
            },
        },
        {
            # TEMPLATE 53: Math Spiral Review
            "template": {
                "slug": "math-spiral-review",
                "name": "Math Spiral Review",
                "description": "Generate a spiral review problem set for any math standard(s) or topic(s).",
                "category": "assessment",
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
                            "description": "Select the grade level for problem difficulty and context.",
                            "enum": [
                                "Kindergarten",
                                "1st grade",
                                "2nd grade",
                                "3rd grade",
                                "4th grade",
                                "5th grade",
                                "6th grade",
                                "7th grade",
                                "8th grade",
                                "9th grade",
                                "10th grade",
                                "11th grade",
                                "12th grade",
                            ],
                        },
                        "number_of_problems": {
                            "type": "string",
                            "title": "Number of Problems",
                            "description": "How many spiral-review items to include in the set.",
                            "enum": ["3", "5", "7", "10"],
                        },
                        "math_content": {
                            "type": "string",
                            "title": "Math Content",
                            "description": "Standard(s), topic(s), or skill focus for the review (e.g., dividing two- and three-digit numbers).",
                            "format": "textarea",
                            "maxLength": 75000,
                        },
                        "additional_criteria": {
                            "type": "string",
                            "title": "Additional Criteria (Optional)",
                            "description": "Optional: format (e.g., word problems only), difficulty mix, context, or constraints.",
                            "format": "textarea",
                            "maxLength": 75000,
                        },
                        "standards_set_to_align_to": {
                            "type": "string",
                            "title": "Standards Set to Align to",
                            "description": "Optional: any standards worldwide (CCSS, TEKS, Ontario, Florida, etc.).",
                            "format": "textarea",
                            "maxLength": 75000,
                        },
                    },
                    "required": [
                        "grade_level",
                        "number_of_problems",
                        "math_content",
                    ],
                },
                "output_schema": {
                    "type": "object",
                    "title": "MathSpiralReviewOutput",
                    "required": ["spiral_review"],
                    "properties": {
                        "spiral_review": {
                            "type": "string",
                            "title": "Exemplar",
                            "description": "Markdown spiral review set with problems and answer key.",
                        }
                    },
                },
                "stub_config": None,
                "prompt_definition": {
                    "description": "Create a cohesive spiral review problem set for the stated grade and math focus, honoring optional criteria and alignment notes.",
                    "context": "Output must match output_schema exactly with one field: spiral_review. Use markdown. Start with ## and a short engaging title that reflects the math topic and grade. On the next line, include **Grade:** and a one-line note if standards_to_align were provided. Then a numbered list (1., 2., …) with exactly as many problems as number_of_problems—each item clear, school-appropriate, and distinct. If additional_criteria ask for word problems, use real-world contexts and complete sentences. After the problems, add a horizontal rule (---) then ### Answer Key with a short italic disclaimer: math answers may be incorrect—teachers must verify before use. Under Answer Key, give concise worked solutions or final answers matching each numbered problem. End with a brief **Reminder:** line telling teachers to double-check calculations. Do not output JSON.",
                    "exemplar_input": {
                        "grade_level": "6th grade",
                        "number_of_problems": "5",
                        "math_content": "Dividing two and three digit numbers",
                        "additional_criteria": "Make them word problems",
                        "standards_set_to_align_to": "",
                    },
                    "exemplar_output": {
                        "spiral_review": "## Dividing with Confidence: Real-World Word Problems for 6th Grade\n\n**Grade:** 6th grade · **Focus:** division with two- and three-digit dividends and divisors (whole-number quotients where appropriate for spiral review)\n\n1. A school bus holds **54** students. If **486** students need rides to a field trip, how many **full** buses are needed? Explain whether there is a remainder and what it means for an extra bus.\n\n2. A bakery packs **144** muffins into boxes of **12**. How many boxes are filled? If the bakery also has **37** muffins left over from another batch, how many **additional** full boxes of **12** can they make from those leftovers, and how many muffins remain?\n\n3. A charity raised **\\$2,340** in equal donations from **45** families. How much did each family donate?\n\n4. A rope is **215** inches long. The art teacher cuts **full** segments that are each **8** inches long for name tags. How many **full** 8-inch segments can be cut, and how many inches of rope are **left over**?\n\n5. A factory produces **6,048** bolts in **36** hours of steady work. Assuming the same rate, how many bolts are produced **per hour**?\n\n---\n\n### Answer Key\n\n*Math answers may be incorrect — always review for accuracy before use.*\n\n1. **\\(486 \\div 54 = 9\\)** with **no** remainder → **9** full buses.\n2. **\\(144 \\div 12 = 12\\)** boxes. From **37** muffins: **\\(37 \\div 12 = 3\\)** R **1** → **3** more full boxes, **1** muffin left over.\n3. **\\(2,340 \\div 45 = 52\\)** → **\\$52** per family.\n4. **\\(215 = 8 \\times 26 + 7\\)** → **26** full 8-inch segments, **7** inches left over.\n5. **\\(6,048 \\div 36 = 168\\)** bolts per hour.\n\n**Reminder:** Always double-check answer key calculations for accuracy before assigning.",
                    },
                },
            },
        },
        {
            # TEMPLATE 54: Teacher Observations
            "template": {
                "slug": "teacher-observations",
                "name": "Teacher Observations",
                "description": "Generate custom feedback for a teacher based on a classroom observation.",
                "category": "communication",
                "subject_default": None,
                "grade_bands_supported": ["K-2", "3-5", "6-8", "9-12"],
            },
            "version": {
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "teachers_observed_areas_of_strength": {
                            "type": "string",
                            "title": "Teacher's Observed Areas of Strength",
                            "description": "What went well—student rapport, clarity of directions, checks for understanding, pacing, classroom culture, etc.",
                            "format": "textarea",
                            "maxLength": 75000,
                        },
                        "teachers_observed_opportunities_for_growth": {
                            "type": "string",
                            "title": "Teacher's Observed Opportunities for Growth",
                            "description": "Neutral, evidence-based notes on what could improve—student engagement, questioning, differentiation, transitions, or assessment use.",
                            "format": "textarea",
                            "maxLength": 75000,
                        },
                        "observation_context": {
                            "type": "string",
                            "title": "Observation Context",
                            "description": "Grade level, subject, lesson segment observed, groupings, and any school or team priorities the feedback should honor.",
                            "format": "textarea",
                            "maxLength": 75000,
                        },
                    },
                    "required": [
                        "teachers_observed_areas_of_strength",
                        "teachers_observed_opportunities_for_growth",
                        "observation_context",
                    ],
                },
                "output_schema": {
                    "type": "object",
                    "title": "TeacherObservationsOutput",
                    "required": ["observation_feedback"],
                    "properties": {
                        "observation_feedback": {
                            "type": "string",
                            "title": "Exemplar",
                            "description": "Markdown coaching feedback: strengths, growth, next steps, disclaimer.",
                        }
                    },
                },
                "stub_config": None,
                "prompt_definition": {
                    "description": "Turn raw observation notes into supportive, specific written feedback a teacher can use after a classroom visit.",
                    "context": "Output must match output_schema exactly with one field: observation_feedback. Use markdown. Open with a short ## title (professional, warm). Mirror the observer's facts—do not invent classroom events not implied by the inputs. Use ### **Areas of strength (keep it up!)** with concise bullets grounded in the strengths text. Use ### **Opportunities for growth / next steps** with bullets; where helpful add nested sub-bullets labeled **Bite-sized next step:** with one concrete action each (timing, sentence stems, a single protocol tweak). Optional ### **Suggested follow-up conversation** with 2–3 neutral coaching prompts. Close with a one-line italic disclaimer that the draft should be reviewed for accuracy and local policy, and that AI has limitations. Tone: respectful, growth-oriented, non-judgmental; avoid evaluative scores or legal claims. Do not output JSON.",
                    "exemplar_input": {
                        "teachers_observed_areas_of_strength": "Warm and personable with students; greets each student at the door by name. Clear learning target posted and referenced twice during the lesson. Strong use of think-pair-share before whole-group discussion.",
                        "teachers_observed_opportunities_for_growth": "Wait time after questions was often under two seconds before the teacher moved on or answered. Small group work had uneven participation—two students dominated while others were quiet. Exit ticket was collected but not previewed with students so success criteria were fuzzy at the end.",
                        "observation_context": "7th grade ELA, 45-minute period, first class after lunch. Focus of visit: academic discourse and formative checks. School priority this semester is increasing student talk time and using data from exit tickets within 48 hours.",
                    },
                    "exemplar_output": {
                        "observation_feedback": "## Post-observation feedback — 7th grade ELA (after lunch)\n\n### **Areas of strength (keep it up!)**\n\n- **Relationships and tone:** Your warm greetings and use of student names set a positive entry routine—especially valuable right after lunch.\n- **Clarity of purpose:** Posting and revisiting the learning target helped students orient to the \"why\" of the lesson.\n- **Discourse structure:** Think–pair–share before whole-group discussion is a strong lever for voice and rehearsal—keep this as a signature move.\n\n### **Opportunities for growth / next steps**\n\n- **Wait time & thinking space**\n  - **Bite-sized next step:** After you ask a question, silently count **4–5** (or tap a sticky note five times) before taking a response. Invite \"turn and talk\" as the default when a question is heavy.\n- **Equitable participation in groups**\n  - **Bite-sized next step:** Assign rotating roles (**Recorder**, **Speaker**, **Timekeeper**) for 6–8 minutes and use a visible participation checklist you scan once mid-task.\n- **Exit ticket alignment**\n  - **Bite-sized next step:** Show the exit prompt **3 minutes** early and read success criteria aloud: *I will look for …* Then collect—aim to sort responses within **48 hours** to match your school priority.\n\n### **Suggested follow-up conversation**\n\n- Which question in today's lesson do you want students to wrestle with longer next time?\n- What is one small data point from the exit ticket that would change your warm-up tomorrow?\n\n---\n\n*Review this closely for accuracy and fit with your school's observation rubric and labor agreements—AI-generated drafts have limitations and should be edited by a human before sharing formally.*",
                    },
                },
            },
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
