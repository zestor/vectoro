from transformers import AutoTokenizer, AutoModelForCausalLM

tokenizer = AutoTokenizer.from_pretrained("EleutherAI/gpt-j-6B")

tokenizer.pad_token = tokenizer.eos_token
tokenizer.pad_token_id = tokenizer.eos_token_id

from peft import PeftModel
from transformers import AutoTokenizer, GPTJForCausalLM, GenerationConfig

model = GPTJForCausalLM.from_pretrained(
    "EleutherAI/gpt-j-6B",
    load_in_8bit=True,
    device_map="auto",
)
model = PeftModel.from_pretrained(model, "samwit/dolly-lora")

def dolly_generate(text):
    inputs = tokenizer(
        PROMPT,
        return_tensors="pt",
    )
    input_ids = inputs["input_ids"].cuda()

    generation_config = GenerationConfig(
        temperature=0.6,
        top_p=0.95,
        repetition_penalty=1.2,
    )

    print("Generating...")
    generation_output = model.generate(
        input_ids=input_ids,
        generation_config=generation_config,
        return_dict_in_generate=True,
        output_scores=True,
        max_new_tokens=128,
        pad_token_id = 0,
        eos_token_id = 50256
    )

    for s in generation_output.sequences:
        print(tokenizer.decode(s))

PROMPT = """Below is an instruction that describes a task. Write a response that appropriately completes the request.
### Instruction:
What are the differences between alpacas and sheep?
### Response:"""

dolly_generate(PROMPT)

PROMPT = """Below is an instruction that describes a task. Write a response that appropriately completes the request.
### Instruction:
Write me a python function that checks if a number is prime.
### Response:"""

dolly_generate(PROMPT)

PROMPT = """Below is an instruction that describes a task. Write a response that appropriately completes the request.
### Instruction:
Write an email explaining why GPT-4 should be open source.
### Response:"""

dolly_generate(PROMPT)