from django.test import TestCase
from .models import Quiz, Question, Choice, Category
import pandas as pd
import io
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch
from django.contrib.auth.models import User
from django.urls import reverse


class QuizModelTest(TestCase):

    def setUp(self):
        # Category
        self.category = Category.objects.create(name='DSA')

        # Create Excel file in memory
        excel_file = io.BytesIO()
        df = pd.DataFrame({
            'Question': ['What is 2*2?', 'What is 4*4?'],
            'A': ['2', '15'],
            'B': ['3', '14'],
            'C': ['4', '10'],
            'D': ['1', '16'],
            'Answer': ['C', 'D']
        })
        df.to_excel(excel_file, index=False, engine="openpyxl")
        excel_file.seek(0)

        # Uploaded file
        self.uploaded_file = SimpleUploadedFile(
            'test_quiz.xlsx',
            excel_file.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

        # Quiz object
        self.quiz = Quiz.objects.create(
            title='Quiz title',
            description='Quiz description',
            category=self.category,
            quiz_file=self.uploaded_file,
        )

    @patch("quiz.models.Quiz.import_quiz_from_excel")
    def test_import_quiz_from_excel(self, mock_import):
        # Mock the DataFrame returned by import function
        mock_df = pd.DataFrame({
            'Question': ['What is 2*2?', 'What is 4*4?'],
            'A': ['2', '15'],
            'B': ['3', '14'],
            'C': ['4', '10'],
            'D': ['1', '16'],
            'Answer': ['C', 'D']
        })

        mock_import.return_value = mock_df

        # Trigger save → import_quiz_from_excel will be called
        self.quiz.save()

        # Assertions quetions and choices created or not
        self.assertEqual(Question.objects.count(), 2)
        self.assertEqual(Choice.objects.count(), 8)

        q1 = Question.objects.get(text='What is 2*2?')
        q2 = Question.objects.get(text='What is 4*4?')

        self.assertEqual(Choice.objects.filter(question=q1).count(), 4)
        self.assertEqual(Choice.objects.filter(question=q2).count(), 4)

    #str
    #additional
    def test_plural_quizzes(self):
        self.assertEqual(str(Quiz._meta.verbose_name_plural), "Quizzes")
        

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from quiz.models import Quiz, Category

class AllQuizTemplateTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')

        self.category1 = Category.objects.create(name='Python')
        self.category2 = Category.objects.create(name='SQL')

        self.quiz1 = Quiz.objects.create(title='Quiz 1', description='Desc 1', category=self.category1)
        self.quiz2 = Quiz.objects.create(title='Quiz 2', description='Desc 2', category=self.category2)

    def test_all_quiz_template(self):
        response = self.client.get(reverse('all_quiz'))
        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'all-quiz.html')

        self.assertIn('quizzes', response.context)
        self.assertIn('categories', response.context)

        self.assertContains(response, 'Quiz 1')
        self.assertContains(response, 'Quiz 2')
        self.assertContains(response, 'Python')
        self.assertContains(response, 'SQL')

    def test_no_quizzes(self):
        Quiz.objects.all().delete()

        response = self.client.get(reverse('all_quiz'))
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, 'There is no quiz available in this category or search.')
        
