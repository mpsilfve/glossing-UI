"""
Plot the timestamps of a glossing-UI run-through on the dev-small set
"""

import matplotlib.pyplot as plt

times = open('times.txt', 'r').readlines()
times = [t.rstrip().split(': ') for t in times]
times = [[t[0], float(t[1])] for t in times]
times = [(t[0], t[1] - times[0][1]) for t in times]

start = [times[0][1]]
sentences = [t[1] for t in times if 'SENTENCE' in t[0]]
pipes_handled = [t[1] for t in times if 'Pipe' in t[0]]
json_computed = [t[1] for t in times if 'JSON' in t[0]]
saved = [t[1] for t in times if 'saved' in t[0]]

levels = [sentences, pipes_handled, json_computed, saved]

plt.style.use('ggplot')

fig, ax = plt.subplots()
ax.set_yticks([1.0, 2.0, 3.0, 4.0], labels=['Sentence\nsubmitted', 'All tokens\nfound', 'JSON\ncomputed', 'Output\nsaved'])

for i in reversed(range(1, 5)):
    x = levels[i-1]
    y = [i for j in range(len(x))]
    plt.scatter(x, y)

plt.title('dev-small set processing')

plt.savefig('times.png')