# https://sleeplessbeastie.eu/2019/04/01/how-to-display-php-fpm-pool-information-using-unix-socket-and-python-script/

import json
import sys
import socket
import struct


class FCGIStatusClient:
    # FCGI protocol version
    FCGI_VERSION = 1

    # FCGI record types
    FCGI_BEGIN_REQUEST = 1
    FCGI_PARAMS = 4

    # FCGI roles
    FCGI_RESPONDER = 1

    # FCGI header length
    FCGI_HEADER_LENGTH = 8

    def __init__(
        self,
        socket_path="/var/run/php-fpm/www.sock",
        socket_timeout=5.0,
        status_path="/status",
    ):
        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.socket_path = socket_path
        self.set_socket_timeout(socket_timeout)
        self.status_path = status_path
        self.request_id = 1

        self.params = {
            "SCRIPT_NAME": status_path,
            "SCRIPT_FILENAME": status_path,
            "QUERY_STRING": "json",
            "REQUEST_METHOD": "GET",
        }

    def set_socket_timeout(self, timeout):
        self.socket_timeout = timeout
        self.socket.settimeout(self.socket_timeout)

    def connect(self):
        try:
            self.socket.connect(self.socket_path)
        except Exception:
            print(sys.exc_info()[1])
            sys.exit(1)

    def close(self):
        self.socket.close()

    def define_begin_request(self):
        fcgi_begin_request = struct.pack("!HB5x", self.FCGI_RESPONDER, 0)
        fcgi_header = struct.pack(
            "!BBHHBx",
            self.FCGI_VERSION,
            self.FCGI_BEGIN_REQUEST,
            self.request_id,
            len(fcgi_begin_request),
            0,
        )
        self.fcgi_begin_request = fcgi_header + fcgi_begin_request

    def define_parameters(self):
        parameters = []
        for name, value in self.params.items():
            parameters.append(chr(len(name)) + chr(len(value)) + name + value)

        parameters = "".join(parameters)
        parameters_length = len(parameters)
        parameters_padding_req = parameters_length & 7
        parameters_padding = b"\x00" * parameters_padding_req

        fcgi_header_start = struct.pack(
            "!BBHHBx",
            self.FCGI_VERSION,
            self.FCGI_PARAMS,
            self.request_id,
            parameters_length,
            parameters_padding_req,
        )
        fcgi_header_end = struct.pack(
            "!BBHHBx",
            self.FCGI_VERSION,
            self.FCGI_PARAMS,
            self.request_id,
            0,
            0,
        )
        self.fcgi_params = (
            fcgi_header_start
            + parameters.encode()
            + parameters_padding
            + fcgi_header_end
        )

    def execute(self):
        try:
            self.socket.send(self.fcgi_begin_request)
            self.socket.send(self.fcgi_params)

            header = self.socket.recv(self.FCGI_HEADER_LENGTH)
            (
                fcgi_version,
                request_type,
                request_id,
                request_length,
                request_padding,
            ) = struct.unpack("!BBHHBx", header)

            if request_type == 6:
                self.raw_status_data = self.socket.recv(request_length)
            else:
                self.raw_status_data = ""
                if request_type == 7:
                    raise Exception("Received an error packet.")
                else:
                    raise Exception("Received unexpected packet type.")
        except Exception:
            print(sys.exc_info()[1])
            sys.exit(2)
        self.status_data = self.raw_status_data.decode().split("\r\n\r\n")[1]

    def make_request(self):
        self.define_begin_request()
        self.define_parameters()
        self.connect()
        self.execute()
        self.close()

    def print_status(self):
        print(self.status_data)


def main():
    """Go Main Go!"""
    client = FCGIStatusClient()
    client.make_request()
    data = json.loads(client.status_data)
    msg = (
        f"FPM pool {data['pool']} | total={data['total processes']};40;50 "
        f"active={data['active processes']};40;50 "
        f"queue={data['listen queue']};10;20"
    )
    print(msg)
    return 0 if data["listen queue"] < 0 else 2


if __name__ == "__main__":
    sys.exit(main())
