# sb_26_warbler
## Time Tracker
|Session|Assignment|Time Elasped|Date|Time|
|-|-|-|-|-|
|01|Preliminary assignment overview and codebase familiarization.|104 min|2022.08.18|13:19 - 15:03|
|02|Refactor `forms.py`, `app.py`, and `models.py`. Still need to figure out storing previous page for error page.|83 min|2022.08.18|17:16 - 18:39|
|03|Done 04.02-04; 01.02-04, 07 (~33%)|108 min|2022.08.19|20:38 - 22:26|
|04|Changed `Likes` implementation in `models.py`^[1]^ and `templates`^[2]^. Finished `error.html` template and basic error codes, `404` and `403`. |min|2022.08.20|10:10 - wx:yz|
|05||min|2022.08.|ab:cd - wx:yz|
||**Total Time**|min|||

295

||min|2022.08.|ab:cd - wx:yz|

^[1]^ Removed `id` as `PRIMARY KEY`sql and made the PK a compound `PRIMARY KEY`sql of `user_id` and `message_id` because integers have limits; also used serial numbers do not get regenerated so theoretically the db can hit its cap of 2^31 - 1 (`SERIAL`sql) or 2^63 - 1 (`BIGSERIAL`sql) while having 0 likes in the rel.
^[2]^ Modularized `users/show.html` to `users/messages.html` so that both `home.html`, `users/detail.html` uses the `messages.html` module to genereate message information.

# 01.07. Notes
- whether or not the user is authenticated is being kept track of by the session object `curr_user` key.
- flask `g` object is short `global` and is the application context. It is a global variable.
- `add_user_to_g` has been renamed to `before_request`; before every request, update the global variable to include the username.
- `@app.before_request` is a flask defined header to execute the following function before every HTTP request.

# 04. Further Study
## Further Study Implemented (6/11)
2. DRY Template (Partial)
3. DRY Authorization
4. DRY URLs

1. Custom 404 Page?

5. optimize queries?
6. private accoutns?

## Further Study Skip Out
- Add Ajax
- Change password form
- Add Admin users
- User Blocking
- Direct Messages


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

# To Do
1. Main Changes
- define `profile()` logic (`app.py`)
- profile edit (5)
- fix homepage (6)
2. Add Likes
3. Add Tests
    - Streamlined Tests:
    - For all routes: attempt to visit while logged out, for all routes: attempt to visit it while logged in.
    - 

Do something clever with  `{% macro %}` and `{% import %}` statements in Jinja to rid a lot of repetition in the user detail, followers, followed_user pages, and more.