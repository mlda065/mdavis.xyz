import re

standardWordsFname = 'standardWords.txt'
extraWordsFname = 'extraWords.txt'

def test():
    testStripXML()
    teststripFancy()
    testStripForSpellcheck()
    testStripMarkdown()

def stripFancy(text,markdown=False):
    text = stripXML(text)
    for char in ['&ldquo;','&rdquo;','&quot;']:
        text = text.replace(char,'"')
    if markdown:
        text = stripMarkdown(text)
    return(text)

def stripXML(text):
    # first, strip any divs which are formulas
    expr = r'<div class="formula">.*?</div>'
    text = re.sub(expr, ' ', text)
    expr = r'<span class="formula">.*?</span>'
    text = re.sub(expr, ' ', text)
    expr = r'<[^<>]+>'
    text = re.sub(expr, '', text)
    return(text)

def testStripXML():
    text = 'This is <div class="something">not a</div> formula and this is <div class="something">not a</div> formula'
    expected = 'This is not a formula and this is not a formula'
    actual = stripXML(text)
    assert(actual == expected)

    text = 'This is <div class="formula">definitely <i>a</i></div> formula'
    expected = 'This is   formula'
    actual = stripXML(text)
    if actual != expected:
        print("Text:     %s" % text)
        print("Expected: %s" % expected)
        print("Actual:   %s" % actual)
    assert(actual == expected)

    text = 'This is <span class="formula">definitely a</span> formula'
    expected = 'This is   formula'
    actual = stripXML(text)
    if actual != expected:
        print("Text:     %s" % text)
        print("Expected: %s" % expected)
        print("Actual:   %s" % actual)
    assert(actual == expected)

def stripMarkdown(text):
    expr = r'```([^`]+)```'
    text = re.sub(expr, r'\1', text)
    lines = text.split('\n')
    newLines = []
    for line in lines:
        expr = r'!\[([^\[\]]+)\]\(([^\)\(]+)\)({[^}{]+})?' # markdown images
        line = re.sub(expr, r'[\1](\2)', line)
        expr = r'\[([^\[\]]+)\]\(([^\(\)]+)\)' # links
        line = re.sub(expr, r'\1', line)
        if (line.count('*') % 2) and line.lstrip().startswith('* '):
            # odd number of *
            expr = r'^\s*\*' # dot list
            line = re.sub(expr, r'', line)
        expr = r'\*\*([^\*]+)\*\*' # bold
        line = re.sub(expr, r'\1', line)
        expr = r'\*([^*]+)\*' # italics
        line = re.sub(expr, r'\1', line)
        expr = r'`([^`]+)`' # code inline
        line = re.sub(expr, r'\1', line)
        expr = r'^\s*>([^<>]*)$' # quote
        line = re.sub(expr, r'\1', line)
        expr = r'^\s*&gt;([^<>]*)$' # quote
        line = re.sub(expr, r'\1', line)
        expr = r'^\s*#+([^#]+)$' # heading
        line = re.sub(expr, r'\1', line)
        newLines.append(line)
    return('\n'.join(newLines).strip())

def testStripMarkdown():
    text = "* this is a *italics* in a line"
    expected = "this is a italics in a line"
    actual = stripMarkdown(text)
    if expected != actual:
        print("Input text: %s" % text)
        print("Expected: %s" % expected)
        print("Actual: %s" % actual)
    assert(actual == expected)

    text = "this is a *italics* in a line"
    expected = "this is a italics in a line"
    actual = stripMarkdown(text)
    if expected != actual:
        print("Input text:\n%s" % text)
        print("Expected:\n%s" % expected)
        print("Actual:\n%s" % actual)
    assert(actual == expected)

    text = "*this* is italics at the start"
    expected = "this is italics at the start"
    actual = stripMarkdown(text)
    if expected != actual:
        print("Input text:\n%s" % text)
        print("Expected:\n%s" % expected)
        print("Actual:\n%s" % actual)
    assert(actual == expected)


    text = "This is an ![image](path)"
    expected = "This is an image"
    actual = stripMarkdown(text)
    if expected != actual:
        print("Input text:\n%s" % text)
        print("Expected:\n%s" % expected)
        print("Actual:\n%s" % actual)
    assert(actual == expected)


    text = "This is an ![image](path){.myclass}"
    expected = "This is an image"
    actual = stripMarkdown(text)
    if expected != actual:
        print("Input text:\n%s" % text)
        print("Expected:\n%s" % expected)
        print("Actual:\n%s" % actual)
    assert(actual == expected)



def teststripFancy():
    original = 'asd'
    expected = 'asd'
    actual = stripFancy(original)
    assert(expected == actual)

    original = '1 <a href="123">blah</a> 2'
    expected = '1 blah 2'
    actual = stripFancy(original)
    assert(expected == actual)

    original = 'This [link](http://example.com) shows [this](./blah)'
    expected = 'This link shows this'
    actual = stripFancy(original,markdown=True)
    if expected != actual:
        print("actual: " + actual)
    assert(expected == actual)

    original = 'This *is* italics'
    expected = 'This is italics'
    actual = stripFancy(original,markdown=True)
    if expected != actual:
        print("actual: " + actual)
    assert(expected == actual)

    original = 'This **is bold** yes'
    expected = 'This is bold yes'
    actual = stripFancy(original,markdown=True)
    if expected != actual:
        print("actual: " + actual)
    assert(expected == actual)

def stripForSpellcheck(word):
    word = stripFancy(word)
    word = word.rstrip(',')
    word = word.strip().rstrip('.?!')

    if word.endswith("™") or word.endswith(":"):
        word = word[:-1]

    expr = [
       r"^\$?-?\d+((\,\d{3})+)?(\.\d+)?$", # numbers (including negative)
       r"^\$?\d+((\,\d{3})+)?(\.\d+)?[BMk]?$", # numbers and dollars
       r"^\d+(\.\d+)?[kMG]?W$", # 1.2GW
       r"^\d+(\.\d+)?[kMG]?Bi\/s$", # 25MBi/s
       r"^\d+((\,\d{3})+)?(\.\d+)?%$", #percentage
       r"^\d{1,2}(:\d{2})?[ap]m$", # time
       r"^\d+\/\d+$", # fractions
       r"^\d+-\d+$", # 2016-2017
       r"^\d{2,4}-\d{1,2}-\d{1,2}$", # 2016-01-02
       r"^\d{1,2}:\d{1,2}(:\d{1,2})?$", # 12:34:13
       r"^(\d+\.?)+$" # 12.1.3
       ]

    for e in expr:
        word = re.sub(e, '', word)

    if any(word.endswith(c) for c in ";™:"):
        word = word[:-1]

    return(word)

def testStripForSpellcheck():
    original = 'asd'
    expected = 'asd'
    actual = stripForSpellcheck(original)
    assert(expected == actual)

    original = 'asd,'
    expected = 'asd'
    actual = stripForSpellcheck(original)
    assert(expected == actual)

    for original in ['$5','123.0','$500,300.12','$5.3M', \
                     '25MBi/s','6am','12:30pm','2016-2017',\
                     '2017-01-2','12:34','13:34:01',
                     '12.2', '13.3.5.']:
        expected = ''
        actual = stripForSpellcheck(original)
        if expected != actual:
            print("original: %s" % original)
            print("Expected: %s" % expected)
            print("Actual: %s" % actual)
        assert(expected == actual)

    original = 'hello123'
    expected = 'hello123'
    actual = stripForSpellcheck(original)
    assert(expected == actual)

    original = 'world!'
    expected = 'world'
    actual = stripForSpellcheck(original)
    assert(expected == actual)

    original = '<i>why</i>? '
    expected = 'why'
    actual = stripForSpellcheck(original)
    assert(expected == actual)


dictionary = None
def init():
    global dictionary
    # initialise dictionary stuff
    with open(standardWordsFname,'r') as f:
        words = [w.strip() for w in f]

    with open(extraWordsFname,'r') as f:
        words += [w.strip() for w in f]

    dictionary = set(words)
    assert('spent' in dictionary)


def addToDict(word):
    dictionary.add(word)
    with open(extraWordsFname,'a') as f:
        f.write(word+'\n')

def checkWord(word):
    if (word != '') and (word not in dictionary) and (word.lower() not in dictionary):
        if word.endswith("'s") or word.endswith("s'"):
            if (word[:-2] in dictionary) or (word[:-2].lower() in dictionary):
                return(True)
        elif word.endswith('s') and ((word[:-1].lower() in dictionary) or (word[:-1] in dictionary)):
            return(True)
        if ('-' in word) and ('--' not in word) and (word.strip('-') == word):
            subwords = word.split('-')
            if all([(w in dictionary) or (w.lower() in dictionary) for w in subwords]):
                return(True)

        print("Error: word %s does not appear in the dictionary" % word)
        if word != word.lower():
           print("   y - add, lowercase %s" % word.lower())
           print("   Y - add, as is %s" % word)
        else:
           print("   y - add as is %s" % word.lower())

        if word.endswith("'s") or word.endswith("s'"):
            print("   a - add lowercase without apostrophe: %s" % word[:-2].lower())
            print("   A - add without apostrophe: %s" % word[:-2])
        elif word.endswith("s"):
            print("   p - add singular lowercase: %s" % word[:-1].lower())
            print("   P - add singular as is : %s" % word[:-1])
        print("   n - don't add. Exit")
        answer = input('')
        if answer.lower().startswith('y'):
            addToDict(word.lower())
        elif answer.lower().startswith('Y'):
            addToDict(word)
        elif answer.startswith('a'):
            addToDict(word[:-2].lower())
        elif answer.startswith('A'):
            addToDict(word[:-2])
        elif answer.startswith('p'):
            addToDict(word[:-1].lower())
        elif answer.startswith('P'):
            addToDict(word[:-1])
        else:
            return(False)
    return(True)

def checkLine(line,markdown=False):
    line = stripFancy(line,markdown=markdown)


    # remove brackets
    expr = r'\(([^\(\)]+)\)'
    line = re.sub(expr, r'\1', line)

    # remove brackets
    expr = r'"([^"]+)"'
    line = re.sub(expr, r'\1', line)

    # remove brackets
    expr = r"\s'([^']+)'[\s,.!?]"
    line = re.sub(expr, r' \1 ', line)

    words = [w.strip() for w in line.split(' ') if w.strip() != '']
    for w in words:
        if not checkWord(stripForSpellcheck(w)):
            return(False)
    return(True)

def checkFile(fname):
    with open(fname,'r') as f:
        content = f.read()
    markdown=(fname.endswith('.md'))
    if markdown:
        print("Passing markdown flag from checkFile to stripFancy")
    content = stripFancy(content,markdown=markdown)
    for (i,line) in enumerate(content.split('\n')):
        if not checkLine(line):
            print("Quitting")
            print("That was file %s line %d" % (fname,i+1))
            print(line)
            return(False)
    return(True)
test()
init()
