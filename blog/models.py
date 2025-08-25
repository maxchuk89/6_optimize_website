from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models import Prefetch


class PostQuerySet(models.QuerySet):
    def year(self, value):
        return self.filter(published_at__year=value)

    def popular(self):
        return self.annotate(likes_count=models.Count('likes')) \
                   .order_by('-likes_count')

    def with_comments_count(self):
        return self.annotate(comments_count=models.Count('comments'))

    def fetch_with_comments_count(self):
        return self.with_comments_count()

    def with_related(self):
        tag_with_counts = Prefetch(
            'tags',
            queryset=Tag.objects.annotate(posts_count=models.Count('posts'))
        )
        comments_with_authors = Prefetch(
            'comments',
            queryset=Comment.objects.select_related('author')
        )
        return (self
                .select_related('author')
                .prefetch_related(comments_with_authors, tag_with_counts))


class Post(models.Model):
    title = models.CharField('Заголовок', max_length=200)
    text = models.TextField('Текст')
    slug = models.SlugField('Название в виде url', max_length=200)
    image = models.ImageField('Картинка')
    published_at = models.DateTimeField('Дата и время публикации')

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        limit_choices_to={'is_staff': True}
    )
    likes = models.ManyToManyField(
        User,
        related_name='liked_posts',
        verbose_name='Кто лайкнул',
        blank=True
    )
    tags = models.ManyToManyField(
        'Tag',
        related_name='posts',
        verbose_name='Теги'
    )

    objects = PostQuerySet.as_manager()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post_detail', args={'slug': self.slug})

    class Meta:
        ordering = ['-published_at']
        verbose_name = 'пост'
        verbose_name_plural = 'посты'


class TagQuerySet(models.QuerySet):
    def popular(self):
        return self.annotate(posts_count=models.Count('posts')) \
                   .order_by('-posts_count')


class Tag(models.Model):
    title = models.CharField('Тег', max_length=20, unique=True)

    objects = TagQuerySet.as_manager()

    def __str__(self):
        return self.title

    def clean(self):
        self.title = self.title.lower()

    def get_absolute_url(self):
        return reverse('tag_filter', args={'tag_title': self.slug})

    class Meta:
        ordering = ['title']
        verbose_name = 'тег'
        verbose_name_plural = 'теги'


class Comment(models.Model):
    post = models.ForeignKey(
        'Post',
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост, к которому написан'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )

    text = models.TextField('Текст комментария')
    published_at = models.DateTimeField('Дата и время публикации')

    def __str__(self):
        return f'{self.author.username} under {self.post.title}'

    class Meta:
        ordering = ['published_at']
        verbose_name = 'комментарий'
        verbose_name_plural = 'комментарии'
