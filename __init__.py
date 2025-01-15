from flask import Flask, render_template, request, redirect, url_for
from Forms import CreateUserForm, CreateCustomerForm
import shelve, User, Customer

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')