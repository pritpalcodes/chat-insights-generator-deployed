from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import pandas as pd
import re
from collections import Counter
import matplotlib.pyplot as plt
import os
import calendar

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = {'txt'}  # Add this line

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def analyze_chat(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        # Parsing the chat data
        data = []
        for line in lines:
            match = re.match(r'(\d{2}/\d{2}/\d{4}), (\d{2}:\d{2}) - (.*?): (.*)', line)
            if match:
                date, time, sender, message = match.groups()
                data.append([date, time, sender, message])

        # Create a DataFrame
        df = pd.DataFrame(data, columns=['Date', 'Time', 'Sender', 'Message'])

        # Convert Date to datetime and extract the day of the week
        df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y')
        df['Day of Week'] = df['Date'].dt.day_name()

        # Analysis 1: Most repeated word in the entire chat
        all_words = ' '.join(df['Message']).split()
        most_common_word = Counter(all_words).most_common(1)[0]

        # Analysis 2: Count "I love you" for each sender
        love_count = df[df['Message'].str.contains('I love you', case=False)].groupby('Sender').size()

        # Analysis 3: Count specific emojis
        emojis = ['😘', '🫡', '🥳', '🫶🏻', '❤️']
        emoji_count = {emoji: df['Message'].str.count(emoji).sum() for emoji in emojis}

        # Analysis 4: Count "I wish you were here"
        wish_count = df['Message'].str.contains('I wish you were here', case=False).sum()

        # Analysis 5: Count "good night", "GN", or "gn"
        good_night_count = df['Message'].str.contains(r'\bgood night\b|\bGN\b|\bgn\b', case=False).sum()

        # Analysis 6: Messages sent day-wise pie chart
        daywise_count = df['Day of Week'].value_counts()
        colors = plt.cm.Reds(daywise_count / max(daywise_count))  # Gradient of red based on count

        plt.figure(figsize=(8, 8))
        plt.pie(daywise_count, labels=daywise_count.index, autopct='%1.1f%%', colors=colors)
        plt.title('Messages Sent Day Wise')
        plt.savefig('./static/pie_chart.png')

        # Convert Date to datetime and extract the hour
        df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y')
        df['Hour'] = pd.to_datetime(df['Time'], format='%H:%M').dt.hour

        # Hourly Distribution of Messages
        hourly_distribution = df['Hour'].value_counts(normalize=True).sort_index() * 100

        # Convert to 12-hour format with AM/PM
        hour_labels = []
        for hour in hourly_distribution.index:
            hour_label = pd.to_datetime(f'{hour}:00', format='%H:%M').strftime('%I:%M %p')
            hour_labels.append(hour_label)

        # Who Texted More?
        sender_distribution = df['Sender'].value_counts(normalize=True) * 100
        sender_message_count = df['Sender'].value_counts()

        # Time Spent Messaging (Number of Days with Messages)
        days_spent_messaging = df['Date'].nunique()

        # Laugh Counter
        laugh_keywords = ['😂', '🤣', 'haha', 'lol', 'rofl', 'hehe']
        laugh_count = df['Message'].apply(lambda msg: any(keyword in msg.lower() for keyword in laugh_keywords)).sum()
        laugh_percentage = (laugh_count / len(df)) * 100

        stats = {
            "most_common_word": most_common_word,
            "love_count": love_count.to_dict(),
            "emoji_count": emoji_count,
            "wish_count": wish_count,
            "good_night_count": good_night_count,
            "daywise_count": daywise_count.to_dict(),
            "hourly_distribution": hourly_distribution.to_dict(),
            "sender_distribution": sender_distribution.to_dict(),
            "days_spent_messaging": days_spent_messaging,
            "laugh_count": laugh_count,
            "laugh_percentage": laugh_percentage,
        }

        return stats

    except pd.errors.ParserError:
        raise ValueError('Error parsing the chat file. Please make sure it\'s in the correct format.')

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'chat_file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['chat_file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            try:
                stats = analyze_chat(file_path)
                return redirect(url_for('results', stats=stats))
            except pd.errors.ParserError:
                flash('Error parsing the chat file. Please make sure it\'s in the correct format.')
                return redirect(request.url)
    return render_template('upload.html')

@app.route('/results')
def results():
    stats = request.args.get('stats')
    if stats:
        stats = eval(stats)  # Convert string representation of dict back to dict
        return render_template('results.html', stats=stats)
    return redirect(url_for('landing'))

if __name__ == "__main__":
    app.run(debug=True)