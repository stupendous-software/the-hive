from python.helpers.api import ApiHandler
from flask import Response
import json

class HealthHandler(ApiHandler):
    @classmethod
    def get_methods(cls) -> list[str]:
        return ['GET']
    @classmethod
    def requires_auth(cls) -> bool:
        return False
    @classmethod
    def requires_loopback(cls) -> bool:
        return False
    @classmethod
    def requires_api_key(cls) -> bool:
        return False
    @classmethod
    def requires_csrf(cls) -> bool:
        return False
    async def process(self, input: dict, request):
        return {'status': 'ok'}
