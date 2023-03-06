import unittest
import server


class MyTestCase(unittest.TestCase):
    def test_add_buttons(self):
        with open("test/add_buttons.in.htm", "r") as htm_f:
            htm_in = htm_f.read()
        with open("test/add_buttons.out.htm", "r") as htm_f:
            htm_out = htm_f.read()
        self.assertEqual(htm_out, server.add_buttons(htm_in, "vec_ops", "STATS_STR"))


if __name__ == '__main__':
    unittest.main()
