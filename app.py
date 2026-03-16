import os
from flask import Flask, request

app = Flask(__name__)

@app.get('/')
def home():
    return "<h1>საიტი ჩაირთო!</h1><p>ახლა Twilio-ს კოდებია საჭირო.</p>"

if __name__ == "__main__":
    app.run(debug=True)
