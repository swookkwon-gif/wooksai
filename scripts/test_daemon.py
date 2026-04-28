import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))
from auto_blog_daemon import process_gmail_newsletters
process_gmail_newsletters()
