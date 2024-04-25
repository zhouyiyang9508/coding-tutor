from openai import OpenAI

from flask import Flask, session, request, jsonify, render_template
from flask_session import Session

import os
import json

import random
import string

app = Flask("coding tutor")
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

API_KEY = ""
Assistant_ID = 'asst_wPLldqr2EUWyRLpWD8zqmFVq'
Assistant_ID_Chinese = 'asst_Dy1JjzKpWatNcEWThDYIjHcF'
os.makedirs("flask_session", exist_ok=True)

def get_or_create_thread(session_id, client):
    storage_file_path = 'session_storage.json'
    
    if not os.path.exists(storage_file_path):
        with open(storage_file_path, 'w') as file:
            json.dump({}, file)
    
    with open(storage_file_path, 'r') as file:
        session_storage = json.load(file)
    
    if session_id in session_storage:
        print("session id already in db, retrieve it......")
        return client.beta.threads.retrieve(session_storage[session_id]) 
    else:
        print("first time user, create new thread......")
        thread = client.beta.threads.create()
        session_storage[session_id] = thread.id
        with open(storage_file_path, 'w') as file:
            json.dump(session_storage, file)
        return thread

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/learn')
def learn():
    language = request.args.get('language', 'en')  # Default to English if nothing is selected
    session_id = request.args.get('session', None)
    if session_id:
        print("user want to recover from previous session...... session_id is ", session_id)
        session['user_id'] = session_id
    else:
        print("a new user is coming......")
        session['user_id'] = generate_unique_user_id()
        print("the assigned user_id is ", session['user_id'])
    session['language'] = language
    print("the language is ", language)
    return render_template('learn.html', language=language, session_id=session['user_id'])

def generate_unique_user_id():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

@app.route('/tutor', methods=['POST'])
def tutor():
    data = request.get_json()
    client = OpenAI(api_key=API_KEY)
    question = data['question']
    language = session.get('language')
    if language == 'en':
        assistant = client.beta.assistants.retrieve(Assistant_ID)
    elif language == 'zh':
        assistant = client.beta.assistants.retrieve(Assistant_ID_Chinese)
    if "user_id" not in session:
        session["user_id"] = generate_unique_user_id()
    thread = get_or_create_thread(session['user_id'], client)
    print("the thread_id is ", thread.id)
    message = client.beta.threads.messages.create(
        thread_id = thread.id,
        role = 'user',
        content = question
    )
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id
    )
    while run.status != "completed":
        keep_retrieving_run = client.beta.threads.runs.retrieve(
        thread_id=thread.id,
        run_id=run.id
    )
        if keep_retrieving_run.status == "completed":
            print("\n")
            break
    all_messages = client.beta.threads.messages.list(
        thread_id=thread.id
    )
    print("###################################################### \n")
    print(f"USER: {message.content[0].text.value}")
    print(f"ASSISTANT: {all_messages.data[0].content[0].text.value}")
    
    return jsonify(answer=all_messages.data[0].content[0].text.value)


if __name__ == "__main__":
    instruction = '''
You are a Python3 coding tutor dedicated to helping beginners learn how to code. Your approach should be proactive and structured, tailored for students with little to no prior coding knowledge. Here’s how you should conduct the session:

Initial Assessment:
Start by asking the student up to 3 questions to assess their baseline understanding of coding. Carefully review their responses to gauge their initial knowledge level.
Outline of Today's Session:
After the assessment, provide a clear outline of the topics you intend to cover in today’s session. Each session lasts 30 minutes and should focus on foundational aspects of Python3 coding.
Time Management:
As the session approaches the 30-minute mark, check in with the student to see if they wish to extend the session. Be mindful of their time constraints and offer a break or continuation based on their response.
Progress Tracking:
If the student inquires about their progress, estimate and communicate their learning progress as a percentage. Base your judgement on their understanding and mastery of the session's topics.
Interactive Learning:
Incorporate interactive quizzes throughout the session to reinforce the material and enhance the student’s understanding. These quizzes should be engaging and informative, helping to solidify the concepts discussed.
Language Requirement:
Ensure that all communication, explanations, and instructions are given in English, maintaining consistency and clarity throughout the session.
    '''

    # Create an assistant
    # assistant = client.beta.assistants.create(
    #     name="Coding Tutor-Python3",
    #     instructions=instruction,
    #     tools=[{"type": "code_interpreter"}],
    #     model="gpt-4-turbo-preview"
    # )
    # print(assistant)

    app.run(debug=True)


    # thread = client.beta.threads.create()