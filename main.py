import requests
import random
import re
import os
import tkinter as tk
from tkinter import scrolledtext

def get_random_morat_song():
    api_url = ('https://api.genius.com/artists/491975/songs?per_page=1&sort=popularity&page=' +
               str(random.randint(1, 100)))
    response = requests.get(api_url, headers={
        'Authorization': 'Bearer ' + os.environ['GENIUS_ACCESS_TOKEN']
    })
    if response.status_code == 200:
        song = response.json()['response']['songs'][0]
        return song
    else:
        return None

def get_lyrics(artist, title):
    try:
        api_url = f'https://api.lyrics.ovh/v1/{artist}/{title}'
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            return data['lyrics']
        else:
            return None
    except Exception as e:
        return None

def mask_lyrics(lyrics, guessed_words):
    words = re.findall(r'\b\w+\b', lyrics)
    masked_lyrics = ' '.join([word if word.lower() in guessed_words else '_' for word in words])
    return masked_lyrics

def update_masked_lyrics(event=None):
    global current_word
    guess = re.sub(r'[^\w\s]', '', entry.get().strip().lower())
    if guess and guess in re.sub(r'[^\w\s]', '', lyrics.lower()).split() and guess not in guessed_words:
        guessed_words.add(guess)
        entry.delete(0, tk.END)
    masked_lyrics = mask_lyrics(lyrics, guessed_words)
    text.config(state=tk.NORMAL)
    text.delete(1.0, tk.END)
    text.insert(tk.END, masked_lyrics)
    text.config(state=tk.DISABLED)
    if '_' not in masked_lyrics:
        text.config(state=tk.NORMAL)
        text.insert(tk.END, '\nCongratulations! You guessed all the words.')
        text.config(state=tk.DISABLED)

def on_key_release(event):
    update_masked_lyrics()

def on_ctrl_backspace(event):
    current_text = entry.get()
    if current_text:
        words = current_text.split()
        if words:
            new_text = ' '.join(words[:-1])
            entry.delete(0, tk.END)
            entry.insert(0, new_text)

def main():
    global lyrics, guessed_words, entry, text, current_word
    song = get_random_morat_song()
    if not song:
        print('Error fetching song.')
        return

    artist = 'Morat'
    title = song['title']
    lyrics = get_lyrics(artist, title)
    if not lyrics:
        print('Error fetching lyrics.')
        return

    guessed_words = set()
    current_word = ''

    root = tk.Tk()
    root.title(f'Guess the lyrics of the song by {artist}')

    text_frame = tk.Frame(root)
    text_frame.pack(fill=tk.BOTH, expand=True)

    text = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, height=20, width=50)
    text.pack(fill=tk.BOTH, expand=True)
    text.config(state=tk.DISABLED)

    entry = tk.Entry(root)
    entry.pack(fill=tk.X)
    entry.bind('<KeyRelease>', on_key_release)
    entry.bind('<Control-BackSpace>', on_ctrl_backspace)

    masked_lyrics = mask_lyrics(lyrics, guessed_words)
    text.config(state=tk.NORMAL)
    text.insert(tk.END, masked_lyrics)
    text.config(state=tk.DISABLED)

    root.mainloop()

if __name__ == '__main__':
    main()