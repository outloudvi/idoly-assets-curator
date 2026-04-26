from time import perf_counter
from flask import Flask, request, g

from agents.env import EnvironmentAgent
from agents.img import ImageAgent
from utils import log_to_matomo, post_agent

app = Flask(__name__)
global_cache: set[str] = set()


@app.before_request
def before_request():
    g.start_time = perf_counter()


@app.after_request
def after_request(response):
    duration = perf_counter() - g.start_time
    try:
        log_to_matomo(request, duration)
    except Exception as e:
        print(f"Error logging requests: {str(e)}")
    return response


@app.route('/api/img/<slug>', methods=['GET'])
def api_img(slug: str):
    return post_agent(
        ImageAgent(slug).process(global_cache)
    )


@app.route('/api/env/<slug>', methods=['GET'])
def api_env(slug: str):
    return post_agent(
        EnvironmentAgent(slug).process(global_cache)
    )


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def default_route(path: str):
    return "Not found", 404


if __name__ == '__main__':
    app.run()
