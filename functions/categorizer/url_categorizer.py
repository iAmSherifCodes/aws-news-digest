def get_category_from_url(posts):
    """Extract category from AWS blog post URLs and update each post.
    
    Args:
        posts (list): List of post objects with 'url' field
    """
    print("Extracting categories from URLs...")
    base_url = "https://aws.amazon.com/blogs/"
    categories = set()
    for post in posts:
        url = post.get('url', '')
        if base_url in url:
            category = url.replace(base_url, '').split('/')[0]
            post['category'] = category
            categories.add(category)
        else:
            post['category'] = 'unknown'
    return posts, list(categories)