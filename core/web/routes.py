routes = {
    # App name MUST NOT end with .py
    # App name is the same, as script name in /apps
    'apps': {'/api': 'app',
             '/login': 'login'},
    'static': {
        'html': {
            # Values MUST NOT start with '/'
            # Otherwise keys must start with '/'
            '/' : 'index.html',
            '/home': 'index.html',
            '/reg' : 'reg.html',
            '/about' : 'about.html',
            '/chat' : 'chat.html',
            '/error': 'error.html'
        },
        'js': {
            '/auth' : 'auth.js'
        }
    }
}
