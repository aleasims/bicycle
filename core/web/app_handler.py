import importlib


def LaunchApp(appname, args):
    i = importlib.import_module('core.web.apps.' + appname)
    response = i.activate(args)
    return bytes(response, 'utf-8')
