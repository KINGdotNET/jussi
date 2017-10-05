# -*- coding: utf-8 -*-
import argparse
import os

from sanic import Sanic

import jussi.errors
import jussi.handlers
import jussi.listeners
import jussi.logging_config
import jussi.middlewares
from jussi.typedefs import WebApp

STEEMIT_MAX_BLOCK_SIZE = 65536
REQUEST_MAX_SIZE = STEEMIT_MAX_BLOCK_SIZE * 5


def setup_routes(app: WebApp) -> WebApp:
    app.add_route(jussi.handlers.healthcheck, '/', methods=['GET'])
    app.add_route(jussi.handlers.healthcheck, '/health', methods=['GET'])
    app.add_route(
        jussi.handlers.healthcheck,
        '/.well-known/healthcheck.json',
        methods=['GET'])
    app.add_route(jussi.handlers.handle_jsonrpc, '/', methods=['POST'])
    return app


def parse_args(args: list = None):
    """parse CLI args and add them to app.config
    """
    parser = argparse.ArgumentParser(description="jussi reverse proxy server")

    # server config
    parser.add_argument('--debug', type=bool, default=False)
    parser.add_argument('--server_host', type=str, default='0.0.0.0')
    parser.add_argument('--server_port', type=int, default=9000)
    parser.add_argument('--server_workers', type=int, default=os.cpu_count())
    parser.add_argument('--REQUEST_MAX_SIZE', type=int,
                        default=REQUEST_MAX_SIZE)
    parser.add_argument('--REQUEST_TIMEOUT', type=int, default=5)
    parser.add_argument('--KEEP_ALIVE', type=bool, default=True)

    parser.add_argument('--upstream_websocket_timeout', type=int, default=2)
    parser.add_argument('--upstream_http_timeout', type=int, default=2)

    # server version
    parser.add_argument('--source_commit', type=str, default='')
    parser.add_argument('--docker_tag', type=str, default='')

    # upstream url config
    parser.add_argument(
        '--upstream_hivemind_url', type=str,
        default='https://hivemind.steemitdev.com')
    parser.add_argument(
        '--upstream_overseer_url', type=str,
        default='https://overseer.steemitdev.com')
    parser.add_argument(
        '--upstream_sbds_url', type=str, default='https://sbds.steemitdev.com')
    parser.add_argument(
        '--upstream_steemd_url', type=str,
        default='wss://steemd.steemitdev.com')
    parser.add_argument(
        '--upstream_yo_url', type=str, default='https://yo.steemitdev.com')

    # redis config
    parser.add_argument('--redis_host', type=str, default=None)
    parser.add_argument('--redis_port', type=int, default=6379)
    parser.add_argument('--redis_namespace', type=str, default='jussi')

    # stats config
    parser.add_argument('--statsd_host', type=str, default=None)
    parser.add_argument('--statsd_port', type=int, default=8125)
    parser.add_argument('--statsd_prefix', type=str, default='jussi')

    return parser.parse_args(args=args)


if __name__ == '__main__':
    args = parse_args()
    # run app
    app = Sanic(__name__)
    app.config.args = args

    app = jussi.logging_config.setup_logging(app)
    app = setup_routes(app)
    app = jussi.middlewares.setup_middlewares(app)
    app = jussi.errors.setup_error_handlers(app)
    app = jussi.listeners.setup_listeners(app)

    app.config.logger.info('app.run')
    app.run(
        host=app.config.args.server_host,
        port=app.config.args.server_port,
        log_config=jussi.logging_config.LOGGING,
        workers=app.config.args.server_workers)
