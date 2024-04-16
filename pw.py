from random import randint
from langchain_google_genai import ChatGoogleGenerativeAI
import json

topics = ['operating system', 'datastructures', 'java', 'c++']
gemini_key = "AIzaSyDO-1iFi5A0zPE3t7gUvmTwo96v5FIPhqY"

gemini_llm = ChatGoogleGenerativeAI(
        model="gemini-pro",
        google_api_key=gemini_key,
        temperature=0.2,
        convert_system_message_to_human=True,
    )

def chatgpt_api(msg):
    response = gemini_llm.invoke(msg).content
    return response

def ask_question(questions_asked_so_far, time):
    topics_not_asked_so_far = []
    for topic in topics:
        if topic not in questions_asked_so_far:
            topics_not_asked_so_far.append(topic)

    # select random topic
    topic = topics_not_asked_so_far[randint(0, len(topics_not_asked_so_far) - 1)]

    question = chatgpt_api('Generate a question on the topic ' + topic + ' which takes ' + str(time) + ' minutes to answer.')
    return question

def generate_one_dataset():
    dataset_item = []

    num_topics = randint(1, 3)
    # select 1-3 randomly from topics
    topics_to_ask = set()
    while len(topics_to_ask) < num_topics:
        topics_to_ask.add(topics[randint(0, len(topics) - 1)])

    # random interview time
    interview_time = randint(2 * num_topics, 20 * num_topics)

    dataset_item.append({
        'role': 'system',
        'content': 'Candidate is being interviewed for ' + str(interview_time) + ' minutes on ' + ', '.join(topics_to_ask) + '.'
    })
    with open('dataset_item.json', 'w') as f:
        json.dump(dataset_item, f, indent=4)
    
    time_left = interview_time
    questions_asked_so_far = []

    while time_left > 1:

        time_for_next_question = time_left / num_topics
        question = ask_question(questions_asked_so_far, time_for_next_question)
        dataset_item.append({
            'role': 'interviewer',
            'content': question
        })
        with open('dataset_item.json', 'w') as f:
            json.dump(dataset_item, f, indent=4)
        user_answer = chatgpt_api('Generate a response for the question ' + question)
        dataset_item.append({
            'role': 'student',
            'content': user_answer
        })
        with open('dataset_item.json', 'w') as f:
            json.dump(dataset_item, f, indent=4)
        time_taken_by_user = 2 + randint(int(time_for_next_question * 0.8), int(time_for_next_question * 1.2))
        time_left -= time_taken_by_user
        dataset_item.append({
            'role': 'system',
            'content': 'Time taken by user: ' + str(time_taken_by_user) + ' minutes. Time left: ' + str(time_left) + ' minutes.'
        })
        with open('dataset_item.json', 'w') as f:
            json.dump(dataset_item, f, indent=4)

    # collect all question and answers and concatenate it into a string
    conversation = ''
    for i in dataset_item:
        if i['role'] == 'interviewer':
            pass
        else:
            if i['role'] == 'student':
                conversation += 'student: '
            else:
                conversation += 'Interviewer: '
            conversation += i['content'] + '\n'

    return dataset_item


def generate_one_line():
    dataset_item = generate_one_dataset()
    to_dump = {
        'messages': dataset_item
    }
    return to_dump

for i in range(1000):
    try:
        with open('big_dataset.jsonl', 'a') as f:
            json.dump(generate_one_line(), f)
            f.write('\n')
    except Exception as e:
        if 'RECITATION' in str(e):
            print(e)
            print('RECITATION HIT! Retrying...')
            continue
        break
