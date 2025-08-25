from django.shortcuts import render, get_object_or_404
from django.db.models import Count
from blog.models import Post, Tag


def serialize_post(post):
    first_tag = post.tags.all().first()
    return {
        'title': post.title,
        'teaser_text': post.text[:200],
        'author': post.author.username,
        'comments_amount': post.comments_count,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in post.tags.all()],
        'first_tag_title': first_tag.title if first_tag else None,
    }


def serialize_tag(tag):
    return {
        'title': tag.title,
        'posts_with_tag': tag.posts_count,
    }


def index(request):
    most_popular_posts = (
        Post.objects.popular()
        .with_related()[:5]
        .fetch_with_comments_count()
    )

    most_fresh_posts = (
        Post.objects.order_by('-published_at')
        .with_related()[:5]
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
        .with_related()
    )
    post = get_object_or_404(post_qs)

    comments = post.comments.all()
    serialized_comments = [
        {
            'text': comment.text,
            'published_at': comment.published_at,
            'author': comment.author.username,
        }
        for comment in comments
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
        .with_related()[:5]
        .fetch_with_comments_count()
    )

    context = {
        'post': serialized_post,
        'popular_tags': [serialize_tag(t) for t in most_popular_tags],
        'most_popular_posts': [serialize_post(p) for p in most_popular_posts],
    }
    return render(request, 'post-details.html', context)


def tag_filter(request, tag_title):
    tag = get_object_or_404(Tag, title=tag_title)

    most_popular_tags = Tag.objects.popular()[:5]
    most_popular_posts = (
        Post.objects.popular()
        .with_related()[:5]
        .fetch_with_comments_count()
    )

    related_posts = (
        tag.posts.order_by('-published_at')
        .with_related()[:20]
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
