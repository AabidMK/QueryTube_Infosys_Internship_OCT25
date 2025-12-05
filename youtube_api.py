from googleapiclient.discovery import build

api_key = "AIzaSyBAcd63DKLbbwM9ODRDY8VeoovbQFfVzAY"

youtube = build('youtube', 'v3', developerKey=api_key)

response = youtube.channels().list(
    part='id,snippet',
    forHandle='@jestsaikiran'
).execute()

print(response)
