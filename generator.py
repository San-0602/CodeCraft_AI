import cohere
import os


API_KEY = "yHD8B8Zl1AKzAZtLzsdtVjV9PUzNCTaj4iVmdMB7"

co = cohere.Client(API_KEY)

def generate_project(prompt):
    response = co.generate(
        model='command-r-plus',
        prompt=f"""You are an AI that helps students generate computer science projects. 
Generate a full project with:
1. A short title,
2. The source code with comments,
3. A brief project report,
4. 10 viva questions and answers.

Prompt: {prompt}""",
        max_tokens=1500,
        temperature=0.6
    )
    return response.generations[0].text.strip()

# Test it
if __name__ == "__main__":
    user_input = input("Enter your project prompt: ")
    output = generate_project(user_input)
    print("\n--- Generated Project ---\n")
    print(output)
