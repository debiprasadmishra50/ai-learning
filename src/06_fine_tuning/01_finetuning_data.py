import os
import sys
from dotenv import load_dotenv

# Add src directory to Python path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import jsonlines
import pandas as pd
from pprint import pprint

from utils.separator import separator  # type: ignore

load_dotenv()
os.system("clear")

# Load the dataset
print("[+] Loading dataset...")
filename = os.path.join(os.path.dirname(__file__), "data", "lamini_docs.jsonl")
instruction_dataset_df = pd.read_json(filename, lines=True)
print(instruction_dataset_df.head(10))

print(separator(80))
print("[+] Convert the DataFrame to a dictionary....")
examples = instruction_dataset_df.to_dict()

print("[+] Combine question and answer from dictionary...")
if "question" in examples and "answer" in examples:
    text = examples["question"][0] + examples["answer"][0]
elif "instruction" in examples and "response" in examples:
    text = examples["instruction"][0] + examples["response"][0]
elif "input" in examples and "output" in examples:
    text = examples["input"][0] + examples["output"][0]
else:
    text = examples["text"][0]

text = examples["question"][0] + examples["answer"][0]
print(text)


print(separator(80))
# PROMPT TEMPLATES
prompt_template_qa = """### Question:
{question}

### Answer:
{answer}"""

question = examples["question"][0]
answer = examples["answer"][0]

text_with_prompt_template = prompt_template_qa.format(question=question, answer=answer)
print("[+] Example Prompt...")
print(text_with_prompt_template)

print(separator(80))
# PROMPT TEMPLATES
prompt_template_q = """### Question:
{question}

### Answer:"""

num_examples = len(examples["question"])
print(f"[+] Number of examples: {num_examples}")
print(separator(80))

finetuning_dataset_text_only = []
finetuning_dataset_question_answer = []
for i in range(num_examples):
    question = examples["question"][i]
    answer = examples["answer"][i]

    text_with_prompt_template_qa = prompt_template_qa.format(
        question=question, answer=answer
    )
    finetuning_dataset_text_only.append({"text": text_with_prompt_template_qa})

    text_with_prompt_template_q = prompt_template_q.format(question=question)
    finetuning_dataset_question_answer.append(
        {"question": text_with_prompt_template_q, "answer": answer}
    )

print("[+] Example of text only dataset...")
pprint(finetuning_dataset_text_only[0])

print(separator(80))
print("[+] Example of Quention Answer Format...")
pprint(finetuning_dataset_question_answer[0])

print(separator(80))

# Save the dataset
print("[+] Saving the dataset...")

with jsonlines.open(
    (
        os.path.join(
            os.path.dirname(__file__), "data", "finetuning_dataset_text_only.jsonl"
        )
    ),
    "w",
) as writer:
    writer.write_all(finetuning_dataset_question_answer)

print("[+] Dataset saved!")

# finetuning_dataset_name = "lamini/lamini_docs"
# finetuning_dataset = load_dataset(finetuning_dataset_name)
# print(finetuning_dataset)
