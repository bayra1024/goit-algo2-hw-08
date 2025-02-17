import random
from typing import Dict
import time
from collections import deque


class SlidingWindowRateLimiter:
    def __init__(self, window_size: int = 10, max_requests: int = 1):
        self.windows_size = window_size
        self.max_requests = max_requests
        self.dq = deque()
        pass

    # Чистимо чергу від старих повідомлень при кожному виклику функцій
    def _drop_old(self):
        time_now = time.time()
        old = True
        while old:
            if len(self.dq):
                if time_now - self.dq[0]["time"] > self.windows_size:
                    self.dq.popleft()
                else:
                    old = False
            else:
                old = False

    # для очищення застарілих запитів з вікна та оновлення активного часового вікна
    def _cleanup_window(self, user_id: str, current_time: float) -> None:
        self._drop_old()

    # для перевірки можливості відправлення повідомлення в поточному часовому вікні;
    def can_send_message(self, user_id: str) -> bool:
        time_now = time.time()
        self._drop_old()
        msg_count = 0
        for i in self.dq:
            if user_id == i["user_id"]:
                if time_now - i["time"] < self.windows_size:
                    msg_count += 1

        if msg_count < self.max_requests:
            return True
        else:
            return False

    # для запису нового повідомлення й оновлення історії користувача;
    def record_message(self, user_id: str) -> bool:
        time_now = time.time()
        self._drop_old()
        msg_count = 0

        for i in self.dq:
            if user_id == i["user_id"]:
                if time_now - i["time"] < self.windows_size:
                    msg_count += 1

        if msg_count < self.max_requests:
            self.dq.append({"user_id": user_id, "time": time.time()})
            return True
        else:
            return False

    # для розрахунку часу очікування до можливості відправлення наступного повідомлення
    def time_until_next_allowed(self, user_id: str) -> float:
        time_now = time.time()
        send_time = time.time()
        self._drop_old()
        msg_count = 0
        # print(f"time_now = {time.strftime('%H:%M:%S',time.gmtime(time_now)) }")
        for i in self.dq:
            if user_id == i["user_id"]:
                if time_now - i["time"] < 10:
                    msg_count += 1
                    # Якщо дозволено кілька повідомлень, то шукаємо саме старе
                    send_time = min(send_time, i["time"])
                    # print(
                    #     f"msg_time = {time.strftime('%H:%M:%S',time.gmtime(i["time"])) }"
                    # )
                    # print(
                    #     f"send_time = {time.strftime('%H:%M:%S',time.gmtime(send_time)) }"
                    # )

        if msg_count < self.max_requests:
            return 0
        else:
            return self.windows_size - (time_now - send_time)


# Демонстрація роботи
def test_rate_limiter():
    # Створюємо rate limiter: вікно 10 секунд, 1 повідомлення
    limiter = SlidingWindowRateLimiter(window_size=10, max_requests=1)

    # Симулюємо потік повідомлень від користувачів (послідовні ID від 1 до 20)
    print("\n=== Симуляція потоку повідомлень ===")
    for message_id in range(1, 11):
        # Симулюємо різних користувачів (ID від 1 до 5)
        user_id = message_id % 5 + 1

        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))
        # wait_time = wait_time if wait_time else 0
        print(
            f"Повідомлення {message_id:2d} | Користувач {user_id} | "
            f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}"
        )

        # Невелика затримка між повідомленнями для реалістичності
        # Випадкова затримка від 0.1 до 1 секунди
        time.sleep(random.uniform(0.1, 1.0))

    # Чекаємо, поки вікно очиститься
    print("\nОчікуємо 4 секунди...")
    time.sleep(4)

    print("\n=== Нова серія повідомлень після очікування ===")
    for message_id in range(11, 21):
        user_id = message_id % 5 + 1
        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))
        # wait_time = wait_time if wait_time else 0
        print(
            f"Повідомлення {message_id:2d} | Користувач {user_id} | "
            f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}"
        )
        # Випадкова затримка від 0.1 до 1 секунди
        time.sleep(random.uniform(0.1, 1.0))
    # print(limiter.dq)


if __name__ == "__main__":
    test_rate_limiter()
