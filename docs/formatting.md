# String Formatting

Format strings in gallery-dl follow the general rules of [`str.format()`](https://docs.python.org/3/library/string.html#format-string-syntax) ([PEP 3101](https://www.python.org/dev/peps/pep-3101/)) plus several extras.

The syntax for replacement fields is `{<field-name>!<conversion>:<format-specifiers>}`, where `!<conversion>` and `:<format-specifiers>` are both optional and can be used to specify how the value selected by `<field-name>` should be transformed.


## Field Names

Field names select the metadata value to use in a replacement field.

While simple names are usually enough, more complex forms like accessing values by attribute, element index, or slicing are also supported.

| | Example | Result |
| --- | --- | --- |
| Name             | `{title}`         | `Hello World` |
| Element Index    | `{title[6]}`      | `W` |
| Slicing          | `{title[3:8]}`    | `lo Wo` |
| Alternatives     | `{empty\|title}`  | `Hello World` |
| Element Access   | `{user[name]}`    | `John Doe` |
| Attribute Access | `{extractor.url}` | `https://example.org/` |

All of these methods can be combined as needed. For example `{title[24]|empty|extractor.url[15:-1]}` would result in `.org`.


## Conversions

Conversion specifiers allow to *convert* the value to a different form or type. Such a specifier must only consist of 1 character. gallery-dl supports the default three (`s`, `r`, `a`) as well as several others:

| Conversion | Description | Example | Result |
|:---:| --- | --- | --- |
| `l` | Convert a string to lowercase | `{foo!l}` | `foo bar`
| `u` | Convert a string to uppercase | `{foo!u}` | `FOO BAR`
| `c` | Capitalize a string, i.e. convert the first character to uppercase and all others to lowercase | `{foo!c}` | `Foo bar`
| `C` | Capitalize each word in a string | `{foo!C}` | `Foo Bar`
| `t` | Trim a string, i.e. remove leading and trailing whitespace characters | `{bar!t}` | `FooBar`
| `T` | Convert a `datetime` object to a unix timestamp | `{date!T}` | `1262304000`
| `d` | Convert a unix timestamp to a `datetime` object | `{created!d}` | `2010-01-01 00:00:00`
| `s` | Convert value to [`str`](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str) | `{tags!s}` | `['sun', 'tree', 'water']`
| `S` | Convert value to `str` and provide a human-readable representation for lists | `{tags!S}` | `sun, tree, water`
| `r` | Convert value to `str` using [`repr()`](https://docs.python.org/3/library/functions.html#repr) |
| `a` | Convert value to `str` using [`ascii()`](https://docs.python.org/3/library/functions.html#ascii) |


## Format Specifiers

Format specifiers can be used for advanced formatting by using the options provided by Python (see [Format Specification Mini-Language](https://docs.python.org/3/library/string.html#format-specification-mini-language)) like zero-filling a number (`{num:>03}`) or formatting a [`datetime`](https://docs.python.org/3/library/datetime.html#datetime.datetime) object (`{date:%Y%m%d}`), or with gallery-dl's extra formatting specifiers:

| Format Specifier | Description | Example | Result |
| --- | --- | --- | --- |
| `?<before>/<after>/` | Adds `<before>` and `<after>` to the actual value if it evaluates to `True`. Otherwise the whole replacement field becomes an empty string. | `{foo:?[/]/}` <br /> `{empty:?[/]/}` | `[Foo Bar]` <br /> ` `
| `L<maxlen>/<repl>/` | Replaces the entire output with `<repl>` if its length exceeds `<maxlen>` | `{foo:L15/long/}` <br /> `{foo:L3/long/}` | `Foo Bar` <br /> `long`|
| `J<separator>/` | Concatenates elements of a list with `<separator>` using [`str.join()`](https://docs.python.org/3/library/stdtypes.html#str.join) | `{tags:J - /}` | `sun - tree - water` |
| `R<old>/<new>/` | Replaces all occurrences of `<old>` with `<new>` using [`str.replace()`](https://docs.python.org/3/library/stdtypes.html#str.replace) | `{foo:Ro/()/}` | `F()() Bar` |

All special format specifiers (`?`, `L`, `J`, `R`) can be chained and combined with one another, but must always come before any standard format specifiers:

For example `{foo:?//RF/B/Ro/e/> 10}` -> `   Bee Bar`
- `?//` - Test if `foo` has a value
- `RF/B/` - Replace `F` with `B`
- `Ro/e/` - Replace `o` with `e`
- `> 10` - Left-fill the string with spaces until it is 10 characters long
