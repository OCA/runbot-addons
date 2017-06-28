"""
This script is meant to be run by python_odoo to adapt and existing buildout's
buildout.cfg in order to pull the currently tested branch. It wil write a
configuration file on stdout that should be used to run a builout in the target
branch
"""
import argparse
import zc.recipe.egg
from zc.buildout.buildout import Buildout
from anybox.recipe.odoo.base import BaseRecipe

parser = argparse.ArgumentParser(description='Adapt buildout.cfg')
parser.add_argument('buildout_cfg')
parser.add_argument('buildout_section')
parser.add_argument('target_repo')
parser.add_argument('target_commit')
args = parser.parse_args()

buildout = Buildout(args.buildout_cfg, [])
section = buildout[args.buildout_section]
recipe = BaseRecipe(buildout, 'buildout', section)
recipe.parse_addons(section)

path = None
for parts_dir, (loc_type, loc_spec, options) in recipe.sources.iteritems():
    # we only support git urls
    if loc_type != 'git':
        continue
    if args.target_repo == loc_spec[0]:
        path = parts_dir
        break

if not path:
    raise ValueError('No addons line found for %s' % args.target_repo)

print '''[buildout]
extends = %(buildout_cfg)s

[%(buildout_section)s]
addons +=
    git %(target_repo)s %(path)s %(target_commit)s
options.logfile = False
options.workers = 0
options.without_demo = False
options.lang = en_US''' % dict(
        vars(args), path=path
    )
