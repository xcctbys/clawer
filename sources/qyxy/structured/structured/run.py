#!/usr/bin/python
# -*- coding: UTF-8 -*-

from parse import Parse
import settings

test = Parse(mappings_file_path='./mappings.json',
             clawer_file_path='./test1.json',
             settings=settings)

test.handle_companies()
