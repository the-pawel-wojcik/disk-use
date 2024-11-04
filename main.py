import argparse
import os
from datetime import date as dt
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

COLORS = [color for color in mcolors.TABLEAU_COLORS.keys()]
SIGNIFICANT_MEM_USE = 30 * 2**30 / 2**10
DISK_TOTAL_AVAIL = 2459967936


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--disk_use_files",
                        help="File with disk space by user.",
                        nargs="+",
                        required=True)
    args = parser.parse_args()
    return args


def parse_disk_use(data):
    """
    Turn the output of du into a dictinary:
    the username (directory name) works a key
    the size of the user's home directory is the value

    The size is an integer. The default output of du(1), i.e.,
    the disk use in the units of 1024 bytes.
    """
    out = {}
    for line in data:
        space = int(line.split()[0])
        user = line.split()[1]
        if user[0:2] == "./":
            user = user[2:]
        if space > SIGNIFICANT_MEM_USE:
            out[user] = space
        else:
            if 'others' in out.keys():
                out['others'] += space
            else:
                out['others'] = space

    return out


def add_user_to_the_plot(ax, xs, ys, parsed_data_list, user, color):
    new_ys = [y for y in ys]
    for i, day in enumerate(parsed_data_list):
        if user in day['data'].keys():
            new_ys[i] += day['data'][user] / DISK_TOTAL_AVAIL

    ax.fill_between(xs, new_ys, ys, color=color, alpha=0.7, label=user)

    return new_ys


def get_list_of_parsed_data(args):
    parsed_data_list = []
    users = {}
    for file in args.disk_use_files:
        with open(file) as data:
            parsed_data = parse_disk_use(data)
            for user in parsed_data.keys():
                users[user] = 1

            file_name = os.path.basename(file)  # "yyyy-mm-dd.txt"
            date_iso = file_name.split('.')[0]  # "yyyy-mm-dd"
            date = dt.fromisoformat(date_iso)
            parsed_data_list += [{'date': date,
                                 'data': parsed_data}]

    parsed_data_list.sort(key=lambda x: x['date'])
    return (parsed_data_list, users)


def main():
    args = get_args()

    parsed_data_list, users = get_list_of_parsed_data(args)

    plt.rcParams['date.converter'] = 'concise'
    fig = plt.figure(layout='constrained')
    ax = fig.add_axes([0.075, 0.10, 0.7, 0.8])

    xs = [i['date'] for i in parsed_data_list]
    ys = [0 for i in parsed_data_list]

    for i, user in enumerate(users):
        color = COLORS[i % len(COLORS)]
        ys = add_user_to_the_plot(ax, xs, ys, parsed_data_list, user, color)

    ax.set_ylim([0.0, 1.0])
    ax.set_title('Cluster disk usage')
    fig.legend(loc='center right', frameon=False, reverse=True)
    plt.show()


if __name__ == "__main__":
    main()
