#!/usr/bin/env python3
"""
Movie Recommendation Prompt Evaluator
Uses OpenAI API directly for comprehensive prompt testing and analysis
"""

import json
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from utils.tee_output import TeeOutput

# Load environment variables BEFORE importing evals
load_dotenv()

# Model configuration constants - Adjust based on your OpenAI plan
GENERATION_MODEL = "gpt-4.1-nano"  
JUDGE_MODEL = "gpt-4.1-nano" 

# Rate limiting configuration
REQUEST_DELAY = 0.5  # seconds between requests (increase if hitting rate limits)
MAX_RETRIES = 5       # maximum retry attempts for failed requests


class LLMJudgeEval:
    """
    LLM-as-Judge evaluator using OpenAI API directly.
    Uses one model to generate movie recommendations and another model to judge them.
    """

    def __init__(self):
        self.system_prompts = self.load_system_prompts()
        self.judge_prompt = self.load_judge_prompt()
        self.dataset = self.load_dataset()
        # Load analysis prompts
        self.judge_system_prompt = self.load_judge_system_prompt()
        self.analysis_prompt_template = self.load_analysis_prompt_template()
        self.analysis_system_prompt = self.load_analysis_system_prompt()
        self.comparison_prompt_template = self.load_comparison_prompt_template()
        self.comparison_system_prompt = self.load_comparison_system_prompt()


    def load_judge_prompt(self):
        """Load judge prompt from file"""
        judge_prompt_path = Path(__file__).parent / "prompt_evaluator" / "judge_prompts" / "movie_critic_judge.txt"
        with open(judge_prompt_path, 'r', encoding='utf-8') as f:
            return f.read().strip()


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

    def load_judge_system_prompt(self):
        """Load judge system prompt from file"""
        prompt_path = Path(__file__).parent / "prompt_evaluator" / "analysis_prompts" / "judge_system.txt"
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read().strip()

    def load_analysis_prompt_template(self):
        """Load analysis prompt template from file"""
        prompt_path = Path(__file__).parent / "prompt_evaluator" / "analysis_prompts" / "analysis_prompt.txt"
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read().strip()

    def load_analysis_system_prompt(self):
        """Load analysis system prompt from file"""
        prompt_path = Path(__file__).parent / "prompt_evaluator" / "analysis_prompts" / "analysis_system.txt"
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read().strip()

    def load_comparison_prompt_template(self):
        """Load comparison prompt template from file"""
        prompt_path = Path(__file__).parent / "prompt_evaluator" / "analysis_prompts" / "comparison_prompt.txt"
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read().strip()

    def load_comparison_system_prompt(self):
        """Load comparison system prompt from file"""
        prompt_path = Path(__file__).parent / "prompt_evaluator" / "analysis_prompts" / "comparison_system.txt"
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read().strip()

    def run(self):
        """Run LLM-as-Judge evaluation"""
        print("🤖 LLM-AS-JUDGE EVALUATION")
        print("=" * 70)
        print("🎯 Using one model to generate recommendations, another to judge quality")
        print()

        system_prompt_scores = {name: [] for name in self.system_prompts.keys()}

        # Initialize metrics tracking
        prompt_metrics = {}

        for system_name, system_prompt in self.system_prompts.items():
            prompt_metrics[system_name] = {
                'scores': [],
                'response_times': [],
                'prompt_tokens': len(system_prompt.split()) * 1.3,  # Rough token estimation
                'total_tokens': 0,
                'total_time': 0.0
            }

        for i, test_case in enumerate(self.dataset['test_cases'], 1):
            user_input = test_case['user_input']
            print(f"\n📝 USER INPUT {i}: {user_input}")
            print("-" * 60)

            for system_name, system_prompt in self.system_prompts.items():
                # Add configurable delay between requests to avoid rate limits
                import time
                time.sleep(REQUEST_DELAY)
                print(f"\n🔄 System prompt: {system_name.upper()}")

                # Generate response using OpenAI API directly (like in PromptEval)
                from openai import OpenAI
                import time
                client = OpenAI()

                # Measure response time
                start_time = time.time()

                response = client.chat.completions.create(
                    model=GENERATION_MODEL,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_input},
                    ],
                    temperature=0.7,
                    max_tokens=500,
                )

                end_time = time.time()
                response_time = end_time - start_time
                model_output = response.choices[0].message.content

                # Track metrics
                prompt_metrics[system_name]['response_times'].append(response_time)
                prompt_metrics[system_name]['total_time'] += response_time
                if hasattr(response, 'usage') and response.usage:
                    prompt_metrics[system_name]['total_tokens'] += response.usage.total_tokens

                # Judge the response using the judge model
                judge_score, judge_reasoning = self.evaluate_with_judge(user_input, model_output)

                print(f"  📄 Generated response: {model_output}")
                print(f"  ⏱️  Response time: {response_time:.2f}s")
                print(f"  🤖 Judge evaluation: {judge_score:.2f}")
                print(f"  📝 Detailed reasoning: {judge_reasoning}")
                print("-" * 80)

                prompt_metrics[system_name]['scores'].append(judge_score)

        # Show final results and get winner information
        result = self.show_final_results(system_prompt_scores, prompt_metrics)

        # If show_final_results returned early (no valid results), return a default result
        if result is None:
            return {"best_system": None, "best_score": 0.0,
                    "avg_response_time": 0.0, "prompt_tokens": 0}

        # Return the winner information from show_final_results
        return result

    def evaluate_with_judge(self, user_input, model_output):
        """Use LLM as judge to evaluate the generated response with rate limit handling"""
        judge_prompt = self.judge_prompt.format(user_input=user_input, model_output=model_output)

        import time
        import re
        from openai import OpenAI, RateLimitError

        max_retries = MAX_RETRIES
        base_delay = 1  # seconds

        for attempt in range(max_retries):
            try:
                client = OpenAI()

                judge_response = client.chat.completions.create(
                    model=JUDGE_MODEL,
                    messages=[
                        {"role": "system", "content": self.judge_system_prompt},
                        {"role": "user", "content": judge_prompt}
                    ],
                    temperature=0.0,  # Zero temperature for maximum consistency in judging
                    max_tokens=500,   # Need more tokens for detailed reasoning
                )
                judge_text = judge_response.choices[0].message.content.strip()

                # Extract score and reasoning from response
                # Look for "Score: X.XX" pattern first
                score_pattern = r'Score:\s*(\d+\.?\d*)'
                score_match = re.search(score_pattern, judge_text, re.IGNORECASE)

                if score_match:
                    score = float(score_match.group(1))
                    score = max(0.0, min(1.0, score))  # Clamp to 0-1 range

                    # Extract reasoning (everything after "Score: X.XX")
                    score_end_pos = judge_text.find(score_match.group(0)) + len(score_match.group(0))
                    reasoning = judge_text[score_end_pos:].strip()
                    if reasoning.startswith('.') or reasoning.startswith(',') or reasoning.startswith(':'):
                        reasoning = reasoning[1:].strip()

                    return score, reasoning if reasoning else "No detailed reasoning provided"
                else:
                    # Fallback: look for any number if "Score:" pattern not found
                    score_match = re.search(r'(\d+\.?\d*)', judge_text)
                    if score_match:
                        score = float(score_match.group(1))
                        score = max(0.0, min(1.0, score))
                        reasoning = "Score extracted but no detailed reasoning provided in expected format"
                        return score, reasoning
                    else:
                        print(f"  ⚠️ Could not parse judge score: {judge_text}")
                        return 0.5, "Failed to parse score from judge response"

            except RateLimitError as e:
                if "insufficient_quota" in str(e).lower():
                    print(f"  ❌ Quota exceeded. Please upgrade your OpenAI plan at https://platform.openai.com/account/billing")
                    return 0.3, f"OpenAI quota exceeded: {str(e)}"

                # Extract wait time from error message if available
                wait_time = 20  # default
                if "try again in" in str(e).lower():
                    import re
                    time_match = re.search(r'try again in (\d+)', str(e).lower())
                    if time_match:
                        wait_time = int(time_match.group(1))

                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt) + wait_time  # exponential backoff + suggested wait
                    print(f"  ⏳ Rate limit hit (attempt {attempt + 1}/{max_retries}). Waiting {delay}s...")
                    time.sleep(delay)
                    continue
                else:
                    print(f"  ❌ Max retries exceeded for rate limit: {e}")
                    return 0.4, f"Rate limit exceeded after {max_retries} attempts: {str(e)}"

            except Exception as e:
                error_msg = str(e)
                if "connection" in error_msg.lower() or "timeout" in error_msg.lower():
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)
                        print(f"  🔄 Connection error (attempt {attempt + 1}/{max_retries}). Retrying in {delay}s...")
                        time.sleep(delay)
                        continue

                print(f"  ⚠️ Judge evaluation failed: {e}")
                return 0.5, f"Evaluation error: {error_msg}"

    def show_final_results(self, system_prompt_scores, prompt_metrics):
        """Show final comparison results with comprehensive analysis including performance metrics"""
        print("\n" + "=" * 120)
        print("🏆 COMPREHENSIVE EVALUATION RESULTS - LLM-AS-JUDGE ANALYSIS WITH PERFORMANCE METRICS")
        print("=" * 120)

        # Load test cases info
        test_cases = self.dataset['test_cases']

        # Calculate comprehensive stats including performance metrics
        prompt_stats = {}
        for system_name, scores in system_prompt_scores.items():
            # Skip system prompts with no scores to avoid division by zero
            if not scores:
                print(f"⚠️ Skipping {system_name} - no evaluation scores collected")
                continue

            avg_score = sum(scores) / len(scores)
            metrics = prompt_metrics[system_name]
            avg_response_time = sum(metrics['response_times']) / len(metrics['response_times']) if metrics['response_times'] else 0
            efficiency_score = avg_score / (1 + avg_response_time + metrics['prompt_tokens']/1000)  # Combined score

            prompt_stats[system_name] = {
                'avg_score': avg_score,
                'scores': scores,
                'avg_response_time': avg_response_time,
                'prompt_tokens': metrics['prompt_tokens'],
                'total_tokens': metrics['total_tokens'],
                'efficiency_score': efficiency_score,
                'prompt_text': self.system_prompts[system_name]
            }

        # Check if we have any valid results to analyze
        if not prompt_stats:
            print("\n❌ ERROR: No system prompts had successful evaluations. Cannot determine winner.")
            print("This might be due to API errors, rate limiting, or other issues during evaluation.")
            return None

        # Determine winner considering both quality and efficiency
        # First priority: highest average score
        # Second priority: lowest response time (when scores are close)
        # Third priority: lowest prompt token count (when scores and times are close)
        winner = max(prompt_stats.keys(), key=lambda x: (
            prompt_stats[x]['avg_score'],  # Primary: quality score
            -prompt_stats[x]['avg_response_time'],  # Secondary: speed (negative for maximization)
            -prompt_stats[x]['prompt_tokens']  # Tertiary: token efficiency (negative for maximization)
        ))
        winner_stats = prompt_stats[winner]

        # Header
        print(f"\n🎯 TEST CASES EVALUATED: {len(test_cases)}")
        for i, tc in enumerate(test_cases, 1):
            print(f"   {i}. {tc['category'].replace('_', ' ').title()}: \"{tc['user_input']}\"")

        print(f"\n🏆 WINNER: {winner.upper()} (Score: {winner_stats['avg_score']:.3f}, Time: {winner_stats['avg_response_time']:.2f}s, Tokens: {winner_stats['prompt_tokens']:.0f})")

        # Detailed results table with performance metrics
        print(f"\n{'─' * 140}")
        print("📊 COMPREHENSIVE RESULTS BY SYSTEM PROMPT")
        print(f"{'─' * 140}")
        header = "<12"
        print(f"{'Prompt':<12} {'Avg Score':<10} {'Avg Time':<9} {'PromptTok':<10} {'Efficiency':<11} {'Individual Scores':<25}")
        print(f"{'─' * 140}")

        for system_name in sorted(prompt_stats.keys(), key=lambda x: prompt_stats[x]['avg_score'], reverse=True):
            stats = prompt_stats[system_name]
            scores_str = ', '.join([f'{s:.2f}' for s in stats['scores']])
            marker = "🏆" if system_name == winner else "  "
            print(f"{marker} {system_name:<10} {stats['avg_score']:<10.3f} {stats['avg_response_time']:<9.2f} {stats['prompt_tokens']:<10.0f} {stats['efficiency_score']:<11.3f} {scores_str:<25}")

        print(f"{'─' * 140}")

        # Performance insights
        print("\n💡 PERFORMANCE INSIGHTS:")
        print(f"   • Fastest response: {min(prompt_stats.keys(), key=lambda x: prompt_stats[x]['avg_response_time']).upper()} ({min([stats['avg_response_time'] for stats in prompt_stats.values()]):.2f}s)")
        print(f"   • Most token-efficient: {min(prompt_stats.keys(), key=lambda x: prompt_stats[x]['prompt_tokens']).upper()} ({min([stats['prompt_tokens'] for stats in prompt_stats.values()]):.0f} tokens)")
        print(f"   • Highest efficiency score: {max(prompt_stats.keys(), key=lambda x: prompt_stats[x]['efficiency_score']).upper()} ({max([stats['efficiency_score'] for stats in prompt_stats.values()]):.3f})")

        # LLM Analysis of winner prompt
        print(f"\n🤖 LLM ANALYSIS OF WINNING PROMPT: {winner.upper()}")
        print(f"{'─' * 60}")

        winner_analysis = self.analyze_prompt_with_llm(winner, winner_stats['prompt_text'])
        print(winner_analysis)

        # Compare with other prompts
        print(f"\n⚖️  COMPARISON WITH OTHER PROMPTS:")
        print(f"{'─' * 60}")

        for system_name in sorted(prompt_stats.keys()):
            if system_name != winner:
                stats = prompt_stats[system_name]
                comparison = self.compare_prompts_with_llm(
                    winner, winner_stats['prompt_text'],
                    system_name, stats['prompt_text'],
                    winner_stats['avg_score'], stats['avg_score']
                )
                print(f"\n🎯 {winner.upper()} vs {system_name.upper()}:")
                print(f"   Score difference: {winner_stats['avg_score'] - stats['avg_score']:+.3f}")
                print(f"   {comparison}")

        print(f"\n{'=' * 100}")
        print("✨ EVALUATION COMPLETE - LLM-AS-JUDGE ANALYSIS PROVIDES DEEP INSIGHTS")
        print(f"{'=' * 100}")

        # Return winner information for the calling method
        return {
            "best_system": winner,
            "best_score": winner_stats['avg_score'],
            "avg_response_time": winner_stats['avg_response_time'],
            "prompt_tokens": winner_stats['prompt_tokens']
        }

    def analyze_prompt_with_llm(self, prompt_name, prompt_text):
        """Use LLM to analyze why a system prompt works well"""
        analysis_prompt = self.analysis_prompt_template.format(prompt_text=prompt_text)

        try:
            from openai import OpenAI
            client = OpenAI()

            response = client.chat.completions.create(
                model=JUDGE_MODEL,
                messages=[
                    {"role": "system", "content": self.analysis_system_prompt},
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.1,
                max_tokens=400,
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            return f"LLM analysis failed: {str(e)}. Prompt name: {prompt_name}"

    def compare_prompts_with_llm(self, winner_name, winner_prompt, loser_name, loser_prompt, winner_score, loser_score):
        """Use LLM to compare two system prompts"""
        comparison_prompt = self.comparison_prompt_template.format(
            winner_name=winner_name,
            winner_score=winner_score,
            winner_prompt=winner_prompt,
            loser_name=loser_name,
            loser_score=loser_score,
            loser_prompt=loser_prompt
        )

        try:
            from openai import OpenAI
            client = OpenAI()

            response = client.chat.completions.create(
                model=JUDGE_MODEL,
                messages=[
                    {"role": "system", "content": self.comparison_system_prompt},
                    {"role": "user", "content": comparison_prompt}
                ],
                temperature=0.1,
                max_tokens=200,
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            return f"Comparison failed: {str(e)}"


class PromptEval:
    """Custom evaluator using OpenAI API directly"""

    def __init__(self):
        self.system_prompts = self.load_system_prompts()
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

    def eval_sample(self, sample):
        """Evaluate a single sample using evals framework"""
        user_input = sample["input"]
        expected = sample.get("ideal", "")

        results = {}

        # Test each system prompt
        for system_name, system_prompt in self.system_prompts.items():
            # Use OpenAI client directly instead of evals completion function
            from openai import OpenAI
            client = OpenAI()

            # Get response
            response = client.chat.completions.create(
                model=GENERATION_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                max_tokens=500,
                temperature=0.7
            )

            output = response.choices[0].message.content

            # Evaluate the response
            evaluation = self.evaluate_response(output, expected, user_input)
            results[system_name] = evaluation

            # Print response for debugging/verification
            print(f"  📄 Response: {output}")
            print(f"  📊 Metrics: JSON={evaluation['is_valid_json']}, Items={evaluation['has_expected_items']}, Fields={evaluation['has_required_fields']}, Score={evaluation['quality_score']:.2f}")

        return results

    def _validate_response_structure(self, parsed):
        """Validate the structure of the parsed response"""
        items = parsed.get('items', parsed.get('recommendations', parsed.get('results', parsed.get('movies', []))))
        if not items:
            return False

        # Check if items have basic structure - at least one item should have meaningful fields
        required_fields = ['title', 'name', 'item', 'text', 'content']
        for item in items:
            if isinstance(item, dict) and any(field in item for field in required_fields):
                return True
        return False

    def _display_response_items(self, parsed_json):
        """Display the response items in a generic way"""
        items = parsed_json.get('items', parsed_json.get('recommendations', parsed_json.get('results', parsed_json.get('movies', []))))
        if items:
            print("📋 Response items:")
            for k, item in enumerate(items[:3], 1):
                if isinstance(item, dict):
                    title = item.get('title', item.get('name', item.get('item', f'Item {k}')))
                    description = item.get('reason', item.get('description', item.get('text', 'N/A')))
                    print(f"  {k}. {title}")
                    print(f"     Details: {description}")
                else:
                    print(f"  {k}. {item}")

    def evaluate_response(self, output, expected, user_input):
        """Evaluate a single response - same logic as original evaluator"""
        try:
            # Clean the result
            cleaned_result = output.strip()
            if cleaned_result.startswith('```json'):
                cleaned_result = cleaned_result.replace('```json', '').replace('```', '').strip()
            elif cleaned_result.startswith('```'):
                cleaned_result = cleaned_result.replace('```', '').strip()

            parsed = json.loads(cleaned_result)
            is_valid_json = True
            # Generic evaluation - look for any field containing a list of recommendations
            items = parsed.get('items', parsed.get('recommendations', parsed.get('results', parsed.get('movies', []))))
            has_expected_items = len(items) >= 3
            has_required_fields = self._validate_response_structure(parsed)
            quality_score = (is_valid_json + has_expected_items + has_required_fields) / 3

            return {
                'raw_output': output,
                'parsed_json': parsed,
                'is_valid_json': is_valid_json,
                'has_expected_items': has_expected_items,
                'has_required_fields': has_required_fields,
                'quality_score': quality_score,
                'user_input': user_input
            }

        except json.JSONDecodeError:
            return {
                'raw_output': output,
                'parsed_json': None,
                'is_valid_json': False,
                'has_expected_items': False,
                'has_required_fields': False,
                'quality_score': 0,
                'user_input': user_input
            }

    def run(self):
        """Run the evaluation using evals framework"""
        all_results = []
        system_prompt_scores = {name: [] for name in self.system_prompts.keys()}

        print("🎯 PROMPT EVALUATOR (Using OpenAI Evals)")
        print("=" * 70)
        print("🎯 Testing different SYSTEM prompts with evals framework")

        for i, test_case in enumerate(self.dataset['test_cases'], 1):
            sample = {"input": test_case['user_input'], "ideal": ""}

            print(f"\n📝 USER INPUT {i} ({test_case['category']}): {test_case['user_input']}")
            print("-" * 50)

            # Evaluate this sample
            results = self.eval_sample(sample)

            for system_name, result in results.items():
                print(f"\n🔄 System prompt: {system_name.upper()}")
                print(f"✅ Valid JSON: {'Yes' if result['is_valid_json'] else 'No'}")
                print(f"✅ Expected items: {'Yes' if result['has_expected_items'] else 'No'}")
                print(f"✅ Complete fields: {'Yes' if result['has_required_fields'] else 'No'}")
                print(f"📊 Score: {result['quality_score']:.2%}")

                if result['parsed_json'] and result['quality_score'] > 0:
                    self._display_response_items(result['parsed_json'])

                all_results.append(result)
                system_prompt_scores[system_name].append(result['quality_score'])

        # Final summary
        self.show_summary(system_prompt_scores)
        best_system_prompt = self.get_best_prompt(system_prompt_scores)
        self.show_best_system_prompt(best_system_prompt)
        self.show_examples(all_results)

        return {"best_system_prompt": best_system_prompt}

    def show_summary(self, system_prompt_scores):
        """Show final summary"""
        print("\n" + "=" * 60)
        print("📊 FINAL SUMMARY - SYSTEM PROMPT COMPARISON (with evals)")
        print("=" * 60)

        for system_name, scores in system_prompt_scores.items():
            if scores:
                avg_score = sum(scores) / len(scores)
                success_rate = sum(1 for s in scores if s >= 0.99) / len(scores)  # Avoid float equality
                print(f"\n🎯 {system_name.upper()}:")
                print(f"   Average score: {avg_score:.2%}")
                print(f"   Success rate (≥99%): {success_rate:.2%}")
                print(f"   Test cases: {len(scores)}")

    def get_best_prompt(self, system_prompt_scores):
        """Determine best system prompt"""
        best_system_prompt = max(system_prompt_scores.keys(),
                         key=lambda x: sum(system_prompt_scores[x]) / len(system_prompt_scores[x]) if system_prompt_scores[x] else 0)
        best_score = sum(system_prompt_scores[best_system_prompt]) / len(system_prompt_scores[best_system_prompt]) if system_prompt_scores[best_system_prompt] else 0

        print(f"\n🏆 WINNER: {best_system_prompt.upper()} with {best_score:.2%} average score")
        return best_system_prompt

    def show_best_system_prompt(self, best_system_prompt_name):
        """Show the best system prompt"""
        print(f"\n📋 RECOMMENDED SYSTEM PROMPT FOR CHALLENGE: {best_system_prompt_name.upper()}")
        print("=" * 60)
        print(self.system_prompts[best_system_prompt_name])
        print("=" * 60)

    def show_examples(self, results):
        """Show 2 examples of input -> output"""
        print(f"\n📋 EXAMPLES OF INPUT → OUTPUT")
        print("=" * 60)

        examples_shown = 0
        for result in results:
            if result['quality_score'] >= 0.99 and examples_shown < 2:  # Avoid float equality
                examples_shown += 1
                print(f"\n📝 EXAMPLE {examples_shown}:")
                print(f"INPUT: {result['user_input']}")
                print(f"OUTPUT:")
                if result['parsed_json']:
                    formatted_json = json.dumps(result['parsed_json'], indent=2, ensure_ascii=False)
                    print(formatted_json)
                print("-" * 40)

        if examples_shown < 2:
            for result in results:
                if result['quality_score'] > 0 and examples_shown < 2:
                    examples_shown += 1
                    print(f"\n📝 EXAMPLE {examples_shown}:")
                    print(f"INPUT: {result['user_input']}")
                    print(f"OUTPUT:")
                    print(result['raw_output'])
                    print("-" * 40)




def main():
    """Main function - runs evaluation with OpenAI API"""
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Error: OPENAI_API_KEY not found in .env file")
        return


    # Choose evaluation type
    import sys
    eval_type = sys.argv[1] if len(sys.argv) > 1 else "heuristic"

    if eval_type not in ["heuristic", "llm-judge"]:
        print("❌ Invalid evaluation type. Use: 'heuristic' or 'llm-judge'")
        return

    # Create output file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"results/evaluation_report_{eval_type}_{timestamp}.txt"

    with TeeOutput(output_file):
        if eval_type == "heuristic":
            print("🚀 Using HEURISTIC evaluation with OpenAI API")
            print("🎯 Evaluation criteria: JSON validity, item count, field completeness")
            print()

            # Initialize and run heuristic evaluation
            evaluator = PromptEval()
            evaluator.run()

        elif eval_type == "llm-judge":
            print("🤖 Using LLM-AS-JUDGE evaluation with OpenAI API")
            print("🎯 One model generates recommendations, another model judges quality")
            print()

            # Initialize and run LLM-judge evaluation
            evaluator = LLMJudgeEval()
            evaluator.run()

        print(f"\n✨ {eval_type.upper()} evaluation completed with OpenAI API!")

    print(f"\n💾 Report saved to: {output_file}")
    print("\n💡 Usage:")
    print("   python movie_evaluator_with_evals.py heuristic  # Rule-based evaluation")
    print("   python movie_evaluator_with_evals.py llm-judge  # LLM-as-judge evaluation")


if __name__ == "__main__":
    main()