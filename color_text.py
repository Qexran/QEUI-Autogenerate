def print_suc(string: str):
    print(f'\033[92m- {string}\033[0m')


def print_err(string: str):
    print(f'\033[1;31m- {string}\033[0m')


def print_warn(string: str):
    print(f'\033[1;33m- {string}\033[0m')


def print_info(string: str):
    print(f"\033[34m- {string}\033[0m")


if __name__ == '__main__':
    print_suc("success")
    print_info("info")
    print_warn("warn")
    print_err("error!")
