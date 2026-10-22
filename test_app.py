"""Run with: python -m unittest -v"""
import tempfile
import unittest
from pathlib import Path
from app import create_app


class AllergyAppTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.app = create_app({'TESTING': True, 'SECRET_KEY': 'test-only',
                               'DATABASE': str(Path(self.temp.name) / 'test.sqlite')})
        self.client = self.app.test_client()
        self.client.get('/')
        with self.client.session_transaction() as session:
            self.token = session['csrf_token']

    def tearDown(self):
        self.temp.cleanup()

    def save(self, **overrides):
        data = {'csrf_token': self.token, 'name': 'Alex', 'status': 'yes',
                'allergen': ['Peanuts', 'Milk'], 'reaction': ['Hives', '']}
        data.update(overrides)
        return self.client.post('/', data=data, follow_redirects=True)

    def test_save_edit_export_and_persistence(self):
        self.assertEqual(self.save().status_code, 200)
        self.assertIn(b'Peanuts', self.client.get('/card').data)
        export = self.client.get('/download')
        self.assertIn(b'Reported reaction: Hives', export.data)
        self.assertIn('attachment', export.headers['Content-Disposition'])
        other_browser = self.app.test_client()
        self.assertIn(b'Peanuts', other_browser.get('/').data)
        self.save(allergen=['Sesame'], reaction=[''])
        card = self.client.get('/card').data
        self.assertIn(b'Sesame', card)
        self.assertNotIn(b'Peanuts', card)

    def test_invalid_input_preserves_saved_record(self):
        self.save()
        for fields in [{'name': ' '}, {'status': 'invalid'},
                       {'allergen': ['Peanuts', ' peanuts ']},
                       {'allergen': []}, {'allergen': [' ']},
                       {'reaction': ['x' * 301]}]:
            with self.subTest(fields=fields):
                self.assertEqual(self.save(**fields).status_code, 422)
                self.assertIn(b'Peanuts', self.client.get('/card').data)

    def test_no_and_unknown_clear_previous_allergies(self):
        self.save()
        for status, expected in [('no', b'No known allergies reported'),
                                 ('unsure', b'Allergy status unknown')]:
            self.assertEqual(self.save(status=status).status_code, 200)
            card = self.client.get('/card').data
            self.assertIn(expected, card)
            self.assertNotIn(b'Peanuts', card)

    def test_csrf_and_html_escaping(self):
        self.assertEqual(self.client.post('/', data={'name': 'Alex'}).status_code, 400)
        self.save(name='<script>alert(1)</script>')
        card = self.client.get('/card').data
        self.assertNotIn(b'<script>alert(1)</script>', card)
        self.assertIn(b'&lt;script&gt;', card)
        self.assertEqual(self.client.post('/reset').status_code, 400)

    def test_delete_and_empty_download(self):
        self.assertEqual(self.client.get('/download').status_code, 404)
        self.save()
        self.client.post('/reset', data={'csrf_token': self.token})
        self.assertEqual(self.client.get('/download').status_code, 404)
        self.assertEqual(self.client.get('/card').status_code, 302)


if __name__ == '__main__':
    unittest.main()
