from Parser import getLines
import sys
import os
import json
import re
import textwrap
import locale
import io
from graphviz import Graph

connections = r"(?=SELECT\s+.+\s+FROM\s+((?!.+\..+)(?P<ftable_1>\[?\S+\]?)|(?P<fschema_1>\[?\S+\]?)\.(?P<ftable_2>\[?\S+\]?)|(?P<fdb>\[?\S+\]?)\.(?P<fschema_2>\[?\S+\]?)\.(?P<ftable_3>\[?\S+\]?))\b.+?\s+(?P<operator>UNION|UNION\sALL|EXCEPT|INTERSECT)\s+SELECT\s+.+\s+FROM\s+((?!.+\..+)(?P<stable_1>\[?\S+\]?)|(?P<sschema_1>\[?\S+\]?)\.(?P<stable_2>\[?\S+\]?)|(?P<sdb>\[?\S+\]?)\.(?P<sschema_2>\[?\S+\]?)\.(?P<stable_3>\[?\S+\]?))\s+)"
regex = [
    # r'(?<!\S)(?:\[?\w+\]?)\.(?:\[?[^\(\)\s]+\]?)(?!\S)',
    r'(?<=JOIN\s|FROM\s)\[?\w+\]?(?!\S)',#one \ [one]
    r'(?<=JOIN\s|FROM\s)\[?\w+\]?\.\[?\w+\]?(?!\S)',#one.two \ [one].[two]
    r'(?<=JOIN\s|FROM\s)\[\w+\]\.\w+(?!\S)',#[one].two
    r'(?<!\S)\[?\w+\]?\.\[?\w+\]?(?!\S)',#one.two
    r'(?<!\S)\w+\.\w+\.\w+(?!\S)',#one.two.three
    r'(?<!\S)\[[^\]+]+\]\.\[[^\]+]+\](?!\S^;)',#[one].[two]
    r'(?<!\S)\[[^\]+]+\]\.\[[^\]+]+\]\.\[[^\]+]+\](?!\S^;)',#[one].[two].[three]
    r'(?<!\S)\[[^\]+]+\]\.\[[^\]+]+\]\.\[[^\]+]+\]\.\[[^\]+]+\](?!\S^;)',#[one].[two].[three].[four]
    ]



# Graph object that holds our graph.
dot = Graph( strict=True)
def findJoinsUpdated(filedir, name, other, tabdict, simple, neato, conn, edges):
    # Performs a secondary parse of the sql file, looking for select statements within objects.
    # When they are found, we look for a join statement. If we find one, we assume all the tables
    # we find within that select statement are somewhat correlated, and draw connections between
    # them in a graphviz undirected graph. We display this to user and save it to disk. It can in
    # future be converted to a networkx graph easily to allow for graphical analysis to be performed.

    lines = getLines(filedir)

    # The current list of regular expressions used to match tables. Needs to be expanded to account for all
    # possible ways a table can be referenced in sql.


    # list of colors used to color the graph created.
    colors = ["red", "blue", "green", "yellow", "orange", "purple", "black", "brown", "cyan",
              "pink", "magenta", "black", "chartreuse", "coral", "crimson", "chocolate", "indigo",
              "fuchsia", "lime", "maroon", "olive", "navy", "teal", "yellowgreen", "rosybrown", "orangered", "orchid",
              "tomato"]
    col = 0

    currobj = ""
    objs = []
    dot.name=name+".T"

    # Iterate through all of the lines of the sql file, looking for create statements for each of the objects we are looking for.
    for i in range(len(lines)):
        matchV = re.match(r'\bCREATE\s+VIEW\s+(?P<schema>\[?.+\]?)\.(?P<view>\[?.+?\]?)\s', lines[i], re.I)
        matchF = re.match(r'\bCREATE\s+FUNCTION\s+(?P<schema>\[?.+\]?)\.(?P<func>\[?.+?\]?)\s', lines[i], re.I)
        matchP = re.match(r'\bCREATE\s+PROC\s+(?P<schema>\[?.+\]?)\.(?P<proc>\[?.+?\]?)\s', lines[i], re.I)
        matchT = re.match(r'\bCREATE\s+TRIGGER\s+(?P<schema>\[?.+\]?)\.(?P<trig>\[?.+?\]?)\s', lines[i], re.I)

        if matchV or matchF or matchP or matchT:
            # When we find a match, record the name of the object so we can later know what object is creating these joins.
            if matchV:
                currobj = matchV.group('schema') + '.' + matchV.group('view')
            elif matchP:
                currobj = matchP.group('schema') + '.' + matchP.group('proc')
            elif matchF:
                currobj = matchF.group('schema') + '.' + matchF.group('func')
            elif matchT:
                currobj = matchT.group('schema') + '.' + matchT.group('trig')

            # Handle selecting a color for this object.
            if currobj not in objs:
                objs.append(currobj)
            col = objs.index(currobj) % len(colors)

            # Look through all the lines in the declaration of this object.
            for line in range(i + 1, len(lines)):
                # Look for select
                select = re.search(r'select', lines[line], re.I)

                if select:
                    foundSel(line,lines,select.end(),currobj,other, tabdict, simple,  conn, edges,colors,col)

                    break

    dot.graph_attr['overlap'] = "scalexy"

    # Neato attempts to spread out the graph as spherical as possible. It is a user option in the GUI.
    if neato:
        dot.graph_attr['layout'] = "neato"

    dot.format = 'svg'
    dot.render(view=True)
    # This graph is saved, but it is here automatically rendered to the user in svg format.


def foundSel(lineIndex,lines,firstLineIndex,currobj,other, tabdict, simple,  conn, edges,colors,col):
    joins = False  # Records if there is a join in this select statement
    tables = []  # Holds all the tables within this select statement


    # Look through all the lines in this select.
    for sel in range(lineIndex, len(lines)):
        if sel == lineIndex:
            foundFrom = re.search(r'from', lines[sel][firstLineIndex:], re.I)
            foundWhere = re.search(r'where', lines[sel][firstLineIndex:], re.I)
            foundSelect = re.search(r'select', lines[sel][firstLineIndex:], re.I)
            foundJoins = re.search(r'join', lines[sel][firstLineIndex:], re.I)
        else:
            foundFrom = re.search(r'from', lines[sel], re.I)
            foundWhere = re.search(r'where', lines[sel], re.I)
            foundSelect = re.search(r'select', lines[sel], re.I)
            foundJoins = re.search(r'join', lines[sel], re.I)

        if foundJoins:
            joins = True
        if foundSelect and not foundFrom and not foundWhere:
            foundSel(lineIndex,lines,foundSelect.end(),currobj,other, tabdict, simple,  conn, edges,colors,col)
        elif foundFrom:
            if foundSelect and foundSelect.start()<foundFrom.start():
                foundSel(lineIndex,lines,foundSelect.end(),currobj,other, tabdict, simple,  conn, edges,colors,col)
            else:
                # Check every table regex against each line we find.
                for r in regex:
                    table = re.findall(r, lines[sel],flags=re.I|re.X)
                    if '[nrnClinic].EvalSubcategoryCodes' in table:
                        print('[nrnClinic].EvalSubcategoryCodes met')
                    tables = tables + table

        elif foundWhere or lines[sel].startswith("GO") or lines[sel].startswith("\n"):
            if (foundSelect and foundWhere) and foundSelect.start()<foundWhere.start():
                foundSel(lineIndex=lineIndex,lines=lines,firstLineIndex=foundSelect.end())
            else:
                # Finish checking for a select statement, as we dont want to check too far.
                if foundWhere or lines[sel].startswith("GO") or lines[sel].startswith("\n"):
                    # If there were joins, we can now record these tables on the graph.
                    if joins:
                        # All tables in tables[] should be interconnected

                        # But first we need to remove all of the aliases

                        tab = []

                        # Look through the list of tables we have collected for this select statement.
                        for f in range(len(tables)):
                            # Split it up into each of the words that make it up, as in, "[one].[two]" becomes ["one","two"]
                            s = re.findall(r'\[(.+?)\]', tables[f], re.I)
                            if tables[f] == '[nrnClinic].EvalSubcategoryCodes':
                                print("[nrnClinic].EvalSubcategoryCodes: met")

                            if not s:
                                s = re.split(r'\.', tables[f], re.I)
                            if currobj=="[dbo].[EvalIncompleteErrorsList]":
                                print("[dbo].[EvalIncompleteErrorsList]: "+str(s))
                            if len(s)==1:
                                db =currobj.split('.')[0]
                                db = db.replace('[','')
                                db = db.replace(']','')
                                s = [db,s[0]]
                            print('--'+str(s))
                            # Other is the list of valid databases, and this will exclude aliases.
                            if ( s[0] and s[0] in other.keys()) or (len(s)>1 and s[1] in other.keys()):

                                print('--')

                                # We want to skip over certain two ways that are the first two parts of a three way table name
                                # We have a current object in s, and the next object that was found in temp.
                                # We do this by looking to the next object and doing the same conversion as earlier to it.
                                # Because of the way the regex works, it will be [one].[two] in s, and [one].[two].[three] in temp if it is a three way.
                                # Thus, if one=one, two=two, and temp has three parts, we can be sure that this current s should be excluded in favor of
                                # the three way it is a incomplete part of.
                                threeway = False
                                for k in range(len(tables)):
                                    temp = re.findall(r'\[(.+?)\]', tables[k], re.I)

                                    if not temp:
                                        temp = re.split(r'\.', tables[k], re.I)

                                    if temp[0] == s[0] and len(s)>1 and len(temp)>1and temp[1] == s[1] and len(temp) > 2:
                                        threeway = True
                                        break
                                if threeway:
                                    continue
                                # Now we simply need to convert this ["one","two"] format back into a single string (with no brackets)
                                # Simple means we limit it to tables that were found by the findTables function.
                                # If simple is not true then we simply need to do the conversion for all the tables we found
                                # (This will often also include some views that were referenced like tables in joins, which can be good or bad,
                                # which is why this is a user option of whether or not they want a simplified table.)
                                print("lCheck")
                                if simple:
                                    if s[0] in tabdict:
                                        if len(s)>1 and s[1] in tabdict[s[0]]:
                                            st = s[0]
                                            for v in range(1, len(s)):
                                                st = st + '.' + s[v]
                                            tab.append(st)
                                else:
                                    st = s[0]
                                    for v in range(1, len(s)):
                                        st = st + '.' + s[v]
                                    tab.append(st)
                                # In either case, we add all formatted tables to tab[]

                        # Now we need to handle making each table into a node, and adding edges between every node
                        # As we are assuming every table is equally interconnected as they are all within the same
                        # select statement and all joined together.

                        # We simply go through tab[] and use dot.node(), then specify the:
                        # label - What is shown on the graph
                        # id - What is used to connect the nodes
                        # color - the color corresponding to the parent object.
                        # The conn condition refers to whether we want the same table, if referenced by multiple objects
                        # to only occupy one node, or whether we want each object's reference to that table to be its own
                        # node. We do this by either making the nodeid (what is used to determine unique nodes) simply the
                        # name of the table, or the combination of table name and parent object name (the same thing displayed
                        # as the label in either case).
                        for t in tab:
                            if conn:
                                nodeid = t.lower()
                                nodelabel = t + '\n' + currobj
                            else:
                                nodeid = t.lower() + '\n' + currobj
                                nodelabel = t + '\n' + currobj

                            dot.node(nodeid, nodelabel, color=colors[col])

                        # Now we go through in a double loop, adding edges for each possible. Duplicates are automatically filtered
                        # by the condition "String = True" when we created the dot object. If conn is true we use just the table names,
                        # but if conn is false then we use the combination of table and object names to connect them.

                        # If edges is true we label the edges with the object that created them, otherwise we don't.
                        for t in tab:
                            for t1 in tab:
                                if t != t1:
                                    if conn:
                                        node1id = t.lower()
                                        node2id = t1.lower()
                                    else:
                                        node1id = t.lower() + '\n' + currobj
                                        node2id = t1.lower() + '\n' + currobj

                                    if edges:
                                        dot.edge(node1id, node2id, label=currobj, color=colors[col])
                                    else:
                                        dot.edge(node1id, node2id, color=colors[col])


                    # If we find the word "GO" we know we have reached the end of this particular object, and need to continue.
                    end = re.match(r'go', lines[lineIndex], re.I)
                    if end:
                        return
