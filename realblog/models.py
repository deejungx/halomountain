from django.db import models
from django import forms

from modelcluster.fields import ParentalKey, ParentalManyToManyField
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase
from wagtail.core import blocks
from wagtail.core.models import Page, Orderable
from wagtail.core.fields import RichTextField, StreamField
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel, MultiFieldPanel, StreamFieldPanel
from wagtail.images.edit_handlers import ImageChooserPanel

from wagtail.search import index

from wagtailcodeblock.blocks import CodeBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail.snippets.models import register_snippet


# Tags
class BlogPageTag(TaggedItemBase):
    content_object = ParentalKey(
        'BlogPage',
        related_name='tagged_items',
    )


# Category
@register_snippet
class BlogCategory(models.Model):
    name = models.CharField(max_length=255)

    panels = [
        FieldPanel('name'),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'blog categories'


# Index page
class BlogIndexPage(Page):
    intro = RichTextField(blank=True)

    def get_context(self, request):
        # Update context to include only published posts, ordered by reverse-chron
        context = super().get_context(request)
        blogpages = self.get_children().live().order_by('-first_published_at').type(BlogPage)
        mainfeatured = BlogPage.objects.live().filter(tags__name='main').order_by('-first_published_at')[:1]
        featuredpages = BlogPage.objects.live().filter(tags__name='featured').order_by('-first_published_at')[:2]
        context['featuredpages'] = featuredpages
        context['mainfeatured'] = mainfeatured
        context['blogpages'] = blogpages
        return context


# Blog page
class BlogPage(Page):
    date = models.DateField("Post date")
    intro = models.CharField(max_length=250)
    body = StreamField([
        ('first_paragraph', blocks.CharBlock()),
        ('pullquotes', blocks.CharBlock()),
        ('blockquotes', blocks.StructBlock([
            ('quote', blocks.CharBlock()),
            ('cite', blocks.CharBlock()),
            ('cite_link', blocks.URLBlock(required=False)),
        ], template='blocks/bquote.html')),
        ('image', ImageChooserBlock()),
        ('list', blocks.ListBlock(blocks.CharBlock())),
        ('paragraph', blocks.RichTextBlock()),
        ('code', CodeBlock()),
        ('raw_html', blocks.RawHTMLBlock()),
    ])
    tags = ClusterTaggableManager(through=BlogPageTag, blank=True)
    categories = ParentalManyToManyField('realblog.BlogCategory', blank=True)

    def main_image(self):
        gallery_item = self.gallery_images.first()
        if gallery_item:
            return gallery_item.image
        else:
            return None

    search_fields = Page.search_fields + [
        index.SearchField('intro'),
        index.SearchField('body'),
    ]

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('date'),
            FieldPanel('tags'),
            FieldPanel('categories', widget=forms.CheckboxSelectMultiple),
        ], heading="Blog information"),
        FieldPanel('intro'),
        StreamFieldPanel('body'),
        InlinePanel('gallery_images', label="Gallery images"),
    ]

    parent_page_types = [BlogIndexPage, ]


# Image gallery
class BlogPageGalleryImage(Orderable):
    page = ParentalKey(BlogPage, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ForeignKey(
        'wagtailimages.Image', on_delete=models.CASCADE, related_name='+'
    )
    caption = models.CharField(blank=True, max_length=250)

    panels = [
        ImageChooserPanel('image'),
        FieldPanel('caption'),
    ]


# Tag Index Page
class BlogTagIndexPage(Page):

    def get_context(self, request):

        # Filter by tag
        tag = request.GET.get('tag')
        blogpages = BlogPage.objects.filter(tags__name=tag)

        # Update template context
        context = super().get_context(request)
        context['blogpages'] = blogpages
        return context


class FeaturedPage(Page):

    def get_context(self, request):
        mainfeatured = BlogPage.objects.live().filter(tags__name='main').order_by('-first_published_at')[:1]
        featuredpages = BlogPage.objects.live().filter(tags__name='featured').order_by('-first_published_at')[:2]
        context = super().get_context(request)
        context['featuredpages'] = featuredpages
        context['mainfeatured'] = mainfeatured
        return context


# Category page
class CategoryPage(Page):

    def get_context(self, request):
        # Filter by Category
        category = request.GET.get('category')
        blogpages = BlogPage.objects.filter(categories__name=category)
        # Update template context
        context = super().get_context(request)
        context['blogpages'] = blogpages
        return context


class AboutPage(Page):
    intro = models.CharField(max_length=300)
    description = RichTextField()

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
        FieldPanel('description', classname='full'),
    ]
