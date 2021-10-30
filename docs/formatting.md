# String Formatting

Format strings in gallery-dl follow the general rules of [`str.format()`](https://docs.python.org/3/library/string.html#format-string-syntax) ([PEP 3101](https://www.python.org/dev/peps/pep-3101/)) plus several extras.

The syntax for replacement fields is `{<field-name>!<conversion>:<format-specifiers>}`, where `!<conversion>` and `:<format-specifiers>` are both optional and can be used to specify how the value selected by `<field-name>` should be transformed.


## Field Names

Field names select the metadata value to use in a replacement field.

While simple names are usually enough, more complex forms like accessing values by attribute, element index, or slicing are also supported.

|                  | Example           | Result                 |
| ---------------- | ----------------- | ---------------------- |
| Name             | `{title}`         | `Hello World`          |
| Element Index    | `{title[6]}`      | `W`                    |
| Slicing          | `{title[3:8]}`    | `lo Wo`                |
| Alternatives     | `{empty\|title}`  | `Hello World`          |
| Element Access   | `{user[name]}`    | `John Doe`             |
| Attribute Access | `{extractor.url}` | `https://example.org/` |

All of these methods can be combined as needed.
For example `{title[24]|empty|extractor.url[15:-1]}` would result in `.org`.


## Conversions

Conversion specifiers allow to *convert* the value to a different form or type. Such a specifier must only consist of 1 character. gallery-dl supports the default three (`s`, `r`, `a`) as well as several others:

<table>
<thead>
<tr>
    <th>Conversion</th>
    <th>Description</th>
    <th>Example</th>
    <th>Result</th>
</tr>
</thead>
<tbody>
<tr>
    <td align="center"><code>l</code></td>
    <td>Convert a string to lowercase</td>
    <td><code>{foo!l}</code></td>
    <td><code>foo bar</code></td>
</tr>
<tr>
    <td align="center"><code>u</code></td>
    <td>Convert a string to uppercase</td>
    <td><code>{foo!u}</code></td>
    <td><code>FOO BAR</code></td>
</tr>
<tr>
    <td align="center"><code>c</code></td>
    <td>Capitalize a string, i.e. convert the first character to uppercase and all others to lowercase</td>
    <td><code>{foo!c}</code></td>
    <td><code>Foo bar</code></td>
</tr>
<tr>
    <td align="center"><code>C</code></td>
    <td>Capitalize each word in a string</td>
    <td><code>{foo!C}</code></td>
    <td><code>Foo Bar</code></td>
</tr>
<tr>
    <td align="center"><code>j</code></td>
    <td>Serialize value to a JSON formatted string</td>
    <td><code>{tags!j}</code></td>
    <td><code>["sun", "tree", "water"]</code></td>
</tr>
<tr>
    <td align="center"><code>t</code></td>
    <td>Trim a string, i.e. remove leading and trailing whitespace characters</td>
    <td><code>{bar!t}</code></td>
    <td><code>FooBar</code></td>
</tr>
<tr>
    <td align="center"><code>T</code></td>
    <td>Convert a <code>datetime</code> object to a unix timestamp</td>
    <td><code>{date!T}</code></td>
    <td><code>1262304000</code></td>
</tr>
<tr>
    <td align="center"><code>d</code></td>
    <td>Convert a unix timestamp to a <code>datetime</code> object</td>
    <td><code>{created!d}</code></td>
    <td><code>2010-01-01 00:00:00</code></td>
</tr>
<tr>
    <td align="center"><code>s</code></td>
    <td>Convert value to <a href="https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str" rel="nofollow"><code>str</code></a></td>
    <td><code>{tags!s}</code></td>
    <td><code>['sun', 'tree', 'water']</code></td>
</tr>
<tr>
    <td align="center"><code>S</code></td>
    <td>Convert value to <code>str</code> while providing a human-readable representation for lists</td>
    <td><code>{tags!S}</code></td>
    <td><code>sun, tree, water</code></td>
</tr>
<tr>
    <td align="center"><code>r</code></td>
    <td>Convert value to <code>str</code> using <a href="https://docs.python.org/3/library/functions.html#repr" rel="nofollow"><code>repr()</code></a></td>
    <td></td>
    <td></td>
</tr>
<tr>
    <td align="center"><code>a</code></td>
    <td>Convert value to <code>str</code> using <a href="https://docs.python.org/3/library/functions.html#ascii" rel="nofollow"><code>ascii()</code></a></td>
    <td></td>
    <td></td>
</tr>
</tbody>
</table>


## Format Specifiers

Format specifiers can be used for advanced formatting by using the options provided by Python (see [Format Specification Mini-Language](https://docs.python.org/3/library/string.html#format-specification-mini-language)) like zero-filling a number (`{num:>03}`) or formatting a [`datetime`](https://docs.python.org/3/library/datetime.html#datetime.datetime) object (`{date:%Y%m%d}`), or with gallery-dl's extra formatting specifiers:

<table>
<thead>
<tr>
    <th>Format Specifier</th>
    <th>Description</th>
    <th>Example</th>
    <th>Result</th>
</tr>
</thead>
<tbody>
<tr>
    <td rowspan="2"><code>?&lt;start&gt;/&lt;end&gt;/</code></td>
    <td rowspan="2">Adds <code>&lt;start&gt;</code> and <code>&lt;end&gt;</code> to the actual value if it evaluates to <code>True</code>. Otherwise the whole replacement field becomes an empty string.</td>
    <td><code>{foo:?[/]/}</code></td>
    <td><code>[Foo&nbsp;Bar]</code></td>
</tr>
<tr>
    <td><code>{empty:?[/]/}</code></td>
    <td><code></code></td>
</tr>
<tr>
    <td rowspan="2"><code>L&lt;maxlen&gt;/&lt;repl&gt;/</code></td>
    <td rowspan="2">Replaces the entire output with <code>&lt;repl&gt;</code> if its length exceeds <code>&lt;maxlen&gt;</code></td>
    <td><code>{foo:L15/long/}</code></td>
    <td><code>Foo&nbsp;Bar</code></td>
</tr>
<tr>
    <td><code>{foo:L3/long/}</code></td>
    <td><code>long</code></td>
</tr>
<tr>
    <td><code>J&lt;separator&gt;/</code></td>
    <td>Concatenates elements of a list with <code>&lt;separator&gt;</code> using <a href="https://docs.python.org/3/library/stdtypes.html#str.join" rel="nofollow"><code>str.join()</code></a></td>
    <td><code>{tags:J - /}</code></td>
    <td><code>sun - tree - water</code></td>
</tr>
<tr>
    <td><code>R&lt;old&gt;/&lt;new&gt;/</code></td>
    <td>Replaces all occurrences of <code>&lt;old&gt;</code> with <code>&lt;new&gt;</code> using <a href="https://docs.python.org/3/library/stdtypes.html#str.replace" rel="nofollow"><code>str.replace()</code></a></td>
    <td><code>{foo:Ro/()/}</code></td>
    <td><code>F()()&nbsp;Bar</code></td>
</tr>
</tbody>
</table>

All special format specifiers (`?`, `L`, `J`, `R`) can be chained and combined with one another, but must always come before any standard format specifiers:

For example `{foo:?//RF/B/Ro/e/> 10}` -> `   Bee Bar`
- `?//` - Tests if `foo` has a value
- `RF/B/` - Replaces `F` with `B`
- `Ro/e/` - Replaces `o` with `e`
- `> 10` - Left-fills the string with spaces until it is 10 characters long


## Special Type Format Strings

Starting a format string with '\f<Type> ' allows to set a different format string type than the default. Available ones are:

<table>
<thead>
<tr>
    <th>Type</th>
    <th>Description</th>
    <th width="32%">Usage</th>
</tr>
</thead>
<tbody>
<tr>
    <td align="center"><code>T</code></td>
    <td>A template file containing the actual format string</td>
    <td><code>\fT ~/.templates/booru.txt</code></td>
</tr>
<tr>
    <td align="center"><code>E</code></td>
    <td>An arbitrary Python expression</td>
    <td><code>\fE title.upper().replace(' ', '-')</code></td>
</tr>
<tr>
    <td align="center"><code>M</code></td>
    <td> Name of a Python module followed by one of its functions.
     This function gets called with the current metadata dict as
     argument and should return a string.</td>
    <td><code>\fM my_module:generate_text</code></td>
</tr>
</tbody>
</table>

