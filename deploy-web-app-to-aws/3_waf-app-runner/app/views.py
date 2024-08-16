from flask import Flask, redirect, render_template, request, url_for
from models import delete_item, get_item, put_item, scan_items, update_item

app = Flask(__name__)


@app.route("/")
def index():
    items = scan_items()
    return render_template("index.html", items=items)


@app.route("/todos")
def todo_form():
    item = get_item(request.args)
    return render_template("todo_form.html", item=item)


@app.route("/todos/add", methods=["POST"])
def add_todo():
    put_item(request.form)
    return redirect(url_for("index"))


@app.route("/todos/update", methods=["POST"])
def update_todo():
    update_item(request.form)
    return redirect(url_for("index"))


@app.route("/todos/delete", methods=["POST"])
def delete_todo():
    delete_item(request.form["todo_id"])
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
