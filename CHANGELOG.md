## 1.28.3 - 2025-01-04
### Extractors
#### Additions
- [civitai] add `user-videos` extractor ([#6644](https://github.com/mikf/gallery-dl/issues/6644))
- [szurubooru] support `visuabusters.com/booru` ([#6729](https://github.com/mikf/gallery-dl/issues/6729))
#### Fixes
- [8muses] skip albums without valid `permalink` ([#6717](https://github.com/mikf/gallery-dl/issues/6717))
- [batoto] update domains ([#6714](https://github.com/mikf/gallery-dl/issues/6714))
- [deviantart:tiptap] fix deviation embeds without `token`
- [hitomi] fix searches ([#6713](https://github.com/mikf/gallery-dl/issues/6713))
- [instagram:reels] fix `pinned` values ([#6719](https://github.com/mikf/gallery-dl/issues/6719))
- [kemonoparty] handle `discord` favorites ([#6706](https://github.com/mikf/gallery-dl/issues/6706))
- [piczel] fix extraction ([#6735](https://github.com/mikf/gallery-dl/issues/6735))
- [poipiku] fix downloads when post has a warning ([#6736](https://github.com/mikf/gallery-dl/issues/6736))
- [sankaku] support alphanumeric book/pool IDs ([#6757](https://github.com/mikf/gallery-dl/issues/6757))
- [subscribestar] fix attachment downloads ([#6721](https://github.com/mikf/gallery-dl/issues/6721), [#6724](https://github.com/mikf/gallery-dl/issues/6724), [#6758](https://github.com/mikf/gallery-dl/issues/6758))
- [subscribestar] improve `content` metadata extraction ([#6761](https://github.com/mikf/gallery-dl/issues/6761))
- [tapas] fix `TypeError` for locked episodes ([#6700](https://github.com/mikf/gallery-dl/issues/6700))
#### Improvements
- [boosty] support `file` post attachments ([#6760](https://github.com/mikf/gallery-dl/issues/6760))
- [deviantart:tiptap] support more content block types ([#6686](https://github.com/mikf/gallery-dl/issues/6686))
- [directlink] use domain as `subcategory` ([#6703](https://github.com/mikf/gallery-dl/issues/6703))
- [hitomi] provide `search_tags` metadata for `tag` and `search` results ([#6756](https://github.com/mikf/gallery-dl/issues/6756))
- [subscribestar] support `audio` files ([#6758](https://github.com/mikf/gallery-dl/issues/6758))
### Miscellaneous
- [workflows:executables] build with Python 3.13
