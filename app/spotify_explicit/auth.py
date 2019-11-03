import logging, sys, os, json

# Path to API Credentials file
PATH = os.path.join(sys.path[0], 'auth.json')

# Ensure the file exists, if not, generate one and error with a reason
if not os.path.exists(PATH):
    with open(PATH, 'w') as file:
        # Dump a pretty-printed dictionary with default values
        json.dump(
            {
                'USERNAME' : 'Your Username Here',
                'CLIENT_ID' : 'Your Client ID Here',
                'CLIENT_SECRET' : 'Your Client Secret Here',
                'REDIRECT_URI' : 'Your Redirect URI Callback Here', 
                'SCOPE' : ['Your Scopes Here']
            },
            file,
            indent=3
        )
        # Error critically, then exit
        logging.critical("No \'auth.json\' file detected, one has been created for you")
        logging.critical("Please fill out with your Spotify credentials, and then restart the program")
        sys.exit()

# Open and parse file
FILE = json.load(open(PATH, 'r'))

# Load all configuration variables
USERNAME = FILE['USERNAME']
CLIENT_ID = FILE['CLIENT_ID']
CLIENT_SECRET = FILE['CLIENT_SECRET']
REDIRECT_URI = FILE['REDIRECT_URI']
SCOPE = ' '.join(FILE['SCOPE'])