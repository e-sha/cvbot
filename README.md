# Compute Vision Bot (CVBot)

An interface for creating a telegram bot with computer vision.

# Features
1. Provides an interface for sending and receiving data of different types (Text, Image, Video and File).
2. Provides a logger of the input requests.
3. Provides standard commands like `/help` and `/stat`.
4. Provides an interface for receiving images from a webcam with multiple threads.
5. Provides an interface for making Singleton processor that handles requests on a GPU.
6. Allows local testing without telegram usage

# Usage

## Debugging

To debug your bot you can try [TestBot](https://github.com/e-sha/cvbot/blob/master/test_bot.py) instead of [Bot](https://github.com/e-sha/cvbot/blob/master/bot.py).
In this mode the bot receives commands from a file and writes results to the output directory.

Use manage.py to create commands for debugging.

# Example
1. [CamBot](https://github.com/e-sha/cambot) shows an image from a webcam with the detected objects.
