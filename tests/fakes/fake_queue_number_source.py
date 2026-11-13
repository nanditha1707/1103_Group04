class FakeQueueNumberSource:
    def __init__(
        self, highest_number: int | None
    ) -> None:
        self.__highest_number = highest_number
        self.__requests: list[tuple[str, str]] = []

    @property
    def requests(self) -> list[tuple[str, str]]:
        return list(self.__requests)

    def get_highest_queue_number(self, prefix: str, date: str) -> int | None:
        self.__requests.append((prefix, date))
        return self.__highest_number
