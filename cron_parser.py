from sys import argv
from typing import List, Tuple, Union
import re
from texttable import Texttable


cron_days = {
    1: 'SUN',
    2: 'MON',
    3: 'TUE',
    4: 'WED',
    5: 'THU',
    6: 'FRI',
    7: 'SAT'
    }

cron_months = {
    1: 'JAN',
    2: 'FEB',
    3: 'MAR',
    4: 'APR',
    5: 'MAY',
    6: 'JUN',
    7: 'JUL',
    8: 'AUG',
    9: 'SEP',
    10: 'OCT',
    11: 'NOV',
    12: 'DEC'
}


minute_re = re.compile(
    "{0}|{1}|{2}|{3}|{4}".format(
        "(?P<all>\\*)",
        "(?P<specific>[0-5]?\\d)",
        "(?P<range>[0-5]?\\d-[0-5]?\\d)",
        "(?P<list>[0-5]?\\d(,[0-5]?\\d)+)",
        "(?P<step>(\\*|[0-5]?\\d)/(([0-5]?[1-9])|([1-5]0)))",
    )
)

hour_re = re.compile(
    "{0}|{1}|{2}|{3}|{4}".format(
        "(?P<all>\\*)",
        "(?P<specific>[01]?\\d|2[0-3])",
        "(?P<range>([01]?\\d|2[0-3])-([01]?\\d|2[0-3]))",
        "(?P<list>([01]?\\d|2[0-3])(,([01]?\\d|2[0-3]))+)",
        "(?P<step>(\\*|[01]?\\d|2[0-3])/([01]?[1-9]|2[0-3]|10))",
    )
)

day_of_month_re = re.compile(
    "{0}|{1}|{2}|{3}|{4}".format(
        "(?P<all>\\*)",
        "(?P<specific>[1-2]?[1-9]|[1-3]0|31)",
        "(?P<range>([1-2]?[1-9]|[1-3]0|31)-([1-2]?[1-9]|[1-3]0|31))",
        "(?P<list>([1-2]?[1-9]|[1-3]0|31)(,([1-2]?[1-9]|[1-3]0|31))+)",
        "(?P<step>(\\*|[1-2]?[1-9]|[1-3]0|31)/([1-2]?[1-9]|[1-3]0|31))",
    )
)

month_re = re.compile(
    "{0}|{1}|{2}|{3}|{4}".format(
        "(?P<all>\\*)",
        "(?P<specific>[1-9]|1[0-2])",
        "(?P<range>([1-9]|1[0-2])-([1-9]|1[0-2]))",
        "(?P<list>([1-9]|1[0-2])(,([1-9]|1[0-2]))+)",
        "(?P<step>(\\*|[1-9]|1[0-2])/([1-9]|1[0-2]))",
    )
)

day_of_week_re = re.compile(
    "{0}|{1}|{2}|{3}|{4}".format(
        "(?P<all>\\*)", 
        "(?P<specific>[0-6])", 
        "(?P<range>[0-6]-[0-6])", 
        "(?P<list>[0-6](,[0-6])+)", 
        "(?P<step>(\\*|[0-6])/[1-6])"
    )
)

regex_list = [minute_re, hour_re, day_of_month_re, month_re, day_of_week_re]


def parse(cron_expr: List[str]) -> Union[str, List]:
    '''
    This function does the validation as well as regex evaluation for 
    cron expression. This function take list of cron expression, validates it
    and convert it to list of tuple. Where each tuple represents the type of
    cron expression and cron expression.
    Input:
        cron_expr(list[str]): list of cron expression split on space
    return:
        list[tuple(type, expr)]: list of tuple of cron expr type and expr
    '''

    if len(cron_expr) < 6:
        return "Invalid number of arguments", None
    
    # convert JAN-DEC format to 1-12 format
    for month_number in cron_months:
        cron_expr[3] = cron_expr[3].upper().replace(
            cron_months[month_number], str(month_number))

    # convert SUN-SAT format to 0-6 format
    for day_number in cron_days:
            cron_expr[4] = cron_expr[4].upper().replace(
                cron_days[day_number], str(day_number))
    
    # convert ? to * only for DOM and DOW
    cron_expr[2] = cron_expr[2].replace("?", "*")
    cron_expr[4] = cron_expr[4].replace("?", "*")
    
    parsed_expr = [0]*5
    for i in range(0, 5):
        m = regex_list[i].fullmatch(cron_expr[i])
        if not m:
            return f"Invalid expression: {cron_expr[i]}", None
    
        for key, value in m.groupdict().items():
            if value:
                parsed_expr[i] = (key,value)
                break

    return None, parsed_expr


def get_range(type: str, expr: str, limit: int, range_start_from=0) -> List:
    '''
    This function converts the given type and expr into range.
    For example if type is step and expression is 5/15 and limit is 60. 
    This function will return [5, 30, 45]
    Input:
        type(str) : type of cron expression
        expr(str) : cron expression
        limit(int) : limit, e.g for minute 60 is limit
        range_start_from(int) : range start, for min and hour it is 0 and 1 for others
    Return:
        list: list of execution points
    '''

    if type == 'all':
        return [i for i in range(range_start_from,limit)]
    
    if type == 'specific':
        return [int(expr)] 
    
    if type == 'range':
        start, end = expr.split('-')
        start, end = int(start), int(end)
        if start > end:
            raise ValueError("invalid input")
        return [i for i in range(start, end+1)]
    
    if type == 'list':
        elements = expr.split(',')
        return [int(e) for e in elements]
    
    if type == 'step':
        start, step = expr.split('/')
        start = int(start) if start!='*' else 0
        step  = int(step)
        r = list()
        while start < limit:
            r.append(start)
            start+=step 
        return r
    
    raise ValueError(f"Invalid type {type}")


if __name__ == '__main__':
    cron_expr = argv[1].split(" ")
    validation_error, parsed_expr = parse(cron_expr)
    if validation_error:
        print(validation_error)
        exit(0)
    
    table = Texttable()

    #get minute range
    min_range = get_range(parsed_expr[0][0], parsed_expr[0][1], 60)
    table.add_row(["minute", ' '.join(map(str,min_range))])

    #get hour range
    hour_range = get_range(parsed_expr[1][0], parsed_expr[1][1], 24)
    table.add_row(["hour", ' '.join(map(str, hour_range))])

    #get day of month
    day_of_month = get_range(parsed_expr[2][0], 
                                    parsed_expr[2][1], 32, range_start_from=1)
    
    table.add_row(["day of month", ' '.join(map(str, day_of_month))])

    #get month
    months = get_range(parsed_expr[3][0], parsed_expr[3][1], 13, range_start_from=1)
    table.add_row(["month", ' '.join(map(str, months))])

    #get day of week
    day_of_week = get_range(parsed_expr[4][0], parsed_expr[4][1], 8, range_start_from=1)
    table.add_row(["day of week", ' '.join(map(str, day_of_week))])

    #command
    print(' '.join(cron_expr[5:]))
    table.add_row(["command",' '.join(cron_expr[5:])])

    print(table.draw())
