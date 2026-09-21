"""Tests for Person C's work: validation, login gating, and the classify view."""

from unittest.mock import patch

import numpy as np
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase, TestCase

from .validation import UploadError, parse_upload


def make_csv(arr, name="digit.csv"):
    text = "\n".join(",".join(str(v) for v in row) for row in arr)
    return SimpleUploadedFile(name, text.encode("utf-8"))


def raw(content, name="digit.csv"):
    if isinstance(content, str):
        content = content.encode("utf-8")
    return SimpleUploadedFile(name, content)


class ParseUploadTests(SimpleTestCase):
    def assertRejects(self, upload, message_part):
        with self.assertRaises(UploadError) as ctx:
            parse_upload(upload)
        self.assertIn(message_part, str(ctx.exception))

    def test_accepts_zero_to_one_scale(self):
        arr = np.random.rand(28, 28).round(3)
        out = parse_upload(make_csv(arr))
        self.assertEqual(out.shape, (28, 28))
        self.assertLessEqual(out.max(), 1.0)

    def test_scales_zero_to_255(self):
        arr = np.random.randint(0, 256, (28, 28))
        arr[0, 0] = 255
        out = parse_upload(make_csv(arr))
        self.assertAlmostEqual(out.max(), 1.0)

    def test_all_black_image_is_fine(self):
        out = parse_upload(make_csv(np.zeros((28, 28), dtype=int)))
        self.assertEqual(out.max(), 0.0)

    def test_excel_bom_is_ok(self):
        text = "\n".join(",".join(["0"] * 28) for _ in range(28))
        out = parse_upload(raw(b"\xef\xbb\xbf" + text.encode()))
        self.assertEqual(out.shape, (28, 28))

    def test_windows_line_endings_are_ok(self):
        text = "\r\n".join(",".join(["0"] * 28) for _ in range(28))
        self.assertEqual(parse_upload(raw(text)).shape, (28, 28))

    def test_not_csv(self):
        self.assertRejects(make_csv(np.zeros((28, 28), dtype=int), "digit.txt"),
                           "isn't a .csv")

    def test_not_text(self):
        self.assertRejects(raw(b"\xff\xfe\x00\x81\x82", "x.csv"), "readable as text")

    def test_empty_file(self):
        self.assertRejects(raw("", "x.csv"), "empty")

    def test_header_row(self):
        rows = [",".join(f"px{i}" for i in range(28))]
        rows += [",".join(["0"] * 28) for _ in range(28)]
        self.assertRejects(raw("\n".join(rows)), "header row")

    def test_blank_cell(self):
        rows = [",".join(["0"] * 28) for _ in range(28)]
        rows[3] = ",".join(["0"] * 10 + [""] + ["0"] * 17)
        self.assertRejects(raw("\n".join(rows)), "comma-separated numbers")

    def test_wrong_shape(self):
        self.assertRejects(make_csv(np.zeros((27, 28), dtype=int)),
                           "Expected 28x28, got 27 by 28")

    def test_single_row(self):
        self.assertRejects(raw(",".join(["0"] * 28)), "Expected 28x28, got 1 by 28")

    def test_out_of_range(self):
        arr = np.zeros((28, 28), dtype=int)
        arr[5, 5] = 300
        self.assertRejects(make_csv(arr), "between 0 and 255")
        arr[5, 5] = -1
        self.assertRejects(make_csv(arr), "between 0 and 255")

    def test_nan_cell(self):
        arr = np.zeros((28, 28), dtype=int).astype(object)
        arr[2, 2] = "nan"
        self.assertRejects(make_csv(arr), "non-numeric")


class ViewTests(TestCase):
    # Throwaway test-only credentials. The real `dan` account is created with
    # createsuperuser at the terminal, never in code.
    PASSWORD = "test-only-password"

    def setUp(self):
        get_user_model().objects.create_user("tester", password=self.PASSWORD)

    def login(self):
        self.assertTrue(self.client.login(username="tester", password=self.PASSWORD))

    def test_every_page_requires_login(self):
        for url in ("/", "/classify/", "/mock/"):
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302, url)
            self.assertIn("/accounts/login/", response["Location"], url)

    def test_post_requires_login(self):
        response = self.client.post("/classify/", {})
        self.assertEqual(response.status_code, 302)

    def test_classify_page_loads(self):
        self.login()
        self.assertEqual(self.client.get("/classify/").status_code, 200)

    @patch("classifier.views.predict", return_value=np.eye(10, dtype=np.float32)[3])
    def test_valid_upload_is_classified(self, _):
        self.login()
        upload = make_csv(np.random.rand(28, 28).round(3))
        response = self.client.post("/classify/", {"csv_file": upload})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["prediction"], 3)
        self.assertEqual(len(response.context["probabilities"]), 10)
        self.assertTrue(response.context["image_uri"].startswith("data:image/png;base64,"))
        self.assertIsNone(response.context["error"])

    @patch("classifier.views.predict")
    def test_bad_upload_shows_message_not_error_page(self, mock_predict):
        self.login()
        upload = make_csv(np.zeros((27, 28), dtype=int))
        response = self.client.post("/classify/", {"csv_file": upload})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Expected 28x28", response.context["error"])
        mock_predict.assert_not_called()

    def test_submit_with_no_file(self):
        self.login()
        response = self.client.post("/classify/", {})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Choose a .csv", response.context["error"])
