#!/usr/bin/env python3
"""
Movie recommendation prompt evaluator
"""

import json
import os
import time
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class MovieEvaluator:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

        # Prompt versions to compare
        self.prompts = {
            "basic": """
Recommend 3 movies based on user preferences.
Respond only in JSON format with this structure:
{{
  "movies": [
    {{"title": "", "genre": "", "reason": ""}},
    {{"title": "", "genre": "", "reason": ""}},
    {{"title": "", "genre": "", "reason": ""}}
  ]
}}

User preferences: {preferences}
            """.strip(),

            "detailed": """
You are a cinema expert who recommends personalized movies.

INSTRUCTIONS:
1. Analyze user preferences
2. Recommend exactly 3 different movies
3. Respond ONLY in valid JSON format

RESPONSE FORMAT (copy exactly):
{{
  "movies": [
    {{"title": "Movie Name", "genre": "Main Genre", "reason": "Specific recommendation reason"}},
    {{"title": "Movie Name", "genre": "Main Genre", "reason": "Specific recommendation reason"}},
    {{"title": "Movie Name", "genre": "Main Genre", "reason": "Specific recommendation reason"}}
  ]
}}

User preferences: {preferences}
            """.strip(),

            "contextual": """
PERSONAL MOVIE RECOMMENDER

As a cinema expert, I'll recommend 3 perfect movies for you.

Your preferences: {preferences}

JSON response (don't add additional text):
{{
  "movies": [
    {{"title": "", "genre": "", "reason": ""}},
    {{"title": "", "genre": "", "reason": ""}},
    {{"title": "", "genre": "", "reason": ""}}
  ]
}}
            """.strip()
        }

        # Test cases
        self.test_cases = [
            "I like romantic comedies and 90s movies",
            "I prefer science fiction and psychological thrillers",
            "I love superhero action movies",
            "Looking for award-winning historical or biographical dramas"
        ]

    def validate_api_key(self):
        """Validate OpenAI API key with a simple test call"""
        try:
            print("🔑 Validating OpenAI API key...")
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=5
            )
            print("✅ API key is valid!")
            return True
        except Exception as e:
            print(f"❌ API key validation failed: {str(e)}")
            return False

    def test_prompt(self, prompt_name, prompt_template, user_preferences):
        """Test a specific prompt with user preferences"""
        try:
            prompt = prompt_template.format(preferences=user_preferences)

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.7
            )

            result = response.choices[0].message.content

            # Try to parse as JSON
            try:
                # Clean the result - sometimes API returns markdown code blocks
                cleaned_result = result.strip()
                if cleaned_result.startswith('```json'):
                    cleaned_result = cleaned_result.replace('```json', '').replace('```', '').strip()
                elif cleaned_result.startswith('```'):
                    cleaned_result = cleaned_result.replace('```', '').strip()

                parsed = json.loads(cleaned_result)
                is_valid_json = True
                has_3_movies = len(parsed.get('movies', [])) == 3
                has_required_fields = all(
                    'title' in movie and 'genre' in movie and 'reason' in movie
                    for movie in parsed.get('movies', [])
                )
                quality_score = (is_valid_json + has_3_movies + has_required_fields) / 3
            except json.JSONDecodeError as e:
                print(f"     JSON Parse Error: {str(e)}")
                print(f"     Raw response: {repr(result[:100])}...")
                parsed = None
                is_valid_json = False
                has_3_movies = False
                has_required_fields = False
                quality_score = 0

            return {
                'prompt_name': prompt_name,
                'user_input': user_preferences,
                'raw_output': result,
                'parsed_json': parsed,
                'is_valid_json': is_valid_json,
                'has_3_movies': has_3_movies,
                'has_required_fields': has_required_fields,
                'quality_score': quality_score
            }

        except Exception as e:
            print(f"Error testing prompt '{prompt_name}': {str(e)}")
            return None

    def run_evaluation(self):
        """Run complete evaluation"""
        print("🎬 MOVIE RECOMMENDATION PROMPT EVALUATOR")
        print("=" * 60)

        all_results = []
        prompt_scores = {name: [] for name in self.prompts.keys()}

        for i, test_case in enumerate(self.test_cases, 1):
            print(f"\n📝 TEST CASE {i}: {test_case}")
            print("-" * 50)

            for j, (prompt_name, prompt_template) in enumerate(self.prompts.items()):
                print(f"\n🔄 Testing prompt: {prompt_name.upper()}")


                result = self.test_prompt(prompt_name, prompt_template, test_case)
                if result:
                    all_results.append(result)
                    prompt_scores[prompt_name].append(result['quality_score'])

                    # Show result
                    print(f"✅ Valid JSON: {'Yes' if result['is_valid_json'] else 'No'}")
                    print(f"✅ 3 movies: {'Yes' if result['has_3_movies'] else 'No'}")
                    print(f"✅ Complete fields: {'Yes' if result['has_required_fields'] else 'No'}")
                    print(f"📊 Score: {result['quality_score']:.2%}")

                    if result['parsed_json'] and result['quality_score'] > 0:
                        print("🎭 Recommended movies:")
                        for k, movie in enumerate(result['parsed_json'].get('movies', []), 1):
                            print(f"  {k}. {movie.get('title', 'N/A')} ({movie.get('genre', 'N/A')})")
                            print(f"     Reason: {movie.get('reason', 'N/A')}")


        # Final summary
        print("\n" + "=" * 60)
        print("📊 FINAL SUMMARY - PROMPT COMPARISON")
        print("=" * 60)

        for prompt_name, scores in prompt_scores.items():
            if scores:
                avg_score = sum(scores) / len(scores)
                success_rate = sum(1 for s in scores if s == 1.0) / len(scores)
                print(f"\n🎯 {prompt_name.upper()}:")
                print(f"   Average score: {avg_score:.2%}")
                print(f"   Success rate (100%): {success_rate:.2%}")
                print(f"   Test cases: {len(scores)}")

        # Determine best prompt
        best_prompt = max(prompt_scores.keys(),
                         key=lambda x: sum(prompt_scores[x]) / len(prompt_scores[x]) if prompt_scores[x] else 0)
        best_score = sum(prompt_scores[best_prompt]) / len(prompt_scores[best_prompt]) if prompt_scores[best_prompt] else 0

        print(f"\n🏆 WINNER: {best_prompt.upper()} with {best_score:.2%} average score")

        return best_prompt, all_results

    def show_best_prompt(self, best_prompt_name):
        """Show the best prompt to use in the challenge"""
        print(f"\n📋 RECOMMENDED PROMPT FOR CHALLENGE: {best_prompt_name.upper()}")
        print("=" * 60)
        # Remove the double braces for the final recommendation
        clean_prompt = self.prompts[best_prompt_name].replace('{{', '{').replace('}}', '}')
        print(clean_prompt)
        print("=" * 60)


def main():
    """Main function"""
    # Check OpenAI configuration
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Error: OPENAI_API_KEY not found in .env file")
        print("💡 Create a .env file with your OpenAI API key:")
        print("   OPENAI_API_KEY=sk-your_api_key_here")
        return

    evaluator = MovieEvaluator()

    # Validate API key first
    if not evaluator.validate_api_key():
        print("\n💡 Please check your OpenAI configuration and try again.")
        print("   1. Verify your API key and endpoint in portal")
        print("   2. Check your deployment name exists")
        print("   3. Update your .env file with correct values")
        return

    best_prompt, results = evaluator.run_evaluation()
    evaluator.show_best_prompt(best_prompt)

    print("\n✨ Evaluation completed! Use the winning prompt for your challenge.")


if __name__ == "__main__":
    main()