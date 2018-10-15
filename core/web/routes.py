routes = {
    # App name MUST NOT end with .py
    # App name is the same, as script name in /apps
    '/login': 'login',
    # Values MUST NOT start with '/'
    # Otherwise keys must start with '/'
    '/static' : 'static',
    '/' : '/home',
    '/home': '/static?file=html/index.html',
    '/reg' : '/static?file=html/reg.html',
    '/about' : '/static?file=html/about.html',
    '/chat' : '/static?file=html/chat.html',
}
