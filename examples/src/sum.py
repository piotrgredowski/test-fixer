def sum_printer(*args: list[int]):
    sum_ = sum(args)

    return " + ".join([str(a) for a in args]) + f" = {sum_ * 2}"
