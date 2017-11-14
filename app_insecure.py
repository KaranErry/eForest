import google_auth_oauthlib.flow
import google.oauth2.credentials
import oauth2client
from googleapiclient.discovery import build
import os
import requests
from flask import Flask, render_template, session, redirect, request, url_for
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


    if entryStudent== None and entryProf== None:
        return render_template("newUser.html", userinfo=userinfo)
    else:
        if entryStudent!=None:
            if username in entryStudent:
                return render_template("landingStudent.html", userinfo=userinfo)
        elif entryProf!=None:
            if username in entryProf:
                return render_template("landingProf.html", userinfo=userinfo)
        else:
            return render_template("newUser.html", userinfo=userinfo)


@app.route('/landingHome', methods=["POST", "GET"])
def landingHome():
    if request.method == "POST":
        selectOption=request.form.get("select")
        # Load credentials from the session:
        credentials = google.oauth2.credentials.Credentials(**session['credentials'])
        # Build the service object for the Google OAuth v2 API:
        oauth = build('oauth2', 'v2', credentials=credentials)
        # Call methods on the service object to return a response with the user's info:
        userinfo = oauth.userinfo().get().execute()

        conn = psycopg2.connect(database = "d2h7mc7fbep9fg", user = "ayqraqktgwqdwa", password = "2ae940eb19dca2ea77e40352d8a36ddaf964c9240053a5ea3252da2a63a35132", host = "ec2-54-163-255-181.compute-1.amazonaws.com", port = "5432")
        cur = conn.cursor()

        if selectOption == "Student":
            entries=cur.execute("INSERT INTO student_p (id, first_name, last_name, expected_grad) VALUES(%s, %s, %s, %s)", (userinfo['email'][:userinfo['email'].index('@')], userinfo['given_name'], userinfo['family_name'], None))
            conn.commit()
            conn.close()
            return render_template("landingStudent.html", userinfo=userinfo)
        elif selectOption =="DepartmentHead":
            entries=cur.execute("INSERT INTO prof_m (id, first_name, last_name, dept_abbr) VALUES(%s,%s,%s,%s)",(userinfo['email'][:userinfo['email'].index('@')], userinfo['given_name'], userinfo['family_name'],None, True))
            conn.close()
            return render_template("landingDeptHead.html", userinfo=userinfo)
        elif selectOption =="Professor":
            entries=cur.execute("INSERT INTO prof_m (id, first_name, last_name, dept_abbr) VALUES(%s,%s,%s,%s)",(userinfo['email'][:userinfo['email'].index('@')], userinfo['given_name'], userinfo['family_name'], None, False))
            conn.commit()
            conn.close()
            return render_template("landingProf.html", userinfo=userinfo)

@app.route('/landingStudent', methods=["POST","GET"])
def landingStudent():
    if request.method == "POST":
        studentMajor=request.form.get("studentMajor")
        studentMinor= request.form.get("studentMinor")
        studentProgram= request.form.get("studentProgram")
        studentCoursePref= request.form.get("studentCoursePref")
        studentGradYear= request.form.get("studentGradYear")
        # Load credentials from the session:
        credentials = google.oauth2.credentials.Credentials(**session['credentials'])
        # Build the service object for the Google OAuth v2 API:
        oauth = build('oauth2', 'v2', credentials=credentials)
        # Call methods on the service object to return a response with the user's info:
        userinfo = oauth.userinfo().get().execute()

        conn = psycopg2.connect(database = "d2h7mc7fbep9fg", user = "ayqraqktgwqdwa", password = "2ae940eb19dca2ea77e40352d8a36ddaf964c9240053a5ea3252da2a63a35132", host = "ec2-54-163-255-181.compute-1.amazonaws.com", port = "5432")
        cur = conn.cursor()

        cur.execute("INSERT INTO program_m(name, type) VALUES(%s,%s)", (studentMajor, "major"))
        cur.execute("INSERT INTO program_m(name, type) VALUES(%s,%s)", (studentMinor, "minor"))
        cur.execute("INSERT INTO program_m(name, type) VALUES(%s,%s)", (studentProgram, "program"))


        print(studentMajor, studentMinor, studentProgram, studentCoursePref, studentGradYear)

    return render_template("landingStudent.html", userinfo=userinfo)

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
    return render_template("search.html")

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
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.run('localhost', 8080, debug=True)
