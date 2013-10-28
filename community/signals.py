from django.contrib.auth import get_user_model
from django.contrib.comments.models import Comment
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save
from django.dispatch import receiver

from mezzanine.generic.models import Rating, ThreadedComment

from posts.models import PostType, News, Picture
from models import KarmaAction, KarmaChange


@receiver(post_save, sender=Rating)
def new_rating(sender, instance, signal, created, **kwargs):
    if isinstance(instance.content_object, ThreadedComment)
    and isinstance(instance.content_object.content_object, PostType):
        try:
            user = get_user_model().objects.get(pk=instance.user.id)

            object_id = instance.content_object.id
            post = instance.content_object.content_object

            if post.status == 3:
                if int(instance.value) > 0:
                    action_id = 'post_positive_comment'
                else:
                    action_id = 'post_negative_comment'

                output = user.change_karma(action_id,
                                           content_type=instance.content_type,
                                           object_id=object_id)

        except KarmaAction.DoesNotExist:
            pass
