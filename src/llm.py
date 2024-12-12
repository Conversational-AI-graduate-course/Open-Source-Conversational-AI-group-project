# Function that takes a string and returns a paraphrased random choice using T5 Paws LLM
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline


def LLM_paraphrase(mystring):
    # DEFINING THE TOKENISER AND MODEL
    tokenizer = AutoTokenizer.from_pretrained("Vamsi/T5_Paraphrase_Paws")  
    model = AutoModelForSeq2SeqLM.from_pretrained("Vamsi/T5_Paraphrase_Paws")
    
    # PROMPT
    text =  "Paraphrase: " + mystring + " </s>"
    encoding = tokenizer.encode_plus(text,padding='max_length', return_tensors="pt")
    input_ids, attention_masks = encoding["input_ids"], encoding["attention_mask"]


    outputs = model.generate(
        input_ids=input_ids, attention_mask=attention_masks,
        max_length=256,
        do_sample=True,
        top_k=120,
        top_p=0.91,
        early_stopping=False,
        num_return_sequences=1
    )
    
    line= ""
    for output in outputs:
        line = tokenizer.decode(output, skip_special_tokens=True,clean_up_tokenization_spaces=True)
        
    return line

def LLM_response(input):
    olmo_pipe = pipeline("text-generation", model="allenai/OLMo-1B-hf")
    return olmo_pipe("Question: " + input + " Answer: ")[0]['generated_text'].split("Answer: ")[1].split("Question")[0].strip()