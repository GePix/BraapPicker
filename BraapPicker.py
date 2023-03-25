from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import tkinter as tk
from tkinter import Label, Entry, BooleanVar, Checkbutton, Button
import random


# enter API Key for Youtube Data V3
API_KEY = "ADD API KEY HERE"


def get_video_id(url):
    if "youtube.com/watch" in url:
        return url.split("=")[1]
    elif "youtu.be" in url:
        return url.split("/")[-1]
    else:
        raise ValueError("Invalid YouTube URL")



def get_youtube_service(api_version='v3'):
    try:
        youtube = build('youtube', api_version, developerKey=API_KEY, static_discovery=False)
        return youtube
    except HttpError as error:
        print(f'An error occurred: {error}')
        return None

def get_comments(video_id, keyword):
    youtube = get_youtube_service()

    # retrieve the top-level comments for the video
    results = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        textFormat="plainText",
    ).execute()

    comments = []

    # iterate over the top-level comments and add them to the list
    while results:
        for item in results["items"]:
            comment = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
            author = item['snippet']['topLevelComment']['snippet']['authorDisplayName']
            if keyword is None or keyword.lower() in comment.lower():
                comments.append((comment, author))

        # check if there are more comments to retrieve
        if "nextPageToken" in results:
            next_page_token = results["nextPageToken"]
            results = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                pageToken=next_page_token,
                textFormat="plainText",
            ).execute()
        else:
            break

    return comments

# remove comments from the same authors
def remove_same_author_comments(comments):
    seen_authors = set()
    filtered_comments = []
    counter = 0

    authors = [comment[1] for comment in comments]

    for comment in comments:
        author=authors[counter]
        counter += 1
        if author not in seen_authors:
            filtered_comments.append(comment)
            seen_authors.add(author)

    return filtered_comments

# select a random comment from the list
def select_random_comment(comments):
    random_comment, random_author = None, None
    if comments:
        random_comment_author_pair = random.choice(comments)
        if len(random_comment_author_pair) == 2:
            random_comment, random_author = random_comment_author_pair
        else:
            random_comment = random_comment_author_pair[0]
    return random_comment, random_author


def main():
    # create the GUI window
    window = tk.Tk()
    window.title("BraapPicker")
    window.geometry("800x600")
    window.configure(background="red4")

    url_label = tk.Label(window, text="Youtube URL eingeben:")
    url_label.configure(background="red4", foreground="white")
    url_label.pack(padx=10, pady=10, anchor="w")
    url_entry = tk.Entry(window, width=100)
    url_entry.configure(background="grey80")
    url_entry.bind("<Return>", lambda event: get_random_comment())
    url_entry.pack(padx=10, pady=10, anchor="w")

    keyword_label = tk.Label(window, text="Nach spezifischem Keyword suchen (oder leer lassen):")
    keyword_label.configure(background="red4", foreground="white")
    keyword_label.pack(padx=10, pady=10, anchor="w")
    keyword_entry = tk.Entry(window, width=50)
    keyword_entry.configure(background="grey80")
    keyword_entry.bind("<Return>", lambda event: get_random_comment())
    keyword_entry.pack(padx=10, pady=10, anchor="w")

    allow_same_author = tk.BooleanVar()
    allow_same_author_checkbox = tk.Checkbutton(window, text="Mehrere Kommentare des selben Nutzers erlauben?", variable=allow_same_author)
    allow_same_author_checkbox.configure(background="red4", foreground="white")
    allow_same_author_checkbox.pack(padx=10, pady=10, anchor="w")

    count_label = tk.Label(window, text="")
    count_label.configure(background="red4", foreground="white")
    count_label.pack(padx=10, anchor="w")

    comment_label = tk.Label(window, width=100,  text="")
    comment_label.configure(background="red4", foreground="white")
    comment_label.pack(padx=10, pady=20, anchor="w")

    author_label = tk.Label(window, text="")
    author_label.configure(background="red4", foreground="white")
    author_label.pack(padx=10, anchor="w")

    # create a button to select a random comment
    def get_random_comment():
        video_id = get_video_id(url_entry.get())

        keyword = keyword_entry.get()
        if not keyword:
            comments = get_comments(video_id, keyword=None)
        comments = get_comments(video_id, keyword=keyword)

        # filter out comments from the same author if necessary
        if not allow_same_author.get():
            comments = remove_same_author_comments(comments)

        count_label.config(text=f"Kommentare analysiert gesamt: {len(comments)}")

        # select a random comment from the remaining comments
        selected_comment, selected_author = select_random_comment(comments)

        comment_label.config(text=f"{selected_comment} \n")
        author_label.config(text=f"Von: {selected_author}")

    select_button = tk.Button(window, text="Zufälligen Kommentar auswählen", command=get_random_comment)
    select_button.configure(background="white")
    select_button.pack(side=tk.BOTTOM,anchor="se" ,pady=10, padx=10)

    # GUI main loop
    window.mainloop()

if __name__ == "__main__":
    main()
