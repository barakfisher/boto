import ast
import requests
from bottle import route, run, template, static_file, request, response
from random import choice
import json

swears = ["asshole", "fuck", "idiot", "stupid"]

robo_state = {"afraid": ["Scary...", "scared", "afraid", "pissed", "angry", "kill"],
              "board": ["boooring!", "bored", "boring"],
              "confused": ["what?what?"],
              "crying": ["thats sad..", "sad", "crying"],
              "dancing": ["wooo", "dance", "dancing", "party"],
              "dog": ["dogs are cool", "animal", "dog", "cat", "pet", "dogs"],
              "exited": ["im exited", "exited", "play", "game", "birthday"],
              "giggling": ["You can always Google it", "why", "who", "what", "where", "how", "when"],
              "takeoff": ["takeoff", "leave", "leaving", "go", "going"]
              }


def check_state(msg):
    for key, value in robo_state.items():
        if any(word in msg for word in value):
            return json.dumps({"animation": key, "msg": robo_state[key][0]})
        if msg == ("stop!" or "reset!"):
            return json.dumps({"animation": key, "msg": "Hello, my name is Boto, what is yours?"})
        if "you are not" in msg:
            return json.dumps({"animation": "crying", "msg": "I am sorry to hear that"})
    return json.dumps({"animation": key, "msg": "what do do do ?"})


def is_swear(msg):
    for word in msg:
        if word in swears:
            return True
    return False


def shuffle_quick_answer():
    quick_answer = ["yes", "no", "never", "maybe", "maybe later", "I don't know yet"]
    return choice(quick_answer)


def get_news():
    if not request.get_cookie("news_count"):
        count = 0
        response.set_cookie("news_count", str(count))
    else:
        count = int(request.get_cookie("news_count"))
        count += 1
        response.set_cookie("news_count", str(count))
    news = requests.get(
        "https://newsapi.org/v2/top-headlines?country=us&apiKey=4e0464b1925748ac97520b8418f73ad5").json()
    if int(news["totalResults"]) > count:
        return news["articles"][count]["title"]
    return "no more news for now"


@route('/', method='GET')
def index():
    return template("chatbot.html")


@route("/chat", method='POST')
def chat():
    user_message = request.POST.get('msg')
    if is_swear(user_message):
        return json.dumps({"animation": "no", "msg": "Why like this?"})
    if not request.get_cookie("name"):
        response.set_cookie("name", user_message)
        return json.dumps({"animation": "no", "msg": "Nice to finally meet you {}".format(user_message)})
    if ("joke" or "chuck norris") in user_message:
        joke = requests.get("http://api.icndb.com/jokes/random?exclude=[nerdy,explicit]")
        return json.dumps({"animation": "inlove", "msg": ast.literal_eval(joke.text)["value"]["joke"]})
    if "news" in user_message:
        return json.dumps({"animation": "heartbroke", "msg": get_news()})
    if user_message.split(" ")[0] in (["is", "are", "am", "did", "will", "have", "can"]):
        return json.dumps({"animation": "money", "msg": shuffle_quick_answer()})
    if user_message.split(" ")[0] == ("stop!" or "reset!"):
        delete_cookies()
    return check_state(user_message)


def delete_cookies():
    response.delete_cookie("name")
    response.delete_cookie("news_count")


@route("/test", method='POST')
def chat():
    user_message = request.POST.get('msg')
    return json.dumps({"animation": "inlove", "msg": user_message})


@route('/js/<filename:re:.*\.js>', method='GET')
def javascripts(filename):
    return static_file(filename, root='js')


@route('/css/<filename:re:.*\.css>', method='GET')
def stylesheets(filename):
    return static_file(filename, root='css')


@route('/images/<filename:re:.*\.(jpg|png|gif|ico)>', method='GET')
def images(filename):
    return static_file(filename, root='images')


def main():
    run(host='localhost', port=7000)


if __name__ == '__main__':
    main()
