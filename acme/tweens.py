from pyramid.settings import asbool
import logging

log = logging.getLogger(__name__)


def autocsrf_tween_factory(handler, registry):
    if asbool(registry.settings.get('autocsrf')):
        # if auto-csrf support is enabled, return a wrapper
        def autocsrf_tween(request):
            response = handler(request)
            try:
                if response.content_type in [
                        'text/html', 'application/xhtml+xml']:
                    response.text = unicode(
                                        response.text.replace(
                                            '__csrf_placeholder__',
                                            request.session.get_csrf_token()
                                        ))
            except Exception as emsg:
                import sys
                sys.stderr.write("AUTOCSRF failed %s\n" % emsg)
            return response
        return autocsrf_tween
    # if auto-csrf support is not enabled, return the original
    # handler
    return handler
