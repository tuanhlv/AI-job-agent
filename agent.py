from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel
import os

load_dotenv()


class JobAnalysis(BaseModel):
    fit_summary: str
    skill_gap: str
    learning_action: str


class CareerMatchAgent:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found! Check .env file and its location.")
        self.client = genai.Client(api_key=api_key)
        self.model_name = 'gemini-2.5-flash'

    def format_chroma_results(self, chroma_results: dict) -> list[str]:
        """Formats raw ChromaDB dictionary results into a readable string for the LLM."""
        formatted_text = []
        try:
            for i in range(len(chroma_results['documents'][0])):
                title = chroma_results['metadatas'][0][i].get('Title', 'Unknown Title')
                description = chroma_results['documents'][0][i]
                formatted_text.append(f"--- MATCH {i + 1}: {title} ---\n{description}")
        except (KeyError, IndexError) as e:
            print(f"Error parsing ChromaDB results: {e}")

        return formatted_text

    def analyze_candidate(self, user_profile: str, top_jobs_text: str) -> JobAnalysis:
        """Sends the profile and jobs to Gemini and returns structured Pydantic data."""
        prompt = f"""
        You are an expert technical recruiter. 

        Candidate Profile:
        {user_profile}

        Top 3 Matching Job Descriptions:
        {top_jobs_text}

        Analyze the candidate against these roles. Identify the summary of fit, 
        and exactly 2 critical skill gaps with 1 highly specific, actionable learning step for each.
        """

        print("Agent is analyzing the data...")

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config={
                # Force the model to return JSON that perfectly matches our Pydantic schema
                'response_mime_type': 'application/json',
                'response_schema': JobAnalysis,
            }
        )

        # Parse the JSON string response back into our Pydantic object
        return JobAnalysis.model_validate_json(response.text)