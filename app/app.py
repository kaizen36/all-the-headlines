from flask import Flask, render_template
from data_management import download_data, get_data

app = Flask(__name__)


@app.route("/")
def index():
    download_data()
    return render_template("index.html", data = get_data())


@app.route("/map")
def map_view():
    download_data()
    return render_template("map.html", data = get_data())


if __name__ == "__main__":
    app.run(
        debug=True,
        host="0.0.0.0",
    )
