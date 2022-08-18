# warbler_models_overview.md

User
    # users
-
id
email
username Text unique
image_url Text unique
header_image_url Text       # default "/static/images/default-pic.png"
bio Text nullable           # default "/static/images/warbler-hero.jpg"
location Text nullable
password Text
# is_private boolean        # default False

Follows
    # follows; parent model: User ("users")
-
user_being_followed_id int FK - User.id
user_following_id int FK - User.id

Message
    # messages; parent model: User ("users")
-
id int PK
text String(140)
timestamp DateTime          # default datetime.utcnow()
user_id int FK - User.id

Likes
    # likes; parent model: User ("users") and message ("messages")
-
id int PK
user_id  int FK - User.id
message_id int FK

# interesting extras: 404, dry templates, dry authorization, dry urls, optimize queries, private accounts
# probably skipping: ajax like/unlike
# skipping "change password form", "add admin users", "user blocking"

# `models.py`
    - User
        - classmethods: signup, authenticate
        - instance methods: is_follow..., is_following, 
# `app.py`
    - `User`: User.query.get, User.query.filter (like), user.messages.append

    - what is 'g'?: it is application context (basically globally available data
    - Message.query....
    - interesting: there is custom method decorators, i.e. `@app.before_request` (before each request) and `@app.after_request` (after each...)
        search `@app` in https://flask.palletsprojects.com/en/2.2.x/api/?highlight=beforerequest
        - `@app....`
            - `route`, `errorhandler`, `beforerequest`, `afterrequest`, 
            - `template_filter`, `template_global`, `template_test`, `endpoint`,  
        - `@copy_current_request_context`
        - `@app_after_this_request` (nested within view function)

    - to dry, can I class a group of requests for certain @app.before_request? i.e.
```python
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
```
        - there is Flask-Login and Flask-Admin for managing views...
        - something interesting with blueprints to organize a large flask app but this is not it.
        - [Define a custom decorator](https://medium.com/@nguyenkims/python-decorator-and-flask-3954dd186cda)
            - `from functools import wraps` ... to define a custom decorator
