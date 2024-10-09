import re, json, asyncio
# from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent
# from langchain.memory import ConversationBufferMemory
# from langchain.prompts import StringPromptTemplate
# from langchain.schema import AgentAction, AgentFinish
# from langchain.tools import BaseTool
from typing import Dict, List, Union, Optional
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
from prompts import BIAS_DETECTOR_TEMPLATE, BIASED_REVIEWER_TEMPLATE, UNBIASED_REVIEWER_TEMPLATE
from models import groq, init_groq, GROQ_API_KEY
import uuid

# Enums for standardization
class BiasLevel(str, Enum):
    BIASED = "biased"
    UNBIASED = "unbiased"
    
class DecisionStatus(str, Enum):
    ACCEPT = "accept"
    REJECT = "reject"
    UNDECIDED = "undecided"
    # PENDING = "pending"
    
class ReviewScore(BaseModel):
    category: str
    score: float
    max_score: int = 10
    comments: Optional[str] = None
    
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
    
class ReviewerFeedback(BaseModel):
    reviewer_name: str
    bias_level: BiasLevel
    specialization: str
    review_score: ReviewScore
    strengths: List[str]
    weaknesses: List[str]
    areas_of_concern: List[str]
    recommendation: DecisionStatus
    justification: str
    # additional_comments: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    
    async def _get_reviewer_feedback(self, reviewer: Reviewer, application: str) -> ReviewerFeedback:
        prompt = self._get_reviewer_prompt(reviewer, application)
        response = await self._get_llm_response(prompt)
        
        # Parse LLM response into structured feedback
        parsed_feedback = self._parse_reviewer_response(response, reviewer)
        
        return ReviewerFeedback(
            reviewer_name=reviewer.name,
            bias_level=reviewer.bias_level,
            specialization=reviewer.specialization.domain,
            review_score=parsed_feedback['scores'],
            strengths=parsed_feedback['strengths'],
            weaknesses=parsed_feedback['weaknesses'],
            recommendation=parsed_feedback['recommendation'],
            justification=parsed_feedback['justification']
        )

class BiasAnalysis(BaseModel):
    # metrics: BiasMetrics
    detected_biases: List[BiasIndicator]
    overall_bias_level: float
    recommendations: List[str]
    analysis_summary: str
    timestamp: datetime = Field(default_factory=datetime.now)

class ApplicationReview(BaseModel):
    application_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    biased_review: ReviewerFeedback
    unbiased_review: ReviewerFeedback
    bias_analysis: BiasAnalysis
    decision: DecisionStatus
    confidence_score: float
    evaluation_timestamp: datetime = Field(default_factory=datetime.now)

class EvaluationResult(BaseModel):
    application_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    reviews: List[ReviewerFeedback]
    bias_analysis: BiasAnalysis
    # improvements: ImprovementSuggestions
    decision: DecisionStatus
    confidence_score: float
    evaluation_timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "application_id": "12345",
                "decision": "pending",
                "confidence_score": 0.85
            }
        }


# Base reviewer class
class Reviewer(BaseModel):
    name: str
    bias_level: str  # "biased" or "unbiased"
    specialization: str = Field(default="general")
    
    class Config:
        arbitrary_types_allowed = True

class DevilsAdvocateSystem:
    def __init__(self, groq_client: groq.Groq):
        self.client = groq_client
        self.reviewers = self._initialize_reviewers()
        self.bias_detector = self._initialize_bias_detector()
        
    def _initialize_reviewers(self) -> List[Reviewer]:
        return [
            Reviewer(name="Reviewer A", bias_level="biased", specialization="technical"),
            Reviewer(name="Reviewer B", bias_level="biased", specialization="leadership"),
            Reviewer(name="Reviewer C", bias_level="unbiased", specialization="general")
        ]
    
    def _initialize_bias_detector(self):
        return BiasDetector(self.client)
    
    def _get_reviewer_prompt(self, reviewer: Reviewer, application: str) -> str:
        template = BIASED_REVIEWER_TEMPLATE if reviewer.bias_level == "biased" else UNBIASED_REVIEWER_TEMPLATE
        return template.format(name=reviewer.name, application=application)
    
    async def evaluate_application(self, application: str) -> Dict:
        # Collect reviews from all reviewers
        reviews = []
        for reviewer in self.reviewers:
            prompt = self._get_reviewer_prompt(reviewer, application)
            response = self.client(prompt, "")
            reviews.append({
                "reviewer": reviewer.name,
                "bias_level": reviewer.bias_level,
                "feedback": response.choices[0].message.content
            })
        
        # Analyze reviews for bias
        bias_analysis = await self.bias_detector.analyze_reviews(reviews)
        
        # Generate improvement suggestions
        suggestions = self._generate_improvements(reviews, bias_analysis)
        
        return {
            "reviews": reviews,
            "bias_analysis": bias_analysis,
            "improvement_suggestions": suggestions
        }
    
    def _generate_improvements(self, reviews: List[Dict], bias_analysis: Dict) -> List[str]:
        # Implement improvement suggestion generation based on reviews and bias analysis
        prompt = f"""
        Based on the following reviews and bias analysis, suggest specific improvements 
        to strengthen the application and address potential biases:
        
        Reviews: {reviews}
        Bias Analysis: {bias_analysis}
        
        Provide concrete, actionable suggestions for improvement.
        """
        
        response = self.client(prompt, "")
        return response.choices[0].message.content
    

    def export_results(self, evaluation_result: EvaluationResult, 
                      format: str = 'json', file_path: Optional[str] = None) -> Union[str, Dict]:
        """
        Export evaluation results in various formats
        """
        if format.lower() == 'json':
            result = evaluation_result.model_dump_json(indent=2)
        elif format.lower() == 'dict':
            result = evaluation_result.model_dump()
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        if file_path:
            with open(file_path, 'w') as f:
                if isinstance(result, str):
                    f.write(result)
                else:
                    json.dump(result, f, indent=2)
        
        return result

class BiasDetector:
    def __init__(self, groq_client):
        self.client = groq_client
    
    async def analyze_reviews(self, reviews: List[Dict]) -> Dict:

        prompt = BIAS_DETECTOR_TEMPLATE.format(reviews=reviews)
        response = self.client(prompt, "")
        
        return {
            "analysis": response.choices[0].message.content,
            "bias_score": self._calculate_bias_score(reviews)
        }
    
    def _calculate_bias_score(self, reviews: List[Dict]) -> float:
        # Implement bias scoring logic
        # This could analyze language patterns, decision disparities, etc.
        pass

# Usage example
async def main():
    groq_client = init_groq
    # groq_client = groq.Groq(api_key=GROQ_API_KEY,)
    devils_advocate = DevilsAdvocateSystem(groq_client)
    
    application = open("./data/cv.txt", "r")#.read()
    """
    [Your application content here]
    """
    
    evaluation_results = await devils_advocate.evaluate_application(application)


    print(evaluation_results.decision)
    
    # Process and display results
    for review in evaluation_results["reviews"]:
        print(f"\nReview from {review['reviewer']} ({review['bias_level']}):")
        print(review["feedback"])
    
    print("\nBias Analysis:")
    print(evaluation_results["bias_analysis"])
    
    print("\nImprovement Suggestions:")
    print(evaluation_results["improvement_suggestions"])

if __name__ == "__main__":
    asyncio.run(main())