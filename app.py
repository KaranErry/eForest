import google_auth_oauthlib.flow
import google.oauth2.credentials
import oauth2client
from googleapiclient.discovery import build

from flask import Flask, render_template, session, redirect, request, url_for

app=Flask(__name__)
app.secret_key = 'Random value' #TODO: Replace this secret key with an actual secure secret key.

flow = None

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


# Login landing page
@app.route('/login')
def login():
    return render_template('login.html')

# Process OAuth authorization
@app.route('/login/processLogin')
def processLogin():
    if 'credentials' not in session:
        return redirect(url_for('authorize'))

    # Load credentials from the session:
    credentials == google.oauth2.credentials.Credentials(**session['credentials'])
    userInfo = build('oauth2', 'v1', credentials=credentials)


# Authorize using OAuth
@app.route('/login/authorize')
def authorize():
    # Construct the Flow object:
    # global flow # TODO: Remove the global and ask StackOverflow why the flow.fetch_token() call in processAuthCallback() throws a "global value flow is not defined" error. Global values are apparently not great programming practice in python.
    global flow
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
    'client_secret_217930784500-l9noq9hdupkormpjoamplnvsp3078q88.apps.googleusercontent.com.json',
    scopes = ['profile', 'email', 'openid']
    )
    print(type(flow))
    # flow = oauth2client.flow_from_clientsecrets(
    # 'client_secret_217930784500-l9noq9hdupkormpjoamplnvsp3078q88.apps.googleusercontent.com.json',
    # scope = ['profile', 'email', 'openid']
    # )
    # Set the Redirect URI:
    flow.redirect_uri = url_for('processAuthCallback', _external = True)
    # Generate URL for request to Google's OAuth 2.0 server:
    authorization_url, state = flow.authorization_url(
        # Enable offline access so as to be able to refresh an access token withou re-prompting the user for permission
        access_type = 'offline',
        # Enable incremental authorization
        include_granted_scopes = 'true',
        hd = 'drew.edu'
        )
    # Store the state so the callback can verify the auth server response:
    session['state'] = state

    return redirect(authorization_url)

# Process the authorization callback
@app.route('/login/oauth2callback')
def processAuthCallback():
    # Specify the state when creating the flow in the callback so that it can verified in the authorization server response:
    state = session['state']
    # Use the authorization server's response to fetch the OAuth 2.0 tokens:
    authorization_response = request.url
    flow.fetch_token(authorization_response = authorization_response)
    # Store credentials in the session:
    # TODO: When migrating to production, store these credentials in a persistent database instead.
    credentials = flow.credentials
    session['credentials'] = credentials_to_dict(credentials)

    return redirect(url_for('processLogin'))




if __name__== "__main__":
    app.run(debug=True)
