from ._run import CodynfluxAgentSDK

__all__ = ["run"]

_agent = CodynfluxAgentSDK()
run = _agent.run
