from typing import List

# коды объектов
VOID = 0
WALL = 1
BOX = 2
PLACE = 3
MAN = 4  # заменяется на VOID

class BitWriter:
    def __init__(self):
        self.buffer = 0
        self.bit_count = 0
        self.bytes = []

    def write_bits(self, value: int, count: int):
        for i in reversed(range(count)):
            bit = (value >> i) & 1
            self.buffer = (self.buffer << 1) | bit
            self.bit_count += 1
            if self.bit_count == 16:
                self.flush()

    def flush(self):
        if self.bit_count == 0:
            return
        self.buffer <<= (16 - self.bit_count)
        self.buffer &= 0xFFFF
        self.bytes.append((self.buffer >> 8) & 0xFF)
        self.bytes.append(self.buffer & 0xFF)
        self.buffer = 0
        self.bit_count = 0

    def get_bytes(self):
        if self.bit_count > 0:
            self.flush()
        return self.bytes

class LevelEncoder:
    def __init__(self, level: List[List[int]]):
        self.original_level = level
        self.height = len(level)
        self.width = len(level[0]) if level else 0
        self.level = [row[:] for row in level]
        self.man_x = -1
        self.man_y = -1
        self._find_and_replace_man()
        self.flat = [cell for row in self.level for cell in row]

    def _find_and_replace_man(self):
        for y, row in enumerate(self.level):
            for x, value in enumerate(row):
                if value == MAN:
                    self.man_x = x
                    self.man_y = y
                    self.level[y][x] = VOID  # Заменяем на VOID
                    return
        raise ValueError("Игрок (MAN) не найден на карте")

    def encode(self) -> List[int]:
        writer = BitWriter()
        # размеры карты
        writer.write_bits(self.width, 8)
        writer.write_bits(self.height, 8)
        # координаты игрока
        writer.write_bits(self.man_x, 8)
        writer.write_bits(self.man_y, 8)

        i = 0
        while i < len(self.flat):
            current = self.flat[i]
            run_length = 1
            for j in range(i + 1, len(self.flat)):
                if self.flat[j] != current or run_length >= 9:
                    break
                run_length += 1

            if run_length > 1:
                writer.write_bits(1, 1)  # Признак повтора
                writer.write_bits(run_length - 2, 3)  # от 0 до 7
            else:
                writer.write_bits(0, 1)

            # код объекта: 2 бита
            if current not in (VOID, WALL, BOX, PLACE):
                raise ValueError(f"Неизвестный объект: {current}")
            writer.write_bits(current, 2)

            i += run_length

        return writer.get_bytes()

if __name__ == "__main__":
    level = [
        [1, 1, 1, 1, 1, 1, 1],
        [1, 3, 0, 3, 0, 3, 1],
        [1, 0, 2, 2, 2, 0, 1],
        [1, 3, 2, 4, 2, 3, 1],
        [1, 0, 2, 2, 2, 0, 1],
        [1, 3, 0, 3, 0, 3, 1],
        [1, 1, 1, 1, 1, 1, 1],
    ]

    encoder = LevelEncoder(level)
    encoded_bytes = encoder.encode()
    print('[' + ', '.join(f'0x{byte:02X}' for byte in encoded_bytes) + ']')

    # [0x07, 0x07, 0x03, 0x03, 0xE5, 0x86, 0x1C, 0x22, 0x61, 0x0B, 0x41, 0x38, 0x44, 0xC2, 0x16, 0x18, 0x7C, 0x80]
    # [0x07, 0x07, 0x03, 0x03, 0xE5, 0x83, 0x06, 0x84, 0x4C, 0x21, 0x64, 0x13, 0x42, 0x26, 0x10, 0xB0, 0x60, 0xDC, 0x80,
    #  0x00]
