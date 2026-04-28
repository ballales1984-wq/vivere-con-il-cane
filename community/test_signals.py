from django.test import TestCase
from django.contrib.auth.models import User
from community.models import Discussion, Post, Like, Vote, UserReputation, Badge, UserBadge, Category, Notification
from community.signals import check_badges


class SignalDiscussionCreatedTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser")
        self.rep = UserReputation.objects.create(user=self.user, points=0, discussions_created=0)
        self.cat = Category.objects.create(name="Test", slug="test")

    def test_discussion_created_adds_reputation(self):
        disc = Discussion.objects.create(title="Test", author=self.user, category=self.cat, is_approved=True)
        self.rep.refresh_from_db()
        self.assertEqual(self.rep.discussions_created, 1)
        self.assertEqual(self.rep.points, 10)

    def test_discussion_created_awards_badge(self):
        Badge.objects.create(name="Prima Discussione", slug="prima-discussione", requirement_value=1, icon="🔰")
        disc = Discussion.objects.create(title="Test", author=self.user, category=self.cat, is_approved=True)
        self.assertTrue(UserBadge.objects.filter(user=self.user, badge__slug="prima-discussione").exists())


class SignalPostCreatedTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser")
        self.rep = UserReputation.objects.create(user=self.user, points=0, posts_created=0)
        self.cat = Category.objects.create(name="Test", slug="test")
        self.disc = Discussion.objects.create(title="Cat", author=self.user, category=self.cat, is_approved=True)

    def test_post_created_adds_reputation(self):
        Post.objects.create(discussion=self.disc, author=self.user, content="Test")
        self.rep.refresh_from_db()
        self.assertEqual(self.rep.posts_created, 1)
        self.assertEqual(self.rep.points, 2)

    def test_post_created_creates_notification_for_other_author(self):
        other_user = User.objects.create_user(username="other")
        Post.objects.create(discussion=self.disc, author=other_user, content="Reply")
        self.assertTrue(Notification.objects.filter(recipient=self.user, sender=other_user).exists())


class SignalLikeCreatedTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="user1")
        self.user2 = User.objects.create_user(username="user2")
        self.rep = UserReputation.objects.create(user=self.user2, points=0, likes_received=0)
        self.cat = Category.objects.create(name="Test", slug="test")
        self.disc = Discussion.objects.create(title="Test", author=self.user1, category=self.cat, is_approved=True)
        self.post = Post.objects.create(discussion=self.disc, author=self.user2, content="Test")

    def test_like_adds_reputation_to_post_author(self):
        Like.objects.create(user=self.user1, post=self.post)
        self.rep.refresh_from_db()
        self.assertEqual(self.rep.likes_received, 1)
        self.assertEqual(self.rep.points, 1)


class SignalPostDeletedTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser")
        self.rep = UserReputation.objects.create(user=self.user, points=2, posts_created=1)
        self.cat = Category.objects.create(name="Test", slug="test")
        self.disc = Discussion.objects.create(title="Cat", author=self.user, category=self.cat, is_approved=True)
        self.post = Post.objects.create(discussion=self.disc, author=self.user, content="Test")

    def test_post_deleted_removes_reputation(self):
        self.post.delete()
        self.rep.refresh_from_db()
        self.assertEqual(self.rep.posts_created, 0)
        self.assertEqual(self.rep.points, 0)


class SignalVoteCreatedTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="user1")
        self.user2 = User.objects.create_user(username="user2")
        self.rep = UserReputation.objects.create(user=self.user2, points=0, helpful_votes_received=0)
        self.cat = Category.objects.create(name="Test", slug="test")
        self.disc = Discussion.objects.create(title="Test", author=self.user1, category=self.cat, is_approved=True)
        self.post = Post.objects.create(discussion=self.disc, author=self.user2, content="Test")

    def test_upvote_adds_reputation(self):
        Vote.objects.create(post=self.post, user=self.user1, vote_type="up")
        self.rep.refresh_from_db()
        self.assertEqual(self.rep.helpful_votes_received, 1)
        self.assertEqual(self.rep.points, 5)


class BadgeAssignmentTest(TestCase):
    def test_multiple_badges_awarded(self):
        user = User.objects.create_user(username="testuser")
        rep = UserReputation.objects.create(user=user, discussions_created=10, posts_created=25)
        Badge.objects.create(name="Abile Conversatore", slug="abile-conversatore", requirement_value=10, icon="🏆")
        Badge.objects.create(name="Esperto Comunitario", slug="esperto-comunitario", requirement_value=25, icon="🌟")
        Badge.objects.create(name="Collaboratore", slug="collaboratore", requirement_value=5, icon="🤝")
        check_badges(user)
        self.assertEqual(UserBadge.objects.filter(user=user).count(), 3)
