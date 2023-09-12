from flask import Flask, render_template, request, jsonify
import datetime
import os
import openai
import requests


from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import TextLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.indexes import VectorstoreIndexCreator
from langchain.vectorstores import Chroma

import constants

app = Flask(__name__, static_folder="statics" , template_folder="templates")
os.environ["OPENAI_API_KEY"] = constants.APIKEY
print(constants.APIKEY)
# Enable to cache & reuse the model to disk (for repeated queries on the same data)
PERSIST = False
# responses = {"hi": "Hello!", 
#              "how are you?": "I'm doing well, thank you.", 
#              "what's your name?": "My name is Chatbot."}

messages = []

@app.route("/", methods=["GET", "POST"])
def home():
   
    if request.method == "POST":
        # Get user input from the chat interface
        # user_input = request.form["user_input"]
        prompt = request.form['prompt']

        # print(prompt)
        messages.append({"text": prompt, "class": "user-message", "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
        render_template("index.html", messages=messages)
        # process the prompt and generate the response
        response = generate_response(prompt)
        # Get chatbot response from the responses dictionary
        # response_text = responses.get(user_input.lower(), "Sorry, I didn't understand your message.")
        
        # Append the new conversation pair to the list of messages
        messages.append({"text": response, "class": "bot-message", "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
        
    # Render the updated page with the messages list passed to the template
    return render_template("index.html", messages=messages)

@app.route("/clear", methods=["POST"])
def clear():
    global messages
    messages = []
    return jsonify({"status": "success"})


@app.route("/text2text", methods=["POST"])
def text_to_text():
   
    data = request.get_json(force=True)
    prompt = data['prompt']

    # print(prompt)
    messages.append({"text": prompt, "class": "user-message", "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})

    # process the prompt and generate the response
    response = generate_response(prompt)
 
    # Append the new conversation pair to the list of messages
    messages.append({"text": response, "class": "bot-message", "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
    
    return response

def generate_response(prompt):
    try:
        if PERSIST and os.path.exists("persist"):
            print("Reusing index...\n")
            vectorstore = Chroma(persist_directory="persist", embedding_function=OpenAIEmbeddings(request_timeout=60))
            from langchain.indexes.vectorstore import VectorStoreIndexWrapper
            index = VectorStoreIndexWrapper(vectorstore=vectorstore)
        else:
            loader = TextLoader('data.txt')
            if PERSIST:
                index = VectorstoreIndexCreator(vectorstore_kwargs={"persist_directory":"persist"}).from_loaders([loader])
            else:
                index = VectorstoreIndexCreator().from_loaders([loader])

        chain = RetrievalQA.from_chain_type(
            llm=ChatOpenAI(model="gpt-3.5-turbo"),
            retriever=index.vectorstore.as_retriever(search_kwargs={"k": 1}),
        )

        response = chain.run(prompt)
        return jsonify({"response": response}),200
    
    except Exception as e:
        # Handle the exception here

        return "ChatGPT is currently broken, sorry."

@app.route("/show_token", methods=["GET"])    
def get_token_count():
    # usage = openai.Usage.retrieve()
    # tokens_left = usage['usage']['total_tokens'] - usage['usage']['used_tokens']
    # return tokens_left
    try:
        completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": "Hello world"}])
        print(completion.usage.prompt_tokens)
        print(completion.usage.completion_tokens)
        print(completion.usage.total_tokens)
        return jsonify({"total_tokens": completion.usage.total_tokens})
    except Exception as e:
        return jsonify({"error": str(e)})



if __name__ == "__main__":
    app.run(debug=True)