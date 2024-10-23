NUM_DAYS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
INTERVAL = 20 # with each iteration we will jump forward 40 days
interval = INTERVAL
month, day = (1, 1)

def get_days_left(month, day) -> int:
    return NUM_DAYS[month-1] - day + 1

def iterate_month(month: int, day: int, init_interval: int) -> tuple[int, int, int]:
    interval = init_interval
    # for intervals greater than a month, we go month by month
    while (interval > NUM_DAYS[month-1]):
        interval -= get_days_left(month, day)
        day = 1
        month += 1

    return month, day, interval

def iterate_day(month: int, day: int, interval: int, num_days: list[int]):
    if ((day + interval) > num_days[month-1]):
        return (month + 1, (day + interval) % num_days[month-1])
    return (month, day + interval)

def full_iteration(month, day, interval) -> tuple[int, int, int]:
    for i in range(4):
        # month, day, interval = iterate_month(month, day, interval)
        return iterate_day(*iterate_month(month, day, INTERVAL), NUM_DAYS)
        # print(f"Date after iterating MONTH: ({month},{day}), remaining interval: {interval}")
        # print(f"Days in month {month}: {NUM_DAYS[month-1]}")

        # after we've iterated the month, add the remaining # of days in the interval and wrap around
        if ((day + interval) > NUM_DAYS[month-1]):
            day = (day + interval) % NUM_DAYS[month-1]
            month += 1
        else:
            day = day + interval
        print(f"Date after adding remaining interval: ({month},{day})")

print(f'before iteration: ({month}, {day}, {interval}), after iteration: {full_iteration(month, day, interval)}')


