import unittest

from osah.ui.qt.services.format_ai_chat_message_html import format_ai_chat_message_html


class FormatAiChatMessageHtmlTests(unittest.TestCase):
    def test_bullet_lines_render_as_list(self) -> None:
        html_text = format_ai_chat_message_html(
            "AI",
            "Заголовок\n\nПріоритетні записи:\n• Перший\n• Другий",
        )
        self.assertIn("<ul", html_text)
        self.assertIn("<li", html_text)
        self.assertIn("Перший", html_text)
        self.assertIn("Другий", html_text)

    def test_escapes_html_in_user_text(self) -> None:
        html_text = format_ai_chat_message_html("Ви", "<script>alert(1)</script>")
        self.assertNotIn("<script>", html_text)
        self.assertIn("&lt;script&gt;", html_text)


if __name__ == "__main__":
    unittest.main()
