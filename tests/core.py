import unittest
from mock import MagicMock
import time

import edi.core
import edi.emit


class TestCmdRoundtrip(unittest.TestCase):
    def setUp(self):
        self.cmd = "edilib_test_command"
        edi.core.init()


    def tearDown(self):
        edi.core.teardown()

    def test_cmd_recv(self):
        cmd_body = {"cmd" : self.cmd,
                    "args" : "" }

        f = MagicMock()
        edi.core.register_command(f, self.cmd)

        edi.emit.cmd(edi.core.chan, **cmd_body)

        edi.core.chan.wait()
        f.assert_called_with(**cmd_body)
