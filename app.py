from flask import Flask
from agents.adv import AdvAgent

from agents.img import ImageAgent
from agents.sud import SoundAgent
from utils import post_agent

app = Flask(__name__)


@app.route('/api/img/<slug>', methods=['GET'])
def api_img(slug: str):
    return post_agent(
        ImageAgent(slug).process()
    )


@app.route('/api/sud/<slug>', methods=['GET'])
def api_snd(slug: str):
    return post_agent(
        SoundAgent(slug).process()
    )


@app.route('/api/adv/<slug>', methods=['GET'])
def api_adv(slug: str):
    return post_agent(
        AdvAgent(slug).process()
    )


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def default_route(path: str):
    return "Not found", 404


if __name__ == '__main__':
    app.run()
