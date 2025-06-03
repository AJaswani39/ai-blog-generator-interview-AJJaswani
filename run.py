# run.py
# Simple script to run the Flask app
# all you have to is run this app in the terminal
# The command to run it is: python run.py

from app.app import app

if __name__ == '__main__':
    # The scheduler is already initialized in app.py
    app.run(debug=True, use_debugger=False)


