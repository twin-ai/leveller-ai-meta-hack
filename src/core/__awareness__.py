from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum

# Enums for standardization
class PriorityLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class RecommendationStatus(str, Enum):
    ACCEPT = "accept"
    REJECT = "reject"
    PENDING = "pending"

# Structured Output Models
class Score(BaseModel):
    category: str
    value: float
    weight: Optional[float] = 1.0
    comments: Optional[str] = None

class Improvement(BaseModel):
    category: str
    priority: PriorityLevel
    issue: str
    suggestion: str
    example: Optional[str] = None
    impact_area: str
    implementation_difficulty: PriorityLevel

class BiasMetrics(BaseModel):
    gender_bias_score: float
    language_complexity_score: float
    stereotyping_score: float
    fairness_score: float
    overall_bias_score: float
    timestamp: datetime = Field(default_factory=datetime.now)

class BiasInstance(BaseModel):
    type: str
    severity: float
    context: str
    suggestion: str
    location: Optional[str] = None

class ReviewerFeedback(BaseModel):
    reviewer_name: str
    bias_level: str
    specialization: str
    scores: Dict[str, Score]
    strengths: List[str]
    weaknesses: List[str]
    recommendation: RecommendationStatus
    justification: str
    timestamp: datetime = Field(default_factory=datetime.now)

class BiasAnalysis(BaseModel):
    metrics: BiasMetrics
    detected_biases: List[BiasInstance]
    overall_analysis: str
    recommendations: List[str]
    timestamp: datetime = Field(default_factory=datetime.now)

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
    improvements: ImprovementSuggestions
    overall_recommendation: RecommendationStatus
    confidence_score: float
    evaluation_timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "application_id": "12345",
                "overall_recommendation": "pending",
                "confidence_score": 0.85
            }
        }

# Updated DevilsAdvocateSystem class with structured outputs
class DevilsAdvocateSystem:
    def __init__(self, groq_client):
        self.client = groq_client
        self.reviewers = self._initialize_reviewers()
        self.bias_detector = BiasDetector(groq_client)
    
    async def evaluate_application(self, application: str) -> EvaluationResult:
        # Collect reviews
        reviews = []
        for reviewer in self.reviewers:
            review = await self._get_reviewer_feedback(reviewer, application)
            reviews.append(review)
        
        # Analyze bias
        bias_analysis = await self._get_bias_analysis(reviews)
        
        # Generate improvements
        improvements = await self._generate_improvements(reviews, bias_analysis)
        
        # Calculate overall recommendation
        overall_recommendation = self._calculate_overall_recommendation(reviews)
        confidence_score = self._calculate_confidence_score(reviews, bias_analysis)
        
        return EvaluationResult(
            reviews=reviews,
            bias_analysis=bias_analysis,
            improvements=improvements,
            overall_recommendation=overall_recommendation,
            confidence_score=confidence_score
        )
    
    async def _get_reviewer_feedback(self, reviewer: Reviewer, application: str) -> ReviewerFeedback:
        prompt = self._get_reviewer_prompt(reviewer, application)
        response = await self._get_llm_response(prompt)
        
        # Parse LLM response into structured feedback
        parsed_feedback = self._parse_reviewer_response(response, reviewer)
        
        return ReviewerFeedback(
            reviewer_name=reviewer.name,
            bias_level=reviewer.bias_level,
            specialization=reviewer.specialization.domain,
            scores=parsed_feedback['scores'],
            strengths=parsed_feedback['strengths'],
            weaknesses=parsed_feedback['weaknesses'],
            recommendation=parsed_feedback['recommendation'],
            justification=parsed_feedback['justification']
        )
    
    async def _get_bias_analysis(self, reviews: List[ReviewerFeedback]) -> BiasAnalysis:
        bias_metrics = self.bias_detector._calculate_bias_score(reviews)
        detected_biases = self.bias_detector._detect_bias_instances(reviews)
        
        return BiasAnalysis(
            metrics=bias_metrics,
            detected_biases=detected_biases,
            overall_analysis=await self._generate_overall_analysis(reviews, bias_metrics),
            recommendations=await self._generate_bias_recommendations(detected_biases)
        )
    
    async def _generate_improvements(self, 
                                   reviews: List[ReviewerFeedback], 
                                   bias_analysis: BiasAnalysis) -> ImprovementSuggestions:
        improvements = {
            'technical_improvements': [],
            'language_improvements': [],
            'experience_improvements': [],
            'presentation_improvements': [],
            'bias_mitigation_improvements': []
        }
        
        # Generate improvements for each category
        for category in improvements.keys():
            category_improvements = await self._generate_category_improvements(
                category, reviews, bias_analysis
            )
            improvements[category] = category_improvements
        
        # Calculate priority summary
        priority_summary = self._calculate_priority_summary(improvements)
        
        return ImprovementSuggestions(
            **improvements,
            priority_summary=priority_summary
        )

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

# Example usage
async def main():
    groq_client = init_groq("", "", model="llama-3.1-70b-versatile")
    devils_advocate = DevilsAdvocateSystem(groq_client)
    
    application = """
    [Your application content here]
    """
    
    # Get structured evaluation results
    evaluation_results = await devils_advocate.evaluate_application(application)
    
    # Export results in different formats
    # As JSON string
    json_output = devils_advocate.export_results(evaluation_results, format='json')
    
    # As Python dictionary
    dict_output = devils_advocate.export_results(evaluation_results, format='dict')
    
    # Save to file
    devils_advocate.export_results(
        evaluation_results, 
        format='json', 
        file_path='evaluation_results.json'
    )
    
    # Access specific parts of the structured results
    print("\nOverall Recommendation:", evaluation_results.overall_recommendation)
    print("Confidence Score:", evaluation_results.confidence_score)
    
    # Access bias metrics
    bias_metrics = evaluation_results.bias_analysis.metrics
    print("\nBias Metrics:")
    print(f"Gender Bias Score: {bias_metrics.gender_bias_score:.2f}")
    print(f"Overall Bias Score: {bias_metrics.overall_bias_score:.2f}")
    
    # Access high-priority improvements
    high_priority_improvements = [
        imp for imp in evaluation_results.improvements.technical_improvements 
        if imp.priority == PriorityLevel.HIGH
    ]
    print("\nHigh Priority Improvements:")
    for imp in high_priority_improvements:
        print(f"- {imp.category}: {imp.suggestion}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())