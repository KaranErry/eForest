from flask import Flask, render_template

app=Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/studentForm')
def studentForm():
    return render_template('studentForm.html')

@app.route('/login')
def login():
    return render_template('login.html')



if __name__== "__main__":
    app.run(debug=True)
