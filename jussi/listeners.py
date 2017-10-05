# -*- coding: utf-8 -*-
import aiohttp

import ujson

from .cache import setup_caches
from .typedefs import WebApp
from .upstream.url import deref_urls


def setup_listeners(app: WebApp) -> WebApp:
    # pylint: disable=unused-argument, unused-variable
    @app.listener('before_server_start')
    def setup_jsonrpc_method_url_settings(app: WebApp, loop) -> None:
        loop.set_debug(True)
        logger = app.config.logger
        logger.info('before_server_start -> setup_jsonrpc_method_url_settings')
        args = app.config.args
        mapping = {
            'hivemind_default': args.upstream_hivemind_url,
            'jussi_default': 'localhost',
            'overseer_default': args.upstream_overseer_url,
            'sbds_default': args.upstream_sbds_url,
            'steemd_default': args.upstream_steemd_url,
            'yo_default': args.upstream_yo_url,
        }
        app.config.upstream_urls = deref_urls(
            url_mapping=mapping)

    @app.listener('before_server_start')
    def setup_aiohttp_session(app: WebApp, loop) -> None:
        """use one session for http connection pooling
        """
        logger = app.config.logger
        logger.info('before_server_start -> setup_aiohttp_session')
        aio = dict(session=aiohttp.ClientSession(
            skip_auto_headers=['User-Agent'],
            loop=loop,
            json_serialize=ujson.dumps,
            headers={'Content-Type': 'application/json'}))
        app.config.aiohttp = aio

    @app.listener('before_server_start')
    async def setup_caching(app: WebApp, loop) -> None:
        logger = app.config.logger
        logger.info('before_server_start -> setup_caching')
        cache_group = setup_caches(app, loop)
        app.config.cache_group = cache_group
        app.config.last_irreversible_block_num = 15_000_000

    @app.listener('after_server_stop')
    async def close_aiohttp_session(app: WebApp, loop) -> None:
        logger = app.config.logger
        logger.info('after_server_stop -> close_aiohttp_session')
        session = app.config.aiohttp['session']
        await session.close()

    @app.listener('after_server_stop')
    async def shutdown_caching(app: WebApp, loop) -> None:
        logger = app.config.logger
        logger.info('after_server_stop -> shutdown_caching')
        cache_group = app.config.cache_group
        await cache_group.close()

    return app
