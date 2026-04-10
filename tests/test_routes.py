import unittest

from whispefy.server import build_app


class RouteTests(unittest.TestCase):
    def test_fastapi_routes(self):
        from fastapi.testclient import TestClient

        class DummyApp:
            def __init__(self):
                self.active = False
                self.toggled = 0
                self.stopped = 0

            @property
            def is_active(self):
                return self.active

            def toggle(self):
                self.toggled += 1
                self.active = not self.active

            def stop(self):
                self.stopped += 1

        dummy = DummyApp()
        client = TestClient(build_app(dummy))
        self.assertEqual(client.get("/health").json(), {"status": "ok"})
        self.assertEqual(client.post("/toggle").json(),
                         {"ok": True, "active": True})
        self.assertEqual(client.post("/stop").json(), {"ok": True})
        self.assertEqual(dummy.toggled, 1)
        self.assertEqual(dummy.stopped, 1)


if __name__ == "__main__":
    unittest.main()
