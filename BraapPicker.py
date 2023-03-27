import sys
import os
from PyQt6.QtWidgets import QApplication, QWidget, QLineEdit, QPushButton, QTextEdit, QVBoxLayout, QLabel, QCheckBox
from PyQt6.QtGui import QIcon, QKeyEvent

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import random


# enter API Key for Youtube Data V3
API_KEY = "ENTER YOUR API KEY HERE"

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def get_video_id(url):
    if "youtube.com/watch" in url:
        return url.split("=")[1]
    elif "youtu.be" in url:
        return url.split("/")[-1]
    else:
        raise KeyError("Youtube URL nicht zulässig")



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

# Initialze the PyQt Window
class Picker(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BraapPicker")
        self.resize(800,600)
        self.setStyleSheet("background-color: red")

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.inputFieldUrl = QLineEdit()
        self.inputFieldUrl.setStyleSheet("background-color: white")
        self.inputFieldKeyword = QLineEdit()
        self.inputFieldKeyword.setStyleSheet("background-color: white")
        button = QPushButton("Zufälligen Kommentar auswählen", clicked=self.get_random_comment)
        button.setStyleSheet("background-color: gray")
        button.setDefault(True)
        self.output = QTextEdit()
        self.output.setStyleSheet("color: white")
        self.UrlLabel = QLabel("Youtube URL eingeben:")
        self.UrlLabel.setStyleSheet("color: white")
        self.KeywordLabel = QLabel("Nach Keyword filter, oder leer lassen: ")
        self.KeywordLabel.setStyleSheet("color: white")
        self.AuthorCheckbox = QCheckBox("Mehrere Kommentare des selben Nutzers erlauben?")
        self.AuthorCheckbox.setStyleSheet("color: white")

        layout.addWidget(self.UrlLabel)
        layout.addWidget(self.inputFieldUrl)
        layout.addWidget(self.KeywordLabel)
        layout.addWidget(self.inputFieldKeyword)
        layout.addWidget(self.AuthorCheckbox)
        layout.addWidget(self.output)
        layout.addWidget(button)



    def get_random_comment(self):
        
        video_id = get_video_id(self.inputFieldUrl.text())

        keyword = self.inputFieldKeyword.text()

        if not keyword:
            comments = get_comments(video_id, keyword=None)
        comments = get_comments(video_id, keyword=keyword)

        if not self.AuthorCheckbox.isChecked():
            comments= remove_same_author_comments(comments)

        selected_comment, selected_author = "", ""
        comments_analyzed = "Keine Kommentare gefunden"

        if len(comments) > 0:
            selected_comment, selected_author = select_random_comment(comments)
            comments_analyzed = str(len(comments))
            
        self.output.setText(selected_comment + "\n\nvon: " + selected_author + "\n\nKommentare analysiert gesamt: " + comments_analyzed)
        

    def keyPressEvent(self, event):
        if event.key() == 16777220:
            self.get_random_comment()

app = QApplication(sys.argv)
app.setStyleSheet("""
    QWidget {
        font-size: 25px;
    }

    QPushButton {
        font-size 20px;
    }

""")

window = Picker()
window.show()

app.exec()