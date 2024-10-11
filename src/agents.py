import math, json, asyncio
from collections import Counter
from utils.models import groq, init_groq, GROQ_API_KEY
from utils.prompts import *
from core.base import *

class DevilsAdvocateSystem:
    def __init__(self, groq_client: groq.Groq):
        self.client = groq_client
        self.application_id = str(uuid.uuid4())
        self.reviewers = self._initialize_reviewers()

    def _initialize_reviewers(self) -> List[Reviewer]:
        return [
            Reviewer(name="Reviewer A", bias_level="biased", specialization="technical"),
            Reviewer(name="Reviewer B", bias_level="biased", specialization="leadership"),
            Reviewer(name="Reviewer C", bias_level="unbiased", specialization="general")
        ]

    def _get_reviewer_prompt(self, reviewer: Reviewer, opportunity: str, application: str) -> str:
        template = BIASED_REVIEWER_TEMPLATE if reviewer.bias_level == "biased" else UNBIASED_REVIEWER_TEMPLATE
        return template.format(name=reviewer.name, opportunity=opportunity, application=application)

    async def _parse_reviewer_response(self, response_text: str, reviewer_type: BiasLevel=None):
        response_format = { "type": "json_object" }
        formatted_prompt = REVIEWER_FEEDBACK_OUTPUT_PROMPT_TEMPLATE.format(review_text=response_text)
        response = self.client(formatted_prompt, "", response_format=response_format).choices[0].message.content
        # Parse the JSON response into your Pydantic model
        try:
            response = ReviewerFeedback.model_validate_json(response)
            return response
        except Exception as e:
            raise ValueError(f"Failed to parse reviewer response: {e}")

    async def _get_reviewer_feedback(self, reviewer: Reviewer, opportunity:str, application: str) -> ReviewerFeedback:
        prompt = self._get_reviewer_prompt(reviewer, opportunity, application)
        response = self.client(prompt, "").choices[0].message.content

        # Parse LLM response into structured feedback
        parsed_feedback = await self._parse_reviewer_response(response, reviewer_type=reviewer.bias_level)

        return ReviewerFeedback(
            reviewer=reviewer,
            review_scores=parsed_feedback.review_scores,
            strengths=parsed_feedback.strengths,
            weaknesses=parsed_feedback.weaknesses,
            areas_of_concern=parsed_feedback.areas_of_concern,
            areas_of_potential=parsed_feedback.areas_of_potential,
            recommendation=parsed_feedback.recommendation,
            justification=parsed_feedback.justification,
            timestamp=datetime.now()
        )

class ProfileEvaluationSystem(DevilsAdvocateSystem):
    def __init__(self, groq_client: groq.Groq, application_id=str(uuid.uuid4())):
        # self.client = groq_client
        # self.reviewers = self._initialize_reviewers()

        super().__init__(groq_client)
        self.bias_detector = self._initialize_bias_detector()
        self.application_id = application_id

    def _initialize_bias_detector(self):
        return BiasDetector(self.client)

    async def evaluate_application(self, opportunity, application: str) -> EvaluationResult:
        # Collect reviews from all reviewers
        reviews = []
        for reviewer in self.reviewers:
            # prompt = self._get_reviewer_prompt(reviewer, application)
            # response = self.client(prompt, "")
            feedback = await self._get_reviewer_feedback(reviewer, opportunity, application)
            reviews.append(feedback.model_dump())

        overall_decision = await self._get_overall_decision(reviews)

        # Analyze reviews for bias
        bias_analysis = await self.bias_detector.analyze_reviews(reviews, opportunity, application)

        # Generate improvement suggestions
        # suggestions = self._generate_improvements(reviews, bias_analysis)

        return EvaluationResult(
            application_id=self.application_id,
            reviews=reviews,
            bias_analysis=bias_analysis,
            overall_decision=overall_decision,
            # improvements=suggestions,
            evaluation_timestamp=datetime.now(),
        )

    async def _get_overall_decision(self, reviews: List[ReviewerFeedback]):
        decision_count = Counter([item["recommendation"] for item in reviews])
        decision_threshold =  math.ceil(len(reviews)/2) # round up to nearest whole number
        most_common = decision_count.most_common(decision_threshold)

        # Check if there's a tie for the most common decision
        if len(most_common) > 1 and most_common[0][1] == most_common[1][1]:
            return "reject"

        # Return the most frequent decision
        return most_common[0][0]

class BiasDetector:
    def __init__(self, groq_client):
        self.client = groq_client
    
    async def analyze_reviews(self, reviews: List[Dict], opportunity: str, application: str) -> Dict:

        prompt = BIAS_DETECTOR_TEMPLATE.format(reviews=reviews, opportunity=opportunity, application=application)
        response = self.client(prompt, "").choices[0].message.content
        
        return {
            "analysis_summary": response,
            "bias_score": self._calculate_bias_score(reviews)
        }
    
    def _calculate_bias_score(self, reviews: List[Dict]) -> float:
        # Implement bias scoring logic
        # This could analyze language patterns, decision disparities, etc.
        pass

class ProfileHelper:
    """
        Generate recommendations after Devil's Advocate
        Generate recommendations independent of System Review
    """
    def __init__(self, groq_client: groq.Groq, application_id = str(uuid.uuid4())):
        self.client = groq_client
        self.application_id = application_id

    async def _generate_improvements(self, opportunity, application, reviews: List[Dict] , bias_analysis: Dict):
        # Improvement suggestion generation based on reviews and bias analysis
        prompt = APPLICATION_ENHANCEMENT_PROMPT_TEMPLATE.format(
            opportunity=opportunity, application=application, reviews=reviews, bias_analysis=bias_analysis
        )
        response_format = { "type": "json_object" }
        response = self.client(prompt, "", response_format=response_format).choices[0].message.content

        try:
            json_response = json.loads(response)
            output = {
                **json_response,
                "priority_summary": self._calculate_priority_summary(json_response)
            }

            return ImprovementSuggestions.model_validate(output) 

        except Exception as e:
            raise ValueError(f"Failed to parse reviewer response: {e}")

    async def _generate_improvements_independent(self, opportunity, application):
        # Improvement suggestion generation based on reviews and bias analysis
        prompt = APPLICATION_ENHANCEMENT_PROMPT_TEMPLATE_INDEPENDENT.format(opportunity=opportunity, application=application)
        response_format = { "type": "json_object" }
        response = self.client(prompt, "", response_format=response_format).choices[0].message.content

        try:
            json_response = json.loads(response)
            output = {
                **json_response,
                "priority_summary": self._calculate_priority_summary(json_response)
            }

            return ImprovementSuggestions.model_validate(output) 

        except Exception as e:
            raise ValueError(f"Failed to parse reviewer response: {e}")

    async def _generate_improvements_(
        self, reviews: List[ReviewerFeedback], bias_analysis: BiasAnalysis
    ) -> ImprovementSuggestions:
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

    def _calculate_priority_summary(self, improvements: dict):
        low, medium, high = (0, 0, 0)
        for key, val in improvements.items():
            # print(f"Key: {key} >> Values {val}")
            priorities_list = [item["priority"] for item in val]
            low += priorities_list.count("low")
            medium += priorities_list.count("medium")
            high += priorities_list.count("high")

        return {
            "high": low,
            "medium": medium,
            "low": high
        }
    
def export_results(evaluation_result: EvaluationResult, 
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

async def main():
    groq_client = init_groq

    # devils_advocate = DevilsAdvocateSystem(groq_client)
    profile_evaluator = ProfileEvaluationSystem(groq_client)
    profile_helper = ProfileHelper(groq_client)

    
    opportunity = open("./data/jd.txt", "r")
    application = open("./data/cv.txt", "r")
    evaluation_results = await profile_evaluator.evaluate_application(opportunity, application)
    enhancement_results = await profile_helper._generate_improvements(opportunity, application, evaluation_results.reviews, evaluation_results.bias_analysis)

    export_results(evaluation_results, format='json', file_path="./data/outputs/eval_outputs.json")
    export_results(enhancement_results, format='json', file_path="./data/outputs/helper_outputs.json")

# if __name__ == "__main__":
#     asyncio.run(main())
