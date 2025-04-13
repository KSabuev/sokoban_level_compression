from typing import List

# Коды объектов
VOID = 0
WALL = 1
BOX = 2
PLACE = 3
MAN = 4

class LevelDecoder:
    def __init__(self, data: List[int]):
        self.data = data
        self.byte_index = 0
        self.bit_counter = 0
        self.big_buffer = 0
        self.buffer_ready = False

    def load_bit(self, count: int) -> int:
        result = 0
        for _ in range(count):
            if not self.buffer_ready or self.bit_counter >= 16:
                if self.byte_index + 1 < len(self.data):
                    self.big_buffer = (self.data[self.byte_index] << 8) | self.data[self.byte_index + 1]
                    self.byte_index += 2
                    self.bit_counter = 0
                    self.buffer_ready = True
                else:
                    raise ValueError("Не хватает байтов для чтения.")

            bit = (self.big_buffer & 0x8000) >> 15
            result = (result << 1) | bit
            self.big_buffer = (self.big_buffer << 1) & 0xFFFF
            self.bit_counter += 1

        return result

    def decode(self):
        size_x = self.load_bit(8)
        size_y = self.load_bit(8)
        user_x = self.load_bit(8)
        user_y = self.load_bit(8)
        total_cells = size_x * size_y

        level = [[VOID for _ in range(size_x)] for _ in range(size_y)]

        m = 0
        while m < total_cells:
            # Признак повтора
            is_repeat = self.load_bit(1)
            if is_repeat:
                repeat_code = self.load_bit(3)
                n_replay = repeat_code + 2  # от 2 до 9
            else:
                n_replay = 1

            # 2 бита — тип объекта
            element = self.load_bit(2)
            if element not in (VOID, WALL, BOX, PLACE):
                raise ValueError(f"Некорректный объект: {element}")

            for _ in range(n_replay):
                x = m % size_x
                y = m // size_x
                if y < size_y:
                    level[y][x] = element
                m += 1

        # Вставляем игрока
        level[user_y][user_x] = MAN
        return level

    @staticmethod
    def print_as_array(level):
        print("[")
        for row in level:
            print("  " + str(row) + ",")
        print("]")

if __name__ == "__main__":
    encoded_level = \
        [0x07, 0x07, 0x03, 0x03, 0xE5, 0x86, 0x1C, 0x22, 0x61, 0x0B, 0x41, 0x38, 0x44, 0xC2, 0x16, 0x18, 0x7C, 0x80]

    decoder = LevelDecoder(encoded_level)
    level = decoder.decode()
    decoder.print_as_array(level)

    # [
    #     [1, 1, 1, 1, 1, 1, 1],
    #     [1, 3, 0, 3, 0, 3, 1],
    #     [1, 0, 2, 2, 2, 0, 1],
    #     [1, 3, 2, 4, 2, 3, 1],
    #     [1, 0, 2, 2, 2, 0, 1],
    #     [1, 3, 0, 3, 0, 3, 1],
    #     [1, 1, 1, 1, 1, 1, 1],
    # ]
