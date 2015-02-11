
# DrupalMirror

A simple tools to mirror Drupal modules.
It skips all sandbox projects and by default download
only modules. It can also download selectively, 
themes, distributions, etc.

### Dependencies

Needs python and git.

### How to use?
    drupal module mirror

    positional arguments:
      targetdir             target directory

    optional arguments:
      -h, --help            show this help message and exit
      --type TYPE           Download only this project type (default module)

