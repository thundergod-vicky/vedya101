#!/usr/bin/env python3
"""
Assessment methods for the VEDYA education platform.
Handles quiz generation, grading, and feedback.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from langchain_core.messages import HumanMessage, SystemMessage

class AssessmentMethods:
    """Assessment methods that can be used in any agent class."""
    
    def __init__(self, llm):
        self.llm = llm
    
    async def create_assessment_for_concept(self, concept: str, subject: str, difficulty: str, 
                                  learning_style: str, previous_responses: List[str] = None) -> Dict[str, Any]:
        """Create an assessment quiz for a specific concept."""
        
        # Build assessment prompt
        previous_context = ""
        if previous_responses and len(previous_responses) > 0:
            previous_context = "Previous teaching exchanges:\n\n" + "\n".join([
                f"- {resp[:100]}..." for resp in previous_responses[:3]
            ])

        system_prompt = f"""You are an expert Assessment Agent creating a meaningful quiz to evaluate student understanding of {concept} in {subject}.

CONTEXT:
- Student's Learning Style: {learning_style}
- Difficulty Level: {difficulty}
- Concept Being Assessed: {concept}
{previous_context}

ASSESSMENT DESIGN GUIDELINES:
1. Create exactly 3 questions that test comprehension of {concept}
2. Make questions progressively more challenging
3. Questions should be relevant to what was covered in the teaching session
4. Adapt question style to {learning_style} learners
5. Include a mix of question types (multiple choice, true/false, short answer)
6. Provide clear, informative feedback for each possible answer

OUTPUT FORMAT:
Return a valid JSON object with this exact structure:
{{
  "questions": [
    {{
      "id": "q1",
      "question": "Question text here",
      "type": "multiple_choice|true_false|short_answer",
      "options": ["Option A", "Option B", "Option C", "Option D"], 
      "correct_answer": "Correct option here or index",
      "explanation": "Explanation of the correct answer"
    }},
    ...
  ],
  "passing_score": 2,
  "concept_assessed": "{concept}",
  "difficulty": "{difficulty}"
}}

IMPORTANT:
- For multiple_choice questions, include 3-4 options, with exactly one correct answer
- For true_false questions, provide options ["True", "False"] and correct_answer should be "True" or "False"
- For short_answer questions, provide an empty options array [] and correct_answer should be a string with the expected answer
- Ensure the questions genuinely assess understanding, not just recall
- Target the questions to {difficulty} level"""

        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"Create an assessment for {concept} in {subject} at {difficulty} level")
            ]
            
            response = await self.llm.ainvoke(messages)
            
            # Extract JSON from response
            response_text = response.content
            
            # Try to find JSON in the response
            import re
            import json
            
            json_match = re.search(r'```json\s*([\s\S]*?)\s*```', response_text)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Try to find JSON without code blocks
                json_match = re.search(r'({[\s\S]*})', response_text)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    json_str = response_text
            
            try:
                assessment = json.loads(json_str)
                
                # Ensure assessment has the correct structure
                if not isinstance(assessment, dict) or "questions" not in assessment:
                    raise ValueError("Invalid assessment structure")
                
                # Add assessment metadata
                assessment["concept"] = concept
                assessment["subject"] = subject
                assessment["difficulty"] = difficulty
                assessment["learning_style"] = learning_style
                assessment["created_at"] = datetime.now().isoformat()
                
                return {
                    "success": True,
                    "assessment": assessment
                }
                
            except json.JSONDecodeError:
                print(f"Error parsing assessment JSON: {json_str}")
                # Fallback to basic assessment
                return {
                    "success": False,
                    "error": "Failed to parse assessment JSON",
                    "assessment": self._create_fallback_assessment(concept, subject, difficulty)
                }
                
        except Exception as e:
            print(f"Error creating assessment: {e}")
            return {
                "success": False,
                "error": str(e),
                "assessment": self._create_fallback_assessment(concept, subject, difficulty)
            }
    
    def _create_fallback_assessment(self, concept: str, subject: str, difficulty: str) -> Dict[str, Any]:
        """Create a basic fallback assessment when the main generation fails."""
        return {
            "questions": [
                {
                    "id": "q1",
                    "question": f"Which of the following best describes {concept}?",
                    "type": "multiple_choice",
                    "options": [
                        f"A key concept in {subject}",
                        f"An unrelated topic to {subject}",
                        f"A historical figure in {subject}",
                        f"A tool used only in advanced {subject}"
                    ],
                    "correct_answer": "A key concept in {subject}",
                    "explanation": f"{concept} is indeed a fundamental concept in {subject}."
                },
                {
                    "id": "q2",
                    "question": f"True or False: {concept} is important for understanding {subject}.",
                    "type": "true_false",
                    "options": ["True", "False"],
                    "correct_answer": "True",
                    "explanation": f"{concept} is a crucial component for understanding {subject}."
                }
            ],
            "passing_score": 1,
            "concept_assessed": concept,
            "difficulty": difficulty,
            "created_at": datetime.now().isoformat()
        }
            
    async def grade_assessment(self, user_answers: List[Dict[str, Any]], assessment: Dict[str, Any]) -> Dict[str, Any]:
        """Grade user's assessment answers and provide feedback."""
        
        questions = assessment.get("questions", [])
        passing_score = assessment.get("passing_score", len(questions) // 2)
        concept = assessment.get("concept", "the concept")
        subject = assessment.get("subject", "the subject")
        
        # Match user answers with questions
        correct_count = 0
        question_results = []
        
        for user_answer in user_answers:
            q_id = user_answer.get("id")
            answer = user_answer.get("answer")
            
            # Find matching question
            matching_question = next((q for q in questions if q.get("id") == q_id), None)
            
            if matching_question:
                correct = self._check_answer(answer, matching_question)
                
                if correct:
                    correct_count += 1
                
                question_results.append({
                    "id": q_id,
                    "question": matching_question.get("question"),
                    "user_answer": answer,
                    "correct": correct,
                    "correct_answer": matching_question.get("correct_answer"),
                    "explanation": matching_question.get("explanation")
                })
        
        # Determine if passing
        passed = correct_count >= passing_score
        
        # Generate feedback based on performance
        if passed:
            if correct_count == len(questions):
                feedback = f"Excellent work! You've demonstrated complete mastery of {concept}."
            else:
                feedback = f"Good job! You've shown a solid understanding of {concept}."
        else:
            feedback = f"You're making progress with {concept}, but let's review some key points."
        
        # Calculate percentage score
        score_percentage = (correct_count / len(questions)) * 100 if questions else 0
        
        return {
            "success": True,
            "passed": passed,
            "score": correct_count,
            "total": len(questions),
            "score_percentage": score_percentage,
            "passing_score": passing_score,
            "feedback": feedback,
            "question_results": question_results,
            "concept": concept,
            "subject": subject,
            "completed_at": datetime.now().isoformat()
        }
    
    def _check_answer(self, user_answer: Any, question: Dict[str, Any]) -> bool:
        """Check if user's answer is correct."""
        question_type = question.get("type", "multiple_choice")
        correct_answer = question.get("correct_answer")
        
        if question_type == "multiple_choice":
            # Handle both index-based and value-based answers
            if isinstance(user_answer, int):
                options = question.get("options", [])
                if 0 <= user_answer < len(options):
                    return options[user_answer] == correct_answer
                return False
            else:
                return user_answer == correct_answer
                
        elif question_type == "true_false":
            # Convert to boolean if needed
            if isinstance(user_answer, bool):
                return (user_answer and correct_answer == "True") or (not user_answer and correct_answer == "False")
            else:
                return str(user_answer) == correct_answer
                
        elif question_type == "short_answer":
            # Simple exact match for short answer
            # In a real implementation, this would use more sophisticated matching
            user_answer_lower = str(user_answer).lower().strip()
            correct_answer_lower = str(correct_answer).lower().strip()
            
            # Simple check - in a real implementation, this would use
            # more sophisticated semantic matching
            return user_answer_lower == correct_answer_lower or \
                user_answer_lower in correct_answer_lower or \
                correct_answer_lower in user_answer_lower
                
        # Default case
        return str(user_answer) == str(correct_answer)
