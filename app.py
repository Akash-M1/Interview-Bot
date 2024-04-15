from langchain_community.vectorstores.neo4j_vector import Neo4jVector
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.chat_models import ChatOllama, ChatOpenAI
from langchain.chains import RetrievalQA
from typing import Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from langchain import hub
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.prompts import ChatPromptTemplate
from langchain_community.embeddings import HuggingFaceEmbeddings
from flask import Flask, jsonify, request
import logging
import sys
import os

app = Flask(__name__, static_folder='static', static_url_path='/static')


def init_llm():

    gemini_key = "AIzaSyDO-1iFi5A0zPE3t7gUvmTwo96v5FIPhqY"

    url = "bolt://localhost:7687"
    # url = "bolt://34.172.124.157:7687"
    username = "neo4j"
    password = "llmneo4j"

    model_name = "sentence-transformers/all-mpnet-base-v2"
    model_kwargs = {'device': 'cpu'}
    encode_kwargs = {'normalize_embeddings': False}
    embeddings = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs
    )
    print("Embedding initialized")

    db = Neo4jVector.from_existing_index(
        index_name="vector",
        embedding=embeddings,
        url=url,
        username=username,
        password=password,
    )

    gemini_llm = ChatGoogleGenerativeAI(
        model="gemini-pro",
        google_api_key=gemini_key,
        temperature=0.2,
        convert_system_message_to_human=True,
    )

    CHAIN_PROMPT = hub.pull("rlm/rag-prompt")

    fine_tuned_llm = RetrievalQA.from_chain_type(
        llm=gemini_llm,
        chain_type="stuff",
        retriever=db.as_retriever(search_kwargs={"k":5}),
        chain_type_kwargs={"prompt": CHAIN_PROMPT},
    )

    return gemini_llm, fine_tuned_llm

def reset_user_performance():

    user_performance = {}
    for i in topics_supported:
        user_performance[i] = []

    return user_performance

def get_answer_quality(question, user_answer, attempt=0):
    prompt = f"""Please evaluate the quality of the user's answer to the following question on a scale of 0 to 10, where 0 means the answer is completely incorrect and 10 means the answer is completely correct:

    Question: What is the output of the following Python code?
    ```python
    print(2 + 2)
    ```
    User's answer: 5
    The quality of this answer is: 0

    Question: What is the purpose of the `print()` function in Python?
    User's answer: The print() function is used to display output in the console.
    The quality of this answer is: 9

    Question: What is the difference between a list and a tuple in Python?
    User's answer: Lists are mutable, while tuples are immutable.
    The quality of this answer is: 8

    Question: What is the time complexity of the `sort()` method in Python?
    User's answer: The time complexity of the sort() method is O(n log n).
    The quality of this answer is: 10

    Question: What is the purpose of the `try-except` block in Python?
    User's answer: The try-except block is used to handle exceptions and errors in Python.
    The quality of this answer is: 10

    Question: {question}
    User's answer: {user_answer}
    The quality of this answer is:"""

    response = gemini_llm.invoke(prompt).content
    logging.info(f"Quality of answer: {response}")
    try:
        quality = int(str(response))
        return quality
    except ValueError:
        if attempt < 3:
            return get_answer_quality(question, user_answer, attempt+1)
        else:
            return 0
        
def generate_question(difficulty, topic):
    prompt = f"""Generate a {difficulty} level question on {topic}"""
    response = fine_tuned_llm.invoke(prompt)
    logging.info(f"Generated question: {response['result']}")
    return response['result']

def get_question(user_performance):
    """
    logic for generating a question based on user performance:

    1. If the user has not answered any questions yet, generate "medium" difficulty for first topic
    2. If the user has answered one "medium" question for a topic, if 
        - the quality of the answer is less than 5, generate an "easy" question
        - the quality of the answer is greater than 5, generate a "hard" question
    3. If the user has answered two questions for a topic, move onto the next topic
    """

    for topic in user_performance:
        if len(user_performance[topic]) == 0:
            return { 'question': generate_question('medium', topic), 'topic': topic, 'difficulty': 'medium' }
        
        if len(user_performance[topic]) == 1:
            if user_performance[topic][0]['quality'] < 5:
                return { 'question': generate_question('easy', topic), 'topic': topic, 'difficulty': 'easy' }
            else:
                return { 'question': generate_question('hard', topic), 'topic': topic, 'difficulty': 'hard' }
        
        if len(user_performance[topic]) == 2:
            continue

def get_summary(user_performance):
    summary = "Summary of your performance:\n\n"
    for topic in user_performance:
        summary += f"Topic: {topic}\n"
        for i in user_performance[topic]:
            summary += f"Difficulty: {i['difficulty']}, Quality: {i['quality']}\n"
        summary += "\n"
    return summary

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/converse', methods=['POST'])
def converse():
    global user_performance, previously_asked_question
    json_data = request.json
    
    if json_data is None:
        return jsonify({"error": "No JSON data received", "status": "error"}), 400
    
    if 'is_first_message' in json_data and json_data['is_first_message'] == True:
        user_performance = reset_user_performance()

        question = get_question(user_performance)
        previously_asked_question = question

        return jsonify({"response": question['question'], "status": "success"})
    
    elif 'user_response' in json_data:
        user_response = json_data['user_response']
        
        if previously_asked_question is None:
            return jsonify({"error": "No question was asked", "status": "error"}), 400
        
        quality = get_answer_quality(previously_asked_question['question'], user_response)
        user_performance[previously_asked_question['topic']].append({"difficulty": previously_asked_question['difficulty'], "quality": quality})
        logging.info(f"User performance: {user_performance}")

        questions_asked = sum([len(user_performance[i]) for i in user_performance])
        if questions_asked >= number_of_questions:
            summary = get_summary(user_performance)
            previously_asked_question = None
            return jsonify({"response": summary, "status": "success"})

        question = get_question(user_performance)
        previously_asked_question = question

        return jsonify({"response": question['question'], "status": "success"})
    
    else:
        return jsonify({"error": "Invalid JSON format", "status": "error"}), 400


topics_supported = ['concepts related to operating systems', "object oriented programming"]
gemini_llm, fine_tuned_llm = init_llm()
user_performance = {}
previously_asked_question = {}
number_of_questions = 4

if __name__ == '__main__':

    # set up logging
    if len(sys.argv) > 1:
        log_file_path = sys.argv[1]
    else:
        log_file_path = os.path.join(os.getcwd(), 'logs.txt')
    logging.basicConfig(
        filename=log_file_path,
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    logging.info('Beginning Server...')
    app.run(host='0.0.0.0', port=3000)