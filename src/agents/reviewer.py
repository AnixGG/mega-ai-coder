from typing import List, Dict
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from src.core.config import settings
from src.agents.prompts import REVIEWER_SYSTEM_PROMPT


class ReviewComment(BaseModel):
    path: str = Field(description="File path related to the comment")
    line: int = Field(description="Line number in the new file")
    body: str = Field(description="The comment text (critique or suggestion)")


class ReviewResult(BaseModel):
    general_summary: str = Field(description="Overall feedback (Approve/Request Changes)")
    comments: List[ReviewComment] = Field(description="Inline comments on specific lines")
    action: str = Field(description="APPROVE or REQUEST_CHANGES")


class ReviewerAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.MODEL_NAME,
            api_key=settings.OPENAI_API_KEY,
            temperature=0.2,
        )
        self.structured_llm = self.llm.with_structured_output(ReviewResult)

    def review_pr(self, issue_text: str, pr_diff: str) -> ReviewResult:
        system_prompt = REVIEWER_SYSTEM_PROMPT

        user_prompt = f"""
        ISSUE:
        {issue_text}

        GIT DIFF:
        {pr_diff[:20000]} 
        """

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", user_prompt)
        ])

        return self.structured_llm.invoke({})