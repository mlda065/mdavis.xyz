import yaml
import pprint as pp
from mako.template import Template
from tidylib import tidy_document
import re
import myspellcheck

# pyyaml converts "yes" and "no" to "True" and "False". I don't want that.
from yaml.constructor import Constructor

def loadDictionaries():
    dictionaryFileNames = [
       '/usr/share/dict/american-english',
       '/usr/share/dict/british-english',
       'custom-words.txt']
    words = []
    for fname in dictionaryFileNames:
        with open(fname,'r') as fp:
            words += [w.strip() for w in fp if w.strip() != '']
    return(set(words))

dictionary = loadDictionaries()

def addToDictionary(word):
    fname = 'custom-words.txt'
    with open(fname,'a') as fp:
        fp.write("\n" + word)
    dictionary.add(word)


def isNumber(s):
    try:
        float(s)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass

    return False

def add_bool(self, node):
    return self.construct_scalar(node)

Constructor.add_constructor(u'tag:yaml.org,2002:bool', add_bool)

def main():
    inputFname = 'content.yaml'
    with open(inputFname,'r') as f:
        content = yaml.load(f)

    # pp.pprint(content)
    validate(content)
    html = htmlize(content)
    # print(html)

    with open('stub.html','w') as f:
        f.write(html)
    print('done')

def validate(content):
    for (i,slide) in enumerate(content):
        if 'id' not in slide:
            slide['id'] = "slide-%3d" % i
    allIDs = set([x['id'] for x in content if 'id' in x])
    for (i,slide) in enumerate(content):
        assert('id' in slide)
        print("Validating slide %s" % slide['id'])
        for (elnum,el) in enumerate(slide['content']): # els is dict with one key
            assert(len(el) == 1)
            key = [k for k in el.keys()][0]
            value = el[key]
            assert(key in ['h1','h2','p','button'])
            if not value:
                print("error, empty %s element (#%d) in slide %s" % (k,elnum,slide['id']))
                exit(1)
            if 'button' == key:
                button = value[0]
                # pp.pprint(el)
                if button['destination-type'].lower() == 'absolute':
                    assert(button['destination'] in allIDs)
                else:
                    assert(button['destination-type'].lower() == 'relative')
                    x = int(button['destination'])
                    assert(i+x < len(content))
                    absID = content[i+x]['id']
                    print("resolving %s + %d to %s" % (slide['id'],x,absID))
                    button['destination'] = absID
                    button['destination-type'] = 'absolute'
                assert(button['direction'] in ['left','right','up','down'])
                text = button['text']
                if (not text) or (text.strip() == ''):
                    print("Error: no content for button which is element %d of slide %s" % (elnum,slide['id']))
                    exit(1)
                elif not myspellcheck.checkLine(text):
                    print("error, spelling mistake in button element #%d in slide %s" % (elnum,slide['id']))
                    exit(1)
            else:
                # not button
                assert(type(value.strip()) == type(''))
                if not myspellcheck.checkLine(value):
                    print("error, spelling mistake %s  #%d element in slide %s" % (key,i,slide['id']))
                    exit(1)
def htmlize(content):
    with open('template.html','r') as f:
        template = Template(f.read())
    html = template.render(content=content)

    try:
        document, errAndWarn = tidy_document(html,options={'numeric-entities':1})
        if (errAndWarn != None):
            errAndWarn = errAndWarn.split('\n')
            pp.pprint(errAndWarn)
            warnings = [w for w in errAndWarn if 'warn' in w.lower()]
            errors = [e for e in errAndWarn if e not in warnings if e != '']
            if len(errors) > 0:
                print("Error: invalid html")
                print(errors[0])
                exit(1)
            else:
                print('all warnings, continuing anyway')

        else:
            print("html valid!")
    except OSError:
        print("!!!Warning, skipping html validation")

    return(html)

def unitTests():
    pass

if __name__ == '__main__':
    unitTests()
    main()
