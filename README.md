# 🎬 Movie Recommendation Prompt Evaluator

A **super simple** tool to find the best prompt for recommending movies. Perfect for junior-level AI challenges.

## ⚡ Quick Setup

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure API Key
cp .env.example .env
# Edit .env and add your OpenAI API key

# 4. Run
python movie_evaluator.py
```

## 🎯 What it does?

The script tests **3 different versions** of movie recommendation prompts:

1. **Basic** - Simple and direct prompt
2. **Detailed** - With more specific instructions
3. **Contextual** - With personality and context

For each version it tests **4 different cases**:

- 90s romantic comedies
- Sci-fi and psychological thrillers
- Superhero action movies
- Award-winning historical dramas

## 📊 Automatic Evaluation

Each response is evaluated by:

- ✅ **Valid JSON** - Is the response correct JSON?
- ✅ **3 movies** - Does it return exactly 3 movies?
- ✅ **Complete fields** - Does it have title, genre, and reason?

**Score**: 0% to 100% (average of the 3 criteria)

## 🏆 Result

At the end it tells you:

- Which prompt worked best
- Statistics for each one
- The winning prompt ready to use in your challenge

## 💡 Example Output

```
🎬 MOVIE RECOMMENDATION PROMPT EVALUATOR
============================================================

📝 TEST CASE 1: I like romantic comedies and 90s movies
--------------------------------------------------

🔄 Testing prompt: BASIC
✅ Valid JSON: Yes
✅ 3 movies: Yes
✅ Complete fields: Yes
📊 Score: 100%

🎭 Recommended movies:
  1. You've Got Mail (Romantic Comedy)
     Reason: Classic 90s romantic comedy with Meg Ryan
  2. Sleepless in Seattle (Romantic Comedy)
     Reason: Perfect romantic movie from the decade you like
  3. Pretty Woman (Romantic Comedy)
     Reason: Iconic romantic comedy with Julia Roberts

============================================================
📊 FINAL SUMMARY - PROMPT COMPARISON
============================================================

🎯 BASIC:
   Average score: 85%
   Success rate (100%): 75%
   Test cases: 4

🎯 DETAILED:
   Average score: 95%
   Success rate (100%): 100%
   Test cases: 4

🎯 CONTEXTUAL:
   Average score: 80%
   Success rate (100%): 50%
   Test cases: 4

🏆 WINNER: DETAILED with 95% average score

📋 RECOMMENDED PROMPT FOR CHALLENGE: DETAILED
============================================================
You are a cinema expert who recommends personalized movies.

INSTRUCTIONS:
1. Analyze user preferences
2. Recommend exactly 3 different movies
3. Respond ONLY in valid JSON format

RESPONSE FORMAT (copy exactly):
{
  "movies": [
    {"title": "Movie Name", "genre": "Main Genre", "reason": "Specific recommendation reason"},
    {"title": "Movie Name", "genre": "Main Genre", "reason": "Specific recommendation reason"},
    {"title": "Movie Name", "genre": "Main Genre", "reason": "Specific recommendation reason"}
  ]
}

User preferences: USER_PREFERENCES_HERE
============================================================

✨ Evaluation completed! Use the winning prompt for your challenge.
```

## 🔥 Solution Advantages

- **Super simple**: Just 1 Python file
- **Automatic evaluation**: No need to manually review
- **Junior level**: Easy-to-understand code
- **Focused**: Specific for movie challenge
- **Fast**: Runs in under 1 minute
- **Uses gpt-4o-mini**: Latest OpenAI model

## 🚀 For Your Challenge

1. Run the script
2. Copy the winning prompt
3. Use it to create your .md file for the challenge
4. You have the best version scientifically proven!

---

**Why is this solution better?**

- ✅ Simple to use and understand
- ✅ Objectively evaluates which prompt works best
- ✅ Gives you the result ready to use
- ✅ Perfect for junior level
- ✅ Focused on the specific problem
