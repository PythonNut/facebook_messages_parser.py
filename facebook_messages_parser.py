import re
import shelve
import urllib.request
import facebook
from bs4 import BeautifulSoup
import numpy as np
from matplotlib import pyplot as plt

def init_graph():
    return facebook.GraphAPI(access_token=input('Token: '), version='2.5')

def plot_metric(metric_fun, ticks=False):
    message_metrics = [(t[0], metric_fun(t[1])) for t in message_map.items()]
    message_metrics.sort(key=lambda p: -p[1])
    X = np.arange(len(message_metrics))

    plt.bar(X, [p[1] for p in message_metrics])
    if ticks:
        plt.xticks(X, [p[0] for p in message_metrics], rotation='vertical')
        plt.subplots_adjust(bottom=0.3)

if __name__ == '__main__':
    # You may want to replace this with a subset from a specific chat
    with open('messages.htm') as f:
        messages_html = f.read()

    # Usernames are cached to avoid repeating expensive network requests
    user_cache = shelve.open('user_cache.dat')

    graph = None
    soup = BeautifulSoup(messages_html, 'html.parser')

    users = soup.find_all('span', {'class': 'user'})

    username_regex = re.compile(r'<span.*?>(.*?)@facebook\.com</span>')
    username_regex_alt = re.compile(r'<span.*?>(.*?)</span>')

    # Pass 1: normalize all names using the Graph API
    for i, user in enumerate(map(str, users)):
        if user not in user_cache:
            try:
                user_id = username_regex.search(str(user)).group(1)
                graph = graph or init_graph()
                name = graph.get_object(id=user_id)['name']
                user_cache[user] = name
                print('Fetched name: {}'.format(name))
            except AttributeError:
                name = username_regex_alt.search(str(user)).group(1)
                user_cache[user] = name

    # Here, we just trust that user spans are 1↔1 with messages
    # (They were, last I checked)
    messages = soup.find_all('p')
    message_map = {}

    # Pass 2: map names to messages
    for user, message in zip(map(str, users), messages):
        name = user_cache[user]
        if name not in message_map:
            message_map[name] = []
        message_map[name].append(message.get_text())

    user_cache.close()

    # Do fun stuff here:
