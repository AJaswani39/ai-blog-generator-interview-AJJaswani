# run.py
# Simple script to run the Flask app
# all you have to is run this app in the terminal
# The command to run it is: python run.py

from app.app import app, scheduler

if __name__ == '__main__':
    # Initialize the scheduler before running the app
    scheduler()
    app.run(debug=True, use_debugger=False)

