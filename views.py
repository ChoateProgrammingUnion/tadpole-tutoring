from flask import render_template, Markup

def render_navbar(state):
    return Markup(render_template("navbar.html", **state))
