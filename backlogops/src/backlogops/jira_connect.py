#! /usr/local/bin/python3
"""A pool of authenticated Jira clients reused across reads and writes.

A :class:`JiraConnections` opens at most one live :class:`jira.JIRA`
client per named connection of a
:class:`backlogops.jira_io_config.JiraIOConfig` and hands the same client
to every read and write that names that connection. Before reusing a
previously opened client it checks the client is still alive, and
reconnects when the Jira server has closed an idle connection. A client
opened in the current call is trusted, so a genuine connection failure is
reported instead of retried forever.

A cloud connection authenticates with the login email and the token; a
server connection uses the token as a personal access token. The token is
materialized through :meth:`JiraConnectConfig.get_token`, asking the
supplied pass phrase provider only when an encrypted storage mode needs
it.
"""

# Copyright (c) 2026, Tom Björkholm
# MIT License

from typing import Callable, Optional
from jira import JIRA, JIRAError
from backlogops.jira_io_config import JiraConnectConfig, JiraIOConfig, JiraType


def _connect(connection: JiraConnectConfig,
             passphrase: Optional[Callable[[], str]]) -> JIRA:
    """Return a Jira client connected with the connection's token."""
    token = connection.get_token(passphrase)
    if connection.jira_type is JiraType.SERVER:
        return JIRA(server=connection.base_url, token_auth=token)
    return JIRA(server=connection.base_url,
                basic_auth=(connection.login_email, token))


def _is_alive(client: JIRA) -> bool:
    """Return whether the client's session still reaches the server."""
    try:
        client.myself()
        return True
    except JIRAError:
        return False


def _safe_close(client: JIRA) -> None:
    """Close a client, ignoring an error from an already-dead session."""
    try:
        client.close()  # type: ignore[no-untyped-call]
    except (JIRAError, OSError):
        pass


class JiraConnections:
    """A reusable pool of live Jira clients keyed by connection name.

    The pool is built from a :class:`JiraIOConfig`, so it can resolve any
    connection named by a read or write preset, and from an optional pass
    phrase provider used when a connection stores an encrypted token. The
    same client is reused for repeated reads and writes that name the same
    connection; a client the Jira server has since closed is replaced on
    the next use.
    """

    def __init__(self, jira_config: JiraIOConfig,
                 passphrase: Optional[Callable[[], str]] = None) -> None:
        """Store the configuration and start with no open clients."""
        self.jira_config = jira_config
        self._passphrase = passphrase
        self._clients: dict[str, JIRA] = {}

    def client(self, connection_name: str) -> JIRA:
        """Return a live client for the named connection, reconnecting it.

        A previously opened client is reused when it is still alive, and
        replaced by a fresh connection when the server has closed it. A
        connection opened in this call is returned without a further live
        check, so a real connection failure raises instead of looping.

        Args:
            connection_name: The name of the connection to use.

        Returns:
            A live Jira client for the connection.

        Raises:
            KeyError: If the configuration has no such connection.
        """
        cached = self._clients.get(connection_name)
        if cached is not None:
            if _is_alive(cached):
                return cached
            _safe_close(cached)
            del self._clients[connection_name]
        connection = self.jira_config.connections[connection_name]
        fresh = _connect(connection, self._passphrase)
        self._clients[connection_name] = fresh
        return fresh

    def close(self) -> None:
        """Close every open client and forget it."""
        for client in self._clients.values():
            _safe_close(client)
        self._clients.clear()
