def reverse_bits(decimal_number, bitwidth):
    # Convert the decimal number to binary and reverse the bits
    binary_str = format(decimal_number, '0' + str(bitwidth) + 'b')
    reversed_binary_str = binary_str[::-1]

    # Convert the reversed binary back to decimal
    reversed_decimal = int(reversed_binary_str, 2)
    return reversed_decimal

# Example usage:
decimal_number = 1
bitwidth = 8
reversed_result = reverse_bits(decimal_number, bitwidth)
print(f"Reversed result for {decimal_number} is {reversed_result}")
