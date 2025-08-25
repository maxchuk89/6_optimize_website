from django.shortcuts import render
from django.db.models import Count, Prefetch
from blog.models import Comment, Post, Tag


def serialize_post(post):
    comments_amount = getattr(post, 'comments_count', None)
    if comments_amount is None:
        comments_amount = len(post.comments.all())
    return {
        'title': post.title,
        'teaser_text': post.text[:200],
        'author': post.author.username,
        'comments_amount': comments_amount,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in post.tags.all()],
        'first_tag_title': post.tags.all()[0].title,
    }


def serialize_tag(tag):
    posts_with_tag = getattr(tag, 'posts_count', None)
    if posts_with_tag is None:
        posts_with_tag = tag.posts.count()
    return {
        'title': tag.title,
        'posts_with_tag': posts_with_tag,
    }


def index(request):
    tag_with_counts = Prefetch(
        'tags',
        queryset=Tag.objects.annotate(posts_count=Count('posts'))
    )

    most_popular_posts = (
        Post.objects.popular()
        .prefetch_related('author', 'comments', tag_with_counts)[:5]
        .fetch_with_comments_count()
    )

    most_fresh_posts = (
        Post.objects.order_by('-published_at')
        .prefetch_related('author', 'comments', tag_with_counts)[:5]
        .fetch_with_comments_count()
    )

    most_popular_tags = Tag.objects.popular()[:5]

    context = {
        'most_popular_posts': [serialize_post(p) for p in most_popular_posts],
        'page_posts': [serialize_post(p) for p in most_fresh_posts],
        'popular_tags': [serialize_tag(t) for t in most_popular_tags],
    }
    return render(request, 'index.html', context)


def post_detail(request, slug):
    post_qs = (
        Post.objects.filter(slug=slug)
        .annotate(likes_count=Count('likes'))
        .prefetch_related(
            Prefetch(
                'comments',
                queryset=Comment.objects.select_related('author')
            ),
            Prefetch(
                'tags',
                queryset=Tag.objects.annotate(posts_count=Count('posts'))
            ),
        )
    )
    post = post_qs.get()

    comments = post.comments.all()
    serialized_comments = [
        {
            'text': c.text,
            'published_at': c.published_at,
            'author': c.author.username,
        }
        for c in comments
    ]

    related_tags = post.tags.all()

    serialized_post = {
        'title': post.title,
        'text': post.text,
        'author': post.author.username,
        'comments': serialized_comments,
        'likes_amount': post.likes_count,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(t) for t in related_tags],
    }

    most_popular_tags = Tag.objects.popular()[:5]
    most_popular_posts = (
        Post.objects.popular()
        .prefetch_related(
            'author',
            'comments',
            Prefetch(
                'tags',
                queryset=Tag.objects.annotate(posts_count=Count('posts'))
            ),
        )[:5]
        .fetch_with_comments_count()
    )

    context = {
        'post': serialized_post,
        'popular_tags': [serialize_tag(t) for t in most_popular_tags],
        'most_popular_posts': [serialize_post(p) for p in most_popular_posts],
    }
    return render(request, 'post-details.html', context)


def tag_filter(request, tag_title):
    tag = Tag.objects.get(title=tag_title)

    most_popular_tags = Tag.objects.popular()[:5]
    most_popular_posts = (
        Post.objects.popular()
        .prefetch_related(
            'author',
            'comments',
            Prefetch(
                'tags',
                queryset=Tag.objects.annotate(posts_count=Count('posts'))
            ),
        )[:5]
        .fetch_with_comments_count()
    )

    related_posts = (
        tag.posts.order_by('-published_at')
        .prefetch_related(
            'author',
            'comments',
            Prefetch(
                'tags',
                queryset=Tag.objects.annotate(posts_count=Count('posts'))
            ),
        )[:20]
        .fetch_with_comments_count()
    )

    context = {
        'tag': tag.title,
        'popular_tags': [serialize_tag(t) for t in most_popular_tags],
        'posts': [serialize_post(p) for p in related_posts],
        'most_popular_posts': [serialize_post(p) for p in most_popular_posts],
    }
    return render(request, 'posts-list.html', context)


def contacts(request):
    return render(request, 'contacts.html', {})
