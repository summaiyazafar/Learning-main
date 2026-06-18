from flask import Flask
app= Flask(__name__)

@app.route('/')
def home():
    return "Welcome to the Flask App!"

@app.route('/About')
def about():
    return 'This is the simple example of route for About this page.'

@app.route('/Contact')
def contact():
    return '<h2>Contact Us</h2><p>Email: summaiyabibi4545@gmail.com</p>'

if __name__=='__main__':
    app.run(debug=True, use_reloader=False)