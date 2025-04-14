from config.database import get_db_connection

class URLModel:
    @staticmethod
    def create_url(original_url, short_code):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'INSERT INTO shortened_urls (original_url, short_code) VALUES (?, ?)',
            (original_url, short_code)
        )
        
        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def get_original_url(short_code):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT original_url FROM shortened_urls WHERE short_code = ?', (short_code,))
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return result[0] if result else None

    @staticmethod
    def short_code_exists(short_code):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM shortened_urls WHERE short_code = ?', (short_code,))
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return bool(result)
