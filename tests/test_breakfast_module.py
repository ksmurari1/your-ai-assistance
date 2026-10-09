import unittest
from breakfast_module import build_breakfast_messages, validate_breakfast_output
from langchain_core.messages import HumanMessage, SystemMessage

class BreakfastModuleTests(unittest.TestCase):
    def test_messages_use_system_and_human_roles(self):
        messages = build_breakfast_messages("vegetarian")
        self.assertIsInstance(messages[0], SystemMessage)
        self.assertIsInstance(messages[1], HumanMessage)
        self.assertIn("exactly five", messages[0].content.lower())
        self.assertIn("vegetarian", messages[1].content)

    def test_valid_five_numbered_lines(self):
        text = "\n".join(f"{i}. Healthy breakfast idea {i}" for i in range(1, 6))
        self.assertEqual(validate_breakfast_output(text)[0], True)

    def test_rejects_wrong_line_count(self):
        self.assertFalse(validate_breakfast_output("1. One\n2. Two")[0])

    def test_rejects_wrong_numbering(self):
        text = "1. One\n2. Two\n3. Three\n4. Four\n6. Six"
        self.assertFalse(validate_breakfast_output(text)[0])

if __name__ == "__main__":
    unittest.main()
