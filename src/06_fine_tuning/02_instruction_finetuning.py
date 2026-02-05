import os
import sys
from dotenv import load_dotenv

import itertools
import jsonlines

# import pandas as pd
from pprint import pprint
from transformers import AutoTokenizer, AutoModelForCausalLM
from datasets import load_dataset

# Add src directory to Python path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.separator import separator
from llama import BasicModelRunner

load_dotenv()
os.system("clear")

# Load the dataset
print("[+] Loading dataset...")
instruction_tuned_dataset = load_dataset(
    "tatsu-lab/alpaca", split="train", streaming=True
)

m = 5
print("Instruction-tuned dataset:")
top_m = list(itertools.islice(instruction_tuned_dataset, m))
for j in top_m:
    print(j)

print(separator(80))

# 2 PROMPT TEMPLATES
prompt_template_with_input = """Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.

### Instruction:
{instruction}

### Input:
{input}

### Response:"""

prompt_template_without_input = """Below is an instruction that describes a task. Write a response that appropriately completes the request.

### Instruction:
{instruction}

### Response:"""

# HYDRATE PROMPTS (Add data to prompts)
print("[+] Hydrating prompts...")
processed_data = []
for j in top_m:
    if not j["input"]:
        processed_prompt = prompt_template_without_input.format(
            instruction=j["instruction"]
        )
    else:
        processed_prompt = prompt_template_with_input.format(
            instruction=j["instruction"], input=j["input"]
        )

    processed_data.append({"input": processed_prompt, "output": j["output"]})

print("[+] Example of processed data...")
pprint(processed_data[0])

print(separator(80))

# Save the dataset
print("[+] Saving the dataset...")
with jsonlines.open(
    f"{os.path.dirname(__file__)}/data/alpaca_processed.jsonl", "w"
) as writer:
    writer.write_all(processed_data)

print("[+] Dataset saved!")

print(separator(80))
# Compare non-instruction tuned vs instruction tuned models
print("[+] Comparing non-instruction tuned and instruction tuned models...")
dataset_path_hf = "lamini/alpaca"
dataset_hf = load_dataset(dataset_path_hf)
print(dataset_hf)

print(separator(80))
non_instruct_model = BasicModelRunner("meta-llama/Llama-2-7b-hf")
non_instruct_output = non_instruct_model("Tell me how to train my dog to sit")
print("Not instruction-tuned output (Llama 2 Base):", non_instruct_output)

print(separator(80))
instruct_model = BasicModelRunner("meta-llama/Llama-2-7b-chat-hf")
instruct_output = instruct_model("Tell me how to train my dog to sit")
print("Instruction-tuned output (Llama 2): ", instruct_output)

print(separator(80))

# Try Smaller Models
tokenizer = AutoTokenizer.from_pretrained("EleutherAI/pythia-70m")
model = AutoModelForCausalLM.from_pretrained("EleutherAI/pythia-70m")


def inference(text, model, tokenizer, max_input_tokens=1000, max_output_tokens=100):
    # Tokenize
    input_ids = tokenizer.encode(
        text, return_tensors="pt", truncation=True, max_length=max_input_tokens
    )

    # Generate
    device = model.device
    generated_tokens_with_prompt = model.generate(
        input_ids=input_ids.to(device), max_length=max_output_tokens
    )

    # Decode
    generated_text_with_prompt = tokenizer.batch_decode(
        generated_tokens_with_prompt, skip_special_tokens=True
    )

    # Strip the prompt
    generated_text_answer = generated_text_with_prompt[0][len(text) :]

    return generated_text_answer


finetuning_dataset_path = "lamini/lamini_docs"
finetuning_dataset = load_dataset(finetuning_dataset_path)
print(finetuning_dataset)

print(separator(80))

test_sample = finetuning_dataset["test"][0]
print(test_sample)

print(inference(test_sample["question"], model, tokenizer))

print(separator(80))

instruction_model = AutoModelForCausalLM.from_pretrained("lamini/lamini_docs_finetuned")
print(inference(test_sample["question"], instruction_model, tokenizer))

print(separator(80))

###
# Pssst! If you were curious how to upload your own dataset to Huggingface
# Here is how we did it

# !pip install huggingface_hub
# !huggingface-cli login

# import pandas as pd
# import datasets
# from datasets import Dataset

# finetuning_dataset = Dataset.from_pandas(pd.DataFrame(data=finetuning_dataset))
# finetuning_dataset.push_to_hub(dataset_path_hf)
###
