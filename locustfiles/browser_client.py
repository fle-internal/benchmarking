import time
import traceback

from locust import HttpLocust, Locust, TaskSet, events, task
from splinter import Browser


class BrowserClient():

    def __init__(self, base_url, browser_type="phantomjs"):
        """
        Initialize the browser client with browser_type, the name of the browser to run.
        Defaults to phantomjs.
        """

        self.browser = Browser(browser_type)
        self.base_url = base_url

    def __getattr__(self, name):

        if name == 'get':
            def func(url):
                self.browser.visit(self.base_url + url)
                return self.browser.html
        else:
            func = getattr(self.browser, name)

        def wrapper(*args, **kwargs):
            starttime = time.time()
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                print traceback.print_exc()
                total_time = int((time.time() - starttime) * 1000)
                events.request_failure.fire(request_type="browser",
                                            name=args[0],
                                            response_time=total_time,
                                            exception=e)
            else:
                total_time = int((time.time() - starttime) * 1000)
                events.request_success.fire(request_type="browser",
                                            name=args[0],
                                            response_time=total_time,
                                            response_length=len(result))
                return result

        return wrapper


class BrowserLocust(Locust):

    host = None

    def __init__(self, *args, **kwargs):
        super(BrowserLocust, self).__init__(*args, **kwargs)
        self.client = BrowserClient(self.host)


class BrowserUser(BrowserLocust):

    class task_set(TaskSet):

        @task(2)
        def get_index(self):
            self.client.get('/')

        @task(2)
        def get_exercise(self):
            self.client.get('/learn/khan/math/early-math/cc-early-math-add-sub-basics/cc-early-math-add-sub-intro/addition_1/')
