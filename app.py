from flask import Flask, render_template, request, redirect, url_for, session, render_template, jsonify
import pandas as pd
from datetime import datetime, timedelta
import os
import webbrowser

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Define the folder and file path
data_folder = "data"
excel_file = os.path.join(data_folder, "projects.xlsx")

# Ensure the data folder exists
if not os.path.exists(data_folder):
    os.makedirs(data_folder)

# Initialize Excel file with headers if it doesn't exist
if not os.path.exists(excel_file):
    df = pd.DataFrame(columns=["Project Name", "Type", "Notes", "Date", "Time"])
    df.to_excel(excel_file, index=False)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/log_project', methods=["POST"])
def log_project():
    project_name = request.form['project_name']
    project_type = request.form['project_type']
    notes = request.form['notes']
    date = datetime.now().strftime("%Y-%m-%d")
    time = datetime.now().strftime("%H:%M:%S")

    # Create a DataFrame with the new entry
    new_entry = pd.DataFrame([{
        "Project Name": project_name,
        "Type": project_type,
        "Notes": notes,
        "Date": date,
        "Time": time
    }])
    excel_file = "data/projects.xlsx"

    # Read the existing data and concatenate the new entry
    df = pd.read_excel(excel_file)
    df = pd.concat([df, new_entry], ignore_index=True)
    
    # Save the updated DataFrame back to the Excel file
    df.to_excel(excel_file, index=False)
    
    return redirect(url_for('home'))


# Route to start a task timer
@app.route('/start_timer', methods=["POST"])
def start_timer():
    project_name = request.form['project_name']
    start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Update the Excel file with the start time
    df = pd.read_excel(excel_file)
    new_entry = {
        "Project Name": project_name,
        "Start Time": start_time,
        "End Time": None,  # Initially None until the task is ended
        "Duration": None   # Initially None
    }
    df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
    df.to_excel(excel_file, index=False)
    
    # Store the start time in session (or you could store the row index)
    session['project_name'] = project_name
    session['start_time'] = start_time
    
    return redirect(url_for('home'))


@app.route('/stop_timer', methods=["POST"])
def stop_timer():
    end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    project_name = session.get('project_name')
    
    if not project_name:
        return "No active project timer found."
    
    # Read the Excel file, find the project, and update end time and duration
    df = pd.read_excel(excel_file)
    project_row = df[(df['Project Name'] == project_name) & (df['End Time'].isna())]
    
    if not project_row.empty:
        start_time = datetime.strptime(session['start_time'], "%Y-%m-%d %H:%M:%S")
        end_time_obj = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
        duration = end_time_obj - start_time  # Calculate duration
        
        # Update the row with end time and duration
        df.loc[project_row.index, 'End Time'] = end_time
        df.loc[project_row.index, 'Duration'] = str(duration)
        df.to_excel(excel_file, index=False)
    
    # Clear session data
    session.pop('project_name', None)
    session.pop('start_time', None)
    
    return redirect(url_for('home'))

# Sample in-memory storage for events (replace with a database in production)
events = []

@app.route('/calendar')
def calendar():
    return render_template('calender.html')

@app.route('/get-events', methods=['GET'])
def get_events():
    return jsonify(events)

@app.route('/add-event', methods=['POST'])
def add_event():
    data = request.get_json()
    event = {
        "title": data['title'],
        "start": data['start'],  # should be in ISO format YYYY-MM-DDTHH:MM:SSZ
        "end": data.get('end', None)  # optional end time
    }
    events.append(event)
    return jsonify(event), 201

# Weekly summary route
@app.route('/weekly_summary')
def weekly_summary():
    # Load data from the Excel file
    df = pd.read_excel(excel_file)
    
    # Ensure 'Duration' column is in timedelta format for summing time
    df['Duration'] = pd.to_timedelta(df['Duration'], errors='coerce')  # Handle any non-timedeltas gracefully
    
    # Filter for entries from the last 7 days
    one_week_ago = datetime.now() - timedelta(days=7)
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')  # Convert Date column to datetime
    df = df[df['Date'] >= one_week_ago]
    
    # Calculate the total duration per project type over the last week
    weekly_summary = df.groupby("Project Name")['Duration'].sum()  # Sum duration by project
    
    # Format summary for display
    summary_data = {project: str(duration) for project, duration in weekly_summary.items()}
    
    return render_template('summary.html', summary_data=summary_data)
@app.route('/summary')
def summary():
    # Generate weekly/monthly summary (could be based on date filtering)
    df = pd.read_excel(excel_file)
    summary_data = df.groupby("Type").size().to_dict()  # Example: Count by type
    return render_template('summary.html', summary_data=summary_data)

if __name__ == '__main__':
    # Open the app in the default browser
    webbrowser.open("http://127.0.0.1:5000")
    app.run(debug=True)
