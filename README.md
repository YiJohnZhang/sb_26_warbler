# sb_26_warbler
## Time Tracker
|Session|Assignment|Time Elasped|Date|Time|
|-|-|-|-|-|
|01|Preliminary assignment overview and codebase familiarization.|104 min|2022.08.18|13:19 - 15:03|
|02|Refactor `forms.py`, `app.py`, and `models.py`. Still need to figure out storing previous page for error page.|83 min|2022.08.18|17:16 - 18:39|
|03|Done 04.02-04; 01.02-04, 07 (~33%)|108 min|2022.08.19|20:38 - 22:26|
|04|Redefined `Likes` implementation in `models.py`^[1]^ and `templates`^[2]^. Almost finished edit user feature w/ debugging. |110 min|2022.08.20|10:10 - 12:00|
|05|Finished edit user feature (01.05). Finished DRY error handling and custom error page for `403` and `404` errors (04.01).|30 min|2022.08.|12:30 - 13:00|
|06|dry query logic in `app.py`, started implementing `Likes`, started reimplementing followers to nosql for `Users`|122 min|2022.08.20|16:00 - 18:02|
|07|Finished `Likes` with dry templating (02). Dropped further development of reimplementing nosql for `Users`. Finished home page (01.06) and improved querying performance (04.06).|158 min|2022.08.20|20:10 - 22:48|
|08|Tests.|62 min|2022.08.21|21:10 - 22:12|
||**Total Time**|777 min|||


^[1]^ Removed `id` as `PRIMARY KEY`sql and made the PK a compound `PRIMARY KEY`sql of `user_id` and `message_id` because integers have limits; also used serial numbers do not get regenerated so theoretically the db can hit its cap of 2^31 - 1 (`SERIAL`sql) or 2^63 - 1 (`BIGSERIAL`sql) while having 0 likes in the rel.
^[2]^ Modularized `users/show.html` to `users/messages.html` so that both `home.html`, `users/detail.html` uses the `messages.html` module to genereate message information.

# Experience Notes Dump
1. The `db.relationship` attribute attached to parent/child/join models are more than a means to navigate to another model; it may also be used to immediately access all elements related through the attribute stored as an [`InstrumentedList`py](https://stackoverflow.com/questions/6654613/what-is-an-instrumentedlist-in-python). I found out when I tried `user.user_likes.returnLikeCountByUserID(user.id)` in `users/detail.html` and was debugging it why `[]` showed up for the unseeded `Likes` model; and in the console `user.followers` and `user.following` contained `User` a `InstrumentedList`py instances.
2. Disregard the `no_sql` attempt comments in `seed.py` and added `sortFollows.py` and miscellaneous additional `.csv` files:
```python
# because I can get all the followers as a property so there is no need to query to optimize the query!
# Use Instructions:
#   1. Run `generator/create_csvs.py`.
#   2. Run `generator/sortFoillowsHelper.py`.
#   3. Paste `user_followers_followedBy_noSQL.csv` contents into `users.csv`.
#     Recreated as `users_nosql.csv`
#     `user_followers_followedBy_noSQL.csv` uses semicolon delimiters because it contains arrays.

#     1 GB is the longest string length for PSQL. BIGINT goes upto 1E18 (19 characters). A legible array has 2 characters of overhead for each entry: `[]` for the 1st and `, ` for the nth after the 1st.
#         therefore each entry, at worst case is 21 chars.
#         UTF-8 standard is 1 byte / character for the basic 128. Therefore Each entry takes 21 bytes.
#         therefore each string may hold a minimum of 47.6 mn entries, legibly. 50 mn - 1 if space-condensed. 50 mn if cheaped out on `[]`
#         theoretically could just 1-to-many rel. the entry strings
#     set data type of `user_follows` and `user_followers` to Text.
```
3. `models.py`, `Like`, `@classmethod toggleLike`: interesting I was doing ` selectedLike = cls.query.get((userID, messageID));` (~71) and because it was initially `None`py, `get_or_404()` automatically yielded the 404 page.
    - To query composite keys in SQLAlchemy, [insert the tuple corresponding to the composite key](https://stackoverflow.com/a/62333875). Not that I needed to know because rn I am half asleep zzzzzz.


# 01.07. Notes
- whether or not the user is authenticated is being kept track of by the session object `curr_user` key.
- flask `g` object is short `global` and is the application context. It is a global variable.
- `add_user_to_g` has been renamed to `before_request`; before every request, update the global variable to include the username.
- `@app.before_request` is a flask defined header to execute the following function before every HTTP request.

# 04. Further Study
## Further Study Implemented (6/11)
1. 06.01: Custom 404 Page
2. 06.03: DRY Template (Partial)
3. 06.04: DRY Authorization
4. 06.05: DRY URLs
5. 06.06: optimize queries

## Further Study Skip Out
- 06.02: Add Ajax
- 06.07: Change password form
- 06.08: private accounts
- 06.09: Add Admin users
- 06.10: User Blocking
- 06.11: Direct Messages


# DRY templates
- condensed `users/signup.html` and `users/login.html` to `users/onboarding.html`
- {% include ... %} unused because the form base for `new.html` and `onboarding.html` (formerly `signup.html` and `login.html`) are different.
- condensed `home-anon.html` and `home.html` into `home.html`
- not touching `{% macro %}` and `{% import %}` because this is actually easier to implement in the front end and delete altogether from the templates for `details.html` and its child templates `followers.html` and `following.html`.

## Notes
- macros are [functions in Jinja](https://jinja.palletsprojects.com/en/3.1.x/templates/#macros). Macros may be called like a function in Jinja, i.e.
```html

    {% macro input(name, value='', type='text', size=20) -%}
        <input type="{{ type }}" name="{{ name }}" value="{{value|e }}" size="{{ size }}">
    {%- endmacro %}

    <!-- ... -->

    <p> {{input('username')}}

```
This, I'm ugessing generates a text input field of type 'text' and an initial value of `''` with a maximum size of 20. Well, the example isn't the best becuase Flask WTF#@!? already does this more efficiently. But it is good for generating dynamic values I guess.

Interestingly, one can [import](https://jinja.palletsprojects.com/en/3.1.x/templates/#import) `macro` from a template and use it as variables, i.e. imagine the previous ex. is in `forms.html` (Jinja Example). One can import `forms.html` and start using the macros as functions:
```html
{% import 'forms.html' as forms %}
<dl>
    <dt>Username</dt>
    <dd>{{ forms.input('username') }}</dd>
    <dt>Password</dt>
    <dd>{{ forms.input('password', type='password') }}</dd>
</dl>
<p>{{ forms.textarea('comment') }}</p>
```

Do something clever with  `{% macro %}` and `{% import %}` statements in Jinja to rid a lot of repetition in the user detail, followers, followed_user pages, and more.
