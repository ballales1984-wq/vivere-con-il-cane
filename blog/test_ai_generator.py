from django.test import TestCase, override_settings
import os
from unittest.mock import patch, MagicMock

from django.test import TestCase, override_settings
from blog.ai_generator import ArticleClassification, DogNewsAggregator, generate_article
from datetime import date


class ArticleClassificationTest(TestCase):
    """Tests for ArticleClassification class."""

    def test_classify_high_importance_health_topic(self):
        importance, length = ArticleClassification.classify(
            "guida completa salute cane"
        )
        self.assertEqual(importance, "high")

    def test_classify_high_importance_emergency(self):
        importance, length = ArticleClassification.classify("emergency situation")
        self.assertEqual(importance, "high")

    def test_classify_medium_importance_news(self):
        importance, length = ArticleClassification.classify(
            "notizia studio nuovo farmaco"
        )
        self.assertEqual(importance, "medium")

    def test_classify_low_importance_generic(self):
        importance, length = ArticleClassification.classify("consigli utili per cani")
        self.assertEqual(importance, "low")

    def test_classify_short_length(self):
        importance, length = ArticleClassification.classify("breve consiglio rapido")
        self.assertEqual(length, "short")

    def test_classify_long_length(self):
        importance, length = ArticleClassification.classify(
            "guida completa approfondita"
        )
        self.assertEqual(length, "long")

    def test_classify_medium_length_default(self):
        importance, length = ArticleClassification.classify("argomento generico")
        self.assertEqual(length, "medium")


class DogNewsAggregatorTest(TestCase):
    """Tests for DogNewsAggregator class."""

    @patch("blog.ai_generator.datetime")
    def test_fetch_latest_news_returns_list(self, mock_datetime):
        mock_datetime.now.return_value = MagicMock()
        mock_datetime.now.return_value.date.return_value = date(2025, 4, 24)
        news = DogNewsAggregator.fetch_latest_news(max_items=5)
        self.assertIsInstance(news, list)
        self.assertEqual(len(news), 3)  # sample_news has 3 items

    @patch("blog.ai_generator.datetime")
    def test_fetch_latest_news_limited(self, mock_datetime):
        mock_datetime.now.return_value = MagicMock()
        mock_datetime.now.return_value.date.return_value = date(2025, 4, 24)
        news = DogNewsAggregator.fetch_latest_news(max_items=2)
        self.assertEqual(len(news), 2)

    def test_fetch_latest_news_structure(self):
        news = DogNewsAggregator.fetch_latest_news()
        if news:
            item = news[0]
            self.assertIn("title", item)
            self.assertIn("summary", item)
            self.assertIn("source", item)
            self.assertIn("date", item)
            self.assertIn("url", item)


class GenerateArticleTest(TestCase):
    """Tests for generate_article function."""

    @patch("blog.ai_generator.OPENAI_API_KEY", "")
    def test_generate_article_without_api_key_returns_sample(self):
        content, importance, length, source = generate_article("alimentazione cane")
        self.assertIn("alimentazione", content.lower())
        self.assertIn("sample", source)
        self.assertIn(importance, ["high", "medium", "low"])
        self.assertIn(length, ["short", "medium", "long", "extended"])

    @patch.dict(os.environ, {"OPENAI_API_KEY": ""})
    def test_generate_article_classification(self):
        content, importance, length, source = generate_article(
            "guida completa salute cane"
        )
        self.assertEqual(importance, "high")
        self.assertEqual(length, "long")

    @patch("blog.ai_generator.OPENAI_API_KEY", "test-key-123")
    @patch("blog.ai_generator.requests.post")
    def test_generate_article_with_openai_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Articolo generato da GPT"}}]
        }
        mock_post.return_value = mock_response

        content, importance, length, source = generate_article(
            "passeggiate cane", importance="medium", length="short"
        )

        self.assertEqual(content, "Articolo generato da GPT")
        self.assertEqual(source, "ai")
        self.assertEqual(importance, "medium")
        self.assertEqual(length, "short")

    @patch("blog.ai_generator.OPENAI_API_KEY", "test-key-123")
    @patch("blog.ai_generator.requests.post")
    def test_generate_article_openai_error(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response

        content, importance, length, source = generate_article("test topic")

        self.assertIn("Error API", content)
        self.assertEqual(source, "error")

    @patch("blog.ai_generator.OPENAI_API_KEY", "test-key-123")
    @patch("blog.ai_generator.requests.post", side_effect=Exception("Network error"))
    def test_generate_article_openai_exception(self, mock_post):
        content, importance, length, source = generate_article("test topic")

        self.assertIn("Error:", content)
        self.assertEqual(source, "error")

    def test_generate_article_explicit_classification(self):
        content, importance, length, source = generate_article(
            "topic", importance="high", length="extended"
        )
        self.assertEqual(importance, "high")
        self.assertEqual(length, "extended")
