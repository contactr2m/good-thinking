from __future__ import unicode_literals

from django.db import models
from django.db.models.fields import TextField

from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailadmin.edit_handlers import FieldPanel


class HomePage(Page):
    banner = RichTextField(blank=True, help_text="Banner at the top of every page")
    body = RichTextField(blank=True, help_text="Description of page")
    lookingfor = RichTextField(blank=True, help_text="Information on how to leave suggestions and what the suggestions are for")
    alpha = RichTextField(blank=True, help_text="What is Alpha")
    alphatext = RichTextField(blank=True, help_text="Why to take part in the alpha")
    footer = RichTextField(blank=True, help_text="Footer text")

    content_panels = Page.content_panels + [
        FieldPanel('banner', classname="full"),
        FieldPanel('body', classname="full"),
        FieldPanel('lookingfor', classname="full"),
        FieldPanel('alpha', classname="full"),
        FieldPanel('alphatext', classname="full"),
        FieldPanel('footer', classname="full"),
    ]
