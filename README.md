# Brumhack60
Mine and C Parker's project for BrumHack6.0.
We called it ItAllChromeInTheFuture, from the Chrome Extension, which was the
actual result of the project.

* handcontrol is the extension.
* slides is the websocket server which powers it all. It also has some stupid
test code, which shows rare pepes to test if the gestures worked.
* displayAndSend.py which draws a test UI and also sends the raw data from the Leap to
the websocket server. You have to edit it to use your own server.

You have to run them all to get the extension to work.
I could only get displayAndSend.py on Linux after manually running leapd and
setting PYTHONPATH to ../lib/ (we ran it from the leap samples directory)

Slides requires setting up a python virtual environment and install several
modules via pip.

Handcontrol is easy enough to run.
