import time
import random
import string


def _to_base36(number: int) -> str:
    if number == 0:
        return '0'
    alphabet = string.digits + string.ascii_lowercase
    result = []
    while number:
        number, remainder = divmod(number, 36)
        result.append(alphabet[remainder])
    return ''.join(reversed(result))


class ConversationIdManager:
    SESSION_KEY = 'conversationId'

    @staticmethod
    def generate_conversation_id() -> str:
        timestamp_b36 = _to_base36(int(time.time()))
        random_suffix = ''.join(
            random.choices(string.ascii_lowercase + string.digits, k=6)
        )
        return f"conv-{timestamp_b36}-{random_suffix}"

    @classmethod
    def get_or_create(cls, session) -> str:
        conversation_id = session.get(cls.SESSION_KEY)
        if not conversation_id:
            conversation_id = cls.generate_conversation_id()
            session[cls.SESSION_KEY] = conversation_id
            session.modified = True
        return conversation_id

    @classmethod
    def reset(cls, session) -> str:
        conversation_id = cls.generate_conversation_id()
        session[cls.SESSION_KEY] = conversation_id
        session.modified = True
        return conversation_id
