# -*- coding: utf8 -*-

import re
import bs4
import subprocess

def num_start(line, nums):
    for num in nums:
        if line.startswith(num + '、'):
            return True
    return False

def big_num_start(line):
    return num_start(line, ['壹', '貳', '參', '肆', '伍', '陸', '柒', '捌', '玖', '拾'])

def small_num_start(line):
    return num_start(line, ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十'])

def is_pure_digit(line):
    try:
        int(line)
        return True
    except:
        return False

def main():
    content = subprocess.check_output(['pdftohtml', '-i', '-stdout', 'test/haha.pdf'])
    content = re.sub('&#160;', '', content)
    soup = bs4.BeautifulSoup(content)
    body = soup.find('body')

    start = False
    buf = ''
    for node in body.children:
        if not node.string:
            continue
        line = node.string.encode('utf8').strip()
        if not line or is_pure_digit(line):
            continue

        if big_num_start(line):
            print '\n# {}\n'.format(line)
            start = True
        elif small_num_start(line):
            print '\n## {}\n'.format(line)
        elif start:
            buf += line
            if buf.endswith('。'):
                print buf
                buf = ''

if __name__ == '__main__':
    main()

