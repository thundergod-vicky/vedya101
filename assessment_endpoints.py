@app.post("/teaching/assessment/create")
async def create_assessment(request: dict):
    """Create an assessment for a specific concept."""
    try:
        concept = request.get("concept", "")
        subject = request.get("subject", "Artificial Intelligence")
        difficulty = request.get("difficulty", "Intermediate")
        learning_style = request.get("learning_style", "Visual + Hands-on")
        previous_responses = request.get("previous_responses", [])
        
        if not concept:
            raise HTTPException(status_code=400, detail="Concept is required")
        
        # Use the AssessmentAgent to create an assessment
        if agent_system and hasattr(agent_system, 'agents') and 'assessment' in agent_system.agents:
            assessment_agent = agent_system.agents['assessment']
            result = await assessment_agent.create_assessment_for_concept(
                concept=concept,
                subject=subject,
                difficulty=difficulty,
                learning_style=learning_style,
                previous_responses=previous_responses
            )
            return result
        else:
            # Fallback response
            return {
                "success": True,
                "assessment": {
                    "questions": [
                        {
                            "id": "q1",
                            "question": f"Which of the following best describes {concept}?",
                            "type": "multiple_choice",
                            "options": [
                                "A fundamental concept in AI",
                                "An advanced mathematical theory",
                                "A programming language",
                                "A hardware component"
                            ],
                            "correct_answer": "A fundamental concept in AI",
                            "explanation": f"{concept} is indeed a fundamental concept in AI."
                        },
                        {
                            "id": "q2",
                            "question": f"True or False: {concept} is important for understanding AI systems.",
                            "type": "true_false",
                            "options": ["True", "False"],
                            "correct_answer": "True",
                            "explanation": f"{concept} is a crucial component for understanding AI systems."
                        }
                    ],
                    "passing_score": 1,
                    "concept_assessed": concept,
                    "difficulty": difficulty,
                    "created_at": datetime.now().isoformat()
                }
            }
        
    except Exception as e:
        print(f"Error creating assessment: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create assessment: {str(e)}")

@app.post("/teaching/assessment/grade")
async def grade_assessment(request: dict):
    """Grade a user's assessment answers."""
    try:
        user_answers = request.get("user_answers", [])
        assessment = request.get("assessment", {})
        
        if not user_answers or not assessment:
            raise HTTPException(status_code=400, detail="User answers and assessment are required")
        
        # Use the AssessmentAgent to grade the assessment
        if agent_system and hasattr(agent_system, 'agents') and 'assessment' in agent_system.agents:
            assessment_agent = agent_system.agents['assessment']
            result = await assessment_agent.grade_assessment(
                user_answers=user_answers,
                assessment=assessment
            )
            return result
        else:
            # Fallback response
            return {
                "success": True,
                "passed": True,
                "score": 1,
                "total": 2,
                "score_percentage": 50.0,
                "feedback": "Good job! You've shown a solid understanding of the concept.",
                "question_results": [
                    {
                        "id": user_answers[0].get("id", "q1"),
                        "question": "Question text",
                        "user_answer": user_answers[0].get("answer", ""),
                        "correct": True,
                        "correct_answer": "Correct answer",
                        "explanation": "Explanation of the correct answer."
                    }
                ],
                "concept": assessment.get("concept_assessed", "the concept"),
                "subject": "Artificial Intelligence",
                "completed_at": datetime.now().isoformat()
            }
        
    except Exception as e:
        print(f"Error grading assessment: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to grade assessment: {str(e)}")

@app.post("/teaching/assessment/recommendations")
async def get_teaching_recommendations(request: dict):
    """Get teaching recommendations based on assessment results."""
    try:
        assessment_result = request.get("assessment_result", {})
        
        if not assessment_result:
            raise HTTPException(status_code=400, detail="Assessment result is required")
        
        # Use the AssessmentAgent to provide recommendations
        if agent_system and hasattr(agent_system, 'agents') and 'assessment' in agent_system.agents:
            assessment_agent = agent_system.agents['assessment']
            result = await assessment_agent.provide_teaching_recommendations(assessment_result)
            return result
        else:
            # Fallback response
            passed = assessment_result.get("passed", False)
            concept = assessment_result.get("concept", "the concept")
            
            if passed:
                return {
                    "success": True,
                    "should_continue": True,
                    "message": f"Great job! You've demonstrated understanding of {concept}. Let's continue with the next concept.",
                    "next_action": "continue_teaching"
                }
            else:
                return {
                    "success": True,
                    "should_continue": False,
                    "message": f"Let's review {concept} a bit more before moving on.",
                    "review_points": [
                        "Review the key definitions and examples",
                        "Try to apply the concept in different contexts",
                        "Focus on understanding the underlying principles"
                    ],
                    "next_action": "review_concept"
                }
        
    except Exception as e:
        print(f"Error getting teaching recommendations: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get teaching recommendations: {str(e)}")
