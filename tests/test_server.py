import copy
import pathlib
import tempfile
import tomllib
import unittest.mock
from importlib import resources

import tomli_w

from imbi_gateway import server
from tests import helpers


class RunServerTests(helpers.TestCase):
    def setUp(self) -> None:
        super().setUp()
        cfg_file = resources.files('imbi_common') / 'log-config.toml'
        self.default_config = tomllib.loads(cfg_file.read_text())
        self.uvicorn_module = self.enterContext(
            unittest.mock.patch('imbi_gateway.server.uvicorn')
        )

    @staticmethod
    def get_args(**overrides: object) -> dict[str, object]:
        """Returns the default kwargs for uvicorn.run with overrides."""
        return {
            'env_file': None,
            'factory': True,
            'host': '127.0.0.1',
            'log_config': unittest.mock.ANY,
            'port': 8000,
        } | overrides

    def test_running_server_with_no_args(self) -> None:
        server.serve('package:create_app')
        self.uvicorn_module.run.assert_called_once_with(
            'package:create_app',
            **self.get_args(log_config=self.default_config),
        )

    def test_running_server_with_custom_host(self) -> None:
        server.serve('package:create_app', host='192.168.10.10')
        self.uvicorn_module.run.assert_called_once_with(
            'package:create_app',
            **self.get_args(host='192.168.10.10'),
        )

    def test_running_server_with_custom_port(self) -> None:
        server.serve('package:create_app', port=1234)
        self.uvicorn_module.run.assert_called_once_with(
            'package:create_app',
            **self.get_args(port=1234),
        )

    def test_running_server_with_custom_log_config(self) -> None:
        custom_cfg = copy.deepcopy(self.default_config)
        loggers = custom_cfg.setdefault('loggers', {})
        loggers['uvicorn'] = {'level': 'DEBUG'}

        with tempfile.NamedTemporaryFile() as f:
            tomli_w.dump(custom_cfg, f)
            f.seek(0)
            server.serve(
                'package:create_app',
                log_config=pathlib.Path(f.name),
            )
        self.uvicorn_module.run.assert_called_once_with(
            'package:create_app',
            **self.get_args(log_config=custom_cfg),
        )

    def test_running_server_in_verbose_mode(self) -> None:
        log_config = copy.deepcopy(self.default_config)
        log_config['loggers']['package'] = {'level': 'DEBUG'}
        log_config['loggers']['imbi_common'] = {'level': 'DEBUG'}

        server.serve('package:create_app', verbose=True)
        self.uvicorn_module.run.assert_called_once_with(
            'package:create_app',
            **self.get_args(log_config=log_config),
        )

    def test_running_server_in_dev_mode(self) -> None:
        server.serve('package:create_app', dev=True)
        self.uvicorn_module.run.assert_called_once_with(
            'package:create_app',
            **self.get_args(reload=True),
        )
