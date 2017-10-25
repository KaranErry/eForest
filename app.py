from flask import Flask, render_template

app=Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

#student form
@app.route('/studentForm')
def studentForm():
    return render_template('studentForm.html')

#Professor Form
@app.route('/professorForm')
def professorForm():
    return render_template('professorForm.html')

#Department Head/Chair Form
@app.route('/departmentHeadForm')
def departmentHeadForm():
    return render_template('departmentHeadForm.html')

#Registrar/Dean Form
@app.route('/deanForm')
def deanForm():
    return render_template('deanForm.html')



@app.route('/login')
def login():
    return render_template('login.html')



if __name__== "__main__":
    app.run(debug=True)
