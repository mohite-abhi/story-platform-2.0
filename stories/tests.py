from django.test import TestCase
from django.urls import reverse
from .models import Story
from django.contrib.auth import get_user_model


class StoryListTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create some test stories
        User = get_user_model()
        cls.user = User.objects.create_user(username="testuser", password="testpassword")
        Story.objects.create(title="Test Story 1", content="Content for story 1", status="draft", author=cls.user)
        Story.objects.create(title="Test Story 2", content="Content for story 2", status="published", author=cls.user)

    def test_story_list(self):
        response = self.client.get(reverse("story_list"))
        self.assertEqual(response.status_code, 200)

    # def test_story_list_with_status_filter(self):
    #     response = self.client.get(reverse("story_list") + "?status=draft")
    #     self.assertEqual(response.status_code, 200)
    #     self.assertContains(response, "Test Story 1")
    #     self.assertNotContains(response, "Test Story 2")

    #     response = self.client.get(reverse("story_list") + "?status=published")
    #     self.assertEqual(response.status_code, 200)
    #     self.assertContains(response, "Test Story 2")
    #     self.assertNotContains(response, "Test Story 1")

class StoryDetailTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.user = User.objects.create_user(username="testuser", password="testpassword")
        cls.story = Story.objects.create(title="My Story", author=cls.user, content="My content", status="draft")

    def test_story_detail_returns_200(self):
        response = self.client.get(reverse("story_detail", args=[self.story.id]))
        self.assertEqual(response.status_code, 200)

    def test_story_detail_not_found(self):
        response = self.client.get(reverse("story_detail", args=[999999])) 
        self.assertEqual(response.status_code, 404)


class StoryCreateTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.user = User.objects.create_user(username="testuser", password="testpassword")

    def test_story_creatd_successfully(self):
        self.client.login(username="testuser", password="testpassword")
        story = {
            "title": "My Story",
            "content": "My content",
            "status": "draft"
        }
        story_count = Story.objects.count()
        response = self.client.post(reverse("story_create"), data=story)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Story.objects.count(), story_count+1)

        new_story = Story.objects.last()
        self.assertEqual(new_story.title, story["title"])
        self.assertEqual(new_story.content, story["content"])
        self.assertEqual(new_story.status, story["status"])
        self.assertEqual(new_story.author, self.user)


    def test_story_create_fails_with_short_title(self):
        self.client.login(username="testuser", password="testpassword")
        story = {
            "title": "abc",
            "content": "My content",
            "status": "draft"
        }
        story_count = Story.objects.count()
        response = self.client.post(reverse("story_create"), data=story)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Story.objects.count(), story_count)
        self.assertContains(response, "Title should be at least 5 characters.")


    def test_anonymous_story_create_redirects_to_login(self):
        story = {
            "title": "abc",
            "content": "My content",
            "status": "draft"
        }

        story_count = Story.objects.count()

        response = self.client.post(reverse("story_create"), data=story)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/accounts/login/?next=/stories/create/")
        self.assertEqual(Story.objects.count(), story_count)

class StoryEditTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.alice = User.objects.create_user(username="alice", password="testpassword", email="alice@email.com")
        cls.bob = User.objects.create_user(username="bob", password="testpassword", email="bob@email.com")
        cls.alice_story = Story.objects.create(title="My Story", author=cls.alice, content="My content", status="draft")


    def test_alice_get_story_edit_page_succeeds(self):
        self.client.login(username="alice", password="testpassword")
        response = self.client.get(reverse("story_edit", args=[self.alice_story.id]))
        self.assertEqual(response.status_code, 200)
    

    def test_bob_cannot_get_alices_story_edit_page(self):
        self.client.login(username="bob", password="testpassword")
        response = self.client.get(reverse("story_edit", args=[self.alice_story.id]))
        self.assertEqual(response.status_code, 403)


    def test_bob_cannot_edit_alices_story(self):
        original_title = self.alice_story.title
        self.client.login(username="bob", password="testpassword")
        data = {"title": "Bob hacked this", "content":"My content", "status": "draft"}
        response = self.client.post(reverse("story_edit", args=[self.alice_story.id]), data=data)

        self.assertEqual(response.status_code, 403)

        self.alice_story.refresh_from_db()
        self.assertEqual(original_title, self.alice_story.title)
    

    def test_alice_can_edit_her_story(self):
        self.client.login(username="alice", password="testpassword")

        data = {
            "title": "Updated Story",
            "content": "Updated content",
            "status": "published",
        }

        response = self.client.post(
            reverse("story_edit", args=[self.alice_story.id]),
            data=data,
        )

        self.assertEqual(response.status_code, 302)

        self.alice_story.refresh_from_db()

        self.assertEqual(self.alice_story.title, "Updated Story")
        self.assertEqual(self.alice_story.content, "Updated content")
        self.assertEqual(self.alice_story.status, "published")
        self.assertEqual(self.alice_story.author, self.alice)



class StoryDeleteTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.alice = User.objects.create_user(username="alice", password="testpassword", email="alice@email.com")
        cls.bob = User.objects.create_user(username="bob", password="testpassword", email="bob@email.com")
        cls.alice_story = Story.objects.create(title="My Story", author=cls.alice, content="My content", status="draft")


    def test_bob_cannot_delete_alices_story(self):
        story_id = self.alice_story.id
        self.client.login(username="bob", password="testpassword")

        response = self.client.post(reverse("story_delete", args=[story_id]))

        self.assertEqual(response.status_code, 403)
        self.assertTrue(Story.objects.filter(id=story_id).exists())


    def test_alice_can_delete_her_story(self):
        story_id = self.alice_story.id
        self.client.login(username="alice", password="testpassword")

        response = self.client.post(reverse("story_delete", args=[story_id]))

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Story.objects.filter(id=story_id).exists())


    def test_anonymous_cannot_delete_story(self):
        story_id = self.alice_story.id

        response = self.client.post(reverse("story_delete", args=[story_id]))

        self.assertEqual(response.status_code, 302)

        expected_next = reverse("story_delete", args=[story_id])
        self.assertRedirects(response, f"/accounts/login/?next={expected_next}")
        self.assertTrue(Story.objects.filter(id=story_id).exists())