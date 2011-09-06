#!/usr/bin/env python

import sys

KMALLOC_CACHES = [
    8, 16, 32, 64, 96, 128, 192, 256, 512, 1024, 2048, 4096, 8192
]

def main():
    if len(sys.argv) != 3:
        print 'usage: %s <data file> <struct name>' % (sys.argv[0])
        sys.exit(1)

    path, target = sys.argv[1:]

    f = open(path)
    data = f.readlines()
    f.close()

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
    print 'target struct %s is allocated in kmalloc-%d' % (target, cache)
    print 'other structs allocated in kmalloc-%d:' % (cache)

    for struct in caches[cache]:
        print '\t%s' % struct

if __name__ == '__main__':
    main()
