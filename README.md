# Project Overview

This project aims for generation a visual documentation for SQL-based databases. The programming language used is Python, the methodology used for query processing is Regular Expressions, and the library used for graphing is Graphviz. Using the 're' library for RegEx, go through the *.sql file and find table names and then search for the relations between tables and each other, the type of the relations, and the Data flow inside the DataBase. 

# Project Steps & Functionalities in Details

## Finding DataBase Objects (completed)

The input given to the program is the path to the *.sql file containing the queries that construct our database, and the DataBase objects that the user want to retrieve, such as Trigger, View, Table, Procedure, etc. Then, the program reads the lines inside the *.sql file and loop through them. For each line, we use certain regular expression to find the DataBase object and its type. After finding them, we store them in dictionaries to present all the objects of the same type together in one dictionary.

*This step can be found in Parser.py in find-type-() methods.*

## Finding Relations Between Tables (In Progress)

In this part, we try to find the relation between each table and all the other tables and their types. There are three types of relations:

* Defined Joins: LEFT (OUTER) JOINS, RIGHT (OUTER) JOINS, (INNER) JOINS

In this type, tables are connected using directly defined joins, as mentioned above there are different types of them. An example:
SELECT * FROM TABLE1 INNER JOIN TABLE2 ON .. LEFT JOIN TABLE3 ...;

* Correlations:  Relations between tables on a certain column. 
 
Example: SELECT * FROM TABLE1 AS A, TABLE2 AS B WHERE A.COLUMN_NAME = B.COLUMN_NAME;

* SubQueries: Relations between tables on a certain column. 

Example: SELECT * FROM TABLE1 AS A WHERE A.COLUMN_NAME IN (SELECT * FROM TABLE2 AS B WHERE B.COLUMN_NAME = VALUE)

------

Some queries combine more than one relation type. Example:

SELECT a.studentid, a.name, b.total_marks
FROM student a, marks b
WHERE a.studentid = b.studentid AND b.total_marks >
(SELECT total_marks
FROM marks
WHERE studentid =  'V002');

-------

In this part, I tried to catch as much as possible but unfortunately I was always limited by the very unlimited variety of SQL Queries that was very hard to capture, and the context-less Regular Expressions so it was quite hard to separate each query accurately. This what I tried to solve in the Parser.py in findJoins(...) function.
