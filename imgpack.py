#!/usr/bin/env python3

from typing import TYPE_CHECKING, NamedTuple
import os
import os.path

if TYPE_CHECKING:
    from _typeshed import ReadableBuffer


def uint32(buf: bytes, offset: int) -> int:
    return int.from_bytes(buf[offset:offset + 4], 'little')


def uint64(buf: bytes, offset: int) -> int:
    return int.from_bytes(buf[offset:offset + 8], 'little')


class AmlResItem(NamedTuple):
    start: int
    "item data offset in the image"
    size: int
    "Image Data Size"
    type: str
    name: str
    to_flash: bool
    data: 'ReadableBuffer | None' = None

    @classmethod
    def from_img(cls, item: 'ReadableBuffer', img: 'ReadableBuffer'):
        start = uint64(item, 0x10)
        size = uint64(item, 0x18)
        type_ = item[0x20:0x120].rstrip(b'\0').decode()
        name = item[0x120:0x220].rstrip(b'\0').decode()
        to_flash = item[0x220] & 1 == 1
        data = img[start:start + size]
        return cls(start, size, type_, name, to_flash, data)

    @property
    def filename(self):
        return f'{self.name}.{self.type}'


class AmlResImg(NamedTuple):
    crc: int
    version: int
    magic: bytes
    items: list[AmlResItem]

    @classmethod
    def from_img(cls, img: 'ReadableBuffer'):
        crc = uint32(img, 0x00)
        version = uint32(img, 0x04)
        magic = img[0x08:0x10]

        items: list[AmlResItem] = []
        for i in range(uint32(img, 0x18)):
            offset = 0x40 + 0x240 * i
            item = AmlResItem.from_img(img[offset:offset + 0x240], img)
            items.append(item)
        return cls(crc, version, magic, items)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Unpack Amlogic upgrade images.')
    parser.add_argument(
        '-d', '--unpack', nargs='*', metavar='ITEM', dest='unpack',
        help='unpack (selected items)')
    parser.add_argument(
        '-f', '--force', action='store_true',
        help='force action, skip all internal checks')
    parser.add_argument(
        'img', metavar='<aml_upgrade_package.img>', type=argparse.FileType('rb'),
        help='Amlogic upgrade packages to extract')
    parser.add_argument(
        'dir', nargs='?', metavar='<DIR>',
        help='Destination directory (default: <filename>.UNPACK)')

    args = parser.parse_args()

    pack = AmlResImg.from_img(args.img.read())

    if args.unpack is not None:
        path = f'{args.img.name}.UNPACK' if not args.dir else args.dir
        print(f'Unpacking image to {path} ...')
        if not os.path.isdir(path):
            os.mkdir(path)
        for item in pack.items:
            if args.unpack and item.filename not in args.unpack:
                print(f'  Skipped {item.filename}')
                continue
            print(f'  Unpacking {item.filename} ...')
            with open(os.path.join(path, item.filename), 'wb') as f:
                f.write(item.data)
        print('Unpacking done.')
    else:
        print(f'Image: {args.img.name}')
        print(f'CRC: 0x{pack.crc:08x}')
        print(f'Version: {pack.version}')
        print(f'Magic: {pack.magic}')
        print('Items:')
        for item in pack.items:
            print(f'  {item.filename:20}  @  0x{item.start:08x}  +  0x{item.size:08x} ({item.size}) {'F' if item.to_flash else ' '}')


if __name__ == '__main__':
    exit(main())
