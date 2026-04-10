import unittest
from unittest.mock import patch

from whispefy.insertion import WaylandInserter


class InsertionTests(unittest.TestCase):
    @patch("whispefy.insertion.subprocess.run")
    @patch("whispefy.insertion.shutil.which")
    def test_wayland_insert_paths(self, which, run):
        which.return_value = "/usr/bin/tool"
        WaylandInserter().insert("hello")
        self.assertEqual(run.call_count, 1)
        self.assertEqual(run.call_args_list[0].args[0], ["wtype", "-"])

        run.reset_mock()
        run.side_effect = [RuntimeError("boom"), None, None]
        WaylandInserter().insert("hello")
        self.assertEqual(run.call_count, 3)
        self.assertEqual(
            run.call_args_list[1].args[0], ["wl-copy", "--type", "text/plain"]
        )
        self.assertEqual(
            run.call_args_list[2].args[0],
            ["wtype", "-M", "ctrl", "-k", "v", "-m", "ctrl"],
        )


if __name__ == "__main__":
    unittest.main()
