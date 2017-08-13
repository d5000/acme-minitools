# # Twill as a WSGI-intercept controller
# import unittest
# import twill
# from pyramid import loadapp, conf_dir


# class TwillTestController(unittest.TestCase):

#     wsgi_app = loadapp('config:test.ini', relative_to=conf_dir)

#     def setUp(self):
#         def build_app():
#             return self.wsgi_app

#         twill.add_wsgi_intercept('localhost', 8080, build_app)

#     def tearDown(self):
#         twill.remove_wsgi_intercept('localhost', 8080)


# # Then I changed {{package}}/tests/functional/test_twillbase.py to
# # from {{package}}.tests import TwillTestController
# # from twill.commands import *
# #
# # class MyTestController(TwillTestController):
# #     def test_index(self):
# #         go('http://localhost:8080/')
# #         find('World')
# #         notfind('Universe')
