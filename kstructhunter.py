#!/usr/bin/env python
#
# kstructhunter.py
#
# Jon Oberheide <jon@oberheide.org>
# http://jon.oberheide.org
#
# Routines for hunting down kernel structs.
#
# Ships with data files for the stock Ubuntu Natty kernels.
#

import os, sys, optparse, platform, gzip, bz2

KMALLOC_CACHES = [
    8, 16, 32, 64, 96, 128, 192, 256, 512, 1024, 2048, 4096, 8192
]

def hunt(data, target):
    structs = {}
    caches = {}

    # prime cache lists
    for cache in KMALLOC_CACHES:
        caches[cache] = []

    for line in data:
        line = line.strip('\n')
        line = line.strip()
        if not line:
            continue

        # parse pahole output
        struct, size_str, _ = line.split('\t')
        size = int(size_str)

        # only consider kmalloc caches for now
        if size > KMALLOC_CACHES[-1]:
            continue

        # naive search for proper cache
        for cache in KMALLOC_CACHES:
            if size <= cache:
                structs[struct] = (size, cache)
                caches[cache].append(struct)
                break

    if target not in structs:
        print 'target struct %s not found' % (target)
        sys.exit(1)

    size, cache = structs[target]

    print 'target struct %s is size %d' % (target, size)
    print
    print 'target struct %s is allocated in kmalloc-%d' % (target, cache)
    print
    print 'other structs allocated in kmalloc-%d:' % (cache)

    for struct in caches[cache]:
        print '\t%s' % struct

def main():
    usage = 'usage: %prog [options] struct_name'
    opt = optparse.OptionParser(usage=usage)
    opt.add_option('-f', '--file', dest='path', help='specify the path to a custom data file', metavar='PATH')
    options, args = opt.parse_args()

    if len(args) != 1:
        opt.error('no target struct name was provided')

    if options.path and not os.path.exists(options.path):
        opt.error('invalid path to the custom data file')

    bits, linkage = platform.architecture()

    if options.path:
        path = options.path
    elif bits == '32bit':
        path = 'structs-32.txt.gz'
    elif bits == '64bit':
        path = 'structs-64.txt.gz'
    else:
        opt.error('invalid architecture')

    if path.endswith('.bz2'):
        fopen = bz2.BZ2File
    elif path.endswith('.gz'):
        fopen = gzip.GzipFile
    else:
        fopen = file

    f = fopen(path, 'rb')
    data = f.readlines()
    f.close()

    hunt(data, args[0])

if __name__ == '__main__':
    main()
