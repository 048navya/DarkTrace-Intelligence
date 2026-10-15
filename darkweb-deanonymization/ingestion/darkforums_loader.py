import os
import json
import hashlib
from datetime import datetime
from corpus_normalization import parse_date as parse_corpus_date, author_label

import psycopg2
from dotenv import load_dotenv


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

DATASET_PATH = os.getenv("DARKTRACE_DATASET_PATH") or os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "data",
    "safe_corpus.jsonl"
)

SOURCE_NAME = os.getenv("DARKTRACE_SOURCE_NAME", "DarkForums Safe Corpus")


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )


# ============================================================
# DATE PARSER
# ============================================================

def parse_date(value):
    return parse_corpus_date(value)


# ============================================================
# CONTENT HASH
# ============================================================

def generate_hash(content):
    """
    Creates a SHA-256 hash for the post content.
    """

    if not content:
        return None

    return hashlib.sha256(
        str(content).encode("utf-8")
    ).hexdigest()


# ============================================================
# NORMALIZE AUTHOR
# ============================================================

def normalize_author(author, post_id=None):
    return author_label(author, post_id)


# ============================================================
# GET OR CREATE PLATFORM
# ============================================================

def get_or_create_platform(
    cursor,
    forum_name
):
    """
    Creates the forum platform if it does not already exist.
    """

    platform_name = forum_name or "Unknown Forum"

    cursor.execute(
        """
        SELECT platform_id
        FROM platforms
        WHERE name = %s
        """,
        (platform_name,)
    )

    result = cursor.fetchone()

    if result:
        return result[0]

    cursor.execute(
        """
        INSERT INTO platforms
        (
            name,
            platform_type,
            source
        )
        VALUES
        (
            %s,
            %s,
            %s
        )
        RETURNING platform_id
        """,
        (
            platform_name,
            "Forum",
            SOURCE_NAME
        )
    )

    return cursor.fetchone()[0]


# ============================================================
# GET OR CREATE HANDLE
# ============================================================

def get_or_create_handle(
    cursor,
    username,
    platform_id
):
    """
    Creates a handle for a forum author.

    A handle is NOT considered a real-world identity.
    """

    username = normalize_author(username)

    cursor.execute(
        """
        SELECT handle_id
        FROM handles
        WHERE platform_id = %s
        AND username = %s
        """,
        (
            platform_id,
            username
        )
    )

    result = cursor.fetchone()

    if result:
        return result[0]

    cursor.execute(
        """
        INSERT INTO handles
        (
            actor_id,
            platform_id,
            username,
            source
        )
        VALUES
        (
            NULL,
            %s,
            %s,
            %s
        )
        RETURNING handle_id
        """,
        (
            platform_id,
            username,
            SOURCE_NAME
        )
    )

    return cursor.fetchone()[0]


# ============================================================
# INSERT THREAD
# ============================================================

def insert_thread(
    cursor,
    thread
):
    """
    Inserts one DarkForums thread.
    """

    if thread.get("thread_id") is None or not str(thread["thread_id"]).strip():
        raise ValueError("Missing thread_id")
    thread_id = str(thread["thread_id"])

    title = thread.get("title")

    category = thread.get("category")

    forum_name = thread.get("forum_name")

    date_posted = parse_date(
        thread.get("date_posted")
    )

    platform_id = get_or_create_platform(
        cursor,
        forum_name
    )

    cursor.execute(
        """
        INSERT INTO threads
        (
            thread_id,
            platform_id,
            title,
            category,
            forum_name,
            created_at,
            source
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
        ON CONFLICT (thread_id)
        DO UPDATE SET
            title = EXCLUDED.title,
            category = EXCLUDED.category,
            forum_name = EXCLUDED.forum_name,
            created_at = EXCLUDED.created_at
        """,
        (
            thread_id,
            platform_id,
            title,
            category,
            forum_name,
            date_posted,
            SOURCE_NAME
        )
    )

    return platform_id


# ============================================================
# INSERT POST
# ============================================================

def insert_post(
    cursor,
    thread,
    post,
    platform_id
):
    """
    Inserts a post belonging to a thread.
    """

    if post.get("post_id") is None or not str(post["post_id"]).strip():
        raise ValueError("Missing post_id")
    post_id = str(post["post_id"])

    if thread.get("thread_id") is None or not str(thread["thread_id"]).strip():
        raise ValueError("Missing thread_id")
    thread_id = str(thread["thread_id"])

    username = normalize_author(
        post.get(
            "author",
            thread.get("author")
        ),
        post_id=post_id
    )

    post_number = post.get(
        "post_number"
    )

    # Convert "#1" -> 1
    if post_number:
        try:
            post_number = int(
                str(post_number)
                .replace("#", "")
                .strip()
            )
        except ValueError:
            post_number = None

    content = post.get(
        "content",
        ""
    )

    post_date = parse_date(
        post.get(
            "post_date"
        )
    )

    handle_id = get_or_create_handle(
        cursor,
        username,
        platform_id
    )

    content_hash = generate_hash(
        content
    )

    cursor.execute(
        """
        INSERT INTO posts
        (
            post_id,
            thread_id,
            handle_id,
            post_number,
            content,
            created_at,
            source,
            language,
            content_hash
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
        ON CONFLICT (post_id)
        DO UPDATE SET
            thread_id = EXCLUDED.thread_id,
            handle_id = EXCLUDED.handle_id,
            post_number = EXCLUDED.post_number,
            content = EXCLUDED.content,
            created_at = EXCLUDED.created_at,
            content_hash = EXCLUDED.content_hash
        """,
        (
            post_id,
            thread_id,
            handle_id,
            post_number,
            content,
            post_date,
            SOURCE_NAME,
            "en",
            content_hash
        )
    )


# ============================================================
# IMPORT DATASET
# ============================================================

def import_dataset():
    if not os.path.isfile(DATASET_PATH):
        raise FileNotFoundError('Dataset not found: '+DATASET_PATH)
    stats={'threads':0,'posts':0,'empty_threads':0,'undated_threads':0,'undated_posts':0,'failed_lines':[]}
    conn=get_connection()
    try:
        with conn.cursor() as cursor, open(DATASET_PATH,encoding='utf-8-sig') as stream:
            for number,line in enumerate(stream,1):
                if not line.strip():continue
                cursor.execute('SAVEPOINT import_thread')
                try:
                    thread=json.loads(line)
                    if not isinstance(thread,dict) or not isinstance(thread.get('posts',[]),list):
                        raise ValueError('Expected a thread object with a posts array')
                    platform_id=insert_thread(cursor,thread)
                    posts=thread.get('posts',[])
                    for post in posts:insert_post(cursor,thread,post,platform_id)
                    cursor.execute('RELEASE SAVEPOINT import_thread')
                    stats['threads']+=1;stats['posts']+=len(posts)
                    stats['empty_threads']+=int(not posts)
                    stats['undated_threads']+=int(parse_date(thread.get('date_posted')) is None)
                    stats['undated_posts']+=sum(parse_date(p.get('post_date')) is None for p in posts)
                except Exception as exc:
                    cursor.execute('ROLLBACK TO SAVEPOINT import_thread')
                    cursor.execute('RELEASE SAVEPOINT import_thread')
                    stats['failed_lines'].append({'line':number,'error_type':type(exc).__name__})
            conn.commit()
    except Exception:
        conn.rollback();raise
    finally:conn.close()
    print(json.dumps(stats,indent=2))
    if stats['failed_lines']:raise RuntimeError('Some lines failed; see line numbers above. Successful threads were retained.')
    return stats

if __name__=='__main__':import_dataset()
