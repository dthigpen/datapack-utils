def coordinate_range(min_coord: tuple[int, int, int], max_coord: tuple[int, int, int]):
    values = set()
    for x in range(min_coord[0], max_coord[0] + 1):
        for y in range(min_coord[1], max_coord[1] + 1):
            for z in range(min_coord[2], max_coord[2] + 1):
                value = (x, y, z)
                if value not in values:
                    print(value)
                    values.add(value)
                    yield value


def permute_range(start, end):
    for i in range(start, end + 1):
        for j in range(start, i + 1):
            yield (i, j)
