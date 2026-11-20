import json
from groq import Groq
from app.config import GROQ_API_KEY
import logging
from ddgs import DDGS

logger = logging.getLogger(__name__)

class AIAnalyzer:
    _client = None

    @classmethod
    def get_client(cls):
        if cls._client is None:
            cls._client = Groq(api_key=GROQ_API_KEY)
        return cls._client

    @classmethod
    def _search_web(cls, query: str, max_results: int = 3) -> str:
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))
                snippets = [r.get("body", "") for r in results if r.get("body")]
                return "\n".join(snippets)
        except Exception:
            return ""

    @classmethod
    def _refine_with_web(cls, data: dict) -> dict:
        subject_name = data.get("subject_name")
        if not subject_name or subject_name == "UNKNOWN":
            return data
        missing = []
        if data.get("subject_code") == "UNKNOWN":
            missing.append("subject_code")
        if data.get("semester") == "UNKNOWN":
            missing.append("semester")
        if data.get("module") == "UNKNOWN":
            missing.append("module")
        if not missing:
            return data

        query = f"{subject_name} subject code semester module college"
        search_results = cls._search_web(query)
        if not search_results:
            return data

        client = cls.get_client()
        prompt = f"""
Extract subject_code, semester, module from these results. Return JSON.
Subject Name: {subject_name}
Results: {search_results[:3000]}
{{"subject_code": "string", "semester": "string", "module": "string"}}
"""
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            raw = response.choices[0].message.content.strip()
            extracted = json.loads(raw)
            for key in missing:
                if key in extracted and extracted[key] not in ["UNKNOWN", "", None]:
                    data[key] = extracted[key]
        except Exception:
            pass
        return data

    @classmethod
    def analyze_document(cls, raw_text: str, filename: str = "", user_text: str = "") -> dict:
        if not raw_text or len(raw_text.strip()) < 50:
            return {"subject_code": "UNKNOWN", "subject_name": "UNKNOWN", "semester": "UNKNOWN", "module": "UNKNOWN", "questions": []}
        
        prompt = f"""
Analyze this college PDF text. Return JSON with: subject_code, subject_name, semester, module, questions (Q&A pairs).
Filename: {filename}
User note: {user_text}
Text: {raw_text[:15000]}
"""
        try:
            response = cls.get_client().chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            data = json.loads(response.choices[0].message.content.strip())
            for k in ["subject_code", "subject_name", "semester", "module", "questions"]:
                if k not in data:
                    data[k] = "UNKNOWN" if k != "questions" else []
            if data.get("subject_name") not in ["UNKNOWN", "", None]:
                data = cls._refine_with_web(data)
            return data
        except Exception as e:
            return {"subject_code": "ERROR", "subject_name": "ERROR", "semester": "ERROR", "module": "ERROR", "questions": [], "error": str(e)}

    @classmethod
    def analyze_timetable(cls, raw_text: str, filename: str = "", user_text: str = "") -> dict:
        if not raw_text or len(raw_text.strip()) < 50:
            return {"semester": "UNKNOWN", "subjects": [], "module": "UNKNOWN", "schedule": []}
        
        prompt = f"""
Extract timetable data. Return JSON: semester, module, subjects (code, name), schedule (day, time, subject_code, room).
Text: {raw_text[:15000]}
"""
        try:
            response = cls.get_client().chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content.strip())
        except Exception:
            return {"semester": "UNKNOWN", "subjects": [], "module": "UNKNOWN", "schedule": []}