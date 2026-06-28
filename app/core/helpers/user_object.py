from typing import List, TypedDict


class UserObject(TypedDict):
    userId: int
    userEmail: str
    userName: str
    profile: str
    roles: List[str]
    memoryEnabled: bool


class UserObjectBuilder:
    @staticmethod
    def build(user) -> UserObject:
        full_name = f"{user.first_name} {user.last_name}".strip()
        user_name = full_name if full_name else user.username

        if user.perfil != 'Usuario IC':
            roles_list: List[str] = []
        else:
            roles_list = list(user.roles.values_list('name', flat=True))

        return UserObject(
            userId=user.id,
            userEmail=user.email,
            userName=user_name,
            profile=user.perfil,
            roles=roles_list,
            memoryEnabled=user.memoria_habilitada,
        )
