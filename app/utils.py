import pandas as pd
import matplotlib.pyplot as plt

def analyze_chat(file_path):
    # Load chat data from file
    chat_data = pd.read_csv(file_path)
    
    # Calculate statistics
    total_messages = len(chat_data)
    unique_users = len(chat_data['user'].unique())
    total_words = chat_data['text'].str.split().str.len().sum()
    avg_words_per_message = total_words / total_messages
    
    # Plot word frequency
    word_freq = chat_data['text'].str.split().explode().value_counts()
    plt.figure(figsize=(10, 6))
    plt.bar(word_freq.index[:10], word_freq.values[:10])
    plt.title('Top 10 Words in Chat')
    plt.xlabel('Word')
    plt.ylabel('Frequency')
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig('word_freq.png')
    
    # Plot user activity
    user_activity = chat_data.groupby('user')['text'].count().reset_index()
    plt.figure(figsize=(10, 6))
    plt.bar(user_activity['user'], user_activity['text'])
    plt.title('User Activity')
    plt.xlabel('User')
    plt.ylabel('Messages')
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig('user_activity.png')
    
    # Save statistics to file
    with open('stats.txt', 'w') as f:
        f.write(f'Total Messages: {total_messages}\n')
        f.write(f'Unique Users: {unique_users}\n')
        f.write(f'Total Words: {total_words}\n')
        f.write(f'Average Words per Message: {avg_words_per_message:.2f}\n')
    
    return {
        'total_messages': total_messages,
        'unique_users': unique_users,
        'total_words': total_words,
        'avg_words_per_message': avg_words_per_message
    }
