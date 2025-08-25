import types
from backend.interface import mysql_interface

def test_connect_db_uses_port(monkeypatch):
    called = {}

    class DummyConn:
        def is_connected(self):
            return True

    def dummy_connect(**kwargs):
        called.update(kwargs)
        return DummyConn()

    dummy_module = types.SimpleNamespace(connect=dummy_connect, Error=Exception, errorcode=types.SimpleNamespace())
    monkeypatch.setattr(mysql_interface, 'mysql_connector_lib', dummy_module)
    monkeypatch.setattr(mysql_interface, 'MYSQL_AVAILABLE', True)

    iface = mysql_interface.MySQLInterface(host='h', user='u', password='p', database='d', port=1234)
    iface.connect_db()

    assert called['port'] == 1234
