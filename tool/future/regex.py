# -*- coding: utf-8 -*-

import re

pattern = re.compile(r'\[历时:(\d+)ms\]')


def main():
    a = 0
    b = 0
    c = 0
    d = 0
    with open('nlptrans.log') as fp:
        for line in fp:
            match = pattern.search(line)
            if match:
                time = int(match.group(1))
                if time < 400:
                    a = a + 1
                elif time < 600:
                    b = b + 1
                elif time < 800:
                    c = c + 1
                else:
                    d = d + 1
    total = a + b + c + d
    print ("0~400:{}次，占比{:10.2f}".format(a, float(a) / total))
    print ("400~600:{}次，占比{:10.2f}".format(b, float(b) / total))
    print ("600~800:{}次，占比{:10.2f}".format(c, float(c) / total))
    print ("800以上:{}次，占比{:10.2f}".format(d, float(d) / total))


if __name__ == '__main__':
    main()
