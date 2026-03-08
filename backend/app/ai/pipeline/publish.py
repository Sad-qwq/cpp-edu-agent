from typing import Any, Dict

from app.models.ai_question_generation import QuestionDraft


def draft_to_problem_payload(draft: QuestionDraft, display_order: int) -> Dict[str, Any]:
    return {
        "type": draft.type,
        "content": draft.content,
        "score": draft.estimated_score or 10,
        "display_order": display_order,
        "options": draft.options,
        "correct_answer": draft.correct_answer,
        "code_template": draft.code_template,
        "test_cases": draft.test_cases,
    }