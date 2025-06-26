import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from playwright.async_api import async_playwright, Page, Browser, Playwright, BrowserContext
from playwright.async_api import TimeoutError as PlaywrightTimeoutError


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/blog_scraper.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

TARGET_DATE = datetime.now().strftime("%m/%d/%Y")

class BlogScraperError(Exception):
    """Custom exception for blog scraper errors."""
    pass

class BlogScraper:
    """AWS Blog scraper with proper error handling and logging."""
    
    def __init__(self, target_date: str = TARGET_DATE, max_loads: int = 50, timeout: int = 60000):
        self.target_date = target_date
        self.max_loads = max_loads
        self.timeout = timeout
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self._initialize_browser()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit with proper cleanup."""
        await self._cleanup()
        if exc_type:
            logger.error(f"Exception occurred: {exc_type.__name__}: {exc_val}")
    
    async def _initialize_browser(self) -> None:
        """Initialize browser and page with comprehensive configuration."""
        try:
            logger.info("Initializing browser with optimized configuration...")
            self.playwright = await async_playwright().start()
            
            # Launch browser with all necessary parameters for robust scraping
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=[
                    "--disable-gpu",
                    "--no-sandbox",
                    "--single-process",
                    "--disable-dev-shm-usage",
                    "--no-zygote",
                    "--disable-setuid-sandbox",
                    "--disable-accelerated-2d-canvas",
                    "--disable-dev-shm-usage",
                    "--no-first-run",
                    "--no-default-browser-check",
                    "--disable-background-networking",
                    "--disable-background-timer-throttling",
                    "--disable-client-side-phishing-detection",
                    "--disable-component-update",
                    "--disable-default-apps",
                    "--disable-domain-reliability",
                    "--disable-features=AudioServiceOutOfProcess",
                    "--disable-hang-monitor",
                    "--disable-ipc-flooding-protection",
                    "--disable-popup-blocking",
                    "--disable-prompt-on-repost",
                    "--disable-renderer-backgrounding",
                    "--disable-sync",
                    "--force-color-profile=srgb",
                    "--metrics-recording-only",
                    "--mute-audio",
                    "--no-pings",
                    "--use-gl=swiftshader",
                    "--window-size=1280,1696"
                ]
            )
            
            # Create context with realistic user agent
            self.context = await self.browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            )
            
            # Create page from context
            self.page = await self.context.new_page()
            
            # Set comprehensive HTTP headers
            await self.page.set_extra_http_headers({
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Cache-Control": "max-age=0",
            })
            
            # Set content security policy
            await self.page.set_content("<meta http-equiv='X-Content-Type-Options' content='nosniff'>")
            
            logger.info("Browser initialized successfully with optimized configuration")
        except Exception as e:
            logger.error(f"Failed to initialize browser: {e}")
            await self._cleanup()
            raise BlogScraperError(f"Browser initialization failed: {e}")
    
    async def _cleanup(self) -> None:
        """Clean up browser resources."""
        try:
            if self.context:
                await self.context.close()
                logger.info("Browser context closed")
            if self.browser:
                await self.browser.close()
                logger.info("Browser closed")
            if self.playwright:
                await self.playwright.stop()
                logger.info("Playwright stopped")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    async def navigate_to_url(self, url: str) -> None:
        """Navigate to the specified URL with comprehensive loading strategy."""
        if not self.page:
            raise BlogScraperError("Page not initialized")
        
        try:
            logger.info(f"Navigating to: {url}")
            await self.page.goto(url, timeout=self.timeout)
        
            logger.info("Navigation and initial loading completed successfully")
            
        except PlaywrightTimeoutError:
            logger.error(f"Navigation timeout after {self.timeout}ms")
            raise BlogScraperError(f"Navigation timeout to {url}")
        except Exception as e:
            logger.error(f"Navigation failed: {e}")
            raise BlogScraperError(f"Failed to navigate to {url}: {e}")
    
    async def extract_post_info(self, blog_element) -> Optional[Dict[str, str]]:
        """Extract post information from a blog element with comprehensive error handling."""
        try:
            # Extract post date and author
            info_div = await blog_element.query_selector("div.m-card-info")
            if not info_div:
                logger.debug("No info div found in blog element")
                return None
            
            info_text = await info_div.text_content()
            if not info_text or not info_text.strip():
                logger.debug("Empty info text found")
                return None
            
            parts = [x.strip() for x in info_text.strip().split(",")]
            if len(parts) < 2:
                logger.debug(f"Insufficient info parts: {parts}")
                return None
            
            post_date = parts[-1]
            authors = ", ".join(parts[:-1])
            
            # Extract title and URL
            title_anchor = await blog_element.query_selector("div.m-card-title a")
            if not title_anchor:
                logger.debug("No title anchor found")
                return None
            
            title_text = await title_anchor.text_content()
            title = title_text.strip() if title_text else ""
            
            url_attr = await title_anchor.get_attribute("href")
            url = url_attr.strip() if url_attr else ""
            
            # Extract description
            desc_div = await blog_element.query_selector("div.m-card-description")
            desc_text = await desc_div.text_content() if desc_div else ""
            description = desc_text.strip() if desc_text else ""
            
            if not title or not url:
                logger.debug("Missing title or URL")
                return None
            
            return {
                "title": title,
                "url": url,
                "author": authors,
                "date": post_date,
                "description": description
            }
            
        except Exception as e:
            logger.warning(f"Error extracting post info: {e}")
            return None
    
    async def process_blog_posts(self, existing_posts: List[Dict]) -> Tuple[List[Dict], bool]:
        """Process all blog posts on current page and return matching posts."""
        if not self.page:
            raise BlogScraperError("Page not initialized")
        
        try:
            # Wait for posts to load
            await self.page.wait_for_selector("ul.aws-directories-container li", timeout=10000)
        except PlaywrightTimeoutError:
            logger.error("Timeout waiting for blog posts to load")
            raise BlogScraperError("Blog posts failed to load")
        
        try:
            blog_elements = await self.page.query_selector_all("ul.aws-directories-container li")
            logger.info(f"Processing {len(blog_elements)} posts")
            
            matching_posts = []
            last_post_matches = False
            
            for i, blog in enumerate(blog_elements):
                post_info = await self.extract_post_info(blog)
                if not post_info:
                    continue
                
                # Check if this post matches the target date
                if post_info["date"] == self.target_date:
                    # Add to matching posts (avoid duplicates by checking URL)
                    if not any(post['url'] == post_info['url'] for post in existing_posts + matching_posts):
                        matching_posts.append(post_info)
                        logger.info(f"✓ Found matching post: {post_info['title']}")
                
                # Check if this is the last post and if it matches target date
                if i == len(blog_elements) - 1 and post_info["date"] == self.target_date:
                    last_post_matches = True
                    logger.info(f"Last post matches target date: {post_info['date']}")
            
            return matching_posts, last_post_matches
            
        except Exception as e:
            logger.error(f"Error processing blog posts: {e}")
            raise BlogScraperError(f"Failed to process blog posts: {e}")
    
    async def find_load_more_button(self):
        """Find the load more button using multiple selectors."""
        if not self.page:
            raise BlogScraperError("Page not initialized")
        
        load_more_selectors = [
            "a.m-directories-more.m-directories-more-arrow.m-cards-light.m-active",
            "a.m-directories-more",
            "div.m-directories-more-container a",
            "div.m-directories-more-container button",
            "[role='button'][title*='More']"
        ]
        
        for selector in load_more_selectors:
            try:
                load_more_btn = await self.page.query_selector(selector)
                if load_more_btn:
                    logger.debug(f"Found load more button with selector: {selector}")
                    return load_more_btn
            except Exception as e:
                logger.debug(f"Error with selector {selector}: {e}")
                continue
        
        logger.debug("No load more button found")
        return None
    
    async def wait_for_new_content(self, previous_count: int) -> bool:
        """Wait for new content to load using multiple strategies."""
        if not self.page:
            raise BlogScraperError("Page not initialized")
        
        logger.info("Waiting for new content to load...")
        
        # Strategy 1: Wait for count increase
        try:
            await self.page.wait_for_function(
                f'document.querySelectorAll("ul.aws-directories-container li").length > {previous_count}',
                timeout=15000
            )
            logger.info("✓ New posts loaded (count increased)")
            return True
        except PlaywrightTimeoutError:
            logger.debug("Strategy 1 failed (timeout), trying strategy 2...")
        except Exception as e:
            logger.debug(f"Strategy 1 failed with error: {e}, trying strategy 2...")
        
        # Strategy 2: Wait longer and manually check
        try:
            await self.page.wait_for_timeout(5000)
            current_elements = await self.page.query_selector_all("ul.aws-directories-container li")
            current_count = len(current_elements)
            if current_count > previous_count:
                logger.info(f"✓ New posts loaded after timeout (count: {previous_count} -> {current_count})")
                return True
        except Exception as e:
            logger.debug(f"Strategy 2 failed: {e}")
        
        # Strategy 3: Check if button disappeared
        try:
            await self.page.wait_for_timeout(3000)
            button_still_exists = await self.page.query_selector("a.m-directories-more")
            if not button_still_exists:
                logger.info("Load more button disappeared, assuming end of content")
                return False
        except Exception as e:
            logger.debug(f"Error checking button existence: {e}")
        
        # Final check
        try:
            current_elements = await self.page.query_selector_all("ul.aws-directories-container li")
            current_count = len(current_elements)
            if current_count > previous_count:
                logger.info(f"✓ Content loaded despite timeout (count: {previous_count} -> {current_count})")
                return True
        except Exception as e:
            logger.error(f"Error in final content check: {e}")
        
        logger.warning("Failed to load new content")
        return False
    
    async def click_load_more_button(self, load_more_btn) -> bool:
        """Click the load more button and handle the interaction."""
        if not self.page:
            raise BlogScraperError("Page not initialized")
        
        try:
            is_enabled = await load_more_btn.is_enabled()
            is_visible = await load_more_btn.is_visible()
            
            if not (is_enabled and is_visible):
                logger.warning(f"Load More button not clickable (enabled: {is_enabled}, visible: {is_visible})")
                return False
            
            logger.info("Clicking load more button...")
            previous_elements = await self.page.query_selector_all("ul.aws-directories-container li")
            previous_count = len(previous_elements)
            
            await load_more_btn.scroll_into_view_if_needed()
            await self.page.wait_for_timeout(2000)
            await load_more_btn.click()
            
            # Wait for new content
            return await self.wait_for_new_content(previous_count)
            
        except Exception as e:
            logger.error(f"Error clicking load more button: {e}")
            return False
    
    async def get_blog_posts_for_date(self, url: str) -> List[Dict[str, str]]:
        """Main function to get all blog posts for a specific date."""
        logger.info(f"Starting blog scraping for date: {self.target_date}")
        logger.info(f"Target URL: {url}")
        
        await self.navigate_to_url(url)
        
        posts = []
        load_count = 0
        
        logger.info(f"Searching for posts on: {self.target_date}")
        
        try:
            while load_count < self.max_loads:
                logger.info(f"\n--- Load {load_count + 1} ---")
                
                # Process current page posts
                matching_posts, last_post_matches = await self.process_blog_posts(posts)
                posts.extend(matching_posts)
                
                logger.info(f"Found {len(matching_posts)} new matching posts")
                logger.info(f"Total posts for {self.target_date}: {len(posts)}")
                
                # If last post doesn't match, we're done
                if not last_post_matches:
                    logger.info("Last post does not match target date, stopping")
                    break
                
                # Try to load more posts
                load_more_btn = await self.find_load_more_button()
                if not load_more_btn:
                    logger.info("No Load More button found, stopping")
                    break
                
                # Click load more and wait for content
                content_loaded = await self.click_load_more_button(load_more_btn)
                if not content_loaded:
                    logger.info("Failed to load more content, stopping")
                    break
                
                load_count += 1
                logger.info("Successfully loaded more posts, continuing...")
            
            if load_count >= self.max_loads:
                logger.warning(f"Reached maximum load limit ({self.max_loads})")
            
            logger.info(f"Scraping completed. Total posts found: {len(posts)}")
            return posts
            
        except Exception as e:
            logger.error(f"Error during blog post scraping: {e}")
            raise BlogScraperError(f"Scraping failed: {e}")


# class BlogScraper:
    """AWS Blog scraper with proper error handling and logging."""
    
    def __init__(self, target_date: str = TARGET_DATE, max_loads: int = 50, timeout: int = 60000):
        self.target_date = target_date
        self.max_loads = max_loads
        self.timeout = timeout
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self._initialize_browser()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit with proper cleanup."""
        await self._cleanup()
        if exc_type:
            logger.error(f"Exception occurred: {exc_type.__name__}: {exc_val}")
    
    async def _initialize_browser(self) -> None:
        """Initialize browser and page with error handling."""
        # async with async_playwright() as p:
        #     self.playwright = p
        try:
            logger.info("Initializing browser...")
            self.playwright = await async_playwright().start()
            # self.browser = await self.playwright.chromium.launch(headless=True)
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=[
                "--disable-gpu",
                "--no-sandbox",
                "--single-process",
                "--disable-dev-shm-usage",
                "--no-zygote",
                "--disable-setuid-sandbox",
                "--disable-accelerated-2d-canvas",
                "--disable-dev-shm-usage",
                "--no-first-run",
                "--no-default-browser-check",
                "--disable-background-networking",
                "--disable-background-timer-throttling",
                "--disable-client-side-phishing-detection",
                "--disable-component-update",
                "--disable-default-apps",
                "--disable-domain-reliability",
                "--disable-features=AudioServiceOutOfProcess",
                "--disable-hang-monitor",
                "--disable-ipc-flooding-protection",
                "--disable-popup-blocking",
                "--disable-prompt-on-repost",
                "--disable-renderer-backgrounding",
                "--disable-sync",
                "--force-color-profile=srgb",
                "--metrics-recording-only",
                "--mute-audio",
                "--no-pings",
                "--use-gl=swiftshader",
                "--window-size=1280,1696"
            ]
            )
            # self.page = await self.browser.new_page()
            context = await self.browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            )
            self.page = await context.new_page()
            await self.page.set_extra_http_headers({
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Cache-Control": "max-age=0",
            })

            await self.page.set_content("<meta http-equiv='X-Content-Type-Options' content='nosniff'>")

            logger.info("Browser initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize browser: {e}")
            await self._cleanup()
            raise BlogScraperError(f"Browser initialization failed: {e}")
    
    async def _cleanup(self) -> None:
        """Clean up browser resources."""
        try:
            if self.browser:
                await self.browser.close()
                logger.info("Browser closed")
            if self.playwright:
                await self.playwright.stop()
                logger.info("Playwright stopped")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    async def navigate_to_url(self, url: str) -> None:
        """Navigate to the specified URL with error handling."""
        if not self.page:
            raise BlogScraperError("Page not initialized")
        
        try:
            logger.info(f"Navigating to: {url}")
            await self.page.goto(url, timeout=self.timeout)
            logger.info("Navigation successful")
        except PlaywrightTimeoutError:
            logger.error(f"Navigation timeout after {self.timeout}ms")
            raise BlogScraperError(f"Navigation timeout to {url}")
        except Exception as e:
            logger.error(f"Navigation failed: {e}")
            raise BlogScraperError(f"Failed to navigate to {url}: {e}")
    
    async def extract_post_info(self, blog_element) -> Optional[Dict[str, str]]:
        """Extract post information from a blog element with comprehensive error handling."""
        try:
            # Extract post date and author
            info_div = await blog_element.query_selector("div.m-card-info")
            if not info_div:
                logger.debug("No info div found in blog element")
                return None
            
            info_text = await info_div.text_content()
            if not info_text or not info_text.strip():
                logger.debug("Empty info text found")
                return None
            
            parts = [x.strip() for x in info_text.strip().split(",")]
            if len(parts) < 2:
                logger.debug(f"Insufficient info parts: {parts}")
                return None
            
            post_date = parts[-1]
            authors = ", ".join(parts[:-1])
            
            # Extract title and URL
            title_anchor = await blog_element.query_selector("div.m-card-title a")
            if not title_anchor:
                logger.debug("No title anchor found")
                return None
            
            title_text = await title_anchor.text_content()
            title = title_text.strip() if title_text else ""
            
            url_attr = await title_anchor.get_attribute("href")
            url = url_attr.strip() if url_attr else ""
            
            # Extract description
            desc_div = await blog_element.query_selector("div.m-card-description")
            desc_text = await desc_div.text_content() if desc_div else ""
            description = desc_text.strip() if desc_text else ""
            
            if not title or not url:
                logger.debug("Missing title or URL")
                return None
            
            return {
                "title": title,
                "url": url,
                "author": authors,
                "date": post_date,
                "description": description
            }
            
        except Exception as e:
            logger.warning(f"Error extracting post info: {e}")
            return None
    
    async def process_blog_posts(self, existing_posts: List[Dict]) -> Tuple[List[Dict], bool]:
        """Process all blog posts on current page and return matching posts."""
        if not self.page:
            raise BlogScraperError("Page not initialized")
        
        try:
            # Wait for posts to load
            await self.page.wait_for_selector("ul.aws-directories-container li", timeout=10000)
        except PlaywrightTimeoutError:
            logger.error("Timeout waiting for blog posts to load")
            raise BlogScraperError("Blog posts failed to load")
        
        try:
            blog_elements = await self.page.query_selector_all("ul.aws-directories-container li")
            logger.info(f"Processing {len(blog_elements)} posts")
            
            matching_posts = []
            last_post_matches = False
            
            for i, blog in enumerate(blog_elements):
                post_info = await self.extract_post_info(blog)
                if not post_info:
                    continue
                
                # Check if this post matches the target date
                if post_info["date"] == self.target_date:
                    # Add to matching posts (avoid duplicates by checking URL)
                    if not any(post['url'] == post_info['url'] for post in existing_posts + matching_posts):
                        matching_posts.append(post_info)
                        logger.info(f"✓ Found matching post: {post_info['title']}")
                
                # Check if this is the last post and if it matches target date
                if i == len(blog_elements) - 1 and post_info["date"] == self.target_date:
                    last_post_matches = True
                    logger.info(f"Last post matches target date: {post_info['date']}")
            
            return matching_posts, last_post_matches
            
        except Exception as e:
            logger.error(f"Error processing blog posts: {e}")
            raise BlogScraperError(f"Failed to process blog posts: {e}")
    
    async def find_load_more_button(self):
        """Find the load more button using multiple selectors."""
        if not self.page:
            raise BlogScraperError("Page not initialized")
        
        load_more_selectors = [
            "a.m-directories-more.m-directories-more-arrow.m-cards-light.m-active",
            "a.m-directories-more",
            "div.m-directories-more-container a",
            "div.m-directories-more-container button",
            "[role='button'][title*='More']"
        ]
        
        for selector in load_more_selectors:
            try:
                load_more_btn = await self.page.query_selector(selector)
                if load_more_btn:
                    logger.debug(f"Found load more button with selector: {selector}")
                    return load_more_btn
            except Exception as e:
                logger.debug(f"Error with selector {selector}: {e}")
                continue
        
        logger.debug("No load more button found")
        return None
    
    async def wait_for_new_content(self, previous_count: int) -> bool:
        """Wait for new content to load using multiple strategies."""
        if not self.page:
            raise BlogScraperError("Page not initialized")
        
        logger.info("Waiting for new content to load...")
        
        # Strategy 1: Wait for count increase
        try:
            await self.page.wait_for_function(
                f'document.querySelectorAll("ul.aws-directories-container li").length > {previous_count}',
                timeout=15000
            )
            logger.info("✓ New posts loaded (count increased)")
            return True
        except PlaywrightTimeoutError:
            logger.debug("Strategy 1 failed (timeout), trying strategy 2...")
        except Exception as e:
            logger.debug(f"Strategy 1 failed with error: {e}, trying strategy 2...")
        
        # Strategy 2: Wait longer and manually check
        try:
            await self.page.wait_for_timeout(5000)
            current_elements = await self.page.query_selector_all("ul.aws-directories-container li")
            current_count = len(current_elements)
            if current_count > previous_count:
                logger.info(f"✓ New posts loaded after timeout (count: {previous_count} -> {current_count})")
                return True
        except Exception as e:
            logger.debug(f"Strategy 2 failed: {e}")
        
        # Strategy 3: Check if button disappeared
        try:
            await self.page.wait_for_timeout(3000)
            button_still_exists = await self.page.query_selector("a.m-directories-more")
            if not button_still_exists:
                logger.info("Load more button disappeared, assuming end of content")
                return False
        except Exception as e:
            logger.debug(f"Error checking button existence: {e}")
        
        # Final check
        try:
            current_elements = await self.page.query_selector_all("ul.aws-directories-container li")
            current_count = len(current_elements)
            if current_count > previous_count:
                logger.info(f"✓ Content loaded despite timeout (count: {previous_count} -> {current_count})")
                return True
        except Exception as e:
            logger.error(f"Error in final content check: {e}")
        
        logger.warning("Failed to load new content")
        return False
    
    async def click_load_more_button(self, load_more_btn) -> bool:
        """Click the load more button and handle the interaction."""
        if not self.page:
            raise BlogScraperError("Page not initialized")
        
        try:
            is_enabled = await load_more_btn.is_enabled()
            is_visible = await load_more_btn.is_visible()
            
            if not (is_enabled and is_visible):
                logger.warning(f"Load More button not clickable (enabled: {is_enabled}, visible: {is_visible})")
                return False
            
            logger.info("Clicking load more button...")
            previous_elements = await self.page.query_selector_all("ul.aws-directories-container li")
            previous_count = len(previous_elements)
            
            await load_more_btn.scroll_into_view_if_needed()
            await self.page.wait_for_timeout(2000)
            await load_more_btn.click()
            
            # Wait for new content
            return await self.wait_for_new_content(previous_count)
            
        except Exception as e:
            logger.error(f"Error clicking load more button: {e}")
            return False
    
    async def get_blog_posts_for_date(self, url: str) -> List[Dict[str, str]]:
        """Main function to get all blog posts for a specific date."""
        logger.info(f"Starting blog scraping for date: {self.target_date}")
        logger.info(f"Target URL: {url}")
        
        await self.navigate_to_url(url)
        
        posts = []
        load_count = 0
        
        logger.info(f"Searching for posts on: {self.target_date}")
        
        try:
            while load_count < self.max_loads:
                logger.info(f"\n--- Load {load_count + 1} ---")
                
                # Process current page posts
                matching_posts, last_post_matches = await self.process_blog_posts(posts)
                posts.extend(matching_posts)
                
                logger.info(f"Found {len(matching_posts)} new matching posts")
                logger.info(f"Total posts for {self.target_date}: {len(posts)}")
                
                # If last post doesn't match, we're done
                if not last_post_matches:
                    logger.info("Last post does not match target date, stopping")
                    break
                
                # Try to load more posts
                load_more_btn = await self.find_load_more_button()
                if not load_more_btn:
                    logger.info("No Load More button found, stopping")
                    break
                
                # Click load more and wait for content
                content_loaded = await self.click_load_more_button(load_more_btn)
                if not content_loaded:
                    logger.info("Failed to load more content, stopping")
                    break
                
                load_count += 1
                logger.info("Successfully loaded more posts, continuing...")
            
            if load_count >= self.max_loads:
                logger.warning(f"Reached maximum load limit ({self.max_loads})")
            
            logger.info(f"Scraping completed. Total posts found: {len(posts)}")
            return posts
            
        except Exception as e:
            logger.error(f"Error during blog post scraping: {e}")
            raise BlogScraperError(f"Scraping failed: {e}")
        
