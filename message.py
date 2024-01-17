# message.py
import json



class Message:
    def __init__(self, text):
        self.text = text

    def encode_message(self, header, text):
        text_message = {
            "Header": header,
            "Message": text,
        }
        json_message = json.dumps(text_message).encode("utf-8")
        return json_message

    def decode_message(self, text):
        try:
            text_message = json.loads(text)
            return text_message["Header"], text_message['Message']
        except json.decoder.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            print("Problematic JSON text:")
            print(e.doc)


