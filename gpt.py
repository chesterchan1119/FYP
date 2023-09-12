
import openai
APIKEY = "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"
#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
response = openai.Completion.create(
  model="text-davinci-003",
  prompt="Write a tagline for an ice cream shop."
)

def get_GPT_response2():
  openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
          {"role": "system", "content": "You are a helpful assistant."},
          {"role": "user", "content": "Who is the current President of US"}
      ]
  )
  response_message = response["choices"][0]["message"]
  return response_message

def get_GPT_response2():
    prompt = user_name + ": " + user_input + "\n" + bot_name+ ": "

    conversation += prompt  # allows for context

    # fetch response from open AI api
    response = openai.Completion.create(engine='text-davinci-002', prompt=conversation, max_tokens=100)
    response_str = response["choices"][0]["text"].replace("\n", "")
    response_str = response_str.split(user_name + ": ", 1)[0].split(bot_name + ": ", 1)[0]

    conversation += response_str + "\n"
    print(response_str)