import os
import io


model = ''
authorized_separator = '<!-- If authorized -->'


def load_model(www_dir):
    global model
    path = os.path.join(www_dir, 'index.html')
    model = open(path, mode='r', encoding='utf-8').read()


logged_menu = '''
<a class="menubutton" href="/">Home
<a class="menubutton" href="/about">About
<a class="menubutton right" id="logOutButton" onclick="logOut()">Logout
<a class="menubutton right" href="/account" id="accImg">
<img src="/img/acc_logo.png" height="20">%(name)s</a>
'''

not_logged_menu = '''
<a class="menubutton" href="/">Home
<a class="menubutton" href="/about">About
<a class="menubutton right" href="/reg" id="newAccButton">Create account</a>
'''


__error_message_model = '''
<h1>Error %(code)d - %(message)s</h1>
<p>Error code %(code)s - %(explain)s.</p>
'''


def error_message(user):
    if user is None:
        page = model % {'menu': not_logged_menu, 'content': __error_message_model}
    else:
        page = (model % {'menu': logged_menu, 'content': __error_message_model}) % user
    return page


def fill(path, user):
    content = open(path, mode='r', encoding='utf-8').read()
    cases = content.split(authorized_separator, 1)
    not_logged = cases[0]
    if len(cases) > 1:
        logged = cases[1]
    else:
        logged = cases[0]
    if user is None:
        page = model % {'menu': not_logged_menu, 'content': not_logged}
    else:
        page = (model % {'menu': logged_menu, 'content': logged}) % user
    return page