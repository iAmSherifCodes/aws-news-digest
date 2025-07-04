import os

def get_category_from_url(posts):
    base_url = os.environ.get('AWS_BLOGS_BASE_URL')
    unknown_category = os.environ.get('UNKNOWN_CATEGORY', 'unknown')
    categories = set()
    for post in posts:
        url = post.get('url', '')
        if base_url in url:
            category = url.replace(base_url, '').split('/')[0]
            post['category'] = category
            categories.add(category)
        else:
            post['category'] = unknown_category
    return posts, list(categories)