#!/usr/bin/env python3
"""
Movie recommendation prompt evaluator
"""

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
from utils.tee_output import TeeOutput

# Load environment variables
load_dotenv()

# Model configuration constants
GENERATION_MODEL = "gpt-4.1-nano"  # Model used for generating movie recommendations

class MovieEvaluator:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

        # Load system prompts from files
        self.system_prompts = self.load_system_prompts()

        # Load test dataset
        self.dataset = self.load_dataset()

    def load_system_prompts(self):
        """Load system prompts from separate files"""
        prompts_dir = Path(__file__).parent / "prompt_evaluator" / "system_prompts"
        system_prompts = {}

        for prompt_file in prompts_dir.glob("*.txt"):
            prompt_name = prompt_file.stem
            with open(prompt_file, 'r', encoding='utf-8') as f:
                system_prompts[prompt_name] = f.read().strip()

        return system_prompts

    def load_dataset(self):
        """Load test dataset from JSON file"""
        dataset_path = Path(__file__).parent / "prompt_evaluator" / "datasets" / "movie_preferences.json"

        with open(dataset_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def validate_api_key(self):
        """Validate OpenAI API key with a simple test call"""
        try:
            print("🔑 Validating OpenAI API key...")
            response = self.client.chat.completions.create(
                model=GENERATION_MODEL,
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=5
            )
            print("✅ API key is valid!")
            return True
        except Exception as e:
            print(f"❌ API key validation failed: {str(e)}")
            return False

    def test_system_prompt(self, system_prompt_name, system_prompt, user_prompt):
        """Test a specific system prompt with user input"""
        try:
            response = self.client.chat.completions.create(
                model=GENERATION_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
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
                'system_prompt_name': system_prompt_name,
                'user_input': user_prompt,
                'raw_output': result,
                'parsed_json': parsed,
                'is_valid_json': is_valid_json,
                'has_3_movies': has_3_movies,
                'has_required_fields': has_required_fields,
                'quality_score': quality_score
            }

        except Exception as e:
            print(f"Error testing system prompt '{system_prompt_name}': {str(e)}")
            return None

    def run_evaluation(self):
        """Run complete evaluation"""
        print("🎬 SYSTEM PROMPT EVALUATOR FOR MOVIE RECOMMENDATIONS")
        print("=" * 60)
        print("🎯 Testing different SYSTEM prompts with the SAME user inputs")

        all_results = []
        system_prompt_scores = {name: [] for name in self.system_prompts.keys()}

        for i, test_case in enumerate(self.dataset['test_cases'], 1):
            user_prompt = test_case['user_input']
            print(f"\n📝 USER INPUT {i} ({test_case['category']}): {user_prompt}")
            print("-" * 50)

            for j, (system_name, system_prompt) in enumerate(self.system_prompts.items()):
                print(f"\n🔄 Testing system prompt: {system_name.upper()}")

                result = self.test_system_prompt(system_name, system_prompt, user_prompt)
                if result:
                    all_results.append(result)
                    system_prompt_scores[system_name].append(result['quality_score'])

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
        print("📊 FINAL SUMMARY - SYSTEM PROMPT COMPARISON")
        print("=" * 60)

        for system_name, scores in system_prompt_scores.items():
            if scores:
                avg_score = sum(scores) / len(scores)
                success_rate = sum(1 for s in scores if s == 1.0) / len(scores)
                print(f"\n🎯 {system_name.upper()}:")
                print(f"   Average score: {avg_score:.2%}")
                print(f"   Success rate (100%): {success_rate:.2%}")
                print(f"   Test cases: {len(scores)}")

        # Determine best system prompt
        best_system_prompt = max(system_prompt_scores.keys(),
                         key=lambda x: sum(system_prompt_scores[x]) / len(system_prompt_scores[x]) if system_prompt_scores[x] else 0)
        best_score = sum(system_prompt_scores[best_system_prompt]) / len(system_prompt_scores[best_system_prompt]) if system_prompt_scores[best_system_prompt] else 0

        print(f"\n🏆 WINNER: {best_system_prompt.upper()} with {best_score:.2%} average score")

        return best_system_prompt, all_results

    def show_best_system_prompt(self, best_system_prompt_name):
        """Show the best system prompt to use in the challenge"""
        print(f"\n📋 RECOMMENDED SYSTEM PROMPT FOR CHALLENGE: {best_system_prompt_name.upper()}")
        print("=" * 60)
        print(self.system_prompts[best_system_prompt_name])
        print("=" * 60)

    def show_examples(self, results):
        """Show 2 examples of input -> output as required"""
        print(f"\n📋 EXAMPLES OF INPUT → OUTPUT")
        print("=" * 60)

        # Get examples from results
        examples_shown = 0
        for result in results:
            if result['quality_score'] == 1.0 and examples_shown < 2:  # Show perfect examples
                examples_shown += 1
                print(f"\n🎬 EXAMPLE {examples_shown}:")
                print(f"INPUT: {result['user_input']}")
                print(f"OUTPUT:")
                if result['parsed_json']:
                    formatted_json = json.dumps(result['parsed_json'], indent=2, ensure_ascii=False)
                    print(formatted_json)
                print("-" * 40)

        if examples_shown < 2:
            # If we don't have enough perfect examples, show any good ones
            for result in results:
                if result['quality_score'] > 0 and examples_shown < 2:
                    examples_shown += 1
                    print(f"\n🎬 EXAMPLE {examples_shown}:")
                    print(f"INPUT: {result['user_input']}")
                    print(f"OUTPUT:")
                    print(result['raw_output'])
                    print("-" * 40)


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

    # Create output file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"results/evaluation_report_{timestamp}.txt"

    # Capture output to both console and file
    with TeeOutput(output_file):
        best_system_prompt, results = evaluator.run_evaluation()
        evaluator.show_best_system_prompt(best_system_prompt)
        evaluator.show_examples(results)

        print("\n✨ Evaluation completed! Use the winning system prompt for your challenge.")
        print("📋 Remember: This is a SYSTEM prompt - use it in the 'system' role, not 'user' role.")

    print(f"\n💾 Report saved to: {output_file}")


if __name__ == "__main__":
    main()