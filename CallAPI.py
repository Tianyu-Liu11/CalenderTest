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
        max_token = 3500,
        top_p = 1,
        frequency_penalty = 0.2,
        presence_penalty=0.2,
        timeout = 120
    )
except Exception as e:
  print("Exception happened:", 0)
  return []
response = json.loads(resp['choices'][0])


  
