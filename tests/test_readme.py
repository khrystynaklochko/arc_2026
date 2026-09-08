import unittest
import os

class TestReadmeDocumentation(unittest.TestCase):
    def setUp(self):
        with open('README.md', 'r') as f:
            self.content = f.read()

    def test_project_overview_section(self):
        self.assertIn('Project Overview', self.content, 'AC-1: README missing Project Overview section')

    def test_getting_started_section(self):
        self.assertIn('Getting Started', self.content, 'AC-2: README missing Getting Started section')
        self.assertIn('python', self.content.lower(), 'AC-2: Getting Started section should mention python or running commands')

    def test_evaluation_submission_section(self):
        self.assertIn('Evaluation and Submission', self.content, 'AC-3: README missing Evaluation and Submission section')
        self.assertIn('Kaggle', self.content, 'AC-3: Evaluation and Submission should mention Kaggle')

    def test_content_length(self):
        self.assertGreater(len(self.content), 500, 'AC-4: Documentation content appears too short')

if __name__ == '__main__':
    unittest.main()