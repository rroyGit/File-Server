
import pytest

from file_server.web.endpoints.directory_contents import DirectoryContentsEndpoint
from file_server.util import create_object
from file_server.util.test_util import start_test_server, send_api_request
from file_server.web.account import Account

import os, inspect, json

def test_directory_contents():

    server = start_test_server()

    # Signup so we have authentication for directorycontents
    response = send_api_request("signup", {"name": "test", "password": "test"})
    assert response is not None

    response = json.loads(response)
    assert "session" in response

    session = response["session"]

    # Verify correct response
    response = send_api_request("directorycontents", {"path": "./"}, session)
    assert response is not None
    assert response == str(server.hub_processor.snapshot)

    response = send_api_request("directorycontents", {"path": "./hello"}, session)
    assert response is not None

    response = json.loads(response)
    assert "error" in response
    assert response["error"] == "Could not load path"

    server.kill()