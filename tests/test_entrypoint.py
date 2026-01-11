import unittest.mock

from imbi_gateway import entrypoint
from tests import helpers


class EntrypointTests(helpers.TestCase):
    def test_entrypoint_defaults(self) -> None:
        with unittest.mock.patch('imbi_gateway.entrypoint.server') as mocked:
            entrypoint.serve()
            mocked.serve.assert_called_once_with(
                'imbi_gateway.app:create_app',
                dev=False,
                env_file=None,
                host='127.0.0.1',
                log_config=None,
                port=8000,
                verbose=False,
            )

    def test_entrypoint_parameters(self) -> None:
        with unittest.mock.patch('imbi_gateway.entrypoint.server') as mocked:
            entrypoint.serve(
                dev=unittest.mock.sentinel.dev,
                env_file=unittest.mock.sentinel.env_file,
                host=unittest.mock.sentinel.host,
                log_config=unittest.mock.sentinel.log_config,
                port=unittest.mock.sentinel.port,
                verbose=unittest.mock.sentinel.verbose,
            )
            mocked.serve.assert_called_once_with(
                'imbi_gateway.app:create_app',
                dev=unittest.mock.sentinel.dev,
                env_file=unittest.mock.sentinel.env_file,
                host=unittest.mock.sentinel.host,
                log_config=unittest.mock.sentinel.log_config,
                port=unittest.mock.sentinel.port,
                verbose=unittest.mock.sentinel.verbose,
            )
