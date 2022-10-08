import re


def main():
    q = "from [dsadsa].dsa left outer join [wqewq].[qwee] join [wqew1q].[qwee] join [wqe2wq].[qwee] join [wqew3q].[qwee] join [wqewq].[qwee]"


    # rName = '(?:\[?[^\(\] \.\,\']+\]?)(?:\s*\.\s*(?:\[?[^\(\] \.\,\']+\]?))*'
    # rFrom = r'FROM\s+'+rName
    # rJoins = r'(?P<type>(?:LEFT|RIGHT)?\s*(?:OUTER)?\s+JOIN)\s+(?P<name>'+rName+')'
    # joinsMatches = [match.groups() for match in re.finditer(rJoins,q,flags=re.I)]
    # print(joinsMatches)
    currentCreate = "w1 w2 --comment \n w3 -- csad \n w8"
    hasComment = re.search("--.+?(\n|\\n)",currentCreate,flags=re.I)
    print(hasComment)
    while hasComment:
        currentCreate = currentCreate[:hasComment.start()]+'\n'+currentCreate[hasComment.end():]
        hasComment = re.search("--.+?(\n|\\n)",currentCreate,flags=re.I)
        print(currentCreate)


if __name__ == '__main__':
    main()