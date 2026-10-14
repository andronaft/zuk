#!/usr/bin/env python3
"""Draw ZUK in the middle of the contribution graph.

The graph shows the last 53 weeks; each column is a week (Sunday on top).
Every run rebuilds the art commits on top of the repo's root commit, so the
letters stay centred as the graph scrolls. Commits are empty, so the run is
cheap: about 90 tiny commits and one force push.
"""
import datetime as dt
import os
import subprocess

FONT = {
    "Z": ["#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"],
    "U": ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "K": ["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"],
}
TEXT = "ZUK"
COMMITS_PER_PIXEL = int(os.environ.get("COMMITS_PER_PIXEL", "2"))
NAME = os.environ["ART_NAME"]
EMAIL = os.environ["ART_EMAIL"]


def git(*args, env=None):
    subprocess.run(["git", *args], check=True, env=env)


# Grid columns: letters separated by one empty column.
columns = []
for i, ch in enumerate(TEXT):
    if i:
        columns.append(["."] * 7)
    for c in range(5):
        columns.append([FONT[ch][r][c] for r in range(7)])

today = dt.date.today()
this_sunday = today - dt.timedelta(days=(today.weekday() + 1) % 7)
first_sunday = this_sunday - dt.timedelta(weeks=52)  # 53 columns in total
start_col = (53 - len(columns)) // 2

root = subprocess.run(["git", "rev-list", "--max-parents=0", "HEAD"],
                      check=True, capture_output=True, text=True).stdout.split()[0]
git("checkout", "-q", "--detach", root)

count = 0
for c, column in enumerate(columns):
    for row, cell in enumerate(column):
        if cell != "#":
            continue
        day = first_sunday + dt.timedelta(weeks=start_col + c, days=row)
        for n in range(COMMITS_PER_PIXEL):
            stamp = f"{day.isoformat()}T12:{n:02d}:00+0000"
            env = dict(os.environ,
                       GIT_AUTHOR_NAME=NAME, GIT_AUTHOR_EMAIL=EMAIL, GIT_AUTHOR_DATE=stamp,
                       GIT_COMMITTER_NAME=NAME, GIT_COMMITTER_EMAIL=EMAIL, GIT_COMMITTER_DATE=stamp)
            git("commit", "-q", "--allow-empty", "-m", f"{TEXT} {day}", env=env)
            count += 1

print(f"{count} commits, columns {start_col}-{start_col + len(columns) - 1}, from {first_sunday}")
