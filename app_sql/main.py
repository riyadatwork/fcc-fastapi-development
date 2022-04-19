from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time

app = FastAPI()


class Post(BaseModel):
    title: str
    content: str
    published: bool = True          # Include default value


# Retry connecting to DB every 2 secs, if connection failed
while True:
    try:
        conn = psycopg2.connect(
            host='127.0.0.1', database='fastapidevdb', user='postgres',
            password='postgres', cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print('Database connection successful')
        break
    except Exception as error:
        print('Connection to database failed')
        print('Error:', error)
        time.sleep(2)


my_posts = [
    {'title': 'title of post 1', 'content': 'content of post 1', 'id': 1},
    {'title': 'favorite foods', 'content': 'I like pizza', 'id': 2}
]


def find_post(id):
    for post in my_posts:
        if post['id'] == id:
            return post


def find_post_index(id):
    for index, post in enumerate(my_posts):
        if post['id'] == id:
            return index


@app.get('/')
async def root():
    return {"message": "Hello World"}


@app.get('/posts')
async def get_posts():
    cursor.execute('''SELECT * FROM posts''')
    posts = cursor.fetchall()
    print(posts)
    return {"data": posts}


# Use appropriate status code
@app.post('/posts', status_code=status.HTTP_201_CREATED)
def create_posts(post: Post):
    # Avoid using f string as it's vulnerable to SQL injection
    cursor.execute('''INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *''',
                   (post.title, post.content, post.published, ))
    new_post = cursor.fetchone()
    conn.commit()
    return {"data": new_post}


@app.get('/posts/{id}')                         # {id} is a path parameter
def get_post(id: int, response: Response):      # Ensures that id is converted to int
    cursor.execute('''SELECT * FROM posts WHERE id = %s''',
                   (str(id), ))   # Need to convert id to string since SQL expects string
    post = cursor.fetchone()
    if not post:                                # If post is not found/null
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'post with id {id} not found')
    return {"data": post}


# Use appropriate status code
@app.delete('/posts/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    cursor.execute(
        '''DELETE FROM posts where id = %s RETURNING *''', (str(id),))  # include ,
    deleted_post = cursor.fetchone()
    conn.commit()
    if deleted_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'post with id {id} not found')

    # For DELETE, we shouldn't return any message
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put('/posts/{id}')
def update_posts(id: int, post: Post):
    cursor.execute('''UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *''',
                   (post.title, post.content, post.published, id, ))
    updated_post = cursor.fetchone()
    conn.commit()
    if updated_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'post with id {id} not found')
    return {"data": updated_post}
