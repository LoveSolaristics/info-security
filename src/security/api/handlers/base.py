from aiohttp.web import View, Request


class BaseView(View):
    def __init__(self, request: Request):
        # self.base = self.request.app['pg_db_manager']
        super().__init__(request)
