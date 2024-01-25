#!/usr/bin/env python3

import os
import json
import shutil
import random
import chevron
import markdown
import datetime


RENDER_YEAR = 2024
DIR_OUTPUT = 'build/'
DIR_STATIC = 'static/'

MONTH_NAMES = [
    'January',
    'February',
    'March',
    'April',
    'May',
    'June',
    'July',
    'August',
    'September',
    'October',
    'November',
    'December',
]


def maybe_mkdir(path):
	if not os.path.exists(path):
		os.mkdir(path)

maybe_mkdir(DIR_OUTPUT)


print("copying static assets...")
staticAssets = [
	'style.css',
]
for asset in staticAssets:
	shutil.copyfile(
        os.path.join(DIR_STATIC,asset),
        os.path.join(DIR_OUTPUT,asset))


with open('dataset.json') as f:
	dataset = json.load(f)

months = []
for idx,name in enumerate(MONTH_NAMES):
    layoffs = []
    for item in dataset:
        if item['date'].startswith(f"{RENDER_YEAR}-{(idx+1):02}-"):
            layoffs.append({
                'text': markdown.markdown(item['headline'])[3:-4], # oh god, the hack to strip the <p> and </p>
                'link': item['link']
            })
    # add redacted lines for upcoming months
    now = datetime.datetime.now()
    current_month = now.month
    current_year = now.year
    if RENDER_YEAR >= current_year:
        if idx+1 == current_month:
            layoffs.append({'redacted':True})
        if idx+1 > current_month:
            random.seed(idx+1)
            for x in range(0,random.randrange(2,4)):
                layoffs.append({'redacted':True})
    if layoffs:
        months.append({ 'name': name, 'layoffs': layoffs })


total_this_year = sum([x.get('affected',0) for x in dataset if x['date'].startswith(f"{RENDER_YEAR}-")])


with open('site.mustache', 'r') as f:
    with open(os.path.join(DIR_OUTPUT,'index.html'), 'w') as fout:
        fout.write(chevron.render(
            template = f,
            data = {
                'title': "How many people has the games industry laid off in 2024?",
                'dataset': dataset,
                'months': months,
                'total-this-year': f"{total_this_year:,}",
                'current-year': RENDER_YEAR
            }))
