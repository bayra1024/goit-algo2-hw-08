import time
from typing import Dict
import random


class ThrottlingRateLimiter:
    def __init__(self, min_interval: float = 10.0):
        self.min_interval = min_interval
        self.messages = {}

    def can_send_message(self, user_id: str) -> bool:
        if user_id in self.messages.keys():
            if time.time() - self.messages[user_id] > self.min_interval:
                return True
            else:
                return False
        return True

    def record_message(self, user_id: str) -> bool:
        if user_id in self.messages.keys():
            if time.time() - self.messages[user_id] > self.min_interval:
                self.messages[user_id] = time.time()
                return True
            else:
                return False
        self.messages[user_id] = time.time()
        return True

    def time_until_next_allowed(self, user_id: str) -> float:
        if user_id in self.messages.keys():
            if time.time() - self.messages[user_id] > self.min_interval:
                return 0
            else:
                return self.min_interval - (time.time() - self.messages[user_id])
        return 0


def test_throttling_limiter():
    limiter = ThrottlingRateLimiter(min_interval=10.0)

    print("\n=== Симуляція потоку повідомлень (Throttling) ===")
    for message_id in range(1, 11):
        user_id = message_id % 5 + 1

        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))

        print(
            f"Повідомлення {message_id:2d} | Користувач {user_id} | "
            f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}"
        )

        # Випадкова затримка між повідомленнями
        time.sleep(random.uniform(0.1, 1.0))

    print("\nОчікуємо 4 секунд...")
    time.sleep(4)

    print("\n=== Нова серія повідомлень після очікування ===")
    for message_id in range(11, 21):
        user_id = message_id % 5 + 1
        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))
        print(
            f"Повідомлення {message_id:2d} | Користувач {user_id} | "
            f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}"
        )
        time.sleep(random.uniform(0.1, 1.0))


if __name__ == "__main__":
    test_throttling_limiter()
