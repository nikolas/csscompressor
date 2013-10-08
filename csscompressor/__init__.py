##
# Portions Copyright (c) 2013 Sprymix Inc.
# Author of python port: Yury Selivanov - http://sprymix.com
#
# Author: Julien Lecomte -  http://www.julienlecomte.net/
# Author: Isaac Schlueter - http://foohack.com/
# Author: Stoyan Stefanov - http://phpied.com/
# Contributor: Dan Beam - http://danbeam.org/
# Portions Copyright (c) 2011-2013 Yahoo! Inc.  All rights reserved.
# LICENSE: BSD (revised)
##


import re


_url_re = re.compile(r'''url\s*\(\s*(['"]?)data\:''', re.I)
_ws_re = re.compile(r'\s+')
_str_re = re.compile(r'''("([^\\"]|\\.|\\)*")|('([^\\']|\\.|\\)*')''')
_yui_comment_re = re.compile(r'___YUICSSMIN_PRESERVE_CANDIDATE_COMMENT_(?P<num>\d+)___')
_ms_filter_re = re.compile(r'progid\:DXImageTransform\.Microsoft\.Alpha\(Opacity=', re.I)
_spaces1_re = re.compile(r'(^|\})(([^\{:])+:)+([^\{]*\{)')
_spaces2_re = re.compile(r'\s+([!{};:>+\(\)\],])')
_ie6special_re = re.compile(r':first-(line|letter)(\{|,)', re.I)
_charset1_re = re.compile(r'^(.*)(@charset)\s+("[^"]*";)', re.I)
_charset2_re = re.compile(r'^((\s*)(@charset)\s+([^;]+;\s*))+', re.I)
_dirs_re = re.compile(r'''@(font-face|import|
                            (?:-(?:atsc|khtml|moz|ms|o|wap|webkit)-)?
                                            keyframe|media|page|namespace)''',
                      re.I | re.X)

_pseudo_re = re.compile(r''':(active|after|before|checked|disabled|empty|enabled|
                                    first-(?:child|of-type)|focus|hover|last-(?:child|of-type)|
                                    link|only-(?:child|of-type)|root|:selection|target|visited)''',
                        re.I | re.X)

_common_funcs_re = re.compile(r''':(lang|not|nth-child|nth-last-child|nth-last-of-type|
                                        nth-of-type|(?:-(?:moz|webkit)-)?any)\(''', re.I | re.X)

_common_val_funcs_re = re.compile(r'''([:,\(\s]\s*)(attr|color-stop|from|rgba|to|url|
                                        (?:-(?:atsc|khtml|moz|ms|o|wap|webkit)-)?
                                        (?:calc|max|min|(?:repeating-)?
                                            (?:linear|radial)-gradient)|-webkit-gradient)''',
                                  re.I | re.X)

_space_and_re = re.compile(r'\band\(', re.I)

_space_after_re = re.compile(r'([!{}:;>+\(\[,])\s+')

_semi_re = re.compile(r';+}')

_zero_fmt_spec_re = re.compile(r'''(^|[^0-9])(?:0?\.)?0
                                    (?:px|em|%|in|cm|mm|pc|pt|ex|deg|g?rad|m?s|k?hz)''',
                               re.I | re.X)

_bg_pos_re = re.compile(r'''(background-position|webkit-mask-position|transform-origin|
                                webkit-transform-origin|moz-transform-origin|o-transform-origin|
                                ms-transform-origin):0(;|})''', re.I | re.X)

_quad_0_re = re.compile(r':0 0 0 0(;|})')
_trip_0_re = re.compile(r':0 0 0(;|})')
_coup_0_re = re.compile(r':0 0(;|})')

_point_float_re = re.compile(r'(:|\s)0+\.(\d+)')

_border_re = re.compile(r'''(border|border-top|border-right|border-bottom|
                                border-left|outline|background):none(;|})''', re.I | re.X)

_o_px_ratio_re = re.compile(r'\(([\-A-Za-z]+):([0-9]+)\/([0-9]+)\)')

_empty_rules_re = re.compile(r'[^\}\{/;]+\{\}')

_many_semi_re = re.compile(';;+')

_rgb_re = re.compile(r'rgb\s*\(\s*([0-9,\s]+)\s*\)')

_hex_color_re = re.compile(r'''(\=\s*?["']?)?
                                   \#([0-9a-fA-F])([0-9a-fA-F])
                                     ([0-9a-fA-F])([0-9a-fA-F])
                                     ([0-9a-fA-F])([0-9a-fA-F])
                               (\}|[^0-9a-fA-F{][^{]*?\})''', re.X)

_ie_matrix_re = re.compile(r'\s*filter:\s*progid:DXImageTransform\.Microsoft\.Matrix\(([^\)]+)\);')

_colors_map = {
    'f00':     'red',
    '000080':  'navy',
    '808080':  'gray',
    '808000':  'olive',
    '800080':  'purple',
    'c0c0c0':  'silver',
    '008080':  'teal',
    'ffa500':  'orange',
    '800000':  'maroon'
}

_colors_re = re.compile(r'(:|\s)' + '(\\#(' + '|'.join(_colors_map.keys()) + '))' + r'(;|})', re.I)


def extract_data_urls(css, preserved_tokens):
    max_idx = len(css) - 1
    append_idx = 0
    sb = []

    for match in _url_re.finditer(css):
        start_idx = match.start(0) + 4 # "len" of "url("
        term = match.group(1)

        if not term:
            term = ')'

        found_term = False
        end_idx = match.end(0) - 1
        while not found_term and (end_idx + 1) <= max_idx:
            end_idx = css.find(term, end_idx + 1)

            if end_idx > 0 and css[end_idx - 1] != '\\':
                found_term = True
                if term != ')':
                    end_idx = css.find(')', end_idx)

        sb.append(css[append_idx:match.start(0)])

        if found_term:
            token = css[start_idx:end_idx]
            token = _ws_re.sub('', token)

            preserver = 'url(___YUICSSMIN_PRESERVED_TOKEN_{}___)'.format(len(preserved_tokens))
            preserved_tokens.append(token)
            sb.append(preserver)

            append_idx = end_idx + 1

        else:
            sb.append(css[match.start(0), match.end(0)])
            append_id = match.end(0)

    sb.append(css[append_idx:])

    return ''.join(sb)


def compress_rgb_calls(css):
    # Shorten colors from rgb(51,102,153) to #336699
    # This makes it more likely that it'll get further compressed in the next step.
    def _replace(match):
        rgb_colors = match.group(1).split(',')
        result = '#'
        for comp in rgb_colors:
            comp = int(comp)
            if comp < 16:
                result += '0'
            if comp > 255:
                comp = 255
            result += hex(comp)[2:].lower()
        return result
    return _rgb_re.sub(_replace, css)


def compress_hex_colors(css):
    # Shorten colors from #AABBCC to #ABC. Note that we want to make sure
    # the color is not preceded by either ", " or =. Indeed, the property
    #     filter: chroma(color="#FFFFFF");
    # would become
    #     filter: chroma(color="#FFF");
    # which makes the filter break in IE.
    # We also want to make sure we're only compressing #AABBCC patterns inside { },
    # not id selectors ( #FAABAC {} )
    # We also want to avoid compressing invalid values (e.g. #AABBCCD to #ABCD)

    buf = []

    index = 0
    while True:
        match = _hex_color_re.search(css, index)
        if not match:
            break

        buf.append(css[index:match.start(0)])


        if match.group(1):
            # Restore, as is. Compression will break filters
            buf.append(match.group(1) + ('#' + match.group(2) + match.group(3) + match.group(4) +
                                               match.group(5) + match.group(6) + match.group(7)))

        else:
            if (match.group(2).lower() == match.group(3).lower() and
                match.group(4).lower() == match.group(5).lower() and
                match.group(6).lower() == match.group(7).lower()):

                buf.append('#' + (match.group(2) + match.group(4) + match.group(6)).lower())

            else:
                buf.append('#' + (match.group(2) + match.group(3) + match.group(4) +
                                  match.group(5) + match.group(6) + match.group(7)).lower())


        index = match.end(7)

    buf.append(css[index:])

    return ''.join(buf)


def compress(css, *, max_linelen=0):
    start_idx = end_idx = 0
    total_len = len(css)

    preserved_tokens = []
    css = extract_data_urls(css, preserved_tokens)

    # Collect all comments blocks...
    comments = []
    while True:
        start_idx = css.find('/*', start_idx)
        if start_idx < 0:
            break

        end_idx = css.find('*/', start_idx + 2)
        if end_idx < 0:
            end_idx = total_len

        token = css[start_idx + 2:end_idx]
        comments.append(token)

        css = (css[:start_idx + 2] +
               '___YUICSSMIN_PRESERVE_CANDIDATE_COMMENT_{}___'.format(len(comments)-1) +
               css[end_idx:])

        start_idx += 2

    # preserve strings so their content doesn't get accidentally minified
    def _replace(match):
        token = match.group(0)
        quote = token[0]
        token = token[1:-1]


        # maybe the string contains a comment-like substring?
        # one, maybe more? put'em back then
        if '___YUICSSMIN_PRESERVE_CANDIDATE_COMMENT_' in token:
            token = _yui_comment_re.sub(lambda match: comments[int(match.group('num'))], token)

        token = _ms_filter_re.sub('alpha(opacity=', token)

        preserved_tokens.append(token)
        return (quote +
                '___YUICSSMIN_PRESERVED_TOKEN_{}___'.format(len(preserved_tokens)-1) +
                quote)

    css = _str_re.sub(_replace, css)

    # strings are safe, now wrestle the comments
    comments_iter = iter(comments)
    for i, token in enumerate(comments_iter):
        placeholder = "___YUICSSMIN_PRESERVE_CANDIDATE_COMMENT_{}___".format(i)

        # ! in the first position of the comment means preserve
        # so push to the preserved tokens while stripping the !
        if token.startswith('!'):
            preserved_tokens.append(token)
            css = css.replace(placeholder, '___YUICSSMIN_PRESERVED_TOKEN_{}___'.
                              format(len(preserved_tokens)-1))
            continue

        # \ in the last position looks like hack for Mac/IE5
        # shorten that to /*\*/ and the next one to /**/
        if token.endswith('\\'):
            preserved_tokens.append('\\')
            css = css.replace(placeholder,
                              '___YUICSSMIN_PRESERVED_TOKEN_{}___'.format(len(preserved_tokens)-1))

            # attn: advancing the loop
            next(comments_iter)

            preserved_tokens.append('')
            css = css.replace('___YUICSSMIN_PRESERVE_CANDIDATE_COMMENT_{}___'.format(i+1),
                              '___YUICSSMIN_PRESERVED_TOKEN_{}___'.format(len(preserved_tokens)-1))

            continue

        # keep empty comments after child selectors (IE7 hack)
        # e.g. html >/**/ body
        if not token:
            start_idx = css.find(placeholder)
            if start_idx > 2:
                if css[start_idx-3] == '>':
                    preserved_tokens.append('')
                    css = css.replace(placeholder,
                                      '___YUICSSMIN_PRESERVED_TOKEN_{}___'.
                                      format(len(preserved_tokens)-1))

        # in all other cases kill the comment
        css = css.replace('/*{}*/'.format(placeholder), '')

    # Normalize all whitespace strings to single spaces. Easier to work with that way.
    css = _ws_re.sub(' ', css)

    def _replace(match):
        token = match.group(1)
        preserved_tokens.append(token);
        return ('filter:progid:DXImageTransform.Microsoft.Matrix(' +
                '___YUICSSMIN_PRESERVED_TOKEN_{}___);'.format(len(preserved_tokens)-1))
    css = _ie_matrix_re.sub(_replace, css)

    # Remove the spaces before the things that should not have spaces before them.
    # But, be careful not to turn "p :link {...}" into "p:link{...}"
    # Swap out any pseudo-class colons with the token, and then swap back.
    css = _spaces1_re.sub(lambda match: match.group(0) \
                                            .replace(':', '___YUICSSMIN_PSEUDOCLASSCOLON___'), css)

    css = _spaces2_re.sub(lambda match: match.group(1), css)

    css = css.replace('!important', ' !important');

    # bring back the colon
    css = css.replace('___YUICSSMIN_PSEUDOCLASSCOLON___', ':')

    # retain space for special IE6 cases
    css = _ie6special_re.sub(
                lambda match: ':first-{} {}'.format(match.group(1).lower(), match.group(2)),
                css)

    # no space after the end of a preserved comment
    css = css.replace('*/ ', '*/')

    # If there are multiple @charset directives, push them to the top of the file.
    css = _charset1_re.sub(lambda match: match.group(2).lower() + \
                                         ' ' + match.group(3) + match.group(1),
                           css)

    # When all @charset are at the top, remove the second and after (as they are completely ignored)
    css = _charset2_re.sub(lambda match: match.group(2) + \
                                         match.group(3).lower() + ' ' + match.group(4),
                           css)

    # lowercase some popular @directives (@charset is done right above)
    css = _dirs_re.sub(lambda match: '@' + match.group(1).lower(), css)

    # lowercase some more common pseudo-elements
    css = _pseudo_re.sub(lambda match: ':' + match.group(1).lower(), css)

    # lowercase some more common functions
    css = _common_funcs_re.sub(lambda match: ':' + match.group(1).lower() + '(', css)

    # lower case some common function that can be values
    # NOTE: rgb() isn't useful as we replace with #hex later, as well as and()
    # is already done for us right after this
    css = _common_val_funcs_re.sub(lambda match: match.group(1) + match.group(2).lower(), css)

    # Put the space back in some cases, to support stuff like
    # @media screen and (-webkit-min-device-pixel-ratio:0){
    css = _space_and_re.sub('and (', css)

    # Remove the spaces after the things that should not have spaces after them.
    css = _space_after_re.sub(r'\1', css)

    # remove unnecessary semicolons
    css = _semi_re.sub('}', css)

    # Replace 0(px,em,%) with 0.
    css = _zero_fmt_spec_re.sub(lambda match: match.group(1) + '0', css)

    # Replace 0 0 0 0; with 0.
    css = _quad_0_re.sub(r':0\1', css)
    css = _trip_0_re.sub(r':0\1', css)
    css = _coup_0_re.sub(r':0\1', css)

    # Replace background-position:0; with background-position:0 0;
    # same for transform-origin
    css = _bg_pos_re.sub(lambda match: match.group(1).lower() + ':0 0' + match.group(2), css)

    # Replace 0.6 to .6, but only when preceded by : or a white-space
    css = _point_float_re.sub(r'\1.\2', css)

    css = compress_rgb_calls(css)
    css = compress_hex_colors(css)

    # Replace #f00 -> red; other short color keywords
    css = _colors_re.sub(lambda match: match.group(1) + _colors_map[match.group(3).lower()] +
                                       match.group(4),
                         css)

    # border: none -> border:0
    css = _border_re.sub(lambda match: match.group(1).lower() + ':0' + match.group(2), css)

    # shorter opacity IE filter
    css = _ms_filter_re.sub('alpha(opacity=', css)

    # Find a fraction that is used for Opera's -o-device-pixel-ratio query
    # Add token to add the "\" back in later
    css = _o_px_ratio_re.sub(r'\1:\2___YUI_QUERY_FRACTION___\3', css)

    # Remove empty rules.
    css = _empty_rules_re.sub('', css)

    # Add "\" back to fix Opera -o-device-pixel-ratio query
    css = css.replace('___YUI_QUERY_FRACTION___', '/')

    # Replace multiple semi-colons in a row by a single one
    # See SF bug #1980989
    css = _many_semi_re.sub(';', css)

    # restore preserved comments and strings
    for i, token in reversed(tuple(enumerate(preserved_tokens))):
        css = css.replace('___YUICSSMIN_PRESERVED_TOKEN_{}___'.format(i), token)

    css = css.strip()

    return css
