from typing import List

# Коды объектов
VOID = 0
WALL = 1
BOX = 2
PLACE = 3
MAN = 4

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
        self.level = level
        self.height = len(level)
        self.width = len(level[0]) if level else 0
        self.flat = [cell for row in level for cell in row]

    def encode(self) -> List[int]:
        writer = BitWriter()
        # Размеры
        writer.write_bits(self.width, 8)
        writer.write_bits(self.height, 8)

        for row_index, row in enumerate(level):
            for col_index, value in enumerate(row):
                if value == 4:
                    writer.write_bits(col_index, 8)
                    writer.write_bits(row_index, 8)

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
                # Повтор от 2 до 9
                code = run_length - 2
                writer.write_bits(code, 3)
            else:
                writer.write_bits(0, 1)

            # Код объекта
            if current == VOID:
                writer.write_bits(0, 1)
                writer.write_bits(0, 1)
            elif current == WALL:
                writer.write_bits(0, 1)
                writer.write_bits(1, 1)
            elif current == BOX:
                writer.write_bits(1, 1)
                writer.write_bits(0, 1)
            elif current == PLACE:
                writer.write_bits(1, 1)
                writer.write_bits(1, 1)
                writer.write_bits(0, 1)
            elif current == MAN:
                writer.write_bits(1, 1)
                writer.write_bits(1, 1)
                writer.write_bits(1, 1)
            else:
                raise ValueError(f"Неизвестный объект: {current}")

            i += run_length

        return writer.get_bytes()

if __name__ == "__main__":
    level = [
        [0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 2, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 1, 1, 1, 0, 0, 2, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 1, 0, 0, 2, 0, 0, 2, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [1, 1, 1, 4, 1, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 3, 3, 1],
        [1, 0, 2, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 1],
        [1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 0, 0, 3, 3, 1],
        [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1],
        [0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    ]

    encoder = LevelEncoder(level)
    encoded_bytes = encoder.encode()
    print('[' + ', '.join(f'0x{byte:02X}' for byte in encoded_bytes) + ']')