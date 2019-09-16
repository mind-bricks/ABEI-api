from redis import Redis

from mbcom.interfaces import (
    IStorage,
    IService,
    service_entry as _
)


class Service(IService):

    def __init__(self, service_site, **kwargs):
        service = service_site.get_service(_(IStorage))
        redis_host = service.get_value('redis:host')
        redis_port = service.get_value('redis:port')
        redis_password = service.get_value('redis:password')
        self.redis = Redis(
            host=redis_host or '127.0.0.1',
            port=redis_port or '6379',
            password=redis_password or '2v0eps4o')
        print("----service redis component initialized----")
