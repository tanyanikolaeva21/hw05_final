from django.test import TestCase


class ViewTestClass(TestCase):
    def test_error_page(self):
        response = self.client.get('/none/')
        self.assertEqual(response.status_code, 404)

    def test_about_url_uses_correct_template(self):
        """Проверка шаблона для адреса none."""
        response = self.client.get('/none/')
        self.assertTemplateUsed(response, 'core/404.html')
