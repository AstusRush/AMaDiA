#region General Import
from ._import_temp import *
import types
import builtins
#endregion General Import

#region AGe Import
from ._AGeNotify import ExceptionOutput, trap_exc_during_debug, NotificationEvent, NC
from ._AGeFunctions import *
from ._AGeWidgets import *
from ._AGeAWWF import *
#endregion AGe Import

#region Special Imports

import keyword
import weakref
#endregion Special Imports


SH_COLOUR_DICT_TEMP_SPYDER_DARK = {
                        "background"   : "#19232D" ,
                        "currentline"  : "#3a424a" ,
                        "currentcell"  : "#292d3e" ,
                        "occurrence"   : "#509ea5" ,
                        "ctrlclick"    : "#179ae0" ,
                        "sideareas"    : "#222b35" ,
                        "matched_p"    : "#0bbe0b" ,
                        "unmatched_p"  : "#ff4340" ,
                        "normal"       : ('#ffffff', False, False) ,
                        "keyword"      : ('#c670e0', False, False) ,
                        "builtin"      : ('#fab16c', False, False) ,
                        "definition"   : ('#57d6e4', True, False) ,
                        "comment"      : ('#999999', False, False) ,
                        "string"       : ('#b0e686', False, True) ,
                        "number"       : ('#faed5c', False, False) ,
                        "instance"     : ('#ee6772', False, True)
}

def getSHColour():
    SH_COLOUR_DICT_TEMP = {
                            "background"   : App().Palette1.color(QtGui.QPalette.Active,QtGui.QPalette.Base) ,
                            "currentline"  : App().Palette1.color(QtGui.QPalette.Active,QtGui.QPalette.Base) ,
                            "currentcell"  : App().Palette1.color(QtGui.QPalette.Active,QtGui.QPalette.Base) ,
                            "occurrence"   : App().Palette1.color(QtGui.QPalette.Active,QtGui.QPalette.Base) ,
                            "ctrlclick"    : App().Palette1.color(QtGui.QPalette.Active,QtGui.QPalette.Base) ,
                            "sideareas"    : App().Palette1.color(QtGui.QPalette.Active,QtGui.QPalette.Base) ,
                            "matched_p"    : App().PythonLexerColours["Keyword"].color() ,
                            "unmatched_p"  : App().PythonLexerColours["UnclosedString"].color() ,
                            "normal"       : (App().Palette1.color(QtGui.QPalette.Active,QtGui.QPalette.Text), False, False) ,
                            "keyword"      : (App().PythonLexerColours["Keyword"].color(), False, False) ,
                            "builtin"      : (App().PythonLexerColours["Keyword"].color(), False, False) ,
                            "definition"   : (App().PythonLexerColours["FunctionMethodName"].color(), True, False) ,
                            "comment"      : (App().PythonLexerColours["Comment"].color(), False, False) ,
                            "string"       : (App().PythonLexerColours["DoubleQuotedString"].color(), False, True) ,
                            "number"       : (App().PythonLexerColours["Number"].color(), False, False) ,
                            "instance"     : (App().PythonLexerColours["Keyword"].color(), False, True)
    }
    return SH_COLOUR_DICT_TEMP

#region Spyder SH Copy
"""
The following is a modified version of Spyders Syntax Highlighter.
Spyder is published under the MIT License.
"""

#region misc
def qstring_length(text):
    """
    Tries to compute what the length of an utf16-encoded QString would be.
    """
    utf16_text = text.encode('utf16')
    length = len(utf16_text) // 2
    # Remove Byte order mark.
    # TODO: All unicode Non-characters should be removed
    if utf16_text[:2] in [b'\xff\xfe', b'\xff\xff', b'\xfe\xff']:
        length -= 1
    return length

DEFAULT_PATTERNS = {
    'file':
        r'file:///?(?:[\S]*)',
    'issue':
        (r'(?:(?:(?:gh:)|(?:gl:)|(?:bb:))?[\w\-_]*/[\w\-_]*#\d+)|'
         r'(?:(?:(?:gh-)|(?:gl-)|(?:bb-))\d+)'),
    'mail':
        r'(?:mailto:\s*)?([a-z0-9_\.-]+)@([\da-z\.-]+)\.([a-z\.]{2,6})',
    'url':
        r"https?://([\da-z\.-]+)\.([a-z\.]{2,6})([/\w\.-]*)[^ ^'^\"]+",
}

def any(name, alternates):
    "Return a named group pattern matching list of alternates."
    return "(?P<%s>" % name + "|".join(alternates) + ")"

def create_patterns(patterns, compile=False):
    """
    Create patterns from pattern dictionary.

    The key correspond to the group name and the values a list of
    possible pattern alternatives.
    """
    all_patterns = []
    for key, value in patterns.items():
        all_patterns.append(any(key, [value]))

    regex = '|'.join(all_patterns)

    if compile:
        regex = re.compile(regex)

    return regex


DEFAULT_PATTERNS_TEXT = create_patterns(DEFAULT_PATTERNS, compile=False)
DEFAULT_COMPILED_PATTERNS = re.compile(create_patterns(DEFAULT_PATTERNS, compile=True))

def get_span(match, key=None):
    if key is not None:
        start, end = match.span(key)
    else:
        start, end = match.span()
    start = qstring_length(match.string[:start])
    end = qstring_length(match.string[:end])
    return start, end


def document_cells(block, forward=True, cell_list=None):
    """
    Get cells oedata before or after block in the document.

    Parameters
    ----------
    forward : bool, optional
        Whether to iterate forward or backward from the current block.
    cell_list: list of tuple containing (block_number, oedata)
        This is the list of all cells in a file to avoid having to parse
        the file every time.
    """
    if not block.isValid():
        # Not a valid block
        return

    if forward:
        block = block.next()
    else:
        block = block.previous()

    if not block.isValid():
        return

    if cell_list is not None:
        cell_list = sorted(cell_list)
        block_line = block.blockNumber()
        if forward:
            for cell_line, oedata in cell_list:
                if cell_line >= block_line:
                    yield oedata
        else:
            for cell_line, oedata in cell_list[::-1]:
                if cell_line <= block_line:
                    yield oedata
        return

    # If the cell_list was not provided, search the cells
    while block.isValid():
        data = block.userData()
        if (data
                and data.oedata
                and data.oedata.def_type == OutlineExplorerData.CELL):
            yield data.oedata
        if forward:
            block = block.next()
        else:
            block = block.previous()

class TextBlockHelper(object):
    """
    Helps retrieving the various part of the user state bitmask.

    This helper should be used to replace calls to
    ``QTextBlock.setUserState``/``QTextBlock.getUserState`` as well as
    ``QSyntaxHighlighter.setCurrentBlockState``/
    ``QSyntaxHighlighter.currentBlockState`` and
    ``QSyntaxHighlighter.previousBlockState``.

    The bitmask is made up of the following fields:

        - bit0 -> bit26: User state (for syntax highlighting)
        - bit26: fold trigger state
        - bit27-bit29: fold level (8 level max)
        - bit30: fold trigger flag

        - bit0 -> bit15: 16 bits for syntax highlighter user state (
          for syntax highlighting)
        - bit16-bit25: 10 bits for the fold level (1024 levels)
        - bit26: 1 bit for the fold trigger flag (trigger or not trigger)
        - bit27: 1 bit for the fold trigger state (expanded/collapsed)

    """
    @staticmethod
    def get_state(block):
        """
        Gets the user state, generally used for syntax highlighting.
        :param block: block to access
        :return: The block state

        """
        if block is None:
            return -1
        state = block.userState()
        if state == -1:
            return state
        return state & 0x0000FFFF

    @staticmethod
    def set_state(block, state):
        """
        Sets the user state, generally used for syntax highlighting.

        :param block: block to modify
        :param state: new state value.
        :return:
        """
        if block is None:
            return
        user_state = block.userState()
        if user_state == -1:
            user_state = 0
        higher_part = user_state & 0x7FFF0000
        state &= 0x0000FFFF
        state |= higher_part
        block.setUserState(state)


class BlockUserData(QtGui.QTextBlockUserData):
    def __init__(self, editor, color=None, selection_start=None,
                 selection_end=None):
        QtGui.QTextBlockUserData.__init__(self)
        self.editor = editor
        self.breakpoint = False
        self.breakpoint_condition = None
        self.bookmarks = []
        self.code_analysis = []
        self.todo = ''
        self.color = color
        self.oedata = None
        self.import_statement = None
        self.selection_start = selection_start
        self.selection_end = selection_end

        # Add a reference to the user data in the editor as the block won't.
        # The list should /not/ be used to list BlockUserData as the blocks
        # they refer to might not exist anymore.
        # This prevent a segmentation fault.
        if editor is None:
            # Won't be destroyed
            self.refloop = self
            return
        # Destroy with the editor
        if not hasattr(editor, '_user_data_reference_list'):
            editor._user_data_reference_list = []
        editor._user_data_reference_list.append(self)

    def _selection(self):
        """
        Function to compute the selection.

        This is slow to call so it is only called when needed.
        """
        if self.selection_start is None or self.selection_end is None:
            return None
        document = self.editor.document()
        cursor = self.editor.textCursor()
        block = document.findBlockByNumber(self.selection_start['line'])
        cursor.setPosition(block.position())
        cursor.movePosition(QtGui.QTextCursor.StartOfBlock)
        cursor.movePosition(
            QtGui.QTextCursor.NextCharacter, n=self.selection_start['character'])
        block2 = document.findBlockByNumber(
            self.selection_end['line'])
        cursor.setPosition(block2.position(), QtGui.QTextCursor.KeepAnchor)
        cursor.movePosition(
            QtGui.QTextCursor.StartOfBlock, mode=QtGui.QTextCursor.KeepAnchor)
        cursor.movePosition(
            QtGui.QTextCursor.NextCharacter, n=self.selection_end['character'],
            mode=QtGui.QTextCursor.KeepAnchor)
        return QtGui.QTextCursor(cursor)


class OutlineExplorerData(QtCore.QObject):
    CLASS, FUNCTION, STATEMENT, COMMENT, CELL = list(range(5))
    FUNCTION_TOKEN = 'def'
    CLASS_TOKEN = 'class'

    # Emitted if the OutlineExplorerData was changed
    sig_update = pyqtSignal()

    def __init__(self, block, text=None, fold_level=None, def_type=None,
                 def_name=None, color=None):
        """
        Args:
            text (str)
            fold_level (int)
            def_type (int): [CLASS, FUNCTION, STATEMENT, COMMENT, CELL]
            def_name (str)
            color (PyQt.QtGui.QTextCharFormat)
        """
        super(OutlineExplorerData, self).__init__()
        self.text = text
        self.fold_level = fold_level
        self.def_type = def_type
        self.def_name = def_name
        self.color = color
        # Copy the text block to make sure it is not deleted
        self.block = QtGui.QTextBlock(block)

    def is_not_class_nor_function(self):
        return self.def_type not in (self.CLASS, self.FUNCTION)

    def is_class_or_function(self):
        return self.def_type in (self.CLASS, self.FUNCTION)

    def is_comment(self):
        return self.def_type in (self.COMMENT, self.CELL)

    def get_class_name(self):
        if self.def_type == self.CLASS:
            return self.def_name

    def get_function_name(self):
        if self.def_type == self.FUNCTION:
            return self.def_name

    def get_token(self):
        if self.def_type == self.FUNCTION:
            token = self.FUNCTION_TOKEN
        elif self.def_type == self.CLASS:
            token = self.CLASS_TOKEN

        return token

    @property
    def def_name(self):
        """Get the cell name."""
        # Non cell don't need unique names.
        if self.def_type != self.CELL:
            return self._def_name

        def get_name(oedata):
            name = oedata._def_name
            if not name:
                name = 'Unnamed Cell'
            return name

        self_name = get_name(self)

        existing_numbers = []

        def check_match(oedata):
            # Look for "string"
            other_name = get_name(oedata)
            pattern = '^' + re.escape(self_name) + r'(?:, #(\d+))?$'
            match = re.match(pattern, other_name)
            if match:
                # Check if already has a number
                number = match.groups()[0]
                if number:
                    existing_numbers.append(int(number))
                return True
            return False

        # Count cells
        N_prev = 0
        for oedata in document_cells(self.block, forward=False):
            if check_match(oedata):
                N_prev += 1
        N_fix_previous = len(existing_numbers)

        N_next = 0
        for oedata in document_cells(self.block, forward=True):
            if check_match(oedata):
                N_next += 1

        # Get the remaining indexeswe can use
        free_indexes = [idx for idx in range(N_prev + N_next + 1)
                        if idx + 1 not in existing_numbers]

        idx = free_indexes[N_prev - N_fix_previous]

        if N_prev + N_next > 0:
            return self_name + ', #{}'.format(idx + 1)

        return self_name

    @def_name.setter
    def def_name(self, value):
        """Set name."""
        self._def_name = value

    def update(self, other):
        """Try to update to avoid reloading everything."""
        if (self.def_type == other.def_type and
                self.fold_level == other.fold_level):
            self.text = other.text
            old_def_name = self._def_name
            self._def_name = other._def_name
            self.color = other.color
            self.sig_update.emit()
            if self.def_type == self.CELL:
                if self.cell_level != other.cell_level:
                    return False
                # Must update all other cells whose name has changed.
                for oedata in document_cells(self.block, forward=True):
                    if oedata._def_name in [self._def_name, old_def_name]:
                        oedata.sig_update.emit()
            return True
        return False

    def is_valid(self):
        """Check if the oedata has a valid block attached."""
        block = self.block
        return (block
                and block.isValid()
                and block.userData()
                and hasattr(block.userData(), 'oedata')
                and block.userData().oedata == self
                )

    def has_name(self):
        """Check if cell has a name."""
        if self._def_name:
            return True
        else:
            return False

    def get_block_number(self):
        """Get the block number."""
        if not self.is_valid():
            # Avoid calling blockNumber if not a valid block
            return None
        return self.block.blockNumber()


#endregion misc
        
#==============================================================================
# Syntax highlighting color schemes
#==============================================================================
class BaseSH(QtGui.QSyntaxHighlighter):
    """Base Syntax Highlighter Class"""
    # Syntax highlighting rules:
    PROG = None
    BLANKPROG = re.compile(r"\s+")
    # Syntax highlighting states (from one text block to another):
    NORMAL = 0
    # Syntax highlighting parameters.
    BLANK_ALPHA_FACTOR = 0.31

    sig_outline_explorer_data_changed = pyqtSignal()
    # Signal to advertise a new cell
    sig_new_cell = pyqtSignal(OutlineExplorerData)

    def __init__(self, parent, font=None):
        QtGui.QSyntaxHighlighter.__init__(self, parent)

        self.font = font
        self.color_scheme = getSHColour()

        self.background_color = None
        self.currentline_color = None
        self.currentcell_color = None
        self.occurrence_color = None
        self.ctrlclick_color = None
        self.sideareas_color = None
        self.matched_p_color = None
        self.unmatched_p_color = None

        self.formats = None
        self.setup_formats(font)

        self.cell_separators = None
        self.editor = None
        self.patterns = DEFAULT_COMPILED_PATTERNS

        App().S_ColourChanged.connect(lambda: self.reload_color_scheme())

    def get_background_color(self):
        return QtGui.QColor(self.background_color)

    def get_foreground_color(self):
        """Return foreground ('normal' text) color"""
        return self.formats["normal"].foreground().color()

    def get_currentline_color(self):
        return QtGui.QColor(self.currentline_color)

    def get_currentcell_color(self):
        return QtGui.QColor(self.currentcell_color)

    def get_occurrence_color(self):
        return QtGui.QColor(self.occurrence_color)

    def get_ctrlclick_color(self):
        return QtGui.QColor(self.ctrlclick_color)

    def get_sideareas_color(self):
        return QtGui.QColor(self.sideareas_color)

    def get_matched_p_color(self):
        return QtGui.QColor(self.matched_p_color)

    def get_unmatched_p_color(self):
        return QtGui.QColor(self.unmatched_p_color)

    def get_comment_color(self):
        """ Return color for the comments """
        return self.formats['comment'].foreground().color()

    def get_color_name(self, fmt):
        """Return color name assigned to a given format"""
        return self.formats[fmt].foreground().color().name()

    def setup_formats(self, font=None):
        base_format = QtGui.QTextCharFormat()
        if font is not None:
            self.font = font
        if self.font is not None:
            base_format.setFont(self.font)
        self.formats = {}
        colors = self.color_scheme.copy()
        self.background_color = colors.pop("background")
        self.currentline_color = colors.pop("currentline")
        self.currentcell_color = colors.pop("currentcell")
        self.occurrence_color = colors.pop("occurrence")
        self.ctrlclick_color = colors.pop("ctrlclick")
        self.sideareas_color = colors.pop("sideareas")
        self.matched_p_color = colors.pop("matched_p")
        self.unmatched_p_color = colors.pop("unmatched_p")
        for name, (color, bold, italic) in list(colors.items()):
            format = QtGui.QTextCharFormat(base_format)
            format.setForeground(QtGui.QColor(color))
            if bold:
                format.setFontWeight(QtGui.QFont.Bold)
            format.setFontItalic(italic)
            self.formats[name] = format

    def set_color_scheme(self, color_scheme):
        self.color_scheme = color_scheme
        self.setup_formats()
        self.rehighlight()

    def reload_color_scheme(self):
        self.color_scheme = getSHColour()
        self.setup_formats()
        self.rehighlight()

    @staticmethod
    def _find_prev_non_blank_block(current_block):
        previous_block = (current_block.previous()
                          if current_block.blockNumber() else None)
        # find the previous non-blank block
        while (previous_block and previous_block.blockNumber() and
               previous_block.text().strip() == ''):
            previous_block = previous_block.previous()
        return previous_block

    def update_patterns(self, patterns):
        """Update patterns to underline."""
        all_patterns = DEFAULT_PATTERNS.copy()
        additional_patterns = patterns.copy()

        # Check that default keys are not overwritten
        for key in DEFAULT_PATTERNS.keys():
            if key in additional_patterns:
                # TODO: print warning or check this at the plugin level?
                additional_patterns.pop(key)
        all_patterns.update(additional_patterns)

        self.patterns = create_patterns(all_patterns, compile=True)

    def highlightBlock(self, text):
        """
        Highlights a block of text. Please do not override, this method.
        Instead you should implement
        :func:`spyder.utils.syntaxhighplighters.SyntaxHighlighter.highlight_block`.

        :param text: text to highlight.
        """
        self.highlight_block(text)

    def highlight_block(self, text):
        """
        Abstract method. Override this to apply syntax highlighting.

        :param text: Line of text to highlight.
        :param block: current block
        """
        raise NotImplementedError()

    def highlight_patterns(self, text, offset=0):
        """Highlight URI and mailto: patterns."""
        match = self.patterns.search(text, offset)
        while match:
            for __, value in list(match.groupdict().items()):
                if value:
                    start, end = get_span(match)
                    start = max([0, start + offset])
                    end = max([0, end + offset])
                    font = self.format(start)
                    font.setUnderlineStyle(True)
                    self.setFormat(start, end - start, font)

            match = self.patterns.search(text, match.end())

    def highlight_spaces(self, text, offset=0):
        """
        Make blank space less apparent by setting the foreground alpha.
        This only has an effect when 'Show blank space' is turned on.
        """
        flags_text = self.document().defaultTextOption().flags()
        show_blanks =  flags_text & QtGui.QTextOption.ShowTabsAndSpaces
        if show_blanks:
            format_leading = self.formats.get("leading", None)
            format_trailing = self.formats.get("trailing", None)
            match = self.BLANKPROG.search(text, offset)
            while match:
                start, end = get_span(match)
                start = max([0, start+offset])
                end = max([0, end+offset])
                # Format trailing spaces at the end of the line.
                if end == qstring_length(text) and format_trailing is not None:
                    self.setFormat(start, end - start, format_trailing)
                # Format leading spaces, e.g. indentation.
                if start == 0 and format_leading is not None:
                    self.setFormat(start, end - start, format_leading)
                format = self.format(start)
                color_foreground = format.foreground().color()
                alpha_new = self.BLANK_ALPHA_FACTOR * color_foreground.alphaF()
                color_foreground.setAlphaF(alpha_new)
                self.setFormat(start, end - start, color_foreground)
                match = self.BLANKPROG.search(text, match.end())

    def highlight_extras(self, text, offset=0):
        """
        Perform additional global text highlight.

        Derived classes could call this function at the end of
        highlight_block().
        """
        self.highlight_spaces(text, offset=offset)
        self.highlight_patterns(text, offset=offset)

    def rehighlight(self):
        QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        QtGui.QSyntaxHighlighter.rehighlight(self)
        QtWidgets.QApplication.restoreOverrideCursor()


#==============================================================================
# Python syntax highlighter
#==============================================================================
def make_python_patterns(additional_keywords=None, additional_builtins=None):
    "Strongly inspired from idlelib.ColorDelegator.make_pat"
    if additional_keywords is None:
        additional_keywords = []
    if additional_builtins is None:
        additional_builtins = []
    kwlist = keyword.kwlist + additional_keywords
    builtinlist = [str(name) for name in dir(builtins)
                   if not name.startswith('_')] + additional_builtins
    repeated = set(kwlist) & set(builtinlist)
    for repeated_element in repeated:
        kwlist.remove(repeated_element)
    kw = r"\b" + any("keyword", kwlist) + r"\b"
    builtin = r"([^.'\"\\#]\b|^)" + any("builtin", builtinlist) + r"\b"
    comment = any("comment", [r"#[^\n]*"])
    instance = any("instance", [r"\bself\b",
                                r"\bcls\b",
                                (r"^\s*@([a-zA-Z_][a-zA-Z0-9_]*)"
                                     r"(\.[a-zA-Z_][a-zA-Z0-9_]*)*")])
    number_regex = [r"\b[+-]?[0-9]+[lLjJ]?\b",
                    r"\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\b",
                    r"\b[+-]?0[oO][0-7]+[lL]?\b",
                    r"\b[+-]?0[bB][01]+[lL]?\b",
                    r"\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?[jJ]?\b"]
    prefix = "r|u|R|U|f|F|fr|Fr|fR|FR|rf|rF|Rf|RF|b|B|br|Br|bR|BR|rb|rB|Rb|RB"
    sqstring =     r"(\b(%s))?'[^'\\\n]*(\\.[^'\\\n]*)*'?" % prefix
    dqstring =     r'(\b(%s))?"[^"\\\n]*(\\.[^"\\\n]*)*"?' % prefix
    uf_sqstring =  r"(\b(%s))?'[^'\\\n]*(\\.[^'\\\n]*)*(\\)$(?!')$" % prefix
    uf_dqstring =  r'(\b(%s))?"[^"\\\n]*(\\.[^"\\\n]*)*(\\)$(?!")$' % prefix
    ufe_sqstring = r"(\b(%s))?'[^'\\\n]*(\\.[^'\\\n]*)*(?!\\)$(?!')$" % prefix
    ufe_dqstring = r'(\b(%s))?"[^"\\\n]*(\\.[^"\\\n]*)*(?!\\)$(?!")$' % prefix
    sq3string =    r"(\b(%s))?'''[^'\\]*((\\.|'(?!''))[^'\\]*)*(''')?" % prefix
    dq3string =    r'(\b(%s))?"""[^"\\]*((\\.|"(?!""))[^"\\]*)*(""")?' % prefix
    uf_sq3string = r"(\b(%s))?'''[^'\\]*((\\.|'(?!''))[^'\\]*)*(\\)?(?!''')$" \
                   % prefix
    uf_dq3string = r'(\b(%s))?"""[^"\\]*((\\.|"(?!""))[^"\\]*)*(\\)?(?!""")$' \
                   % prefix
    # Needed to achieve correct highlighting in Python 3.6+
    # See spyder-ide/spyder#7324.
    if sys.version_info[0] >= 3 and sys.version_info[1] >= 6:
        # Based on
        # https://github.com/python/cpython/blob/
        # 81950495ba2c36056e0ce48fd37d514816c26747/Lib/tokenize.py#L117
        # In order: Hexnumber, Binnumber, Octnumber, Decnumber,
        # Pointfloat + Exponent, Expfloat, Imagnumber
        number_regex = [
                r"\b[+-]?0[xX](?:_?[0-9A-Fa-f])+[lL]?\b",
                r"\b[+-]?0[bB](?:_?[01])+[lL]?\b",
                r"\b[+-]?0[oO](?:_?[0-7])+[lL]?\b",
                r"\b[+-]?(?:0(?:_?0)*|[1-9](?:_?[0-9])*)[lL]?\b",
                r"\b((\.[0-9](?:_?[0-9])*')|\.[0-9](?:_?[0-9])*)"
                "([eE][+-]?[0-9](?:_?[0-9])*)?[jJ]?\b",
                r"\b[0-9](?:_?[0-9])*([eE][+-]?[0-9](?:_?[0-9])*)?[jJ]?\b",
                r"\b[0-9](?:_?[0-9])*[jJ]\b"]
    number = any("number", number_regex)

    string = any("string", [sq3string, dq3string, sqstring, dqstring])
    ufstring1 = any("uf_sqstring", [uf_sqstring])
    ufstring2 = any("uf_dqstring", [uf_dqstring])
    ufstring3 = any("uf_sq3string", [uf_sq3string])
    ufstring4 = any("uf_dq3string", [uf_dq3string])
    ufstring5 = any("ufe_sqstring", [ufe_sqstring])
    ufstring6 = any("ufe_dqstring", [ufe_dqstring])
    return "|".join([instance, kw, builtin, comment,
                     ufstring1, ufstring2, ufstring3, ufstring4, ufstring5,
                     ufstring6, string, number, any("SYNC", [r"\n"])])


def get_code_cell_name(text):
    """Returns a code cell name from a code cell comment."""
    name = text.strip().lstrip("#% ")
    if name.startswith("<codecell>"):
        name = name[10:].lstrip()
    elif name.startswith("In["):
        name = name[2:]
        if name.endswith("]:"):
            name = name[:-1]
        name = name.strip()
    return name


class PythonSH(BaseSH):
    """
    Python Syntax Highlighter\n
    Behaves similar to `from spyder.utils.syntaxhighlighters import PythonSH`
    but uses AGeLib colours.
    """
    # Syntax highlighting rules:
    IDPROG = re.compile(r"\s+(\w+)", re.S)
    ASPROG = re.compile(r"\b(as)\b")
    # Syntax highlighting states (from one text block to another):
    (NORMAL, INSIDE_SQ3STRING, INSIDE_DQ3STRING,
     INSIDE_SQSTRING, INSIDE_DQSTRING,
     INSIDE_NON_MULTILINE_STRING) = list(range(6))
    DEF_TYPES = {"def": OutlineExplorerData.FUNCTION,
                 "class": OutlineExplorerData.CLASS}
    # Comments suitable for Outline Explorer
    OECOMMENT = re.compile(r'^(# ?--[-]+|##[#]+ )[ -]*[^- ]+')

    def __init__(self, parent, font=None, additionalKeywords=None):
        if additionalKeywords is None:
            additionalKeywords = []
        additionalKeywords.append('async')
        additionalKeywords.append('await')
        self.PROG = re.compile(make_python_patterns(additional_keywords=additionalKeywords), re.S)
        BaseSH.__init__(self, parent, font)
        self.cell_separators = ('#%%', '# %%', '# <codecell>', '# In[')
        # Avoid updating the outline explorer with every single letter typed
        self.outline_explorer_data_update_timer = QtCore.QTimer()
        self.outline_explorer_data_update_timer.setSingleShot(True)
        self.outline_explorer_data_update_timer.timeout.connect(
            self.sig_outline_explorer_data_changed)

    def highlight_match(self, text, match, key, value, offset,
                        state, import_stmt, oedata):
        """Highlight a single match."""
        start, end = get_span(match, key)
        start = max([0, start+offset])
        end = max([0, end+offset])
        length = end - start
        if key == "uf_sq3string":
            self.setFormat(start, length, self.formats["string"])
            state = self.INSIDE_SQ3STRING
        elif key == "uf_dq3string":
            self.setFormat(start, length, self.formats["string"])
            state = self.INSIDE_DQ3STRING
        elif key == "uf_sqstring":
            self.setFormat(start, length, self.formats["string"])
            state = self.INSIDE_SQSTRING
        elif key == "uf_dqstring":
            self.setFormat(start, length, self.formats["string"])
            state = self.INSIDE_DQSTRING
        elif key in ["ufe_sqstring", "ufe_dqstring"]:
            self.setFormat(start, length, self.formats["string"])
            state = self.INSIDE_NON_MULTILINE_STRING
        else:
            self.setFormat(start, length, self.formats[key])
            if key == "comment":
                if text.lstrip().startswith(self.cell_separators):
                    oedata = OutlineExplorerData(self.currentBlock())
                    oedata.text = str(text).strip()
                    # cell_head: string contaning the first group
                    # of '%'s in the cell header
                    cell_head = re.search(r"%+|$", text.lstrip()).group()
                    if cell_head == '':
                        oedata.cell_level = 0
                    else:
                        oedata.cell_level = qstring_length(cell_head) - 2
                    oedata.fold_level = start
                    oedata.def_type = OutlineExplorerData.CELL
                    def_name = get_code_cell_name(text)
                    oedata.def_name = def_name
                    # Let the editor know a new cell was added in the document
                    self.sig_new_cell.emit(oedata)
                elif self.OECOMMENT.match(text.lstrip()):
                    oedata = OutlineExplorerData(self.currentBlock())
                    oedata.text = str(text).strip()
                    oedata.fold_level = start
                    oedata.def_type = OutlineExplorerData.COMMENT
                    oedata.def_name = text.strip()
            elif key == "keyword":
                if value in ("def", "class"):
                    match1 = self.IDPROG.match(text, end)
                    if match1:
                        start1, end1 = get_span(match1, 1)
                        self.setFormat(start1, end1-start1,
                                       self.formats["definition"])
                        oedata = OutlineExplorerData(self.currentBlock())
                        oedata.text = str(text)
                        oedata.fold_level = (qstring_length(text)
                                             - qstring_length(text.lstrip()))
                        oedata.def_type = self.DEF_TYPES[str(value)]
                        oedata.def_name = text[start1:end1]
                        oedata.color = self.formats["definition"]
                elif value in ("elif", "else", "except", "finally",
                               "for", "if", "try", "while",
                               "with"):
                    if text.lstrip().startswith(value):
                        oedata = OutlineExplorerData(self.currentBlock())
                        oedata.text = str(text).strip()
                        oedata.fold_level = start
                        oedata.def_type = OutlineExplorerData.STATEMENT
                        oedata.def_name = text.strip()
                elif value == "import":
                    import_stmt = text.strip()
                    # color all the "as" words on same line, except
                    # if in a comment; cheap approximation to the
                    # truth
                    if '#' in text:
                        endpos = qstring_length(text[:text.index('#')])
                    else:
                        endpos = qstring_length(text)
                    while True:
                        match1 = self.ASPROG.match(text, end, endpos)
                        if not match1:
                            break
                        start, end = get_span(match1, 1)
                        self.setFormat(start, length, self.formats["keyword"])

        return state, import_stmt, oedata

    def highlight_block(self, text):
        """Implement specific highlight for Python."""
        text = str(text)
        prev_state = TextBlockHelper.get_state(self.currentBlock().previous())
        if prev_state == self.INSIDE_DQ3STRING:
            offset = -4
            text = r'""" '+text
        elif prev_state == self.INSIDE_SQ3STRING:
            offset = -4
            text = r"''' "+text
        elif prev_state == self.INSIDE_DQSTRING:
            offset = -2
            text = r'" '+text
        elif prev_state == self.INSIDE_SQSTRING:
            offset = -2
            text = r"' "+text
        else:
            offset = 0
            prev_state = self.NORMAL

        oedata = None
        import_stmt = None

        self.setFormat(0, qstring_length(text), self.formats["normal"])

        state = self.NORMAL
        match = self.PROG.search(text)
        while match:
            for key, value in list(match.groupdict().items()):
                if value:
                    state, import_stmt, oedata = self.highlight_match(
                        text, match, key, value, offset,
                        state, import_stmt, oedata)

            match = self.PROG.search(text, match.end())

        TextBlockHelper.set_state(self.currentBlock(), state)

        # Use normal format for indentation and trailing spaces
        # Unless we are in a string
        states_multiline_string = [
            self.INSIDE_DQ3STRING, self.INSIDE_SQ3STRING,
            self.INSIDE_DQSTRING, self.INSIDE_SQSTRING]
        states_string = states_multiline_string + [
            self.INSIDE_NON_MULTILINE_STRING]
        self.formats['leading'] = self.formats['normal']
        if prev_state in states_multiline_string:
            self.formats['leading'] = self.formats["string"]
        self.formats['trailing'] = self.formats['normal']
        if state in states_string:
            self.formats['trailing'] = self.formats['string']
        self.highlight_extras(text, offset)

        block = self.currentBlock()
        data = block.userData()

        need_data = (oedata or import_stmt)

        if need_data and not data:
            data = BlockUserData(self.editor)

        # Try updating
        update = False
        if oedata and data and data.oedata:
            update = data.oedata.update(oedata)

        if data and not update:
            data.oedata = oedata
            self.outline_explorer_data_update_timer.start(500)

        if (import_stmt) or (data and data.import_statement):
            data.import_statement = import_stmt

        block.setUserData(data)

    def get_import_statements(self):
        """Get import statment list."""
        block = self.document().firstBlock()
        statments = []
        while block.isValid():
            data = block.userData()
            if data and data.import_statement:
                statments.append(data.import_statement)
            block = block.next()
        return statments

    def rehighlight(self):
        BaseSH.rehighlight(self)


#endregion Spyder SH Copy

#region QSci SH Example
if QSciImported:
    class MyLexer(Qsci.QsciLexerCustom):
        def __init__(self, parent):
            super(MyLexer, self).__init__(parent)
            # Default text settings
            # ----------------------
            self.setDefaultColor(QtGui.QColor("#ff000000"))
            self.setDefaultPaper(QtGui.QColor("#ffffffff"))
            self.setDefaultFont(QtGui.QFont("Consolas", 14))

            # Initialize colors per style
            # ----------------------------
            self.setColor(QtGui.QColor("#ff000000"), 0)   # Style 0: black
            self.setColor(QtGui.QColor("#ff7f0000"), 1)   # Style 1: red
            self.setColor(QtGui.QColor("#ff0000bf"), 2)   # Style 2: blue
            self.setColor(QtGui.QColor("#ff007f00"), 3)   # Style 3: green

            # Initialize paper colors per style
            # ----------------------------------
            self.setPaper(QtGui.QColor("#ffffffff"), 0)   # Style 0: white
            self.setPaper(QtGui.QColor("#ffffffff"), 1)   # Style 1: white
            self.setPaper(QtGui.QColor("#ffffffff"), 2)   # Style 2: white
            self.setPaper(QtGui.QColor("#ffffffff"), 3)   # Style 3: white

            # Initialize fonts per style
            # ---------------------------
            self.setFont(QtGui.QFont("Consolas", 14, weight=QtGui.QFont.Bold), 0)   # Style 0: Consolas 14pt
            self.setFont(QtGui.QFont("Consolas", 14, weight=QtGui.QFont.Bold), 1)   # Style 1: Consolas 14pt
            self.setFont(QtGui.QFont("Consolas", 14, weight=QtGui.QFont.Bold), 2)   # Style 2: Consolas 14pt
            self.setFont(QtGui.QFont("Consolas", 14, weight=QtGui.QFont.Bold), 3)   # Style 3: Consolas 14pt

        def language(self):
            return "SimpleLanguage"

        def description(self, style):
            if style == 0:
                return "myStyle_0"
            elif style == 1:
                return "myStyle_1"
            elif style == 2:
                return "myStyle_2"
            elif style == 3:
                return "myStyle_3"
            ###
            return ""

        def styleText(self, start, end):
            # 1. Initialize the styling procedure
            # ------------------------------------
            self.startStyling(start)

            # 2. Slice out a part from the text
            # ----------------------------------
            text = self.parent().text()[start:end]

            # 3. Tokenize the text
            # ---------------------
            p = re.compile(r"[*]\/|\/[*]|\s+|\w+|\W")

            # 'token_list' is a list of tuples: (token_name, token_len)
            token_list = [ (token, len(bytearray(token, "utf-8"))) for token in p.findall(text)]

            # 4. Style the text
            # ------------------
            # 4.1 Check if multiline comment
            multiline_comm_flag = False
            editor = self.parent()
            if start > 0:
                previous_style_nr = editor.SendScintilla(editor.SCI_GETSTYLEAT, start - 1)
                if previous_style_nr == 3:
                    multiline_comm_flag = True
            # 4.2 Style the text in a loop
            for i, token in enumerate(token_list):
                if multiline_comm_flag:
                    self.setStyling(token[1], 3)
                    if token[0] == "*/":
                        multiline_comm_flag = False
                else:
                    if token[0] in ["for", "while", "return", "int", "include"]:
                        # Red style
                        self.setStyling(token[1], 1)
                    elif token[0] in ["(", ")", "{", "}", "[", "]", "#"]:
                        # Blue style
                        self.setStyling(token[1], 2)
                    elif token[0] == "/*":
                        multiline_comm_flag = True
                        self.setStyling(token[1], 3)
                    else:
                        # Default style
                        self.setStyling(token[1], 0)
#endregion QSci SH Example

#region Qt SH Example

def f_format(color, style=''):
    """Return a QtGui.QTextCharFormat with the given attributes.
    """
    _color = QtGui.QColor()
    _color.setNamedColor(color)

    _format = QtGui.QTextCharFormat()
    _format.setForeground(_color)
    if 'bold' in style:
        _format.setFontWeight(QtGui.QFont.Bold)
    if 'italic' in style:
        _format.setFontItalic(True)

    return _format


# Syntax styles that can be shared by all languages
STYLES = {
    'keyword': f_format('blue'),
    'operator': f_format('red'),
    'brace': f_format('darkGray'),
    'defclass': f_format('black', 'bold'),
    'string': f_format('magenta'),
    'string2': f_format('darkMagenta'),
    'comment': f_format('darkGreen', 'italic'),
    'self': f_format('black', 'italic'),
    'numbers': f_format('brown'),
}


class PythonHighlighter (QtGui.QSyntaxHighlighter):
    """Syntax highlighter for the Python language.
    """
    # Python keywords
    keywords = [
        'and', 'assert', 'break', 'class', 'continue', 'def',
        'del', 'elif', 'else', 'except', 'exec', 'finally',
        'for', 'from', 'global', 'if', 'import', 'in',
        'is', 'lambda', 'not', 'or', 'pass', 'print',
        'raise', 'return', 'try', 'while', 'yield',
        'None', 'True', 'False',
    ]

    # Python operators
    operators = [
        '=',
        # Comparison
        '==', '!=', '<', '<=', '>', '>=',
        # Arithmetic
        '\+', '-', '\*', '/', '//', '\%', '\*\*',
        # In-place
        '\+=', '-=', '\*=', '/=', '\%=',
        # Bitwise
        '\^', '\|', '\&', '\~', '>>', '<<',
    ]

    # Python braces
    braces = [
        '\{', '\}', '\(', '\)', '\[', '\]',
    ]
    def __init__(self, document):
        QtGui.QSyntaxHighlighter.__init__(self, document)

        # Multi-line strings (expression, flag, style)
        # FIXME: The triple-quotes in these two lines will mess up the
        # syntax highlighting from this point onward
        self.tri_single = (QtCore.QRegExp("'''"), 1, STYLES['string2'])
        self.tri_double = (QtCore.QRegExp('"""'), 2, STYLES['string2'])

        rules = []

        # Keyword, operator, and brace rules
        rules += [(r'\b%s\b' % w, 0, STYLES['keyword'])
            for w in PythonHighlighter.keywords]
        rules += [(r'%s' % o, 0, STYLES['operator'])
            for o in PythonHighlighter.operators]
        rules += [(r'%s' % b, 0, STYLES['brace'])
            for b in PythonHighlighter.braces]

        # All other rules
        rules += [
            # 'self'
            (r'\bself\b', 0, STYLES['self']),

            # Double-quoted string, possibly containing escape sequences
            (r'"[^"\\]*(\\.[^"\\]*)*"', 0, STYLES['string']),
            # Single-quoted string, possibly containing escape sequences
            (r"'[^'\\]*(\\.[^'\\]*)*'", 0, STYLES['string']),

            # 'def' followed by an identifier
            (r'\bdef\b\s*(\w+)', 1, STYLES['defclass']),
            # 'class' followed by an identifier
            (r'\bclass\b\s*(\w+)', 1, STYLES['defclass']),

            # From '#' until a newline
            (r'#[^\n]*', 0, STYLES['comment']),

            # Numeric literals
            (r'\b[+-]?[0-9]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b', 0, STYLES['numbers']),
        ]

        # Build a QtCore.QRegExp for each pattern
        self.rules = [(QtCore.QRegExp(pat), index, fmt) for (pat, index, fmt) in rules]


    def highlightBlock(self, text):
        """Apply syntax highlighting to the given block of text.
        """
        # Do other syntax formatting
        for expression, nth, f_format in self.rules:
            index = expression.indexIn(text, 0)

            while index >= 0:
                # We actually want the index of the nth match
                index = expression.pos(nth)
                length = expression.cap(nth).length()
                self.setFormat(index, length, f_format)
                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)

        # Do multi-line strings
        in_multiline = self.match_multiline(text, *self.tri_single)
        if not in_multiline:
            in_multiline = self.match_multiline(text, *self.tri_double)


    def match_multiline(self, text, delimiter, in_state, style):
        """Do highlighting of multi-line strings. ``delimiter`` should be a
        ``QtCore.QRegExp`` for triple-single-quotes or triple-double-quotes, and
        ``in_state`` should be a unique integer to represent the corresponding
        state changes when inside those strings. Returns True if we're still
        inside a multi-line string when this function is finished.
        """
        # If inside triple-single quotes, start at 0
        if self.previousBlockState() == in_state:
            start = 0
            add = 0
        # Otherwise, look for the delimiter on this line
        else:
            start = delimiter.indexIn(text)
            # Move past this match
            add = delimiter.matchedLength()

        # As long as there's a delimiter match on this line...
        while start >= 0:
            # Look for the ending delimiter
            end = delimiter.indexIn(text, start + add)
            # Ending delimiter on this line?
            if end >= add:
                length = end - start + add + delimiter.matchedLength()
                self.setCurrentBlockState(0)
            # No; multi-line string
            else:
                self.setCurrentBlockState(in_state)
                length = text.length() - start + add
            # Apply formatting
            self.setFormat(start, length, style)
            # Look for the next match
            start = delimiter.indexIn(text, start + length)

        # Return True if still inside a multi-line string, False otherwise
        if self.currentBlockState() == in_state:
            return True
        else:
            return False
#endregion Qt SH Example

#region Colours #CLEANUP: This should really be removed...
#PythonLexerColours_Dark = {
#            Qsci.QsciLexerPython.Default                    : QtGui.QColor(255,252,218) ,
#            Qsci.QsciLexerPython.Comment                    : QtGui.QColor(255,252,218) ,
#            Qsci.QsciLexerPython.Number                     : QtGui.QColor(255,252,218) ,
#            Qsci.QsciLexerPython.DoubleQuotedString         : QtGui.QColor(255,252,218) ,
#            Qsci.QsciLexerPython.SingleQuotedString         : QtGui.QColor(255,252,218) ,
#            Qsci.QsciLexerPython.Keyword                    : QtGui.QColor(255,252,218) ,
#            Qsci.QsciLexerPython.TripleSingleQuotedString   : QtGui.QColor(255,252,218) ,
#            Qsci.QsciLexerPython.TripleDoubleQuotedString   : QtGui.QColor(255,252,218) ,
#            Qsci.QsciLexerPython.ClassName                  : QtGui.QColor(255,252,218) ,
#            Qsci.QsciLexerPython.FunctionMethodName         : QtGui.QColor(255,252,218) ,
#            Qsci.QsciLexerPython.Operator                   : QtGui.QColor(255,252,218) ,
#            Qsci.QsciLexerPython.Identifier                 : QtGui.QColor(255,252,218) ,
#            Qsci.QsciLexerPython.CommentBlock               : QtGui.QColor(255,252,218) ,
#            Qsci.QsciLexerPython.UnclosedString             : QtGui.QColor(255,252,218) ,
#            Qsci.QsciLexerPython.HighlightedIdentifier      : QtGui.QColor(255,252,218) ,
#            Qsci.QsciLexerPython.Decorator                  : QtGui.QColor(255,252,218) 
#            }
#endregion Colours

#region QSci Python Lexer
#TODO: Make own Lexer using Qsci.QsciLexerCustom 
#TODO: Make own Lexer for QTextEdit to no longer rely on Spyder
#  https://www.riverbankcomputing.com/static/Docs/QScintilla/classQsciLexerCustom.html
#  https://docs.huihoo.com/pyqt/QScintilla2/classQsciLexerCustom.html
if QSciImported:
    class PythonLexerQsci(Qsci.QsciLexerPython):
        def __init__(self, parent = None, additionalKeywords = None):
            if additionalKeywords is None:
                additionalKeywords = []
            super(PythonLexerQsci, self).__init__(parent)
            self.Styles = {
                "Default"                  : Qsci.QsciLexerPython.Default,
                "Comment"                  : Qsci.QsciLexerPython.Comment,
                "Number"                   : Qsci.QsciLexerPython.Number,
                "DoubleQuotedString"       : Qsci.QsciLexerPython.DoubleQuotedString,
                "SingleQuotedString"       : Qsci.QsciLexerPython.SingleQuotedString,
                "Keyword"                  : Qsci.QsciLexerPython.Keyword,
                "TripleSingleQuotedString" : Qsci.QsciLexerPython.TripleSingleQuotedString,
                "TripleDoubleQuotedString" : Qsci.QsciLexerPython.TripleDoubleQuotedString,
                "ClassName"                : Qsci.QsciLexerPython.ClassName,
                "FunctionMethodName"       : Qsci.QsciLexerPython.FunctionMethodName,
                "Operator"                 : Qsci.QsciLexerPython.Operator,
                "Identifier"               : Qsci.QsciLexerPython.Identifier,
                "CommentBlock"             : Qsci.QsciLexerPython.CommentBlock,
                "UnclosedString"           : Qsci.QsciLexerPython.UnclosedString,
                "HighlightedIdentifier"    : Qsci.QsciLexerPython.HighlightedIdentifier,
                "Decorator"                : Qsci.QsciLexerPython.Decorator
            }
            self.otherKeywords1 = ""
            self.otherKeywords2 = ""
            self.otherKeywords3 = ""
            self.otherKeywords4 = ""
            self.__setAdditionalKeywords(additionalKeywords)

        def recolour(self):
            self.setDefaultPaper(App().Palette1.color(QtGui.QPalette.Active,QtGui.QPalette.Base))
            self.setPaper(App().Palette1.color(QtGui.QPalette.Active,QtGui.QPalette.Base))
            for k,v in App().PythonLexerColours.items():
                self.setColor(v.color(),self.Styles[k])

        def keywords(self, index):
            keywords = Qsci.QsciLexerPython.keywords(self, index) or ''
            # primary keywords
            if index == 1:
                return self.otherKeywords1 + keywords# + " self NC "
            # secondary keywords
            if index == 2:
                return self.otherKeywords2 + keywords
            # doc comment keywords
            if index == 3:
                return self.otherKeywords3 + keywords
            # global classes
            if index == 4:
                return self.otherKeywords4 + keywords
            return keywords

        def __setAdditionalKeywords(self,words1=None,words2=None,words3=None,words4=None):
            """
            Set additional keywords for highlighting. \n
            Must be called in the `__init__` to be recognized.
            """
            if words1 is None: words1 = []
            if words2 is None: words2 = []
            if words3 is None: words3 = []
            if words4 is None: words4 = []
            if type(words1)==str:
                self.otherKeywords1 = words1
            else:
                self.otherKeywords1 = " ".join(words1)+" "
            if type(words2)==str:
                self.otherKeywords2 = words2
            else:
                self.otherKeywords2 = " ".join(words2)+" "
            if type(words3)==str:
                self.otherKeywords3 = words3
            else:
                self.otherKeywords3 = " ".join(words3)+" "
            if type(words4)==str:
                self.otherKeywords4 = words4
            else:
                self.otherKeywords4 = " ".join(words4)+" "
            self.otherKeywords1 += " True False "
    # remember indentation for future QSci Lexer classes and defining them as none in the else case
else:
    PythonLexerQsci = None
# end of Qsci block. below this point no indentation is needed and no Qsci stuff is allowed

#endregion QSci Python Lexer

#region AGe SH

# What do we want?
#   A SH for TextEdit
#   A SH for QSci
#   A base SH that provides the functionality for both SH and has an API that supports both
#       This would be achieved by supplying every method with all the data for both
#       The 2 SH both inherit the Main SH and reimplement the apply method which redirect to setStyling and setFormat respectively
#   A wrapper class that takes 2 SH and applies them to the Editors in AGeIDE
#       There should also be a version of that wrapper that includes the Spyder SH and the build-in Python SH from QSci
#
# What do we have?
#   Examples SH for both
#   A very good version for TextEdit which is bloated and should be stripped down
#
# Where to begin?
#   1. Make the wrapper and make one version that applies the Spyder SH and the build-in Python SH from QSci
#   2. Make the 3 base classes and set them up with minimal functionality so that a version exists that can be tested
#   3. Slowly copy over some of the the Spyder SH functions
#   4. Now that there is some code make a concept of how the finished thing should look
#   5. Copy over the rest of the functions while streamlining them


class _Highlighter_base():
    def lexer(self):
        return ""
    def language(self):
        return ""
    def description(self, ind):
        if self.mode == "QSci":
            if hasattr(self,"Styles"):
                Styles = self.Styles
            else:
                Styles = {
                    "Default"                  : Qsci.QsciLexerPython.Default,
                    "Comment"                  : Qsci.QsciLexerPython.Comment,
                    "Number"                   : Qsci.QsciLexerPython.Number,
                    "DoubleQuotedString"       : Qsci.QsciLexerPython.DoubleQuotedString,
                    "SingleQuotedString"       : Qsci.QsciLexerPython.SingleQuotedString,
                    "Keyword"                  : Qsci.QsciLexerPython.Keyword,
                    "TripleSingleQuotedString" : Qsci.QsciLexerPython.TripleSingleQuotedString,
                    "TripleDoubleQuotedString" : Qsci.QsciLexerPython.TripleDoubleQuotedString,
                    "ClassName"                : Qsci.QsciLexerPython.ClassName,
                    "FunctionMethodName"       : Qsci.QsciLexerPython.FunctionMethodName,
                    "Operator"                 : Qsci.QsciLexerPython.Operator,
                    "Identifier"               : Qsci.QsciLexerPython.Identifier,
                    "CommentBlock"             : Qsci.QsciLexerPython.CommentBlock,
                    "UnclosedString"           : Qsci.QsciLexerPython.UnclosedString,
                    "HighlightedIdentifier"    : Qsci.QsciLexerPython.HighlightedIdentifier,
                    "Decorator"                : Qsci.QsciLexerPython.Decorator
                }
            for k,v in Styles.items():
                if ind == v:
                    return k
            return ""
        else:
            return ""
    def init_base(self, mode):
        self.mode = mode
        self.currentStart = 0
        if self.mode == "QSci":
            self.Styles = {
                "Default"                  : Qsci.QsciLexerPython.Default,
                "Comment"                  : Qsci.QsciLexerPython.Comment,
                "Number"                   : Qsci.QsciLexerPython.Number,
                "DoubleQuotedString"       : Qsci.QsciLexerPython.DoubleQuotedString,
                "SingleQuotedString"       : Qsci.QsciLexerPython.SingleQuotedString,
                "Keyword"                  : Qsci.QsciLexerPython.Keyword,
                "TripleSingleQuotedString" : Qsci.QsciLexerPython.TripleSingleQuotedString,
                "TripleDoubleQuotedString" : Qsci.QsciLexerPython.TripleDoubleQuotedString,
                "ClassName"                : Qsci.QsciLexerPython.ClassName,
                "FunctionMethodName"       : Qsci.QsciLexerPython.FunctionMethodName,
                "Operator"                 : Qsci.QsciLexerPython.Operator,
                "Identifier"               : Qsci.QsciLexerPython.Identifier,
                "CommentBlock"             : Qsci.QsciLexerPython.CommentBlock,
                "UnclosedString"           : Qsci.QsciLexerPython.UnclosedString,
                "HighlightedIdentifier"    : Qsci.QsciLexerPython.HighlightedIdentifier,
                "Decorator"                : Qsci.QsciLexerPython.Decorator
            }
        #self.recolour()

    def recolour(self):
        pass
        if self.mode == "QSci":
            self.setDefaultPaper(App().Palette1.color(QtGui.QPalette.Active,QtGui.QPalette.Base))
            self.setPaper(App().Palette1.color(QtGui.QPalette.Active,QtGui.QPalette.Base))
            for k,v in App().PythonLexerColours.items():
                self.setColor(v.color(),self.Styles[k])
        elif self.mode == "Qt":
            pass
        else:
            raise Exception(str(self.mode)+" is not a valid mode")
        
    def r_highlight(self, text):
        """
        reimplement this for highlighting \n
        text is the text to be highlighted \n
        call `self.apply(start, length, _format)` to apply `_format` to the text from `start` to `start+length`
        """
        pass
            
    def getFormat(self, formatName):
        if self.mode == "QSci":
            return self.Styles[formatName]
        elif self.mode == "Qt":
            _color = App().PythonLexerColours[formatName].color()
            
            _format = QtGui.QTextCharFormat()
            _format.setForeground(_color)
            #if 'bold' in style:
            #    _format.setFontWeight(QtGui.QFont.Bold)
            #if 'italic' in style:
            #    _format.setFontItalic(True)
            
            return _format
        else:
            raise Exception(str(self.mode)+" is not a valid mode")
    
    def apply(self, start, length, _format):
        if self.mode == "QSci":
            self.startStyling(self.currentStart+start)
            self.setStyling(self.currentStart+length, self.getFormat(_format))
        elif self.mode == "Qt":
            self.setFormat(start, length, self.getFormat(_format))
        else:
            raise Exception(str(self.mode)+" is not a valid mode")
            
    def inMultiline(self):
        """
        returns an int \n
        0 means no, 1 means triple single quote, 2 means triple double quote
        """
        if self.mode == "QSci":
            previousStyleNr = self.parent().SendScintilla(self.parent().SCI_GETSTYLEAT, self.currentStart - 1)
            if previousStyleNr == Qsci.QsciLexerPython.TripleSingleQuotedString: #TODO: which is TripleSingleQuotedString
                return 1
            elif previousStyleNr == Qsci.QsciLexerPython.TripleDoubleQuotedString: #TODO: which is TripleDoubleQuotedString
                return 2
            else:
                return 0
        elif self.mode == "Qt":
            return self.previousBlockState()
        else:
            raise Exception(str(self.mode)+" is not a valid mode")
        
    def styleText(self, start, end): # QSci
        self.currentStart = start
        text = self.parent().text()[start:end]
        self.r_highlight(text)
        self.currentStart = 0
        
    def highlightBlock(self, text): # Q
        self.r_highlight(text)

class _Highlighter_Wrapper():
    def __init__(self, QtEditor, QSciEditor, QtSH, QSciSH):
        self.QSciImported = QSciImported
        self.QtSH_Class, self.QSciSH_Class = QtSH, QSciSH
        self.QtEditor, self.QSciEditor = QtEditor, QSciEditor
        self.QtSH = self.QtSH_Class(self.QtEditor.document())
        if self.QSciImported:
            self.QSciSH = self.QSciSH_Class(self.QSciEditor)
            self.QSciEditor.setLexer(self.QSciSH)
        else:
            self.QSciSH = None

    def setFont(self, font):
        if self.QSciImported:
            self.QSciSH.setFont(font)

    def recolour(self):
        if self.QSciImported:
            self.QSciSH.recolour()

class Highlighter_Python_SpyderAndQSci(_Highlighter_Wrapper):
    def __init__(self, QtEditor, QSciEditor, additionalKeywords=None):
        if additionalKeywords is None:
            additionalKeywords = []
        self.QSciImported = QSciImported
        self.QtSH_Class, self.QSciSH_Class = PythonSH, PythonLexerQsci
        self.QtEditor, self.QSciEditor = QtEditor, QSciEditor
        self.QtSH = self.QtSH_Class(self.QtEditor.document(),additionalKeywords=additionalKeywords)
        if self.QSciImported:
            self.QSciSH = self.QSciSH_Class(self.QSciEditor, additionalKeywords)
            self.QSciEditor.setLexer(self.QSciSH)
        else:
            self.QSciSH = None

#region AGe Sh Python
class Highlighter_Python_AGe_base(_Highlighter_base):
    pass #TODO

class Highlighter_Python_AGe_Qt(QtGui.QSyntaxHighlighter, Highlighter_Python_AGe_base):
    pass #TODO

if QSciImported:
    class Highlighter_Python_AGe_QSci(Qsci.QsciLexerCustom, Highlighter_Python_AGe_base):
        pass #TODO
else:
    Highlighter_Python_AGe_QSci = False

class Highlighter_Python_AGe(_Highlighter_Wrapper):
    pass #TODO
#endregion AGe Sh Python

#region AGe Sh Python
class Highlighter_Python_AGeSimple_base(_Highlighter_base):
    """Syntax highlighter for the Python language.
    """
    # Python keywords
    l_keywords = [
        'and', 'assert', 'break', 'class', 'continue', 'def',
        'del', 'elif', 'else', 'except', 'exec', 'finally',
        'for', 'from', 'global', 'if', 'import', 'in',
        'is', 'lambda', 'not', 'or', 'pass', 'print',
        'raise', 'return', 'try', 'while', 'yield',
        'None', 'True', 'False',
    ]
    
    # Python operators
    l_operators = [
        '=',
        # Comparison
        '==', '!=', '<', '<=', '>', '>=',
        # Arithmetic
        '\+', '-', '\*', '/', '//', '\%', '\*\*',
        # In-place
        '\+=', '-=', '\*=', '/=', '\%=',
        # Bitwise
        '\^', '\|', '\&', '\~', '>>', '<<',
    ]
    
    # Python braces
    l_braces = [
        '\{', '\}', '\(', '\)', '\[', '\]',
    ]
    
    
    
    def __init__(self): # Q
        #STYLES = {
        #    'keyword': self.f_format('blue'),
        #    'operator': self.f_format('red'),
        #    'brace': self.f_format('darkGray'),
        #    'defclass': self.f_format('black', 'bold'),
        #    'string': self.f_format('magenta'),
        #    'string2': self.f_format('darkMagenta'),
        #    'comment': self.f_format('darkGreen', 'italic'),
        #    'self': self.f_format('black', 'italic'),
        #    'numbers': self.f_format('brown'),
        #}
        STYLES = {
            'keyword':  "Keyword",
            'operator': "Operator",
            'brace':    "Operator",
            'defclass': "ClassName",
            'string':   "DoubleQuotedString",
            'string2':  "TripleSingleQuotedString",
            'comment':  "Comment",
            'self':     "Keyword",
            'numbers':  "Number",
        }
        #self.Styles = {
        #    "Default"                  : Qsci.QsciLexerPython.Default,
        #    "Comment"                  : Qsci.QsciLexerPython.Comment,
        #    "Number"                   : Qsci.QsciLexerPython.Number,
        #    "DoubleQuotedString"       : Qsci.QsciLexerPython.DoubleQuotedString,
        #    "SingleQuotedString"       : Qsci.QsciLexerPython.SingleQuotedString,
        #    "Keyword"                  : Qsci.QsciLexerPython.Keyword,
        #    "TripleSingleQuotedString" : Qsci.QsciLexerPython.TripleSingleQuotedString,
        #    "TripleDoubleQuotedString" : Qsci.QsciLexerPython.TripleDoubleQuotedString,
        #    "ClassName"                : Qsci.QsciLexerPython.ClassName,
        #    "FunctionMethodName"       : Qsci.QsciLexerPython.FunctionMethodName,
        #    "Operator"                 : Qsci.QsciLexerPython.Operator,
        #    "Identifier"               : Qsci.QsciLexerPython.Identifier,
        #    "CommentBlock"             : Qsci.QsciLexerPython.CommentBlock,
        #    "UnclosedString"           : Qsci.QsciLexerPython.UnclosedString,
        #    "HighlightedIdentifier"    : Qsci.QsciLexerPython.HighlightedIdentifier,
        #    "Decorator"                : Qsci.QsciLexerPython.Decorator
        #}
        # Multi-line strings (expression, flag, style)
        # FIXME: The triple-quotes in these two lines will mess up the
        # syntax highlighting from this point onward
        self.tri_single = (QtCore.QRegExp("'''"), 1, STYLES['string2'])
        self.tri_double = (QtCore.QRegExp('"""'), 2, STYLES['string2'])

        rules = []

        # Keyword, operator, and brace rules
        rules += [(r'\b%s\b' % w, 0, STYLES['keyword'])
            for w in Highlighter_Python_AGeSimple_base.l_keywords]
        rules += [(r'%s' % o, 0, STYLES['operator'])
            for o in Highlighter_Python_AGeSimple_base.l_operators]
        rules += [(r'%s' % b, 0, STYLES['brace'])
            for b in Highlighter_Python_AGeSimple_base.l_braces]

        # All other rules
        rules += [
            # 'self'
            (r'\bself\b', 0, STYLES['self']),

            # Double-quoted string, possibly containing escape sequences
            (r'"[^"\\]*(\\.[^"\\]*)*"', 0, STYLES['string']),
            # Single-quoted string, possibly containing escape sequences
            (r"'[^'\\]*(\\.[^'\\]*)*'", 0, STYLES['string']),

            # 'def' followed by an identifier
            (r'\bdef\b\s*(\w+)', 1, STYLES['defclass']),
            # 'class' followed by an identifier
            (r'\bclass\b\s*(\w+)', 1, STYLES['defclass']),

            # From '#' until a newline
            (r'#[^\n]*', 0, STYLES['comment']),

            # Numeric literals
            (r'\b[+-]?[0-9]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b', 0, STYLES['numbers']),
        ]

        # Build a QtCore.QRegExp for each pattern
        self.rules = [(QtCore.QRegExp(pat), index, fmt) for (pat, index, fmt) in rules]
        
        
    # Syntax styles that can be shared by all languages
    
    def f_format(self, color, style=''): # Q
        """Return a QtGui.QTextCharFormat with the given attributes.
        """
        _color = QtGui.QColor()
        _color.setNamedColor(color)

        _format = QtGui.QTextCharFormat()
        _format.setForeground(_color)
        if 'bold' in style:
            _format.setFontWeight(QtGui.QFont.Bold)
        if 'italic' in style:
            _format.setFontItalic(True)

        return _format


    def TEMPLATE_highlightBlock(self, text): # Q
        """Apply syntax highlighting to the given block of text.
        """
        # Do other syntax formatting
        for expression, nth, f_format in self.rules:
            index = expression.indexIn(text, 0)

            while index >= 0:
                # We actually want the index of the nth match
                index = expression.pos(nth)
                length = expression.cap(nth).length()
                self.setFormat(index, length, f_format)
                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)

        # Do multi-line strings
        in_multiline = self.match_multiline(text, *self.tri_single)
        if not in_multiline:
            in_multiline = self.match_multiline(text, *self.tri_double)


    def TEMPLATE_match_multiline(self, text, delimiter, in_state, style): # Q
        """Do highlighting of multi-line strings. ``delimiter`` should be a
        ``QtCore.QRegExp`` for triple-single-quotes or triple-double-quotes, and
        ``in_state`` should be a unique integer to represent the corresponding
        state changes when inside those strings. Returns True if we're still
        inside a multi-line string when this function is finished.
        """
        # If inside triple-single quotes, start at 0
        if self.previousBlockState() == in_state:
            start = 0
            add = 0
        # Otherwise, look for the delimiter on this line
        else:
            start = delimiter.indexIn(text)
            # Move past this match
            add = delimiter.matchedLength()

        # As long as there's a delimiter match on this line...
        while start >= 0:
            # Look for the ending delimiter
            end = delimiter.indexIn(text, start + add)
            # Ending delimiter on this line?
            if end >= add:
                length = end - start + add + delimiter.matchedLength()
                self.setCurrentBlockState(0)
            # No; multi-line string
            else:
                self.setCurrentBlockState(in_state)
                length = text.length() - start + add
            # Apply formatting
            self.setFormat(start, length, style)
            # Look for the next match
            start = delimiter.indexIn(text, start + length)

        # Return True if still inside a multi-line string, False otherwise
        if self.currentBlockState() == in_state:
            return True
        else:
            return False
    
    def TEMPLATE_styleText(self, start, end): # QSci
        # 1. Initialize the styling procedure
        # ------------------------------------
        self.startStyling(start)

        # 2. Slice out a part from the text
        # ----------------------------------
        text = self.parent().text()[start:end]

        # 3. Tokenize the text
        # ---------------------
        p = re.compile(r"[*]\/|\/[*]|\s+|\w+|\W")

        # 'token_list' is a list of tuples: (token_name, token_len)
        token_list = [ (token, len(bytearray(token, "utf-8"))) for token in p.findall(text)]

        # 4. Style the text
        # ------------------
        # 4.1 Check if multiline comment
        multiline_comm_flag = False
        editor = self.parent()
        if start > 0:
            previous_style_nr = editor.SendScintilla(editor.SCI_GETSTYLEAT, start - 1)
            if previous_style_nr == 3:
                multiline_comm_flag = True
        # 4.2 Style the text in a loop
        for i, token in enumerate(token_list):
            if multiline_comm_flag:
                self.setStyling(token[1], 3)
                if token[0] == "*/":
                    multiline_comm_flag = False
            else:
                if token[0] in ["for", "while", "return", "int", "include"]:
                    # Red style
                    self.setStyling(token[1], 1)
                elif token[0] in ["(", ")", "{", "}", "[", "]", "#"]:
                    # Blue style
                    self.setStyling(token[1], 2)
                elif token[0] == "/*":
                    multiline_comm_flag = True
                    self.setStyling(token[1], 3)
                else:
                    # Default style
                    self.setStyling(token[1], 0)
        
    def r_highlight(self, text):
        # Do other syntax formatting
        print("Hi")
        for expression, nth, f_format in self.rules:
            index = expression.indexIn(text, 0)

            while index >= 0:
                # We actually want the index of the nth match
                index = expression.pos(nth)
                length = len(expression.cap(nth))
                self.apply(index, length, f_format)
                index = expression.indexIn(text, index + length)

        if self.mode == "Qt":
            self.setCurrentBlockState(0)
    def lexer(self):
        return "Python"
    def language(self):
        return "python"
    def autoCompletionWordSeparators(self):
        return [".",]
    #def blockStart(self, style=0):
    #    print(style)
    #    from ctypes import create_string_buffer
    #    c = create_string_buffer(":".encode("ascii"))
    #    return c
    #    #return ":".encode("ascii")
    #    #return ":"
    # instead: https://stackoverflow.com/questions/50459326/how-do-you-add-folding-to-qscilexercustom-subclass
    #
    def blockLookback(self):
        return 0
    

class Highlighter_Python_AGeSimple_Qt(QtGui.QSyntaxHighlighter, Highlighter_Python_AGeSimple_base):
    def __init__(self, document):
        QtGui.QSyntaxHighlighter.__init__(self, document)
        self.init_base("Qt")

if QSciImported:
    class Highlighter_Python_AGeSimple_QSci(Qsci.QsciLexerCustom, Highlighter_Python_AGeSimple_base):
        def __init__(self, parent):
            self.init_base("QSci")
            Qsci.QsciLexerCustom.__init__(self, parent)
        def styleText(self, start, end): # QSci
            self.currentStart = start
            text = self.parent().text()[start:end]
            self.r_highlight(text)
            self.currentStart = 0
else:
    Highlighter_Python_AGe_QSci = False

class Highlighter_Python_AGeSimple(_Highlighter_Wrapper):
    def __init__(self, QtEditor, QSciEditor, additionalKeywords=None):
        if additionalKeywords is None:
            additionalKeywords = []
        self.QSciImported = QSciImported
        self.QtSH_Class, self.QSciSH_Class = Highlighter_Python_AGeSimple_Qt, Highlighter_Python_AGeSimple_QSci
        self.QtEditor, self.QSciEditor = QtEditor, QSciEditor
        self.QtSH = self.QtSH_Class(self.QtEditor.document())
        if self.QSciImported:
            self.QSciSH = self.QSciSH_Class(self.QSciEditor)
            self.QSciEditor.setLexer(self.QSciSH)
        else:
            self.QSciSH = None
#endregion AGe Sh Python
#endregion AGe SH

