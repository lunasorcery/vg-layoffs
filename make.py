#!/usr/bin/env python3

import os
import json
import math
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


# render the visual
PEOPLE_PER_ROW = 50
PERSON_SIZE_PX = 14
SPACING_PX = 3
DOT_RADIUS_PX = 4
ROUNDED_RADIUS = 3

total_people_to_draw = total_this_year
space_for_ellipses = PEOPLE_PER_ROW - (total_people_to_draw % PEOPLE_PER_ROW)
if space_for_ellipses < 3:
    total_people_to_draw -= 3-space_for_ellipses

image_width_px = PEOPLE_PER_ROW * (PERSON_SIZE_PX + SPACING_PX) + SPACING_PX
image_height_px = math.ceil(total_people_to_draw / PEOPLE_PER_ROW) * (PERSON_SIZE_PX + SPACING_PX) + SPACING_PX

with open(os.path.join(DIR_OUTPUT,'visual.svg'), 'w') as f:
    f.write(f'<svg width="{image_width_px}" height="{image_height_px}" xmlns="http://www.w3.org/2000/svg">\n')
    f.write('<g fill="rgb(98,187,255)">\n')
    for idx in range(0, total_people_to_draw):
        x = idx % PEOPLE_PER_ROW
        y = math.floor(idx / PEOPLE_PER_ROW)
        x_px = SPACING_PX + (PERSON_SIZE_PX + SPACING_PX) * x
        y_px = SPACING_PX + (PERSON_SIZE_PX + SPACING_PX) * y
        f.write(f'<rect x="{x_px}" y="{y_px}" width="{PERSON_SIZE_PX}" height="{PERSON_SIZE_PX}" rx="{ROUNDED_RADIUS}" />\n')
    for idx in range(0, 3):
        x = total_people_to_draw % PEOPLE_PER_ROW
        y = math.floor(total_people_to_draw / PEOPLE_PER_ROW)
        x_px = SPACING_PX + (PERSON_SIZE_PX + SPACING_PX) * x + DOT_RADIUS_PX + (DOT_RADIUS_PX * 2 + SPACING_PX) * idx
        y_px = SPACING_PX + (PERSON_SIZE_PX + SPACING_PX) * y + (PERSON_SIZE_PX / 2)
        f.write(f'<ellipse cx="{x_px}" cy="{y_px}" rx="{DOT_RADIUS_PX}" ry="{DOT_RADIUS_PX}" />\n')
    f.write('</g>\n')
    f.write('</svg>\n')
