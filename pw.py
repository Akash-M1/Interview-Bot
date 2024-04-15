from random import randint

topics = ['os', 'ds', 'java', 'c++']

def chatgpt_api(msg):
    # call chatgpt api
    return 'this is the response from chatgpt api'

def ask_question(questions_asked_so_far, time):
    topics_not_asked_so_far = []
    for topic in topics:
        if topic not in questions_asked_so_far:
            topics_not_asked_so_far.append(topic)

    if not topics_not_asked_so_far:
        # generate bonus questions based on topics the user did not perform well in
        pass

    # select random topic
    topic = topics_not_asked_so_far[randint(0, len(topics_not_asked_so_far) - 1)]

    question = chatgpt_api('Generate a question on the topic ' + topic + ' which takes ' + str(time) + ' minutes to answer.')
    return question

def generate_one_dataset():
    dataset_item = []

    # random interview time
    interview_time = randint(30, 120)

    # select 1-3 randomly from topics
    num_topics = randint(1, 3)
    topics_to_ask = set()
    while len(topics_to_ask) < num_topics:
        topics_to_ask.add(topics[randint(0, len(topics) - 1)])

    dataset_item.append[{
        'user': 'system',
        'message': 'Candidate is being interviewed for ' + str(interview_time) + ' minutes on ' + ', '.join(topics_to_ask) + '.'
    }]
    
    time_left = interview_time
    questions_asked_so_far = []

    while time_left:

        time_for_next_question = 0.8 * time_left / num_topics
        question = ask_question(questions_asked_so_far, )
        dataset_item.append[{
            'user': 'interviewer',
            'message': question
        }]
        user_answer = chatgpt_api('Generate a response for the question ' + question)
        dataset_item.append[{
            'user': 'interviewee',
            'message': user_answer
        }]
        time_taken_by_user = randint(time_for_next_question * 0.8, time_for_next_question * 1.2)
        time_left -= time_taken_by_user
        dataset_item.append[{
            'user': 'system',
            'message': 'Time taken by user: ' + str(time_taken_by_user) + ' minutes.'
        }]

    # collect all question and answers and concatenate it into a string
    conversation = ''
    for i in dataset_item:
        if i['user'] == 'interviewer':
            pass
        else:
            if i['user'] == 'interviewee':
                conversation += 'Interviewee: '
            else:
                conversation += 'Interviewer: '
            conversation += i['message'] + '\n'

    # call chatgpt api to generate feedback
    feedback = chatgpt_api('Generate feedback for the interviewee:\n' + conversation)
    dataset_item.append[{
        'user': 'Interviewer',
        'message': feedback
    }]

    return dataset_item