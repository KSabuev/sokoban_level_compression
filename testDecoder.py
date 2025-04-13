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
            # Повторы
            if self.load_bit(1):
                bufer = self.load_bit(3)
                n_replay = 2 + ((bufer >> 2) & 1) * 4 + ((bufer >> 1) & 1) * 2 + (bufer & 1)
            else:
                n_replay = 1

            # Элемент
            if self.load_bit(1):
                if self.load_bit(1):
                    element = MAN if self.load_bit(1) else PLACE
                else:
                    element = BOX
            elif self.load_bit(1):
                element = WALL
            else:
                element = VOID

            for _ in range(n_replay):
                x = m % size_x
                y = m // size_x
                if y < size_y:
                    level[y][x] = element
                m += 1
        level[user_y][user_x] = 4
        return level

    @staticmethod
    def print_as_array(level):
        print("[")
        for row in level:
            print("  " + str(row) + ",")
        print("]")

if __name__ == "__main__":
    encoded_level = \
        [0x16, 0x0B, 0x03, 0x05, 0xA2, 0xDF, 0x38, 0x32, 0x1F, 0x38, 0x2A, 0x03, 0xE6, 0x12, 0xC0, 0xA5, 0xF2, 0x83,
         0x02, 0x81, 0x03, 0xE4, 0x12, 0xB9, 0x12, 0x83, 0x66, 0xB2, 0x11, 0x28, 0xD6, 0x08, 0xD0, 0x85, 0x02, 0xF2,
         0x88, 0xD8, 0x8A, 0x41, 0x14, 0xC1, 0x18, 0xD0, 0x70, 0x96, 0x0C, 0x68, 0xE7, 0xC0]

    decoder = LevelDecoder(encoded_level)
    level = decoder.decode()
    decoder.print_as_array(level)

    # [
    #     [0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 1, 2, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 1, 1, 1, 0, 0, 2, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 1, 0, 0, 2, 0, 0, 2, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [1, 1, 1, 4, 1, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1],
    #     [1, 0, 0, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 3, 3, 1],
    #     [1, 0, 2, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 1],
    #     [1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 0, 0, 3, 3, 1],
    #     [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1],
    #     [0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    # ]