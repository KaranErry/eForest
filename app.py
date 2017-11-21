from flask import Flask, render_template, session, redirect, request, url_for
from googleapiclient.discovery import build
import google_auth_oauthlib.flow, google.oauth2.credentials, oauth2client
import requests
import psycopg2

app=Flask(__name__)
app.secret_key = 'Random value' #TODO: Replace this secret key with an actual secure secret key.

def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route('/')
def home():
    return render_template('home.html')

#student form
@app.route('/forms/studentForm')
def studentForm():
    return render_template('studentForm.html')

#Professor Form
@app.route('/forms/professorForm')
def professorForm():
    return render_template('professorForm.html')

#Department Head/Chair Form
@app.route('/forms/departmentHeadForm')
def departmentHeadForm():
    return render_template('departmentHeadForm.html')

#Registrar/Dean Form
@app.route('/forms/deanForm')
def deanForm():
    return render_template('deanForm.html')

# Login landing page
@app.route('/identity')
def identity():
    return render_template('identityLanding.html')

# Process OAuth authorization
@app.route('/identity/login')
def login():
    if 'credentials' not in session:
        # No user session is active
        return redirect(url_for('authorize'))
    try:
        # Load credentials from the session:
        credentials = google.oauth2.credentials.Credentials(**session['credentials'])
        # Build the service object for the Google OAuth v2 API:
        oauth = build('oauth2', 'v2', credentials=credentials)
        # Call methods on the service object to return a response with the user's info:
        userinfo = oauth.userinfo().get().execute()
        print(userinfo)
    except google.auth.exceptions.RefreshError:
        # Credentials are stale
        return redirect(url_for('authorize'))

    # Verify that the user signed in with a 'drew.ed' email address:
    if 'hd' in userinfo: validDomain = userinfo['hd'] == 'drew.edu'
    else:                validDomain = False
    if not validDomain:
        return redirect(url_for('domainInvalid'))

    conn = psycopg2.connect(database = "d2h7mc7fbep9fg", user = "ayqraqktgwqdwa", password = "2ae940eb19dca2ea77e40352d8a36ddaf964c9240053a5ea3252da2a63a35132", host = "ec2-54-163-255-181.compute-1.amazonaws.com", port = "5432")
    cur = conn.cursor()

    username = userinfo['email'][:userinfo['email'].index('@')]

    print(username)

    cur.execute("SELECT id FROM student_p WHERE id= (%s)", (username,))
    entryStudent = cur.fetchone()
    # print(entryStudent)
    cur.execute("SELECT id FROM prof_m  WHERE id= (%s)", (username,))
    entryProf= cur.fetchone()

    print(type(entryStudent), type(entryProf))

    studentIn= False
    professorIn= False

    if entryStudent== None and entryProf== None:
        return render_template("newUser.html", userinfo=userinfo)
    else:
        if entryStudent!=None:
            if username in entryStudent:
                studentIn= True
                return render_template("landingStudent.html", userinfo=userinfo, studentIn=studentIn)
        elif entryProf!=None:
            if username in entryProf:
                professorIn= True
                return render_template("landingProf.html", userinfo=userinfo, professorIn=professorIn)
        else:
            return render_template("newUser.html", userinfo=userinfo)


@app.route('/landingHome', methods=["POST", "GET"])
def landingHome():
    if request.method == "POST":
        conn = psycopg2.connect(database = "d2h7mc7fbep9fg", user = "ayqraqktgwqdwa", password = "2ae940eb19dca2ea77e40352d8a36ddaf964c9240053a5ea3252da2a63a35132", host = "ec2-54-163-255-181.compute-1.amazonaws.com", port = "5432")
        cur = conn.cursor()
        studentIn= False
        selectOption=request.form.get("select")
        # Load credentials from the session:
        credentials = google.oauth2.credentials.Credentials(**session['credentials'])
        # Build the service object for the Google OAuth v2 API:
        oauth = build('oauth2', 'v2', credentials=credentials)
        # Call methods on the service object to return a response with the user's info:
        userinfo = oauth.userinfo().get().execute()

        if selectOption == "Student":
            entries=cur.execute("INSERT INTO student_p (id, first_name, last_name, expected_grad) VALUES(%s, %s, %s, %s)", (userinfo['email'][:userinfo['email'].index('@')], userinfo['given_name'], userinfo['family_name'], None))
            conn.commit()
            conn.close()
            return render_template("landingStudent.html", userinfo=userinfo, studentIn=studentIn)
        elif selectOption =="DepartmentHead":
            entries=cur.execute("INSERT INTO prof_m VALUES(%s,%s,%s,%s,%s)",(userinfo['email'][:userinfo['email'].index('@')], userinfo['given_name'], userinfo['family_name'],None, True))
            conn.commit()
            conn.close()
            return render_template("landingDeptHead.html", userinfo=userinfo)
        elif selectOption =="Professor":
            print("got to 125")
            entries=cur.execute("INSERT INTO prof_m VALUES(%s,%s,%s,%s,%s)",(userinfo['email'][:userinfo['email'].index('@')], userinfo['given_name'], userinfo['family_name'], None, False))
            conn.commit()
            conn.close()
            return render_template("landingProf.html", userinfo=userinfo)

@app.route('/landingStudent', methods=["POST","GET"])
def landingStudent():
    if request.method == "POST":
        student = {}
        student['majors']=request.form.get("studentMajor")
        student['minors']= request.form.get("studentMinor")
        student['programs']= request.form.get("studentProgram")
        # Load credentials from the session:
        credentials = google.oauth2.credentials.Credentials(**session['credentials'])
        # Build the service object for the Google OAuth v2 API:
        oauth = build('oauth2', 'v2', credentials=credentials)
        # Call methods on the service object to return a response with the user's info:
        userinfo = oauth.userinfo().get().execute()

        conn = psycopg2.connect(database = "d2h7mc7fbep9fg", user = "ayqraqktgwqdwa", password = "2ae940eb19dca2ea77e40352d8a36ddaf964c9240053a5ea3252da2a63a35132", host = "ec2-54-163-255-181.compute-1.amazonaws.com", port = "5432")
        cur = conn.cursor()

        # Get the program IDs
        # TODO handle potential of different programs w/ same name
        id_select = "SELECT id FROM program_m WHERE name = %s"
        cur.execute( id_select, [student['majors']] )
        student['majors'] = cur.fetchone()
        cur.execute( id_select, [student['minors']] )
        student['minors'] = cur.fetchone()
        cur.execute( id_select, [student['programs']] )
        student['programs'] = cur.fetchone()

        # Insert the info
        prog_insert = "INSERT INTO program_members_m VALUES (%s,%s)"
        studentid = userinfo['email'][:userinfo['email'].index('@')]

        cur.execute(prog_insert, (student['majors'], studentid))
        cur.execute(prog_insert, (student['minors'], studentid))
        cur.execute(prog_insert, (student['programs'], studentid))
        # TODO handle multiple of each field except studentGradYear && posibiltiy of not having any && the possibility of duplicate submission attempts

        print( student['majors'], student['minors'])

        # TEST
        cur.execute("SELECT * FROM student_p")
        print(type(cur.fetchall()))


        # Commit & close DB connection
        cur.close()
        conn.commit()
        conn.close()
        studentIn= True

    return render_template("landingStudent.html", userinfo=userinfo, studentIn=studentIn)

@app.route('/landingProf', methods=["POST","GET"])
def landingProf():
    return render_template("landingProf.html")

@app.route('/landingDeptHead', methods=["POST","GET"])
def landingDeptHead():
    return render_template("landingDeptHead.html")

@app.route('/identity/logout')
def logout():
    if 'credentials' in session:
        # Load the credentials from the session:
        credentials = google.oauth2.credentials.Credentials(**session['credentials'])
        # Request the auth server to revoke the specified credentials:
        requests.post('https://accounts.google.com/o/oauth2/revoke',
            params={'token': credentials.token},
            headers = {'content-type': 'application/x-www-form-urlencoded'})
        # Delete the credentials from the session cookie:
        del session['credentials']

    if 'doNext' in request.args and request.args['doNext'] == 'login':
        return redirect(url_for('login'))
    else:
        return render_template('logoutSuccess.html')

@app.route('/search', methods=["POST","GET"])
def search():
    # Load credentials from the session:
    credentials = google.oauth2.credentials.Credentials(**session['credentials'])
    # Build the service object for the Google OAuth v2 API:
    oauth = build('oauth2', 'v2', credentials=credentials)
    # Call methods on the service object to return a response with the user's info:
    userinfo = oauth.userinfo().get().execute()

    conn = psycopg2.connect(database = "d2h7mc7fbep9fg", user = "ayqraqktgwqdwa", password = "2ae940eb19dca2ea77e40352d8a36ddaf964c9240053a5ea3252da2a63a35132", host = "ec2-54-163-255-181.compute-1.amazonaws.com", port = "5432")
    cur = conn.cursor()

    cur.execute("SELECT * FROM program_members_m")
    program_members_ENTIRE = cur.fetchall()
    cur.execute("SELECT * FROM program_m")
    program_ENTIRE = cur.fetchall()
    cur.execute("SELECT * FROM student_p")
    student_ENTIRE = cur.fetchall()
    cur.execute("SELECT * FROM prof_m")
    prof_ENTIRE = cur.fetchall()
    return render_template("search.html", program_members=program_members_ENTIRE, program=program_ENTIRE, student=student_ENTIRE, prof=prof_ENTIRE)

# def showStudents():
#     return render_template()
#
# def showProfs():
#     return render_template()

# Authorize using OAuth
@app.route('/identity/login/authorize')
def authorize():
    # Construct the Flow object:
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
    'client_secret_217930784500-l9noq9hdupkormpjoamplnvsp3078q88.apps.googleusercontent.com.json',
    scopes = ['profile', 'email'])

    # Set the Redirect URI:
    flow.redirect_uri = url_for('oauth2callback', _external = True)

    # Generate URL for request to Google's OAuth 2.0 server:
    authorization_url, state = flow.authorization_url(
        # Enable offline access so as to be able to refresh an access token withou re-prompting the user for permission
        access_type = 'offline',
        # Enable incremental authorization
        include_granted_scopes = 'true',
        # Specify the Google Apps domain so that the user can only login using a 'drew.edu' email address.
        # NOTE: This can be overridden by the user by modifying the request URL in the browser, which is why the login() view  double-checks the domain of the logged-in user's email to ensure it's a 'drew.edu' email address.
        hd = 'drew.edu'
        )

    # Store the state so the callback can verify the auth server response:
    session['state'] = state

    return redirect(authorization_url)

# Process the authorization callback
@app.route('/identity/login/oauth2callback')
def oauth2callback():
    # Specify the state when creating the flow in the callback so that it can verified in the authorization server response:
    state = session['state']

    # Reconstruct the flow object:
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
    'client_secret_217930784500-l9noq9hdupkormpjoamplnvsp3078q88.apps.googleusercontent.com.json',
    scopes = ['profile', 'email'],
    state = state)
    flow.redirect_uri = url_for('oauth2callback', _external = True)

    # Use the authorization server's response to fetch the OAuth 2.0 tokens:
    authorization_response = request.url.strip()
    flow.fetch_token(authorization_response = authorization_response)

    # Store credentials in the session:
    session['credentials'] = credentials_to_dict(flow.credentials)

    return redirect(url_for('login'))

# Display invalid-sign-in page and prompt for re-login:
@app.route('/identity/domainInvalid')
def domainInvalid():
    return render_template('domainInvalid.html')


# HELPER FUNCTIONS

def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}

if __name__== "__main__":
    app.run(debug=True)
