"""
Integration modules connecting ACME to existing projects.

- paperclip: control plane / task scheduling
- agileagents: serverless execution
- momoa: AI consensus/debate
- shoggoth: self-hosting
- actor: distributed execution
"""

from .paperclip_integration import PaperclipBridge
from .security_integration import SecurityComponent, UnifiedSecurityTool

__all__ = [
    "PaperclipBridge",
    "SecurityComponent",
    "UnifiedSecurityTool",
]
