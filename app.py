import subprocess
import wave
from datetime import datetime
from socket import *
import re

from flask import Flask, request

app = Flask(__name__)

terra_socket = socket()
terra_host = "127.0.0.1"
terra_port = 7654
terra_socket.connect((terra_host, terra_port))  # connect to the server


def parse(input_string: bytes) -> list[tuple[int, str]]:
    """Parses the input string into a list of (time, shape) tuples.

   Args:
       input_string: The string to parse.

   Returns:
       A list of (time, shape) tuples.
   """

    parsed = re.findall(b"(.*)\\t(.)", input_string)  # Use raw string for regex
    mouth_shapes = []
    for time_str, shape in parsed:
        time = int(float(time_str) * 1000)  # Convert time to integer milliseconds
        mouth_shapes.append((time, shape))
    return mouth_shapes


@app.route('/', methods=['POST'])
def receive_post():  # put application's code here
    global terra_socket
    now = datetime.now()
    format_string = "%Y-%m-%d_%H:%M:%S"
    datetime_str = now.strftime(format_string)
    filename = datetime_str + ".wav"
    # Get the uploaded file
    wav_file = request.files['wavFile']

    # Save the file (optional)
    wav_file.save(filename)

    print("file received")

    # ./rhubarb/welcome.wav
    command = "./rhubarb/rhubarb --extendedShapes \"\" -q " + filename
    unparsed_mouth_shapes = subprocess.check_output(command, shell=True)
    print(unparsed_mouth_shapes)
    parsed_mouth_shapes = b""
    for (time, shape) in parse(unparsed_mouth_shapes):
        parsed_mouth_shapes += str(time).encode() + b" " + shape + b"\r\n"
    print(parsed_mouth_shapes)
    terra_socket.sendall(parsed_mouth_shapes + b"\r\n")
    return_code = terra_socket.recv(1024)
    if return_code:
        return "OK", 200
    else:
        return "Internal Server Error", 503


if __name__ == '__main__':
    app.run()
