from Dhelpers.launcher import launch


def call(text):
    launch("termux-tts-speak", text)