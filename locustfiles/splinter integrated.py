"""
Author: Aron Fyodor Asor
Last modified: 2015/06/03
Integrated splinter into locust to do benchmark
"""

import time

from locust import Locust, TaskSet, events, task
from splinter import Browser


class BrowserClient():

    def __init__(self, browser_type="phantomjs"):

        self.browser = Browser(browser_type)

    def __getattr__(self, name):

        if name == 'get':
            func = getattr(self.browser, 'visit')
        else:
            func = getattr(self.browser, name)

        def wrapper(*args, **kwargs):
            starttime = time.time()
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                total_time = int((time.time() - starttime) * 1000)
                events.request_failure.fire(request_type="browser",
                                            name=name,
                                            response_time=total_time,
                                            exception=e)
            else:
                total_time = int((time.time() - starttime) * 1000)
                events.request_success.fire(request_type="browser",
                                            name=name,
                                            response_time=total_time,
                                            response_length=0)
                return result

        return wrapper


class BrowserLocust(Locust):

    def __init__(self, *args, **kwargs):
        super(BrowserLocust, self).__init__(*args, **kwargs)
        self.client = BrowserClient()


class BrowserUser(BrowserLocust):
    host = "localhost:8008"

    class task_set(TaskSet):

        @task(2)
        def get_index(self):
            self.client.get(
                'http://localhost:8008/learn/khan/math/early-math/cc-early-math-add-sub-basics/cc-early-math-add-sub-intro/addition_1/')
