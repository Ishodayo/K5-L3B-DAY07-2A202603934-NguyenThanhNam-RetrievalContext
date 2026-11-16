# Chấm context 0/1/2 — `baseline` / test

Đọc context cuối agent nhận được (các chunk dưới), so với đáp án chuẩn và evidence gold. **0** = không có evidence · **1** = có nhưng thiếu điều kiện hoặc nguồn · **2** = đủ evidence và nguồn.

## t01 — What does the built-in function divmod return?

**Đáp án chuẩn:** A tuple of two values: the quotient and the remainder.  
**Evidence gold:** p139: “The built-in function divmod takes two arguments and returns a tuple of two values, the quotient and remainder.”

**Context cuối:** 3 chunk, 3031 ký tự

<details><summary><code>B:thinkpython2:p139:001</code> (trang 139)</summary>

12.3 Tuples as return values Strictly speaking, a function can only return one value, but if the value is a tuple, the effect is the same as returning multiple values. For example, if you want to divide two integers and compute the quotient and remainder, it is inefficient to compute x//y and then x%y. It is better to compute them both at the same time. The built-in function divmod takes two arguments and returns a tuple of two values, the quotient and remainder. You can store the result as a tuple: >>> t = divmod(7, 3) >>> t (2, 1) Or use tuple assignment to store the elements separately: >>> quot, rem = divmod(7, 3) >>> quot 2 >>> rem 1 Here is an example of a function that returns a tuple: def min_max(t): return min(t), max(t) max and min are built-in functions that find the largest and smallest elements of a sequence. min_max computes both and returns a tuple of two values.

</details>

<details><summary><code>B:thinkpython2:p179:001</code> (trang 179)</summary>

16.3 Modifiers Sometimes it is useful for a function to modify the objects it gets as parameters. In that case, the changes are visible to the caller. Functions that work this way are called modifiers. increment, which adds a given number of seconds to a Time object, can be written naturally as a modifier. Here is a rough draft: def increment(time, seconds): time.second += seconds if time.second >= 60: time.second -= 60 time.minute += 1 if time.minute >= 60: time.minute -= 60 time.hour += 1 The first line performs the basic operation; the remainder deals with the special cases we saw before. Is this function correct? What happens if seconds is much greater than sixty? In that case, it is not enough to carry once; we have to keep doing it until time.second is less than sixty. One solution is to replace the if statements with while statements. That would make the function correct, but not very efficient. As an exercise, write a correct version of increment that doesn’t contain any loops.

</details>

<details><summary><code>B:thinkpython2:p160:001</code> (trang 160)</summary>

14.3 Format operator The argument of write has to be a string, so if we want to put other values in a file, we have to convert them to strings. The easiest way to do that is with str: >>> x = 52 >>> fout.write(str(x)) An alternative is to use the format operator, %. When applied to integers, % is the modulus operator. But when the first operand is a string, % is the format operator. The first operand is the format string, which contains one or more format sequences, which specify how the second operand is formatted. The result is a string. For example, the format sequence '%d' means that the second operand should be formatted as a decimal integer: >>> camels = 42 >>> '%d' % camels '42' The result is the string '42', which is not to be confused with the integer value 42. A format sequence can appear anywhere in the string, so you can embed a value in a sentence:

</details>

---

## t02 — What do you call a function that builds and returns a new object without changing any of the objects it was given?

**Đáp án chuẩn:** A pure function.  
**Evidence gold:** p178: “This is called a pure function because it does not modify any of the objects passed to it as arguments” · p182: “pure function: A function that does not modify any of the objects it receives as arguments.”

**Context cuối:** 5 chunk, 3616 ký tự

<details><summary><code>B:thinkpython2:p178:001</code> (trang 178)</summary>

16.2 Pure functions In the next few sections, we’ll write two functions that add time values. They demonstrate two kinds of functions: pure functions and modifiers. They also demonstrate a development plan I’ll call prototype and patch, which is a way of tackling a complex problem by starting with a simple prototype and incrementally dealing with the complications. Here is a simple prototype of add_time: def add_time(t1, t2): sum = Time() sum.hour = t1.hour + t2.hour sum.minute = t1.minute + t2.minute sum.second = t1.second + t2.second return sum The function creates a new Time object, initializes its attributes, and returns a reference to the new object. This is called a pure function because it does not modify any of the objects passed to it as arguments and it has no effect, like displaying a value or getting user input, other than returning a value. To test this function, I’ll create two Time objects: start contains the start time of a movie, like Monty Python and the Holy Grail, and duration contains the run time of the movie, which is one hour 35 minutes. add_time figures out when the movie will be done.

</details>

<details><summary><code>B:thinkpython2:p179:002</code> (trang 179)</summary>

Anything that can be done with modifiers can also be done with pure functions. In fact, some programming languages only allow pure functions. There is some evidence that programs that use pure functions are faster to develop and less error-prone than programs that use modifiers. But modifiers are convenient at times, and functional programs tend to be less efficient.

</details>

<details><summary><code>B:thinkpython2:p180:000</code> (trang 180)</summary>

In general, I recommend that you write pure functions whenever it is reasonable and resort to modifiers only if there is a compelling advantage. This approach might be called a functional programming style. As an exercise, write a “pure” version of increment that creates and returns a new Time object rather than modifying the parameter.

</details>

<details><summary><code>B:thinkpython2:p182:000</code> (trang 182)</summary>

16.6 Glossary prototype and patch: A development plan that involves writing a rough draft of a program, testing, and correcting errors as they are found. designed development: A development plan that involves high-level insight into the problem and more planning than incremental development or prototype development. pure function: A function that does not modify any of the objects it receives as arguments. Most pure functions are fruitful. modifier: A function that changes one or more of the objects it receives as arguments. Most modifiers are void; that is, they return None. functional programming style: A style of program design in which the majority of functions are pure. invariant: A condition that should always be true during the execution of a program. assert statement: A statement that checks a condition and raises an exception if it fails.

</details>

<details><summary><code>B:thinkpython2:p047:003</code> (trang 47)</summary>

3.13 Glossary function: A named sequence of statements that performs some useful operation. Functions may or may not take arguments and may or may not produce a result. function definition: A statement that creates a new function, specifying its name, parameters, and the statements it contains. function object: A value created by a function definition. The name of the function is a variable that refers to a function object. header: The first line of a function definition.

</details>

---

## t03 — When an integer is the left operand and a Time object is on the right of +, which special method makes the addition work?

**Đáp án chuẩn:** __radd__ ("right-side add"), invoked when the Time object appears on the right side of the + operator.  
**Evidence gold:** p189: “the special method __radd__, which stands for “right-side add”. This method is invoked when a Time object appears on the right side of the + operator.”

**Context cuối:** 3 chunk, 1895 ký tự

<details><summary><code>B:thinkpython2:p189:000</code> (trang 189)</summary>

>>> start = Time(9, 45) >>> duration = Time(1, 35) >>> print(start + duration) 11:20:00 >>> print(start + 1337) 10:07:17 Unfortunately, this implementation of addition is not commutative. If the integer is the first operand, you get >>> print(1337 + start) TypeError: unsupported operand type(s) for +: 'int' and 'instance' The problem is, instead of asking the Time object to add an integer, Python is asking an integer to add a Time object, and it doesn’t know how. But there is a clever solution for this problem: the special method __radd__, which stands for “right-side add”. This method is invoked when a Time object appears on the right side of the + operator. Here’s the definition: # inside class Time: def __radd__(self, other): return self.__add__(other) And here’s how it’s used: >>> print(1337 + start) 10:07:17 As an exercise, write an add method for Points that works with either a Point object or a tuple: • If the second operand is a Point, the method should return a new Point whose x coordinate is the sum of the x coordinates of the operands, and likewise for the y coordinates.

</details>

<details><summary><code>B:thinkpython2:p154:001</code> (trang 154)</summary>

13.9 Data structures Using Markov analysis to generate random text is fun, but there is also a point to this exercise: data structure selection. In your solution to the previous exercises, you had to choose: • How to represent the prefixes. • How to represent the collection of possible suffixes.

</details>

<details><summary><code>B:thinkpython2:p061:000</code> (trang 61)</summary>

Chapter 5 Conditionals and recursion The main topic of this chapter is the if statement, which executes different code depending on the state of the program. But first I want to introduce two new operators: floor division and modulus.

</details>

---

## t04 — In the Inheritance chapter, what are class attributes?

**Đáp án chuẩn:** Variables defined inside a class but outside of any method; they are associated with the class object rather than with an instance.  
**Evidence gold:** p194: “which are defined inside a class but outside of any method, are called class attributes because they are associated with the class object” · p202: “class attribute: An attribute associated with a class object. Class attributes are defined inside a class definition but outside any method.”

**Context cuối:** 3 chunk, 3032 ký tự

<details><summary><code>B:thinkpython2:p202:001</code> (trang 202)</summary>

18.11 Glossary encode: To represent one set of values using another set of values by constructing a mapping between them. class attribute: An attribute associated with a class object. Class attributes are defined inside a class definition but outside any method. instance attribute: An attribute associated with an instance of a class. veneer: A method or function that provides a different interface to another function without doing much computation. inheritance: The ability to define a new class that is a modified version of a previously defined class. parent class: The class from which a child class inherits. child class: A new class created by inheriting from an existing class; also called a “subclass”. IS-A relationship: A relationship between a child class and its parent class. HAS-A relationship: A relationship between two classes where instances of one class contain references to instances of the other. dependency: A relationship between two classes where instances of one class use instances of the other class, but do not store them as attributes.

</details>

<details><summary><code>B:thinkpython2:p194:001</code> (trang 194)</summary>

18.2 Class attributes In order to print Card objects in a way that people can easily read, we need a mapping from the integer codes to the corresponding ranks and suits. A natural way to do that is with lists of strings. We assign these lists to class attributes: # inside class Card: suit_names = ['Clubs', 'Diamonds', 'Hearts', 'Spades'] rank_names = [None, 'Ace', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King'] def __str__(self): return '%s of %s' % (Card.rank_names[self.rank], Card.suit_names[self.suit]) Variables like suit_names and rank_names, which are defined inside a class but outside of any method, are called class attributes because they are associated with the class object Card. This term distinguishes them from variables like suit and rank, which are called instance attributes because they are associated with a particular instance. Both kinds of attribute are accessed using dot notation. For example, in __str__, self is a Card object, and self.rank is its rank. Similarly, Card is a class object, and Card.rank_names is a list of strings associated with the class.

</details>

<details><summary><code>B:thinkpython2:p193:000</code> (trang 193)</summary>

Chapter 18 Inheritance The language feature most often associated with object-oriented programming is inheritance. Inheritance is the ability to define a new class that is a modified version of an existing class. In this chapter I demonstrate inheritance using classes that represent playing cards, decks of cards, and poker hands. If you don’t play poker, you can read about it at http://en.wikipedia.org/wiki/Poker, but you don’t have to; I’ll tell you what you need to know for the exercises. Code examples from this chapter are available from https://thinkpython.com/code/ Card.py.

</details>

---

## t05 — In the Analysis of Algorithms appendix, what limitation does the hashtable implementation have regarding keys?

**Đáp án chuẩn:** It only works with hashable keys; mutable types like lists and dictionaries are unhashable.  
**Evidence gold:** p229: “A limitation of this implementation is that it only works with hashable keys. Mutable types like lists and dictionaries are unhashable.”

**Context cuối:** 3 chunk, 3314 ký tự

<details><summary><code>B:thinkpython2:p231:000</code> (trang 231)</summary>

Figure B.1: The cost of a hashtable add. The extra work of rehashing appears as a sequence of increasingly tall towers with increasing space between them. Now if you knock over the towers, spreading the cost of resizing over all adds, you can see graphically that the total cost after n adds is 2n − 2. An important feature of this algorithm is that when we resize the HashTable it grows geometrically; that is, we multiply the size by a constant. If you increase the size arithmetically—adding a fixed number each time—the average time per add is linear. You can download my implementation of HashMap from https://thinkpython.com/ code/Map.py, but remember that there is no reason to use it; if you want a map, just use a Python dictionary.

</details>

<details><summary><code>B:thinkpython2:p228:000</code> (trang 228)</summary>

B.4 Hashtables To explain how hashtables work and why their performance is so good, I start with a simple implementation of a map and gradually improve it until it’s a hashtable. I use Python to demonstrate these implementations, but in real life you wouldn’t write code like this in Python; you would just use a dictionary! So for the rest of this chapter, you have to imagine that dictionaries don’t exist and you want to implement a data structure that maps from keys to values. The operations you have to implement are: add(k, v): Add a new item that maps from key k to value v. With a Python dictionary, d, this operation is written d[k] = v. get(k): Look up and return the value that corresponds to key k. With a Python dictionary, d, this operation is written d[k] or d.get(k). For now, I assume that each key only appears once. The simplest implementation of this interface uses a list of tuples, where each tuple is a key-value pair. class LinearMap: def __init__(self): self.items = [] def add(self, k, v): self.items.append((k, v)) def get(self, k): for key, val in self.items: if key == k:

</details>

<details><summary><code>B:thinkpython2:p230:001</code> (trang 230)</summary>

Rehashing is necessary because changing the number of LinearMaps changes the denominator of the modulus operator in find_map. That means that some objects that used to hash into the same LinearMap will get split up (which is what we wanted, right?). Rehashing is linear, so resize is linear, which might seem bad, since I promised that add would be constant time. But remember that we don’t have to resize every time, so add is usually constant time and only occasionally linear. The total amount of work to run add n times is proportional to n, so the average time of each add is constant time! To see how this works, think about starting with an empty HashTable and adding a sequence of items. We start with 2 LinearMaps, so the first 2 adds are fast (no resizing required). Let’s say that they take one unit of work each. The next add requires a resize, so we have to rehash the first two items (let’s call that 2 more units of work) and then add the third item (one more unit). Adding the next item costs 1 unit, so the total so far is 6 units of work for 4 items. The next add costs 5 units, but the next three are only one unit each, so the total is 14 units for the first 8 adds.

</details>

---

## t06 — How does a generator expression differ from a list comprehension in when it produces its values?

**Đáp án chuẩn:** It does not compute all values at once; it waits to be asked (lazy evaluation via next or a for loop).  
**Evidence gold:** p207: “unlike a list comprehension, it does not compute the values all at once; it waits to be asked.”

**Context cuối:** 3 chunk, 2944 ký tự

<details><summary><code>B:thinkpython2:p207:001</code> (trang 207)</summary>

19.3 Generator expressions Generator expressions are similar to list comprehensions, but with parentheses instead of square brackets: >>> g = (x**2 for x in range(5)) >>> g <generator object <genexpr> at 0x7f4c45a786c0> The result is a generator object that knows how to iterate through a sequence of values. But unlike a list comprehension, it does not compute the values all at once; it waits to be asked. The built-in function next gets the next value from the generator: >>> next(g) 0 >>> next(g) 1 When you get to the end of the sequence, next raises a StopIteration exception. You can also use a for loop to iterate through the values: >>> for val in g: ... print(val) 4 9 16 The generator object keeps track of where it is in the sequence, so the for loop picks up where next left off. Once the generator is exhausted, it continues to raise StopIteration: >>> next(g) StopIteration Generator expressions are often used with functions like sum, max, and min: >>> sum(x**2 for x in range(5)) 30 19.4 any and all Python provides a built-in function, any, that takes a sequence of boolean values and returns True if any of the values are True. It works on lists:

</details>

<details><summary><code>B:thinkpython2:p213:001</code> (trang 213)</summary>

19.10 Glossary conditional expression: An expression that has one of two values, depending on a condition. list comprehension: An expression with a for loop in square brackets that yields a new list. generator expression: An expression with a for loop in parentheses that yields a generator object. multiset: A mathematical entity that represents a mapping between the elements of a set and the number of times they appear. factory: A function, usually passed as a parameter, used to create objects.

</details>

<details><summary><code>B:thinkpython2:p206:001</code> (trang 206)</summary>

19.2 List comprehensions In Section 10.7 we saw the map and filter patterns. For example, this function takes a list of strings, maps the string method capitalize to the elements, and returns a new list of strings: def capitalize_all(t): res = [] for s in t: res.append(s.capitalize()) return res We can write this more concisely using a list comprehension: def capitalize_all(t): return [s.capitalize() for s in t] The bracket operators indicate that we are constructing a new list. The expression inside the brackets specifies the elements of the list, and the for clause indicates what sequence we are traversing. The syntax of a list comprehension is a little awkward because the loop variable, s in this example, appears in the expression before we get to the definition. List comprehensions can also be used for filtering. For example, this function selects only the elements of t that are upper case, and returns a new list: def only_upper(t): res = [] for s in t: if s.isupper(): res.append(s) return res

</details>

---
