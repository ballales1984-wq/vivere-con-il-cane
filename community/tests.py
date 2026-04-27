from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from community.models import (
    Category, Discussion, Post, Like, Vote, 
    Notification, UserReputation, Badge, UserBadge
)
from dog_profile.models import DogProfile

User = get_user_model()


class CommunityViewTests(TestCase):
    """Test per le view della community."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', email='test@test.com', password='testpass'
        )
        self.dog = DogProfile.objects.create(
            owner=self.user, name='Mario', dog_name='Fido', breed='Labrador'
        )
        self.category = Category.objects.create(
            name='Educazione', slug='educazione'
        )
        self.discussion = Discussion.objects.create(
            title='Test discussione',
            content='Contenuto di test',
            author=self.user,
            category=self.category,
            dog=self.dog
        )

    def test_discussion_list_view(self):
        """Test lista discussioni."""
        response = self.client.get(reverse('community:discussion_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'community/list.html')
        self.assertContains(response, 'Test discussione')

    def test_discussion_list_by_category(self):
        """Test filtro per categoria."""
        response = self.client.get(
            reverse('community:discussions_by_category',
                   kwargs={'category_slug': 'educazione'})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Educazione')

    def test_discussion_detail_view(self):
        """Test dettaglio discussione."""
        response = self.client.get(
            reverse('community:discussion_detail',
                   kwargs={'slug': self.discussion.slug})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'community/detail.html')

    def test_discussion_detail_increments_views(self):
        """Test incremento visualizzazioni."""
        initial_views = self.discussion.view_count
        self.client.get(
            reverse('community:discussion_detail',
                   kwargs={'slug': self.discussion.slug})
        )
        self.discussion.refresh_from_db()
        self.assertEqual(self.discussion.view_count, initial_views + 1)

    def test_discussion_create_view_redirects_if_not_logged_in(self):
        """Test creazione discussione richiede login."""
        response = self.client.get(reverse('community:discussion_create'))
        self.assertEqual(response.status_code, 302)

    def test_category_list_view(self):
        """Test lista categorie."""
        response = self.client.get(reverse('community:category_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'community/categories.html')

    def test_user_profile_view(self):
        """Test profilo utente."""
        response = self.client.get(
            reverse('community:user_profile',
                   kwargs={'username': 'testuser'})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'community/user_profile.html')


class CommunityModelTests(TestCase):
    """Test per i modelli della community."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='test@test.com', password='testpass'
        )
        self.dog = DogProfile.objects.create(
            owner=self.user, name='Mario', dog_name='Fido', breed='Labrador'
        )
        self.category = Category.objects.create(
            name='Educazione', slug='educazione'
        )

    def test_discussion_creation(self):
        """Test creazione discussione."""
        discussion = Discussion.objects.create(
            title='Test Discussione',
            content='Contenuto di test',
            author=self.user,
            category=self.category,
            dog=self.dog
        )
        self.assertEqual(discussion.title, 'Test Discussione')
        self.assertEqual(discussion.slug, 'test-discussione')
        self.assertTrue(discussion.is_approved)

    def test_post_creation(self):
        """Test creazione post/risposta."""
        discussion = Discussion.objects.create(
            title='Test Discussione',
            content='Contenuto di test',
            author=self.user,
            category=self.category,
            dog=self.dog
        )
        post = Post.objects.create(
            content='Risposta di test',
            author=self.user,
            discussion=discussion
        )
        self.assertEqual(post.content, 'Risposta di test')
        self.assertEqual(post.discussion, discussion)

    def test_like_creation(self):
        """Test creazione like."""
        discussion = Discussion.objects.create(
            title='Test Discussione',
            content='Contenuto di test',
            author=self.user,
            category=self.category,
            dog=self.dog
        )
        like = Like.objects.create(
            user=self.user,
            content_type='discussion',
            discussion=discussion
        )
        self.assertEqual(like.user, self.user)

    def test_vote_creation(self):
        """Test creazione voto."""
        discussion = Discussion.objects.create(
            title='Test Discussione',
            content='Contenuto di test',
            author=self.user,
            category=self.category,
            dog=self.dog
        )
        post = Post.objects.create(
            content='Risposta di test',
            author=self.user,
            discussion=discussion
        )
        vote = Vote.objects.create(
            user=self.user,
            post=post,
            vote_type='up'
        )
        self.assertEqual(vote.vote_type, 'up')
        self.assertEqual(vote.post, post)

    def test_user_reputation_creation(self):
        """Test creazione reputazione utente."""
        reputation = UserReputation.objects.create(
            user=self.user,
            points=100
        )
        self.assertEqual(reputation.user, self.user)
        self.assertEqual(reputation.level, 1)


class CommunityIntegrationTests(TestCase):
    """Test di integrazione per la community."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', email='test@test.com', password='testpass'
        )
        self.dog = DogProfile.objects.create(
            owner=self.user, name='Mario', dog_name='Fido', breed='Labrador'
        )
        self.category = Category.objects.create(
            name='Educazione', slug='educazione'
        )
        self.discussion = Discussion.objects.create(
            title='Test discussione',
            content='Contenuto di test',
            author=self.user,
            category=self.category,
            dog=self.dog
        )

    def test_create_discussion_and_post_flow(self):
        """Test flusso completo: login, creazione discussione, risposta."""
        self.client.login(username='testuser', password='testpass')
        
        response = self.client.post(
            reverse('community:discussion_create_submit'),
            {
                'title': 'Nuova discussione',
                'content': 'Contenuto nuova discussione',
                'category': self.category.id,
                'dog': self.dog.id
            }
        )
        self.assertEqual(response.status_code, 302)
        
        discussion = Discussion.objects.get(title='Nuova discussione')
        
        response = self.client.post(
            reverse('community:post_create', kwargs={'slug': discussion.slug}),
            {'content': 'Questa e una risposta'}
        )
        self.assertEqual(response.status_code, 302)
        
        post = Post.objects.get(content='Questa e una risposta')
        self.assertEqual(post.discussion, discussion)

    def test_like_toggle(self):
        """Test toggle like su discussione."""
        self.client.login(username='testuser', password='testpass')
        
        response = self.client.post(
            reverse('community:like_toggle'),
            {
                'type': 'discussion',
                'target_id': self.discussion.id
            }
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['liked'])
        self.assertEqual(data['count'], 1)
