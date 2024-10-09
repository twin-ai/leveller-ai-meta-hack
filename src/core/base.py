import uuid, json
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Dict, List, Union, Optional

# Enums for standardization
class BiasLevel(str, Enum):
    BIASED = "biased"
    UNBIASED = "unbiased"
    
class DecisionStatus(str, Enum):
    ACCEPT = "accept"
    REJECT = "reject"
    PENDING = "pending"
    # PENDING = "pending"
    
class ReviewScore(BaseModel):
    category: str
    score: float
    # max_score: int = 10
    comments: Optional[str] = None
    # initial_impression: str
    # technical_assessment: str
    # experience_evaluation: str
    
class BiasIndicator(BaseModel):
    type: str
    description: str
    severity: float
    context: Optional[str] = None
    location: Optional[str] = None

# class BiasInstance(BaseModel):...
# class DecisionStatus(str, Enum):...

# # Enums for standardization
class PriorityLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

# Base reviewer class
class Reviewer(BaseModel):
    name: str
    bias_level: str  # "biased" or "unbiased"
    specialization: str = Field(default="general")
    
    class Config:
        arbitrary_types_allowed = True
    
class ReviewerFeedback(BaseModel):
    # reviewer_name: str
    # bias_level: BiasLevel
    # specialization: str
    reviewer: Reviewer=None
    review_scores: List[ReviewScore]
    strengths: List[str]
    weaknesses: List[str]
    areas_of_concern: List[str]
    areas_of_potential: List[str]
    recommendation: DecisionStatus
    justification: str
    # additional_comments: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

# class BiasAnalysis(BaseModel):
#     # metrics: BiasMetrics
#     detected_biases: List[BiasIndicator]
#     overall_bias_level: float
#     recommendations: List[str]
#     analysis_summary: str
#     timestamp: datetime = Field(default_factory=datetime.now)

class BiasAnalysis(BaseModel):
    # metrics: BiasMetrics
    analysis_summary: str
    bias_score: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class ApplicationReview(BaseModel):
    application_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    biased_review: ReviewerFeedback
    unbiased_review: ReviewerFeedback
    bias_analysis: BiasAnalysis
    decision: DecisionStatus
    confidence_score: float
    evaluation_timestamp: datetime = Field(default_factory=datetime.now)

class Improvement(BaseModel):
    category: str
    priority: PriorityLevel
    issue: str
    suggestion: str
    example: Optional[str] = None
    impact_area: str
    implementation_difficulty: PriorityLevel

class ImprovementSuggestions(BaseModel):
    technical_improvements: List[Improvement]
    language_improvements: List[Improvement]
    experience_improvements: List[Improvement]
    presentation_improvements: List[Improvement]
    bias_mitigation_improvements: List[Improvement]
    priority_summary: Dict[PriorityLevel, int]

class EvaluationResult(BaseModel):
    application_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    reviews: List[ReviewerFeedback]
    bias_analysis: BiasAnalysis
    overall_decision: DecisionStatus
    confidence_score: float=None
    improvements: ImprovementSuggestions=None
    evaluation_timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "application_id": "12345",
                "decision": "pending",
                "confidence_score": 0.85
            }
        }

class ExportData:

    def __init__(self) -> None:
        pass
