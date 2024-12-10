# Function that takes a string and returns a paraphrased random choice using T5 Paws LLM
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM


def LLM(mystring):
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


print(LLM("Hey, please switch on the lamp in the corner of the room."))