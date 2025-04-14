from models.url import URLModel
from utils.utils import generate_random_string

class URLShortener:
    @staticmethod
    def create_short_url(original_url, short_code=None):
        if not short_code or len(short_code) < 10 or len(short_code) > 50 or not short_code.isalnum():
            short_code = generate_random_string()
        URLModel.create_url(original_url, short_code)
        return short_code

    @staticmethod
    def get_original_url(short_code):
        return URLModel.get_original_url(short_code)
