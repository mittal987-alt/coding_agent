class MCPClientError(Exception):
    pass


class MCPConnectionError(MCPClientError):
    pass


class MCPProtocolError(MCPClientError):
    pass


class MCPInitializationError(MCPClientError):
    pass