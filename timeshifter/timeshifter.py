#!/usr/bin/env python
import argparse
import sys
from functools import partial

import pendulum
import regex

time_shift_pattern = r'''
    ^
    (?P<s>[+-m])?                 # sign
    (?P<h>00|0?[1-9]|1\d|2[0-3])  # hours
    (?::(?P<m>[0-5]\d))?          # minutes
    $
'''
time_pattern = r'''
    \b(?|
        (?P<h>00|0?[1-9]|1\d|2[0-3]):(?P<m>[0-5]\d)
        |
        (?P<h>24):(?P<m>00)  # 24:00 - next day 00:00
    )\b
'''

time_shift_reobj = regex.compile(time_shift_pattern, flags=regex.VERBOSE)
time_reobj = regex.compile(time_pattern, flags=regex.VERBOSE)


def shift_time(time: str, hours: int, minutes: int = 0) -> str:
    if time == '24:00':
        time = '23:59'

    dt = pendulum.from_format(time, 'HH:mm')
    dt_shifted = dt.add(hours=hours, minutes=minutes)

    if dt.start_of('day') != dt_shifted.start_of('day'):
        raise ValueError(f'Time {time} being shifted is out of the day.')

    return dt_shifted.format('H:mm')


def evaluate(match, hours, minutes):
    time = match[0]
    return shift_time(time, hours, minutes)


def shift_times_in_text(text: str, hours: int, minutes: int = 0) -> tuple[str, int]:
    return time_reobj.subn(partial(evaluate, hours=hours, minutes=minutes), text)


def shift_type(shift: str):
    match = time_shift_reobj.fullmatch(shift)
    if match:
        h = int(match['h'])
        m = int(match['m'] or 0)
        if match['s'] in ['-', 'm']:
            h *= -1
            m *= -1
        return {'h': h, 'm': m}

    raise argparse.ArgumentTypeError(
        'Wrong value for the time shift (should be in the form [-]hh[:mm]).'
    )


def cli(args=None):
    # sys.stdin.reconfigure(encoding='utf-8')
    # sys.stdout.reconfigure(encoding='utf-8')

    if not args:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser(
        prog='timeshifter',
        description=(
            'Shifts times. For instance, providing the shift 1:30 results in:\n'
            'from 9:00 to 12:00 -> from 10:30 to 13:30'
        )
    )
    parser.add_argument(
        'shift',
        type=shift_type,
        help=(
            'time shift in the form [-]hh[:mm] '
            '(use `m` instead of `-` to avoid usage `--` in `timeshifter -- -1:30`)'
        )
    )
    parser.add_argument(
        '-i',
        '--input',
        metavar='FILE',
        help='input file',
        type=argparse.FileType('r', encoding='utf-8'),
        default=sys.stdin
    )
    parser.add_argument(
        '-o',
        '--output',
        metavar='FILE',
        help='output file',
        type=argparse.FileType('w', encoding='utf-8'),
        default=sys.stdout
    )
    parser.add_argument(
        '-a',
        '--add-info',
        action='store_true',
        help='add info about changes'
    )

    args = parser.parse_args(args)
    text = args.input.read()
    shift = args.shift

    modified_text, changes_count = shift_times_in_text(text, hours=shift['h'], minutes=shift['m'])

    if args.add_info and changes_count:
        ended_with_newline = modified_text.endswith('\n')
        if not ended_with_newline:
            modified_text += '\n'
        modified_text += f'{changes_count} change(s)'
        if ended_with_newline:
            modified_text += '\n'

    print(modified_text, file=args.output, end='')


if __name__ == '__main__':
    cli()
