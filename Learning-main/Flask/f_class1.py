from flask import Flask
app= Flask(__name__)#yeh btata hai app kis file mai hai(resource jesy template dhondy kai liyee)

@app.route('/')#yeh decorator flask ko btata hai kai jb koi user root URL('/') par ayee toh konsa func run krna hai.
def hello_world():
    # Yeh function browser mein show hone wala HTML text return karta hai:
    #  <p>Hello, World!</p>. Browser isay HTML samajh kar render karega.
    return 'Hello World!'


if __name__ == "__main__":#Sirf tab run karo jab ye file directly chal rahi ho, import nahi hui ho kisi aur file mein."
    app.run(debug= True, port=8000)
    #app.run() → Flask ka built-in development server start karta hai.
    # debug=True → Debug mode on karta hai: