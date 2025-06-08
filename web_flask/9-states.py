#!/usr/bin/python3
"""Starts a Flask web application"""
from flask import Flask, render_template
from models import storage
from models.state import State

app = Flask(__name__)

@app.route('/states', strict_slashes=False)
def states():
    """Display a HTML page with the list of states"""
    states = storage.all(State).values()
    return render_template('9-states.html', states=states)

@app.route('/states/<id>', strict_slashes=False)
def state(id):
    """Display a HTML page with the state and its cities"""
    states = storage.all(State).values()
    state = None
    for s in states:
        if s.id == id:
            state = s
            break
    return render_template('9-states.html', states=states, state=state)

@app.teardown_appcontext
def teardown_db(exception):
    """Remove the current SQLAlchemy Session"""
    storage.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
