# -*- coding: utf-8 -*-
import re
import string
import sys

pattern = re.compile(r'(.+)\"(\w+)\"(.+)?')

FIRST_CHARS = string.uppercase + string.lowercase
SECOND_CHARS = string.uppercase + string.lowercase + string.digits

min_ascii = len(FIRST_CHARS) - 1
max_ascii = len(SECOND_CHARS) - 1

first_ascii_index = 0
second_ascii_index = 0


def getNextChar():
    global first_ascii_index
    global second_ascii_index

    data = FIRST_CHARS[first_ascii_index] + SECOND_CHARS[second_ascii_index]
    if second_ascii_index == max_ascii:
        second_ascii_index = 0
        first_ascii_index = first_ascii_index + 1
    else:
        second_ascii_index = second_ascii_index + 1
    return data


def main():
    with open('test.log') as fp:

        for line in fp:

            match = pattern.search(line)
            if match:
                comment = match.group(3) or ""
                print match.group(1) + "\"" + getNextChar() + "\"" + comment
            else:
                sys.stdout.write(line)


if __name__ == '__main__':
    main()
