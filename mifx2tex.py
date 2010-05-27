#!/bin/env python

from xml.dom.minidom import parse
import sys, re, os

def get_table(tag):
    rows1 = []
    rows = tag.getElementsByTagName("Row")
    for r in rows:
        row_data = []
        cells = r.getElementsByTagName("Cell")
        for c in cells:
            tag = getfirst(c, "PgfTag")
            txt = []
            font = getfirstnode(c, "PgfFont")
            if font is not None:
                ftag = getfirst(font, "FTag")
                ffam = getfirst(font, "FFamily")
            else:
                ftag = None
                ffam = None
            strs = c.getElementsByTagName("String")
            for s in strs:
                txt.append(string_val(s))
            txt = "".join(txt)
            row_data.append((ftag, ffam, tag, txt))
        rows1.append(row_data)
    return rows1

def get_table_widths(table):
    wslist = []
    ws = table.getElementsByTagName("TblColumnWidth")
    for w in ws:
        wslist.append(contents(w))
    return wslist

def read_tables(doc):
    symbols = {}
    cmds = []
    tbls = doc.getElementsByTagName("Tbl")
    for t in tbls:
        widths = get_table_widths(t)
        tag = getfirstnode(t, "TblID")
        tag = contents(tag)
        # print >> sys.stderr, "table", tag
        heading = getfirstnode(t, "TblH")
        header = get_table(heading)[0]
        body = getfirstnode(t, "TblBody")
        rows = get_table(body)
        symbols[tag] = (header, rows, widths)
    return symbols

def string_val(node):
    node.normalize()
    t = node.firstChild.data[1:-1]
    t = uniconvert(t)
    try:
        t = t.encode("utf-8")
    except:
        print >> sys.stderr, "can't encode", repr(t.encode("utf-8")), repr(t)
        sys.exit(1)
    t = mifunescape(t)
    return t

def uniconvert(s):
    for (old, new) in (("\xe2\x80\x93", "-"),
                       ("\xe2\x80\x94", "-"),
                       ("\xe2\x80\x98", "'"),
                       ("\xe2\x80\x99", "'"),
                       ("\xe2\x80\x9c", "\""),
                       ("\xe2\x80\x9d", "\"")):
        old = old.decode("utf-8")
        s = s.replace(old, new)
    return s

def contents(node):
    node.normalize()
    return node.firstChild.data.encode("ascii")

def getfirst(node, name):
    children = node.getElementsByTagName(name)
    if len(children) < 1:
        return None
    ch = children[0]
    ch.normalize()
    return ch.firstChild.data.encode("ascii")[1:-1]

def getfirstnode(node, name):
    children = node.getElementsByTagName(name)
    if len(children) < 1:
        return None
    return children[0]

def read_text(doc):
    "read the MIF as an XML DOM and emit formatting commands"
    cmds = []

    flows = doc.getElementsByTagName("TextFlow")
    for f in flows:

        # "A" tagged flows are visible
        # (this is quite unclear in the docs)
        tag = getfirst(f, "TFTag")
        if tag != "A":
            continue

        paras = f.getElementsByTagName("Para")
        for p in paras:
            style = getfirst(p, "PgfTag")
            cmds.append(("Para", style))
            for l in p.getElementsByTagName("ParaLine"):
                incode = False
                cmds.append(("Line", None))                
                for s in l.childNodes:
                    if s.nodeType == doc.ELEMENT_NODE and s.nodeName == "AFrame":
                        cmds.append(("Image", contents(s)))
                    elif s.nodeType == doc.ELEMENT_NODE and s.nodeName == "Marker":
                        mtext = mifunescape(getfirst(s, "MText"))
                        cmds.append(("Index", mtext))
                    elif s.nodeType == doc.ELEMENT_NODE and s.nodeName == "String":
                        t = string_val(s)
                        cmds.append(("String", t))
                    elif s.nodeType == doc.ELEMENT_NODE and s.nodeName == "Char":
                        if contents(s) == "HardReturn":
                            cmds.append(("String", "\n"))
                    elif s.nodeType == doc.ELEMENT_NODE and s.nodeName == "Font":
                        ftag = getfirst(s, "FTag")
                        ffam = getfirst(s, "FFamily")
                        cmds.append(("Font", (ftag, ffam)))
                    elif s.nodeType == doc.ELEMENT_NODE and s.nodeName == "ATbl":
                        cmds.append(("Table", contents(s)))
                        
                cmds.append(("EndLine", None))
            cmds.append(("EndPara", style))
            
    return cmds

def multireplace(text, reps):
    rdict = dict(reps)
    reg = re.compile("|".join("(%s)" % re.escape(l) for (l, r) in reps))
    def rep(m):
        return rdict[m.group()]
    text = reg.sub(rep, text)
    return text

def mifunescape(text):
    reps = (("\\q", "'"),
            ("\\Q", "'"),
            ("\\>", ">"),
            ("\\\\:", ":"),
            ("\\\\", "\\"))
    return multireplace(text, reps)
    
def latexescape(text):
    reps = (("\\", "\\textbackslash{}"),
            ("_", "\\_"),
            ("{", "\\{"),
            ("}", "\\}"),
            ("$", "\\$"),
            (" '", " `"),
            (" \"", " ``"),
            ("%", "\\%"),
            ("&", "\\&"),
            ("~", "\\~{}"),
            ("^", "\\^{}"),
            ("|", "\\textbar{}"),
            ("<", "\\textless{}"),
            (">", "\\textgreater{}"),
            ("#", "\\#"))
    return multireplace(text, reps)

prelude = """\\documentclass{book}
\\usepackage[margin=1in]{geometry}
\\usepackage{times}
\\usepackage{longtable}
\\setcounter{secnumdepth}{3}
\\setcounter{tocdepth}{3}
\\usepackage{makeidx}
\\makeindex
\\usepackage{hyperref}
\\begin{document}
\\tableofcontents
"""

endlude = """\\printindex
\\end{document}
"""

def verb_escape(txt):
    return txt.replace("|", "|\\verb+|+\\verb|")

def drawtable(table):
    txt = []
    (header, rows, widths) = table

    fmt = []
    for n in range(len(rows[0])):
        w = widths[len(widths) - len(rows[0]) + n]
        fmt.append("p{%s}" % w.replace("\"", "in"))
    fmt = "".join(fmt)
    
    rows = [header] + rows

    # limited formatting support 
    font_map = {"Code": "verb",
                "Courier": "verb",
                "Helvetica": "verb",
                "Emphasis": "emph",
                "EquationVariables": "emph"}

    heading_styles = ["CELLHEADING"]
    
    txt.append("\n\\begin{center}")
    txt.append("\\begin{longtable}{%s}\n" % fmt)
    for i0, r in enumerate(rows):
        if i0 == 1:
            txt.append("\\hline\n")
        for i, (ftag, ffam, ptag, c) in enumerate(r):
            if i != 0:
                txt.append(" & ")
            f = font_map.get(ftag, None)
            if f is None:
                f = font_map.get(ffam, None)
            s = latexescape(c)

            if ptag in heading_styles:
                txt.append("\\textbf{%s}" % s)
            elif f == "verb":
                txt.append("\\verb|%s|" % verb_escape(c))
            elif f == "emph":
                txt.append("\\emph{%s}" % s)
            else:
                txt.append(s)
            
        if i0 != len(rows) - 1:
            txt.append("\\\\")
        txt.append("\n")
    txt.append("\\end{longtable}")
    txt.append("\\end{center}\n")
    return "".join(txt)

def format_latex(filename, cmds, tables):

    "latex formatting environments from list of styling commands"

    style_map = {"LISTBULLET1": "itemize",
                 "LISTNUMBER1": "enumerate",
                 "LISTCONTINUE1": "description",
                 "LISTMARK2": "description",

                 "PROGRAM": "verbatim",
                 "PROGRAMINDENT": "verbatim",

                 "LOCALTITLE": "chapter",
                 "HEADING1": "section",
                 "HEADING2": "subsection",
                 "HEADING3": "subsubsection",

                 }

    font_map = {"Code": "verb",
                "Courier": "verb",
                "Emphasis": "emph",
                "EquationVariables": "emph"}

    list_styles = ["itemize", "enumerate", "description"]
    join_styles = ["itemize", "enumerate", "description", "verbatim"]
    line_styles = ["emph", "verb", "chapter", "section", "subsection", "subsubsection"]
    
    # nothing inside verbatim
    # verbatim ends itemize
    
    restart_styles = ["chapter", "section", "subsection", "subsubsection",
                      "verbatim", "itemize", "enumerate", "description"]
    
    begin = {"itemize": "\\begin{itemize}",
             "enumerate": "\\begin{enumerate}",
             "description": "\\begin{description}",
             "emph": "\\emph{",
             "verb": "\\verb|",
             "verbatim": "\\begin{verbatim}",
             "chapter": "\\chapter{",
             "section": "\\section{",
             "subsection": "\\subsection{",
             "subsubsection": "\\subsubsection{"
             }

    end = {"itemize": "\\end{itemize}",
           "enumerate": "\\end{enumerate}",
           "description": "\\end{description}",
           "emph": "}",
           "verb": "|",
           "verbatim": "\end{verbatim}",
           "chapter": "}",
           "section": "}",
           "subsection": "}",
           "subsubsection": "}"
           }

    delayindex_styles = ["verb", "verbatim", "contents", "section", "subsection", "subsubsection"]

    idx = []
    ss = [None]
    txt = []

    def pop_index():
        txt.append("\n".join(idx))
        del idx[:]

    def top():
        return ss[-1]

    def push_style(s):
        ss.append(s)
        txt.append(begin[s])

    def pop_styles():
        l = len(ss)
        for n in range(l-1):
            s = ss.pop()
            txt.append(end[s])
        pop_index()

    def pop_line():
        if top() in line_styles:
            s = ss.pop()
            txt.append(end[s])
        
    for (c, val) in cmds:
        
        if c == "Para":
            style = style_map.get(val, None)

            if style in join_styles and top() == style:
                pass
            elif style in restart_styles:
                pop_styles()
                push_style(style)
            elif style is None:
                pop_styles()
            
            if style in list_styles:
                txt.append("\\item ")
            
        elif c == "String":
            if val == "\n":
                # hard return
                pop_line()
                txt.append(val)
            elif top() == "verb":
                txt.append(verb_escape(val))
            elif top() == "verbatim":
                txt.append(val)
            else:
                txt.append(latexescape(val))
        
        elif c == "EndLine":
            pop_line()
            txt.append("\n")
            
        elif c == "EndPara":
            if top() != "verbatim":
                txt.append("\n")
        
        elif c == "Table":
            pop_styles()
            txt.append(drawtable(tables[val]))
        
        elif c == "Index":
            if top() in delayindex_styles:
                idx.append("\\index{%s}" % latexescape(val))
            else:
                txt.append("\\index{%s}" % latexescape(val))
        
        elif c == "Font":
            (ftag, ffam) = val
            font = font_map.get(ftag, None)
            if font is None:
                font = font_map.get(ffam, None)
            if font is None:
                pop_line()
            elif top() != font:
                pop_line()
                push_style(font)

        elif c == "Image":
            imgname = "%s_%s" % (filename, val)
            pop_line()
            txt.append("\n\n\includegraphics{%s}" % imgname)
            # print >> sys.stderr, "Image: %s" % imgname

    pop_styles()
    
    return txt

def showfonts(cmds):
    fonts = set()
    for (c, val) in cmds:
        if c == "Font":
            fonts.add(val)
    for f in list(fonts):
        print >> sys.stderr, f

def main():

    filename = sys.argv[1]
    print >> sys.stderr, "parsing XML"
    doc = parse(filename)
    print >> sys.stderr, "converting tables"
    tables = read_tables(doc)
    print >> sys.stderr, "converting formatting"
    cmds = read_text(doc)

    print >> sys.stderr, "latex output"
    txt = []
    # txt.append(prelude)
    txt.extend(format_latex(os.path.split(filename)[1].replace(".mif.xml", ""), cmds, tables))
    # txt.append(endlude)
    print "".join(txt)

if __name__ == "__main__":
    main()
    
