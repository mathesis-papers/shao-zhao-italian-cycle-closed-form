import hashlib
import itertools
import json
from fractions import Fraction
from math import comb


def choose(top, bottom):
    return comb(top, bottom) if 0 <= bottom <= top else 0


def coefficient(length, deficit):
    if length < 3 or not 0 <= deficit <= 2 * length:
        raise ValueError('Expected a simple cycle and a deficit between zero and twice its length')
    total = Fraction(0)
    twos = deficit - length
    ones = 2 * length - deficit
    if 0 <= twos and 2 * twos <= length and 0 < ones:
        total += Fraction(length * choose(ones, twos), ones)
    if length % 3 == 0 and 3 * deficit == 4 * length:
        total += 3
    for exceptional in range(deficit // 4 + 1):
        for isolated in range((deficit - 4 * exceptional) // 2 + 1):
            single = deficit - 2 * isolated - 4 * exceptional
            ordinary = length - deficit + isolated + exceptional
            zeros = ordinary + exceptional
            if ordinary >= 1:
                total += Fraction(
                    length * choose(zeros, exceptional)
                    * choose(single + ordinary - 1, single)
                    * choose(single + ordinary, isolated), zeros)
    assert total.denominator == 1
    return total.numerator


def brute_force(length):
    counts = [0] * (2 * length + 1)
    for labels in itertools.product(range(3), repeat=length):
        if all(label != 0 or labels[index - 1] + labels[(index + 1) % length] >= 2
               for index, label in enumerate(labels)):
            counts[2 * length - sum(labels)] += 1
    return counts


def transfer_counts(length):
    counts = [0] * (2 * length + 1)
    for first in range(3):
        for second in range(3):
            states = {(first, second, first + second): 1}
            for position in range(2, length):
                updated = {}
                for (previous, current, weight), count in states.items():
                    for following in range(3):
                        if current != 0 or previous + following >= 2:
                            key = (current, following, weight + following)
                            updated[key] = updated.get(key, 0) + count
                states = updated
            for (previous, last, weight), count in states.items():
                if (last != 0 or previous + first >= 2) and (
                        first != 0 or last + second >= 2):
                    counts[2 * length - weight] += count
    return counts


def convolution_coefficient(length, deficit):
    return sum(choose(length, twos) * choose(length - twos, deficit - 2 * twos)
               for twos in range(deficit // 2 + 1))


def graph_counts(neighbors, roman=False):
    length = len(neighbors)
    counts = [0] * (2 * length + 1)
    for labels in itertools.product(range(3), repeat=length):
        valid = all(label != 0 or (
            any(labels[neighbor] == 2 for neighbor in neighbors[index]) if roman
            else sum(labels[neighbor] for neighbor in neighbors[index]) >= 2)
            for index, label in enumerate(labels))
        if valid:
            counts[2 * length - sum(labels)] += 1
    return counts


def path_counts(length):
    if length == 1:
        return [1, 1, 0]
    counts = [0] * (2 * length + 1)
    states = {(first, second, first + second): 1
              for first in range(3) for second in range(3)
              if first != 0 or second == 2}
    for position in range(2, length):
        updated = {}
        for (previous, current, weight), count in states.items():
            for following in range(3):
                if current != 0 or previous + following >= 2:
                    key = (current, following, weight + following)
                    updated[key] = updated.get(key, 0) + count
        states = updated
    for (previous, last, weight), count in states.items():
        if last != 0 or previous == 2:
            counts[2 * length - weight] += count
    return counts


def multiply_matrices(left, right):
    size = len(left)
    return [[sum(left[row][inner] * right[inner][column] for inner in range(size))
             for column in range(size)] for row in range(size)]


def transfer_matrix_checks():
    states = list(itertools.product(range(3), repeat=2))
    matrix = [[int(current[1] == following[0] and (
        current[1] != 0 or current[0] + following[1] >= 2))
        for following in states] for current in states]
    power = [[int(row == column) for column in range(9)] for row in range(9)]
    traces = [9]
    for exponent in range(1, 10):
        power = multiply_matrices(power, matrix)
        traces.append(sum(power[index][index] for index in range(9)))
        if exponent == 4:
            assert all(value > 0 for row in power for value in row)
    characteristic = [1]
    for order in range(1, 10):
        value = -sum(characteristic[order - offset] * traces[offset]
                     for offset in range(1, order + 1))
        assert value % order == 0
        characteristic.append(value // order)
    assert characteristic == [1, -2, -2, -1, 1, 1, 0, 0, 0, 0]
    return {'matrix_size': 9, 'fourth_power_strictly_positive': True,
            'characteristic_polynomial': 'u^4*(u^5-2*u^4-2*u^3-u^2+u+1)',
            'trace_n3_to_n7': traces[3:8]}


def main():
    rows = {}
    compared = 0
    for length in range(3, 41):
        values = [coefficient(length, deficit) for deficit in range(2 * length + 1)]
        assert values == transfer_counts(length), ('transfer', length)
        if length <= 10:
            assert values == brute_force(length), ('enumeration', length)
        assert values[0] == 1 and values[-1] == 0
        assert all(value >= 0 for value in values)
        for deficit in range(5):
            assert values[deficit] == convolution_coefficient(length, deficit)
        if length >= 4:
            assert values[5] == convolution_coefficient(length, 5) - 2 * length
        rows[length] = values
        compared += len(values)
    for length in range(3, 36):
        current = rows[length + 5]
        for deficit, value in enumerate(current):
            def at(index, offset):
                target = deficit - offset
                return rows[index][target] if 0 <= target < len(rows[index]) else 0
            expected = (at(length + 4, 0) + at(length + 4, 1)
                        + at(length + 3, 2) + at(length + 3, 3)
                        + at(length + 2, 4) - at(length + 1, 5)
                        - at(length, 7))
            assert value == expected, ('weighted recurrence', length, deficit)
    polynomial_checks = 0
    for deficit in range(1, 21):
        first_length = max(3, deficit + 1)
        values = [coefficient(length, deficit)
                  for length in range(first_length, first_length + deficit + 3)]
        for order in range(deficit):
            values = [right - left for left, right in zip(values, values[1:])]
        assert values == [1, 1, 1]
        polynomial_checks += 1
    payload = json.dumps(rows, sort_keys=True, separators=(',', ':')).encode()
    def characteristic(value):
        return value ** 5 - 2 * value ** 4 - 2 * value ** 3 - value ** 2 + value + 1
    assert characteristic(Fraction(2784, 1000)) < 0
    assert characteristic(Fraction(2785, 1000)) > 0
    exclusion_checks = 0
    for deficit in range(5, 21):
        degree = deficit - 4
        values = [convolution_coefficient(length, deficit) - coefficient(length, deficit)
                  for length in range(deficit + 1, deficit + degree + 4)]
        for order in range(degree):
            values = [right - left for left, right in zip(values, values[1:])]
        assert values == [2 * degree] * 3, ('exclusion degree', deficit)
        exclusion_checks += 1
    path_totals = [sum(path_counts(length)) for length in range(1, 11)]
    assert path_totals == [2, 6, 17, 46, 129, 359, 999, 2782, 7746, 21567]
    for length in range(1, 10):
        neighbors = [[other for other in [index - 1, index + 1] if 0 <= other < length]
                     for index in range(length)]
        assert path_counts(length) == graph_counts(neighbors), ('path', length)
    for length in range(3, 11):
        neighbors = [[(index - 1) % length, (index + 1) % length]
                     for index in range(length)]
        roman = graph_counts(neighbors, roman=True)
        differences = [rows[length][deficit] - roman[deficit] for deficit in range(6)]
        assert differences == [0, 0, 0, 0, length, length * (length - 3)]
    for leaves in range(2, 9):
        neighbors = [list(range(1, leaves + 1))] + [[0] for leaf in range(leaves)]
        actual = graph_counts(neighbors)
        expected = [0] * (2 * leaves + 3)
        for deficit in range(2 * leaves + 1):
            expected[deficit] += convolution_coefficient(leaves, deficit)
        for twos in range(leaves + 1):
            expected[leaves + 1 - twos] += choose(leaves, twos)
            expected[leaves + 2 - twos] += choose(leaves, twos)
        assert expected == actual, ('star', leaves)
    matrix_evidence = transfer_matrix_checks()
    print(json.dumps({
        'arithmetic': 'exact integers and rational numbers',
        'formula_vs_transfer': {'cycle_lengths': [3, 40], 'coefficients': compared},
        'formula_vs_direct_enumeration': {'cycle_lengths': [3, 10],
                                        'candidate_functions': sum(3 ** size for size in range(3, 11))},
        'weighted_recurrence': {'base_lengths': [3, 35], 'all_coefficients': True},
        'fixed_deficit_differences': {'deficits': [1, 20], 'cases': polynomial_checks,
                                    'cycle_length_rule': 'max(3,j+1) through max(3,j+1)+j+2',
                                    'order_j_difference': 1},
        'total_counts_n3_to_n7': [sum(rows[length]) for length in range(3, 8)],
        'dominant_root_bracket': {'lower': '2.784', 'upper': '2.785',
                                  'exact_polynomial_signs': [-1, 1]},
        'exclusion_polynomial_differences': {
            'deficits': [5, 20], 'cases': exclusion_checks,
            'degree': 'j-4', 'leading_coefficient': '2/(j-5)!',
            'cycle_length_rule': 'j+1 through 2*j-1'},
        'path_transfer_vs_enumeration': {'path_lengths': [1, 9]},
        'path_totals_n1_to_n10': path_totals,
        'roman_differences': {'cycle_lengths': [3, 10], 'deficits': [0, 5],
                              'values': ['0', '0', '0', '0', 'n', 'n*(n-3)']},
        'star_polynomial_vs_enumeration': {'leaf_counts': [2, 8]},
        'path_and_cycle_transfer_matrix': matrix_evidence,
        'coefficient_table_sha256': hashlib.sha256(payload).hexdigest(),
        'status': 'all finite identities agree'
    }, indent=2))


if __name__ == '__main__':
    main()
