import logging
import json
import requests
from typing import Dict, Any, List, Optional
import time
from config import Config

logger = logging.getLogger(__name__)

class LLMAnalyzer:
    def __init__(self):
        self.api_url = Config.LLM_API_URL
        self.model = Config.LLM_MODEL
        self.max_retries = 3
        self.timeout = 30

    def test_connection(self) -> bool:
        try:
            test_prompt = "Respond with 'OK' if you can read this."
            response = self._call_llm(test_prompt, max_tokens=5)
            return "OK" in response.get("content", "").upper()
        except Exception as e:
            logger.error(f"LLM connection test failed: {e}")
            return False

    def _call_llm(self, prompt: str, max_tokens: int = 500, temperature: float = 0.3) -> Dict[str, Any]:
        headers = {
            "Content-Type": "application/json",
        }

        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a tech news analysis assistant. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": False
        }

        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    self.api_url,
                    headers=headers,
                    json=data,
                    timeout=self.timeout
                )
                response.raise_for_status()

                result = response.json()

                if "choices" in result and len(result["choices"]) > 0:
                    content = result["choices"][0]["message"]["content"]
                    return {"success": True, "content": content.strip()}
                else:
                    logger.warning(f"Unexpected LLM response format: {result}")
                    return {"success": False, "error": "Invalid response format"}

            except requests.exceptions.Timeout:
                logger.warning(f"LLM request timeout (attempt {attempt + 1}/{self.max_retries})")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
                continue

            except requests.exceptions.RequestException as e:
                logger.error(f"LLM request error (attempt {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
                continue

            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse LLM response JSON: {e}")
                return {"success": False, "error": "Invalid JSON response"}

        return {"success": False, "error": "Max retries exceeded"}

    def _parse_llm_json_response(self, content: str) -> Optional[Dict[str, Any]]:
        try:
            # Try to extract JSON from the response
            content = content.strip()

            # Remove any markdown code blocks
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]

            content = content.strip()

            # Try to parse JSON
            return json.loads(content)

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM JSON response: {e}")
            logger.debug(f"Raw content: {content}")
            return None

    def analyze_article(self, title: str, description: str, existing_categories: List[str]) -> Dict[str, Any]:
        if not title.strip():
            return self._get_fallback_analysis("Empty title")

        # Prepare categories list for the prompt
        categories_text = ", ".join(existing_categories) if existing_categories else "No existing categories"

        prompt = f"""
IMMEDIATE FILTER CHECK - BEFORE ANALYSIS:
If ANY of these patterns appear in title or description, set should_filter = true IMMEDIATELY:
- "[D] Self-Promotion Thread", "[D] Who's Hiring", "[D] Who wants to be Hired"
- "[D] Monthly", "[D] Weekly", "[D] Daily Thread"
- "Self-Promotion", "self promotion", "who's hiring", "job postings"
- Title starts with "[D]" and contains "Thread", "Hiring", "Promotion"

Title pattern check: {title.lower()}
Description pattern check: {description[:200].lower() if description else ""}

Now analyze this tech news article and provide a JSON response with the following structure:
{{
    "categories": ["category1", "category2"],
    "relevance_score": 3,
    "tone": "informative",
    "should_filter": false,
    "filter_reason": ""
}}

Title: {title}
Description: {description[:500] if description else "No description"}

Existing categories to prioritize: {categories_text}

Requirements:
1. Categories: Return 1-3 categories from the existing list if possible. Create new categories only if necessary.
2. Relevance Score: 1 (low relevance) to 5 (highly relevant)
3. Tone: Choose one: "informative", "promotional", "opinion", "technical", "news"
4. Filter: Set should_filter to true for ads, spam, irrelevant content, or inappropriate material
5. Filter Reason: Explain why content is being filtered (only if should_filter is true)

CRITICAL FILTERING RULES - Set should_filter = true for ANY of:
- Biology, zoology, nature, evolution articles about animals/insects (ants, bees, etc.)
- Medical/health articles not related to health tech
- Pure scientific research without tech applications
- Entertainment, celebrity news, sports, politics (unless tech policy)
- General news, lifestyle, fashion, travel, food
- Biology articles even if they mention "tech" in passing
- Research papers about ants, insects, animals, plants
- Content about biology, evolution, zoology, ecology
- Reddit self-promotion threads, "Who's Hiring", job postings, collaboration requests
- Meta threads, weekly threads, daily threads that are not actual news
- Reddit threads with "[D]" (Discussion) that are just community posts without news
- Any content that is primarily about self-promotion, hiring, or meta discussions

ACCEPTABLE TECH CATEGORIES:
- Software development, programming, web dev, mobile dev
- AI/ML, data science, cybersecurity, cloud computing
- Hardware, gadgets, electronics, IoT
- DevOps, infrastructure, networking
- Tech startups, business tech, funding
- Open source, frameworks, libraries
- Tech policy, digital rights, privacy
- Gaming, VR/AR, metaverse (tech focus)
- Blockchain, crypto (tech focus)
- Tech tutorials, guides, how-tos

Category guidelines:
- Prefer existing categories when possible
- Use tech-specific categories like "AI", "WEB", "DEV", "MOBILE", "CLOUD", etc.
- Normalize category names (lowercase, no spaces unless necessary)
- When in doubt, filter it out if it's not clearly tech-related

Examples of CONTENT TO FILTER:
- "The evolution of ants and their social structure"
- "Medical breakthrough: new cancer treatment"
- "Climate change effects on wildlife"
- "Political election results"
- "Celebrity gossip and entertainment news"
- "[D] Self-Promotion Thread"
- "[D] Who's Hiring and Who wants to be Hired?"
- "Sunday Daily Thread: What's everyone working on this week?"
- "[D] Monthly Meta Discussion Thread"

Respond with JSON only, no additional text.
"""

        try:
            response = self._call_llm(prompt, max_tokens=300, temperature=0.2)

            if not response["success"]:
                logger.error(f"LLM call failed: {response.get('error', 'Unknown error')}")
                return self._get_fallback_analysis(f"LLM error: {response.get('error', 'Unknown')}")

            # Parse the JSON response
            analysis = self._parse_llm_json_response(response["content"])

            if not analysis:
                logger.error("Failed to parse LLM JSON response")
                return self._get_fallback_analysis("Invalid JSON response")

            # Validate and normalize the analysis
            return self._validate_analysis(analysis)

        except Exception as e:
            logger.error(f"Error analyzing article: {e}")
            return self._get_fallback_analysis(f"Analysis error: {str(e)}")

    def _validate_analysis(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        validated = {}

        # Validate categories
        categories = analysis.get("categories", [])
        if isinstance(categories, list):
            # Normalize categories and filter valid ones
            normalized_categories = []
            for cat in categories:
                if isinstance(cat, str) and cat.strip():
                    normalized_cat = cat.strip().upper()
                    if len(normalized_cat) <= 50:  # Reasonable length limit
                        normalized_categories.append(normalized_cat)

            validated["categories"] = normalized_categories[:3]  # Max 3 categories
        else:
            validated["categories"] = ["GENERAL"]

        # Validate relevance score
        relevance_score = analysis.get("relevance_score", 3)
        try:
            score = int(relevance_score)
            validated["relevance_score"] = max(1, min(5, score))  # Clamp between 1-5
        except (ValueError, TypeError):
            validated["relevance_score"] = 3

        # Validate tone
        valid_tones = ["informative", "promotional", "opinion", "technical", "news"]
        tone = analysis.get("tone", "news").lower()
        validated["tone"] = tone if tone in valid_tones else "news"

        # Validate filter settings
        should_filter = analysis.get("should_filter", False)
        validated["should_filter"] = bool(should_filter)

        filter_reason = analysis.get("filter_reason", "")
        if validated["should_filter"] and filter_reason:
            validated["filter_reason"] = str(filter_reason)[:200]  # Limit length
        else:
            validated["filter_reason"] = ""

        return validated

    def _get_fallback_analysis(self, error_reason: str) -> Dict[str, Any]:
        logger.warning(f"Using fallback analysis due to: {error_reason}")

        return {
            "categories": ["GENERAL"],
            "relevance_score": 3,
            "tone": "news",
            "should_filter": False,
            "filter_reason": "",
            "error": error_reason
        }

    def batch_analyze_articles(self, articles: List[Dict[str, Any]], existing_categories: List[str], delay: float = 1.0) -> List[Dict[str, Any]]:
        analyzed_articles = []

        for i, article in enumerate(articles):
            try:
                logger.info(f"Analyzing article {i+1}/{len(articles)}: {article.get('title', 'Unknown')[:50]}...")

                analysis = self.analyze_article(
                    article.get('title', ''),
                    article.get('description', ''),
                    existing_categories
                )

                # Merge analysis with article data
                analyzed_article = article.copy()
                analyzed_article.update(analysis)

                analyzed_articles.append(analyzed_article)

                # Add delay between requests to avoid overwhelming the LLM
                if delay > 0 and i < len(articles) - 1:
                    time.sleep(delay)

            except Exception as e:
                logger.error(f"Error in batch analysis for article {i}: {e}")

                # Add fallback analysis
                fallback_article = article.copy()
                fallback_article.update(self._get_fallback_analysis(f"Batch error: {str(e)}"))
                analyzed_articles.append(fallback_article)

        return analyzed_articles