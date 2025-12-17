# String Formatting


## Table of Contents

* [Basics](#basics)
* [Field Names](#field-names)
* [Conversions](#conversions)
* [Format Specifiers](#format-specifiers)
* [Global Replacement Fields](#global-replacement-fields)
* [Special Type Format Strings](#special-type-format-strings)


## Basics

Format strings in gallery-dl follow the general rules of [`str.format()`](https://docs.python.org/3/library/string.html#format-string-syntax) ([PEP 3101](https://www.python.org/dev/peps/pep-3101/)) plus several extras.

The syntax for replacement fields is
```
{<field-name>!<conversion>:<format-specifiers>}
```
where
[`<field-name>`](#field-names)
selects a value
<br>
and the optional
[`!<conversion>`](#conversions)
&amp;
[`:<format-specifiers>`](#format-specifiers)
specify how to transform it.

Examples:
* `{title}`
* `{content!W}`
* `{date:Olocal/%Y%m%d %H%M}`


## Field Names

Field names select the metadata value to use in a replacement field.

While simple names are usually enough, more complex forms like accessing values by attribute, element index, or slicing are also supported.

<table>
<thead>
<tr>
    <th></th>
    <th>Example</th>
    <th>Result</th>
</tr>
</thead>
<tbody>
<tr>
    <td>Name</td>
    <td><code>{title}</code></td>
    <td><code>Hello World</code></td>
</tr>
<tr>
    <td>Element Index</td>
    <td><code>{title[6]}</code></td>
    <td><code>W</code></td>
</tr>
<tr>
    <td>Slicing</td>
    <td><code>{title[3:8]}</code></td>
    <td><code>lo Wo</code></td>
</tr>
<tr>
    <td>Slicing (Bytes)</td>
    <td><code>{title_ja[b3:18]}</code></td>
    <td><code>ロー・ワー</code></td>
</tr>
<tr>
    <td>Alternatives</td>
    <td><code>{empty|title}</code></td>
    <td><code>Hello World</code></td>
</tr>
<tr>
    <td>Attribute Access</td>
    <td><code>{extractor.url}</code></td>
    <td><code>https://example.org/</code></td>
</tr>
<tr>
    <td rowspan="2">Element Access</td>
    <td><code>{user[name]}</code></td>
    <td><code>John Doe</code></td>
</tr>
<tr>
    <td><code>{user['name']}</code></td>
    <td><code>John Doe</code></td>
</tr>
</tbody>
</table>

All of these methods can be combined.
<br>
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
    <td align="center"><code>g</code></td>
    <td>Slugify a value</td>
    <td><code>{foo!g}</code></td>
    <td><code>foo-bar</code></td>
</tr>
<tr>
    <td align="center"><code>j</code></td>
    <td>Serialize value to a JSON formatted string</td>
    <td><code>{tags!j}</code></td>
    <td><code>["sun", "tree", "water"]</code></td>
</tr>
<tr>
    <td align="center"><code>L</code></td>
    <td>Convert an <a href="https://en.wikipedia.org/wiki/ISO_639-1">ISO 639-1</a> language code to its full name</td>
    <td><code>{lang!L}</code></td>
    <td><code>English</code></td>
</tr>
<tr>
    <td align="center"><code>n</code></td>
    <td>Return the <a href="https://docs.python.org/3/library/functions.html#len" rel="nofollow">length</a> of a value</td>
    <td><code>{foo!n}</code></td>
    <td><code>7</code></td>
</tr>
<tr>
    <td align="center"><code>W</code></td>
    <td>Sanitize whitespace - Remove leading and trailing whitespace characters and replace <em>all</em> whitespace (sequences) with a single space <code> </code> character</td>
    <td><code>{space!W}</code></td>
    <td><code>Foo Bar</code></td>
</tr>
<tr>
    <td align="center"><code>t</code></td>
    <td>Trim a string, i.e. remove leading and trailing whitespace characters</td>
    <td><code>{bar!t}</code></td>
    <td><code>FooBar</code></td>
</tr>
<tr>
    <td align="center"><code>T</code></td>
    <td>Convert a <code>datetime</code> object to a Unix timestamp</td>
    <td><code>{date!T}</code></td>
    <td><code>1262304000</code></td>
</tr>
<tr>
    <td align="center"><code>d</code></td>
    <td>Convert a Unix timestamp to a <code>datetime</code> object</td>
    <td><code>{created!d}</code></td>
    <td><code>2010-01-01 00:00:00</code></td>
</tr>
<tr>
    <td align="center"><code>D</code></td>
    <td>Convert a Unix timestamp or <a href="https://en.wikipedia.org/wiki/ISO_8601">ISO 8601</a> string to a <code>datetime</code> object</td>
    <td><code>{created!D}</code></td>
    <td><code>2010-01-01 00:00:00</code></td>
</tr>
<tr>
    <td align="center"><code>U</code></td>
    <td>Convert HTML entities</td>
    <td><code>{html!U}</code></td>
    <td><code>&lt;p&gt;foo &amp; bar&lt;/p&gt;</code></td>
</tr>
<tr>
    <td align="center"><code>H</code></td>
    <td>Convert HTML entities &amp; remove HTML tags</td>
    <td><code>{html!H}</code></td>
    <td><code>foo &amp; bar</code></td>
</tr>
<tr>
    <td align="center"><code>R</code></td>
    <td>Extract URLs</td>
    <td><code>{lorem!R}</code></td>
    <td><code>["https://example.org/"]</code></td>
</tr>
<tr>
    <td align="center"><code>s</code></td>
    <td>Convert value to <a href="https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str" rel="nofollow"><code>str</code></a></td>
    <td><code>{tags!s}</code></td>
    <td><code>['sun', 'tree', 'water']</code></td>
</tr>
<tr>
    <td align="center"><code>S</code></td>
    <td>Convert value to <a href="https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str" rel="nofollow"><code>str</code></a> while providing a human-readable representation for lists</td>
    <td><code>{tags!S}</code></td>
    <td><code>sun, tree, water</code></td>
</tr>
<tr>
    <td align="center"><code>r</code></td>
    <td>Convert value to <a href="https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str" rel="nofollow"><code>str</code></a> using <a href="https://docs.python.org/3/library/functions.html#repr" rel="nofollow"><code>repr()</code></a></td>
    <td></td>
    <td></td>
</tr>
<tr>
    <td align="center"><code>a</code></td>
    <td>Convert value to <a href="https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str" rel="nofollow"><code>str</code></a> using <a href="https://docs.python.org/3/library/functions.html#ascii" rel="nofollow"><code>ascii()</code></a></td>
    <td></td>
    <td></td>
</tr>
<tr>
    <td align="center"><code>i</code></td>
    <td>Convert value to <a href="https://docs.python.org/3/library/functions.html#int"><code>int</code></a></td>
    <td></td>
    <td></td>
</tr>
<tr>
    <td align="center"><code>f</code></td>
    <td>Convert value to <a href="https://docs.python.org/3/library/functions.html#float"><code>float</code></a></td>
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
    <td><code>[&lt;start&gt;:&lt;stop&gt;]</code></td>
    <td>Applies a <a href="https://python-reference.readthedocs.io/en/latest/docs/brackets/slicing.html">Slicing</a> operation to the current value, similar to <a href="#field-names">Field Names</a></td>
    <td><code>{foo:[1:-1]}</code></td>
    <td><code>oo&nbsp;Ba</code></td>
</tr>
<tr>
    <td><code>[b&lt;start&gt;:&lt;stop&gt;]</code></td>
    <td>Same as above, but applies to the <a href="https://docs.python.org/3/library/stdtypes.html#bytes"><code>bytes()</code></a> representation of a string in <a href="https://docs.python.org/3/library/sys.html#sys.getfilesystemencoding">filesystem encoding</a></td>
    <td><code>{foo_ja:[b3:-1]}</code></td>
    <td><code>ー・バ</code></td>
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
    <td rowspan="2"><code>Lb&lt;maxlen&gt;/&lt;ext&gt;/</code></td>
    <td rowspan="2">Same as <code>L</code>, but applies to the <a href="https://docs.python.org/3/library/stdtypes.html#bytes"><code>bytes()</code></a> representation of a string in <a href="https://docs.python.org/3/library/sys.html#sys.getfilesystemencoding">filesystem encoding</a></td>
    <td><code>{foo_ja:Lb15/長い/}</code></td>
    <td><code>フー・バー</code></td>
</tr>
<tr>
    <td><code>{foo_ja:Lb8/長い/}</code></td>
    <td><code>長い</code></td>
</tr>
<tr>
    <td rowspan="2"><code>X&lt;maxlen&gt;/&lt;ext&gt;/</code></td>
    <td rowspan="2">Limit output to <code>&lt;maxlen&gt;</code> characters. Cut output and add <code>&lt;ext&gt;</code> to its end if its length exceeds <code>&lt;maxlen&gt;</code></td>
    <td><code>{foo:X15/&nbsp;.../}</code></td>
    <td><code>Foo&nbsp;Bar</code></td>
</tr>
<tr>
    <td><code>{foo:X6/&nbsp;.../}</code></td>
    <td><code>Fo&nbsp;...</code></td>
</tr>
<tr>
    <td rowspan="2"><code>Xb&lt;maxlen&gt;/&lt;ext&gt;/</code></td>
    <td rowspan="2">Same as <code>X</code>, but applies to the <a href="https://docs.python.org/3/library/stdtypes.html#bytes"><code>bytes()</code></a> representation of a string in <a href="https://docs.python.org/3/library/sys.html#sys.getfilesystemencoding">filesystem encoding</a></td>
    <td><code>{foo_ja:Xb15/〜/}</code></td>
    <td><code>フー・バー</code></td>
</tr>
<tr>
    <td><code>{foo_ja:Xb8/〜/}</code></td>
    <td><code>フ〜</code></td>
</tr>
<tr>
    <td><code>J&lt;separator&gt;/</code></td>
    <td>Concatenates elements of a list with <code>&lt;separator&gt;</code> using <a href="https://docs.python.org/3/library/stdtypes.html#str.join" rel="nofollow"><code>str.join()</code></a></td>
    <td><code>{tags:J - /}</code></td>
    <td><code>sun - tree - water</code></td>
</tr>
<tr>
    <td><code>M&lt;key&gt;/</code></td>
    <td>Maps a list of objects to a list of corresponding values by looking up <code>&lt;key&gt;</code> in each object</td>
    <td><code>{users:Mname/}</code></td>
    <td><code>["John", "David", "Max"]</code></td>
</tr>
<tr>
    <td><code>R&lt;old&gt;/&lt;new&gt;/</code></td>
    <td>Replaces all occurrences of <code>&lt;old&gt;</code> with <code>&lt;new&gt;</code> using <a href="https://docs.python.org/3/library/stdtypes.html#str.replace" rel="nofollow"><code>str.replace()</code></a></td>
    <td><code>{foo:Ro/()/}</code></td>
    <td><code>F()()&nbsp;Bar</code></td>
</tr>
<tr>
    <td><code>A&lt;op&gt;&lt;value&gt;/</code></td>
    <td>Apply arithmetic operation <code>&lt;op&gt;</code> (<code>+</code>, <code>-</code>, <code>*</code>) to the current value</td>
    <td><code>{num:A+1/}</code></td>
    <td><code>"2"</code></td>
</tr>
<tr>
    <td><code>C&lt;conversion(s)&gt;/</code></td>
    <td>Apply <a href="#conversions">Conversions</a> to the current value</td>
    <td><code>{tags:CSgc/}</code></td>
    <td><code>"Sun-tree-water"</code></td>
</tr>
<tr>
    <td><code>S&lt;order&gt;/</code></td>
    <td>Sort a list. <code>&lt;order&gt;</code> can be either <strong>a</strong>scending or <strong>d</strong>escending/<strong>r</strong>everse. (default: <strong>a</strong>)</td>
    <td><code>{tags:Sd}</code></td>
    <td><code>['water', 'tree', 'sun']</code></td>
</tr>
<tr>
    <td><code>D&lt;format&gt;/</code></td>
    <td>Parse a string value to a <code>datetime</code> object according to <a href="https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes"><code>&lt;format&gt;</code></a></td>
    <td><code>{updated:D%b %d %Y %I:%M %p/}</code></td>
    <td><code>2010-01-01 00:00:00</code></td>
</tr>
<tr>
    <td rowspan="2"><code>O&lt;offset&gt;/</code></td>
    <td rowspan="2">Apply <code>&lt;offset&gt;</code> to a <code>datetime</code> object, either as <code>±HH:MM</code> or <code>local</code> for local UTC offset</td>
    <td><code>{date:O-06:30/}</code></td>
    <td><code>2009-12-31 17:30:00</code></td>
</tr>
<tr>
    <td><code>{date:Olocal/}</code></td>
    <td><code>2010-01-01 01:00:00</code></td>
</tr>
<tr>
    <td><code>I</code></td>
    <td>Return the current value as is.<br>Do not convert it to <code>str</code></td>
    <td><code>{num:I}</code></td>
    <td><code>1</code></td>
</tr>
</tbody>
</table>

All special format specifiers (`?`, `L`, `J`, `R`, `D`, `O`, etc)
can be chained and combined with one another,
but must always appear before any standard format specifiers:

For example `{foo:?//RF/B/Ro/e/> 10}` -> `   Bee Bar`
- `?//` - Tests if `foo` has a value
- `RF/B/` - Replaces `F` with `B`
- `Ro/e/` - Replaces `o` with `e`
- `> 10` - Left-fills the string with spaces until it is 10 characters long


## Global Replacement Fields

Replacement field names that are available in all format strings.

<table>
<thead>
<tr>
    <th>Field Name</th>
    <th>Description</th>
    <th>Example</th>
    <th>Result</th>
</tr>
</thead>
<tbody>
<tr>
    <td><code>_env</code></td>
    <td>Environment variables</td>
    <td><code>{_env[HOME]}</code></td>
    <td><code>/home/john</code></td>
</tr>
<tr>
    <td><code>_now</code></td>
    <td>Current local date and time</td>
    <td><code>{_now:%Y-%m}</code></td>
    <td><code>2022-08</code></td>
</tr>
<tr>
    <td><code>_nul</code></td>
    <td>Universal <code>null</code> value</td>
    <td><code>{date|_nul:%Y-%m}</code></td>
    <td><code>None</code></td>
</tr>
<tr>
    <td rowspan="2"><code>_lit</code></td>
    <td rowspan="2">String literals</td>
    <td><code>{_lit[foo]}</code></td>
    <td><code>foo</code></td>
</tr>
<tr>
    <td><code>{'bar'}</code></td>
    <td><code>bar</code></td>
</tr>
</tbody>
</table>


## Special Type Format Strings

Starting a format string with `\f<Type> ` allows to set a different format string type than the default. Available ones are:

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
    <td align="center"><code>E</code></td>
    <td>An arbitrary Python expression</td>
    <td><code>\fE title.upper().replace(' ', '-')</code></td>
</tr>
<tr>
    <td align="center"><code>F</code></td>
    <td>An <a href="https://docs.python.org/3/tutorial/inputoutput.html#formatted-string-literals">f-string</a> literal</td>
    <td><code>\fF '{title.strip()}' by {artist.capitalize()}</code></td>
</tr>
<tr>
    <td align="center"><code>J</code></td>
    <td>A <a href="https://jinja.palletsprojects.com/">Jinja</a> template</td>
    <td><code>\fJ '&#123;&#123;title | trim&#125;&#125;' by &#123;&#123;artist | capitalize&#125;&#125;</code></td>
</tr>
<tr>
    <td align="center"><code>T</code></td>
    <td>Path to a template file containing a regular format string</td>
    <td><code>\fT ~/.templates/booru.txt</code></td>
</tr>
<tr>
    <td align="center"><code>TF</code></td>
    <td>Path to a template file containing an <a href="https://docs.python.org/3/tutorial/inputoutput.html#formatted-string-literals">f-string</a> literal</td>
    <td><code>\fTF ~/.templates/fstr.txt</code></td>
</tr>
<tr>
    <td align="center"><code>TJ</code></td>
    <td>Path to a template file containing a <a href="https://jinja.palletsprojects.com/">Jinja</a> template</td>
    <td><code>\fTF ~/.templates/jinja.txt</code></td>
</tr>
<tr>
    <td align="center"><code>M</code></td>
    <td>Path or name of a Python module
        followed by the name of one of its functions.
        This function gets called with the current metadata dict as
        argument and should return a string.</td>
    <td><code>\fM my_module:generate_text</code></td>
</tr>
</tbody>
</table>
