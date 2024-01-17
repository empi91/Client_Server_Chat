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

    def process_message(self, header):
        match header:
            case "credentials":
                return "login"
            case "type":
                pass
            case "help":
                comm_dict = {
                    "help": "Displays list of all server commands",
                    "uptime": "Returns server lifetime",
                    "info": "Returns server version and start date",
                    "stop": "Stops server and client simultaneously"
                }
                return comm_dict

            case "uptime":
                uptime_dict = {
                    "Server uptime": self.calc_uptime(),
                }
                return uptime_dict

            case "info":
                info_dict = {
                    "Server version": self.SERVER_VERSION,
                    "Server start date": f"{self.start_time.tm_year}/{self.start_time.tm_mon}/{self.start_time[2]} {self.start_time.tm_hour}:{self.start_time.tm_min}:{self.start_time.tm_sec}"
                }
                return info_dict

            case "stop":
                shutdown = True
                return shutdown
            case _:
                error_msg = "Wrong command, try again"
                return error_msg

