import json
import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the functions directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'functions', 'scraper'))

import app

class TestScraper(unittest.TestCase):
    @patch('app.requests.get')
    @patch('app.save_posts_to_dynamodb')
    def test_scrape_aws_blog(self, mock_save, mock_get):
        # Mock the response from requests.get
        mock_response = MagicMock()
        mock_response.content = """
        <html>
            <body>
                <article class="blog-post">
                    <h2 class="blog-post-title"><a href="https://aws.amazon.com/blogs/aws/test-post/">Test Post</a></h2>
                </article>
            </body>
        </html>
        """
        mock_get.return_value = mock_response
        
        # Mock the get_post_content function
        app.get_post_content = MagicMock(return_value="Test content")
        
        # Call the function
        result = app.scrape_aws_blog()
        
        # Assert
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['title'], 'Test Post')
        self.assertEqual(result[0]['url'], 'https://aws.amazon.com/blogs/aws/test-post/')
        self.assertEqual(result[0]['content'], 'Test content')
        
    @patch('app.scrape_aws_blog')
    @patch('app.save_posts_to_dynamodb')
    def test_lambda_handler(self, mock_save, mock_scrape):
        # Mock the scrape_aws_blog function
        mock_scrape.return_value = [
            {
                'id': '123',
                'title': 'Test Post',
                'url': 'https://aws.amazon.com/blogs/aws/test-post/',
                'content': 'Test content',
                'timestamp': '2023-01-01T00:00:00'
            }
        ]
        
        # Call the lambda_handler
        result = app.lambda_handler({}, {})
        
        # Assert
        self.assertEqual(result['statusCode'], 200)
        body = json.loads(result['body'])
        self.assertEqual(body['message'], 'Successfully scraped 1 AWS blog posts')
        self.assertEqual(len(body['posts']), 1)
        self.assertEqual(body['posts'][0]['title'], 'Test Post')

if __name__ == '__main__':
    unittest.main()