import unittest
import time

import edi.core
import edi.emit

class TestCmdRoundtrip(unittest.TestCase):
    def setUp(self):
        edi.core.init()
        edi.core.run_background()

    def tearDown(self):
        edi.core.teardown()

    def test_cmd_recv(self):
        reply = None

        def recv_callback(**args):
            reply = args

        cmd = "test__cmd_recv"
        cmd_body = {"cmd" : cmd, "args" : "" }

        edi.core.register_command(recv_callback, cmd)


        edi.emit.cmd(core.chan, cmd_body)
        time.sleep(2)

        self.assertTrue(cmd_body == reply)
