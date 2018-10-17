routes = {
    # Redirecting paths starts with '/'
    # Direct paths point to appname
    '/login': 'login',
    '/static': 'static',
    '/register': 'register',
    '/': '/home',
    '/home': '/static?file=html/index.html',
    '/reg': '/static?file=html/reg.html',
    '/about': '/static?file=html/about.html',
    '/chat': '/static?file=html/chat.html',
}
