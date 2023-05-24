"""
https://sleeplessbeastie.eu/2019/04/01/how-to-display-php-fpm-pool-information-using-unix-socket-and-python-script/
"""

import json
import socket
import struct
import sys


class FCGIStatusClient:
    """FCGIStatusClient class"""

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
        """Init."""
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
        """Set the socket timeout."""
        self.socket_timeout = timeout
        self.socket.settimeout(self.socket_timeout)

    def connect(self):
        """Connect to the socket."""
        try:
            self.socket.connect(self.socket_path)
        except Exception:
            print(sys.exc_info()[1])
            sys.exit(1)

    def close(self):
        """Close the socket."""
        self.socket.close()

    def define_begin_request(self):
        """Define the begin request."""
        fcgi_begin_request = struct.pack("!HB5x", self.FCGI_RESPONDER, 0)
        fcgi_header = struct.pack(
            "!BBHHBx",
            self.FCGI_VERSION,
            self.FCGI_BEGIN_REQUEST,
            self.request_id,
            len(fcgi_begin_request),
            0,
        )
        return fcgi_header + fcgi_begin_request

    def define_parameters(self):
        """Define the parameters."""
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
        return (
            fcgi_header_start
            + parameters.encode()
            + parameters_padding
            + fcgi_header_end
        )

    def execute(self, fcgi_begin_request, fcgi_params):
        """Exec."""
        try:
            self.socket.send(fcgi_begin_request)
            self.socket.send(fcgi_params)

            header = self.socket.recv(self.FCGI_HEADER_LENGTH)
            (
                _fcgi_version,
                request_type,
                _request_id,
                request_length,
                _request_padding,
            ) = struct.unpack("!BBHHBx", header)

            if request_type == 6:
                raw_status_data = self.socket.recv(request_length)
            else:
                if request_type == 7:
                    raise Exception("Received an error packet.")
                raise Exception("Received unexpected packet type.")
        except Exception:
            print(sys.exc_info()[1])
            sys.exit(2)
        return raw_status_data.decode().split("\r\n\r\n")[1]

    def make_request(self):
        """Make the request."""
        fcgi_begin_request = self.define_begin_request()
        fcgi_params = self.define_parameters()
        self.connect()
        status_data = self.execute(fcgi_begin_request, fcgi_params)
        self.close()
        return status_data


def main():
    """Go Main Go!"""
    client = FCGIStatusClient()
    status_data = client.make_request()
    data = json.loads(status_data)
    msg = (
        f"FPM pool {data['pool']} | total={data['total processes']};40;50 "
        f"active={data['active processes']};40;50 "
        f"queue={data['listen queue']};10;20"
    )
    print(msg)
    return 2 if data["listen queue"] > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
