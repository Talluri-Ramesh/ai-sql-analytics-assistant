from typing import Optional
import pandas as pd
from llm import llm_service

class InsightsService:
    """
    Generates plain-English SQL explanations and narrative business insights
    using Groq LLM API calls.
    """

    def explain_sql(self, sql_query: str) -> str:
        """Generates a step-by-step plain-English explanation of the SQL query."""
        if not llm_service.client:
            return "Groq API key not configured."

        system_prompt = (
            "You are a helpful database tutor. Explain the following SQL query in simple, "
            "plain English terms. Keep the explanation concise (2 to 3 sentences max) "
            "and easy to understand for non-technical managers."
        )

        try:
            response = llm_service.client.chat.completions.create(
                model=llm_service.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"SQL Query:\n{sql_query}"}
                ],
                temperature=0.2,
                max_tokens=200
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Unable to generate explanation: {str(e)}"

    def generate_narrative_insight(self, question: str, df: Optional[pd.DataFrame]) -> str:
        """Generates business narrative insights based on query result data."""
        if not llm_service.client:
            return "Groq API key not configured."

        if df is None or df.empty:
            return "No data available to generate business insights."

        # Truncate DataFrame string representation to avoid exceeding context window
        df_summary = df.head(10).to_string(index=False)

        system_prompt = (
            "You are an executive business analytics consultant. Analyze the provided query results "
            "and write a concise 2-bullet executive summary highlighting the key business takeaways "
            "or action items for management."
        )

        user_content = f"Business Question: {question}\n\nQuery Results (Sample):\n{df_summary}"

        try:
            response = llm_service.client.chat.completions.create(
                model=llm_service.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                temperature=0.3,
                max_tokens=250
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Unable to generate business insights: {str(e)}"

    def answer_general_question(self, question: str) -> str:
        """Answers general knowledge questions for Case 3 (Schema-unrelated)."""
        if not llm_service.client:
            return "Groq API key not configured."

        system_prompt = (
            "You are a general knowledge assistant. Answer the user's question clearly, "
            "accurately, and concisely."
        )

        try:
            response = llm_service.client.chat.completions.create(
                model=llm_service.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": question}
                ],
                temperature=0.5,
                max_tokens=400
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Unable to answer question: {str(e)}"

# Singleton instance for export
insights_service = InsightsService()