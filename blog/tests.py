from django.test import TestCase
from django.urls import reverse
from blog.models import Category, BlogPost


class CategoryModelTest(TestCase):
    def test_category_str(self):
        cat = Category(name="Alimentazione")
        self.assertEqual(str(cat), "Alimentazione")

    def test_category_slug_auto_generated(self):
        cat = Category(name="Cura e Salute")
        cat.save()
        self.assertEqual(cat.slug, "cura-e-salute")

    def test_category_slug_unique(self):
        cat1 = Category(name="Training")
        cat1.save()
        cat2 = Category(name="training")
        with self.assertRaises(Exception):
            cat2.save()


class BlogPostModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Test Category")

    def test_blog_post_str(self):
        post = BlogPost(title="Come addestrare il cane", category=self.category)
        self.assertEqual(str(post), "Come addestrare il cane")

    def test_blog_post_slug_auto_generated(self):
        post = BlogPost(title="Il mio primo articolo", category=self.category)
        post.save()
        self.assertEqual(post.slug, "il-mio-primo-articolo")

    def test_blog_post_default_values(self):
        post = BlogPost(title="Test", category=self.category)
        post.save()
        self.assertEqual(post.status, "published")
        self.assertEqual(post.importance, "medium")
        self.assertEqual(post.length, "medium")
        self.assertEqual(post.source, "manual")
        self.assertEqual(post.votes_count, 0)


class BlogPostViewTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Test Cat")
        self.post = BlogPost.objects.create(
            title="Test Post",
            content="Test content",
            category=self.category,
            status="published",
        )

    def test_blog_list_view(self):
        response = self.client.get("/blog/")
        self.assertEqual(response.status_code, 200)

    def test_blog_post_detail_view(self):
        response = self.client.get(f"/blog/{self.post.slug}/")
        self.assertEqual(response.status_code, 200)

    def test_home_page_view(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)


class BlogVoteTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Vote Test Cat")
        self.post = BlogPost.objects.create(
            title="Votami",
            content="Content",
            category=self.category,
            status="published",
        )
        self.post.save()

    def test_vote_view(self):
        response = self.client.post(
            f"/blog/vote/{self.post.id}/", HTTP_X_FORWARDED_FOR="192.168.1.1"
        )
        self.assertEqual(response.status_code, 200)
        self.post.refresh_from_db()
        self.assertEqual(self.post.votes_count, 1)

    def test_duplicate_vote_blocked(self):
        self.client.post(
            f"/blog/vote/{self.post.id}/", HTTP_X_FORWARDED_FOR="192.168.1.1"
        )
        self.client.post(
            f"/blog/vote/{self.post.id}/", HTTP_X_FORWARDED_FOR="192.168.1.1"
        )
        self.post.refresh_from_db()
        self.assertEqual(self.post.votes_count, 1)

    def test_duplicate_vote_blocked(self):
        self.client.post(
            f"/blog/vote/{self.post.id}/", HTTP_X_FORWARDED_FOR="192.168.1.1"
        )
        self.client.post(
            f"/blog/vote/{self.post.id}/", HTTP_X_FORWARDED_FOR="192.168.1.1"
        )
        self.post.refresh_from_db()
        self.assertEqual(self.post.votes_count, 1)

    def test_duplicate_vote_blocked(self):
        self.client.post(
            f"/blog/vote/{self.post.id}/", HTTP_X_FORWARDED_FOR="192.168.1.1"
        )
        self.client.post(
            f"/blog/vote/{self.post.id}/", HTTP_X_FORWARDED_FOR="192.168.1.1"
        )
        self.post.refresh_from_db()
        self.assertEqual(self.post.votes_count, 1)
