# TODO: Este contrato se implementará en spec home-chat-orchestrator-contract
from typing import List, TypedDict


class N8nUserPayload(TypedDict):
    email: str
    perfil: str
    roles: List[str]
    first_name: str
    last_name: str


def build_user_payload(user) -> N8nUserPayload:
    # TODO: Este contrato se implementará en spec home-chat-orchestrator-contract
    return {
        "email": user.email,
        "perfil": user.perfil,
        "roles": list(user.roles.values_list("name", flat=True)),
        "first_name": user.first_name,
        "last_name": user.last_name,
    }
