import google_auth_oauthlib.flow
import google.oauth2.credentials
import oauth2client
from googleapiclient.discovery import build
import os
import requests

from flask import Flask, render_template, session, redirect, request, url_for

app=Flask(__name__)
app.secret_key = 'Random value' #TODO: Replace this secret key with an actual secure secret key.

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
        return redirect(url_for('authorize'))

    # Load credentials from the session:
    credentials = google.oauth2.credentials.Credentials(**session['credentials'])
    # Build the service object for the Google OAuth v2 API:
    oauth = build('oauth2', 'v2', credentials=credentials)
    # Call methods on the service object to return a response with the user's info:
    userinfo = oauth.userinfo().get().execute()

    # Verify whether the user signed in with a 'drew.ed' email address:
    if 'hd' in userinfo: validDomain = userinfo['hd'] == 'drew.edu'
    else:                validDomain = False
    if not validDomain:
        print ("You signed in with a non-drew.edu a/c.")
        return redirect(url_for('logout'))

    # TODO: Store user's profile info in persistent storage.

    return "Hello, " + userinfo['name'] + "!"

# Log user out of app by revoking auth credentials
@app.route('/identity/logout')
def logout():
    if 'credentials' in session:
        # Load the credentials from the session:
        credentials = google.oauth2.credentials.Credentials(**session['credentials'])
        # Request the auth server to revoke the specified credentials:
        requests.post('https://accounts.google.com/o/oauth2/revoke',
            params={'token': credentials.token},
            headers = {'content-type': 'application/x-www-form-urlencoded'})

    return redirect(url_for('identity'))

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
    # TODO: When migrating to production, store these credentials in a persistent database instead.
    session['credentials'] = credentials_to_dict(flow.credentials)

    return redirect(url_for('login'))


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
