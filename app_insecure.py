import google_auth_oauthlib.flow
import google.oauth2.credentials
import oauth2client
from googleapiclient.discovery import build
import os
import requests

from flask import Flask, render_template, session, redirect, request, url_for

app=Flask(__name__)
app.secret_key = 'Random value' #TODO: Replace this secret key with an actual secure secret key.

# flow = None
loginJustBegun = True

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
    global loginJustBegun   # FOR TESTING
    loginJustBegun = True   # FOR TESTING
    return render_template('login.html')

# Process OAuth authorization
@app.route('/login/processLogin')
def processLogin():
    if loginJustBegun:      # FOR TESTING TODO: When finalising, remove all related "FOR TESTING" statements that clear the session whenever the login page is (re)loaded.
        session.clear()     # FOR TESTING
    if 'credentials' not in session:
        print("IIIIIIIIIIIIIII creds not in session")
        return redirect(url_for('authorize'))
    print("IXIXIXIXIXIXIXI creds in session")

    # Load credentials from the session:
    credentials = google.oauth2.credentials.Credentials(**session['credentials'])

    # Build the service object for the Google OAuth v2 API:
    oauth = build('oauth2', 'v2', credentials=credentials)

    # Call methods on the service object to return a response with the user's info:
    userinfo = oauth.userinfo().get().execute()

    # TODO: (Eventually) Since the hd parameter in the authorization can be modified by the user, check that the user signed in with a drew.edu email and if not, log them out and direct to the login landing page again.
    # TODO: Obtain user's profile info
    # TODO: Store user's profile info in persistent storage.

    # This section of commented-out code is specifically for converting the login flow to OIDC-compliant in the future
        # Load the Open ID Discovery Document from Google's URL and then unpack it into a JSON dict:
        # discoveryDoc = json.loads(requests.get('https://accounts.google.com/.well-known/openid-configuration').text)

    return "Hello, " + userinfo['name'] + "!"

# Authorize using OAuth
@app.route('/login/authorize')
def authorize():
    # Construct the Flow object:
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
    'client_secret_217930784500-l9noq9hdupkormpjoamplnvsp3078q88.apps.googleusercontent.com.json',
    scopes = ['profile', 'email'])

    # Set the Redirect URI:
    flow.redirect_uri = url_for('processAuthCallback', _external = True)

    # Generate URL for request to Google's OAuth 2.0 server:
    authorization_url, state = flow.authorization_url(
        # Enable offline access so as to be able to refresh an access token withou re-prompting the user for permission
        access_type = 'offline',
        # Enable incremental authorization
        include_granted_scopes = 'true',
        # Specify the Google Apps domain so that the user can only login using a 'drew.edu' email address.
        # NOTE: This can be overridden by the user by modifying the request URL in the browser, which is why the processLogin() view  double-checks the domain of the logged-in user's email to ensure it's a 'drew.edu' email address.
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

    # Reconstruct the flow object:
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
    'client_secret_217930784500-l9noq9hdupkormpjoamplnvsp3078q88.apps.googleusercontent.com.json',
    scopes = ['profile', 'email'])
    flow.redirect_uri = url_for('processAuthCallback', _external = True)

    # Use the authorization server's response to fetch the OAuth 2.0 tokens:
    authorization_response = request.url.strip()
    flow.fetch_token(authorization_response = authorization_response)

    # Store credentials in the session:
    # TODO: When migrating to production, store these credentials in a persistent database instead.
    session['credentials'] = credentials_to_dict(flow.credentials)

    global loginJustBegun   # FOR TESTING
    loginJustBegun = False  # FOR TESTING
    return redirect(url_for('processLogin'))

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
