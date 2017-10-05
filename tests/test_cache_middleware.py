# -*- coding: utf-8 -*-
import json

from sanic import Sanic

import asynctest
import pytest
from jussi.middlewares.caching import cache_response
from jussi.middlewares.caching import get_response

req = {"id": 1, "jsonrpc": "2.0", "method": "get_block", "params": [1000]}
expected_response = {
    "id": 1,
    "jsonrpc": "2.0",
    "result": {
        "previous": "000003e7c4fd3221cf407efcf7c1730e2ca54b05",
        "timestamp": "2016-03-24T16:55:30",
        "witness": "initminer",
        "transaction_merkle_root": "0000000000000000000000000000000000000000",
        "extensions": [],
        "witness_signature": "207f15578cac20ac0e8af1ebb8f463106b8849577e21cca9fc60da146d1d95df88072dedc6ffb7f7f44a9185bbf9bf8139a5b4285c9f423843720296a44d428856",
        "transactions": [],
        "block_id": "000003e8b922f4906a45af8e99d86b3511acd7a5",
        "signing_key": "STM8GC13uCZbP44HzMLV6zPZGwVQ8Nt4Kji8PapsPiNq1BK153XTX",
        "transaction_ids": []}}


@pytest.mark.live
async def test_cache_response_middleware(test_cli):
    response = await test_cli.post('/', json=req)
    assert await response.json() == expected_response
    response = await test_cli.post('/', json=req)
    assert response.headers['x-jussi-cache-hit'] == 'steemd.database_api.get_block.params=[1000]'


async def test_mocked_cache_response_middleware(mocked_app_test_cli, mocker):
    mocked_ws_conn, test_cli = mocked_app_test_cli
    mocked_ws_conn.receive_json.return_value = expected_response
    print(mocked_ws_conn)
    print(mocked_ws_conn.receive_json)
    with mocker.patch('jussi.handlers.random', getrandbits=lambda x: 1) as mocked_rand:

        response = await test_cli.post('/', json=req)
        assert 'x-jussi-cache-hit' not in response.headers
        assert await response.json() == expected_response

        response = await test_cli.post('/', json=req)
        assert response.headers['x-jussi-cache-hit'] == 'steemd.database_api.get_block.params=[1000]'
        assert await response.json() == expected_response
