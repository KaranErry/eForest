import google_auth_oauthlib.flow
import google.oauth2.credentials
import oauth2client
from googleapiclient.discovery import build
import os
import jsonpickle

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
    global loginJustBegun
    loginJustBegun = True
    return render_template('login.html')

# Process OAuth authorization
@app.route('/login/processLogin')
def processLogin():
    if loginJustBegun:
        session.clear()
    if 'credentials' not in session:
        print("IIIIIIIIIIIIIII creds not in session")
        return redirect(url_for('authorize'))
    print (session)
    print("IXIXIXIXIXIXIXI creds in session")

    # Load credentials from the session:
    credentials = google.oauth2.credentials.Credentials(jsonpickle.decode(session['credentials']))
    userInfo = build('oauth2', 'v1', credentials=credentials)
    return "Hello world!"
    # TODO: (Eventually) Since the hd parameter in the authorization can be modified by the user, check that the user signed in with a drew.edu email and if not, log them out and direct to the login landing page again.
    # TODO: Obtain user's profile info
    # TODO: Store user's profile info in persistent storage.

# Authorize using OAuth
@app.route('/login/authorize')
def authorize():
    # Construct the Flow object:
    # global flow # TODO: Remove the global and ask StackOverflow why the flow.fetch_token() call in processAuthCallback() throws a "global value flow is not defined" error. Global values are apparently not great programming practice in python.
    session.clear()
    # global flow
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
    'client_secret_217930784500-l9noq9hdupkormpjoamplnvsp3078q88.apps.googleusercontent.com.json',
    scopes = ['profile', 'email', 'openid']
    )
    print("XXXXXXXXXXXX", type(flow))
    # flow = oauth2client.flow_from_clientsecrets(
    # 'client_secret_217930784500-l9noq9hdupkormpjoamplnvsp3078q88.apps.googleusercontent.com.json',
    # scope = ['profile', 'email', 'openid']
    # )
    # Set the Redirect URI:
    flow.redirect_uri = url_for('processAuthCallback', _external = True)
    print("XXXXXXXXXXXX", type(flow))
    # Generate URL for request to Google's OAuth 2.0 server:
    authorization_url, state = flow.authorization_url(
        # Enable offline access so as to be able to refresh an access token withou re-prompting the user for permission
        access_type = 'offline',
        # Enable incremental authorization
        include_granted_scopes = 'true',
        #
        hd = 'drew.edu'
        )
    # Store the state so the callback can verify the auth server response:
    session['state'] = state
    # session['flow'] = jsonpickle.encode(flow)
    # print("XXXXXXXXXAAA", type(jsonpickle.decode(session.get('flow'))))
    # print("XXXXXXXXXHHH", type(jsonpickle.decode(session['flow'])))

    return redirect(authorization_url)

# Process the authorization callback
@app.route('/login/oauth2callback')
def processAuthCallback():
    # Specify the state when creating the flow in the callback so that it can verified in the authorization server response:
    state = session['state']
    # flow = jsonpickle.decode(session['flow'])
    # print("XXXXXXXXXIII", type(flow))

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
    'client_secret_217930784500-l9noq9hdupkormpjoamplnvsp3078q88.apps.googleusercontent.com.json',
    scopes = ['profile', 'email', 'openid']
    )
    flow.redirect_uri = url_for('processAuthCallback', _external = True)

    # Use the authorization server's response to fetch the OAuth 2.0 tokens:
    authorization_response = request.url.strip()
    flow.fetch_token(authorization_response = authorization_response)
    # Store credentials in the session:
    # TODO: When migrating to production, store these credentials in a persistent database instead.
    credentials = flow.credentials
    # session['credentials'] = credentials_to_dict(credentials)
    session['credentials'] = jsonpickle.encode(credentials)

    global loginJustBegun
    loginJustBegun = False
    return redirect(url_for('processLogin'))




if __name__== "__main__":
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.run('localhost', 8080, debug=True)
