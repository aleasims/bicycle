routes = {
    'apps': {'/api': 'app'},
    'static': {
        'html': {
            # Values MUST NOT start with '/'
            # Otherwise keys must start with '/'
            '/' : 'index.html',
            '/home': 'index.html',
            '/reg' : 'reg.html',
            '/about' : 'about.html',
            '/chat' : 'chat.html'
        },
        'js': {
            'auth' : 'auth.js'
        }

    },
}