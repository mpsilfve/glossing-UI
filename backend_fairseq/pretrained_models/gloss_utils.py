import re

"""
Functions for passing/displaying text to/from the glossing model
"""


def underlined_to_alt_chars(line: str) -> str:
    # convert the underlined characters into single, special characters
    line = re.sub('X̲|(X_)', 'Χ', line)
    line = re.sub('G̲|(G_)', 'Γ', line)
    line = re.sub('K̲|(K_)', 'К', line)
    line = re.sub('x̲|(x_)', 'χ', line)
    line = re.sub('g̲|(g_)', 'γ', line)
    line = re.sub('k̲|(k_)', 'к', line)
    return line


def alt_to_underline_chars(line: str) -> str:
    # convert back to the underline characters
    line = re.sub('Χ', 'X̲', line)
    line = re.sub('Γ', 'G̲', line)
    line = re.sub('К', 'K̲', line)
    line = re.sub('χ', 'x̲', line)
    line = re.sub('γ', 'g̲', line)
    line = re.sub('к', 'k̲', line)
    return line