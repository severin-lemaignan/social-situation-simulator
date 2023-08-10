from flask import Flask, render_template, jsonify, request, session
import glob
import random
import time
from datetime import datetime
import pandas as pd

MAX_VIDEOS = 10
MIN_SAVING_INTERVAL = 5  # seconds

app = Flask(__name__, template_folder="tpl")
app.secret_key = "391f43849bbae5fe655282c4bc2246cf8338c0b4a1dde06537c33ad403d18795"

videos = [v[:-4] for v in glob.glob("static/videos/*.mp4")]

results = []
last_save = time.time()


@app.route("/submit")
def submit():
    global last_save

    vid1 = request.args["vid1"]

    if vid1 != "":
        vid2 = request.args["vid2"]
        vid3 = request.args["vid3"]
        choice = request.args[request.args["choice"]]

        if session["vid_idx"] == 7 and choice != "vid3":
            print("attention check failed!")
            session["attention_check"] = 1

        if choice == vid2:
            print(f"{vid1} closer to {vid2} than {vid3}")
            results.append(
                (session["id"], vid1, vid2, vid3, 1, session["attention_check"])
            )
        elif choice == vid3:
            print(f"{vid1} closer to {vid3} than {vid2}")
            results.append(
                (session["id"], vid1, vid2, vid3, -1, session["attention_check"])
            )
        elif choice == vid1:
            print(f"Neither {vid2} or {vid3} are similar to {vid1}")
            results.append(
                (session["id"], vid1, vid2, vid3, 0, session["attention_check"])
            )
        else:
            print("Error! invalid choice")

    if time.time() - last_save > MIN_SAVING_INTERVAL:
        pd.DataFrame(
            results,
            columns=["user_id", "vid1", "vid2", "vid3", "choice", "attention_check"],
        ).to_csv(f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}-votes.csv")
        last_save = time.time()

    if session["vid_idx"] == MAX_VIDEOS:
        pd.DataFrame(
            results,
            columns=["user_id", "vid1", "vid2", "vid3", "choice", "attention_check"],
        ).to_csv(f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}-votes.csv")
        last_save = time.time()
        return jsonify({"goto": "end"})

    session["vid_idx"] += 1

    # attention check!
    if session["vid_idx"] == 7:
        new_videos = [
            "static/videos/situation_lfe_1.json-14.0-Violet",
            "static/videos/situation_lfe_1.json-19.0-Emily",
            "static/videos/situation_lfe_1.json-16.0-robot",
        ]
    else:
        new_videos = random.sample(videos, 3)

    return jsonify(
        {"vid1": new_videos[0], "vid2": new_videos[1], "vid3": new_videos[2]}
    )


@app.route("/")
def index():
    return render_template("welcome.html")


@app.route("/example")
def example():
    return render_template("example.html")


@app.route("/choice")
def choice():
    import secrets

    if "id" not in session:
        session["id"] = secrets.token_hex()[:10]
        session["vid_idx"] = 0
        session["attention_check"] = 0

    return render_template("choice.html")


@app.route("/reset")
def reset():
    session["vid_idx"] = 0
    session["attention_check"] = 0
    return render_template("welcome.html")


@app.route("/end")
def end():
    return render_template("end.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
