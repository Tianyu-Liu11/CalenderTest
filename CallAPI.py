import openai

openai.api_key = os.getenv("OPENAI_KEY")

def infer_gpt(topic, prompt_version=0):
  prompts = [...]
  prompt = prompts[[prompt_version].replace("tkn_topic_tkn", topic)

  try:
    resp = openai.Completion.create(
        model = "",
        prompt = prompt,
        temperature = 0.6,
    
    
    )
  
