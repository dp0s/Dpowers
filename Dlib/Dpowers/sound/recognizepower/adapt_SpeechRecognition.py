from ... import DependencyManager


with DependencyManager(__name__) as manager:
    sd = manager.import_module("sounddevice")
            #this is important because it suppresses error messages
    sr = manager.import_module("speech_recognition")

recognizer = sr.Recognizer()

def recognize(language):
    with sr.Microphone() as source:
        audio = recognizer.listen(source)
    # recognize speech using whisper
    try:
        return recognizer.recognize_faster_whisper(audio, language=language)
    except sr.UnknownValueError:
        print("Whisper could not understand audio")
        raise
    except sr.RequestError as e:
        print(f"Could not request results from Whisper; {e}")
        raise