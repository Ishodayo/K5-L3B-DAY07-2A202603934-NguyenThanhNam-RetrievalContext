# Bảng chấm tay — `baseline` / test

Đọc từng câu, đối chiếu câu trả lời với đáp án chuẩn và với **text của từng chunk được trích**, rồi điền file CSV cùng tên. Thang điểm: BENCHMARK.md §3. Chunk ID có dạng `B:thinkpython2:pTTT:NNN` (TTT = trang PDF; trang in = trang PDF − 22).

## t01 — có đáp án — status `answered`

**Câu hỏi:** What does the built-in function divmod return?

**Đáp án chuẩn:** A tuple of two values: the quotient and the remainder.  
**Trang gold:** 139

**Query agent đã tìm:** `divmod`

**Câu trả lời của agent:**

> The built-in function `divmod` takes two arguments and returns a tuple of two values, the quotient and remainder [B:thinkpython2:p139:001].

<details><summary>Citation 1: <code>B:thinkpython2:p139:001</code> (trang 139)</summary>

12.3 Tuples as return values Strictly speaking, a function can only return one value, but if the value is a tuple, the effect is the same as returning multiple values. For example, if you want to divide two integers and compute the quotient and remainder, it is inefficient to compute x//y and then x%y. It is better to compute them both at the same time. The built-in function divmod takes two arguments and returns a tuple of two values, the quotient and remainder. You can store the result as a tuple: >>> t = divmod(7, 3) >>> t (2, 1) Or use tuple assignment to store the elements separately: >>> quot, rem = divmod(7, 3) >>> quot 2 >>> rem 1 Here is an example of a function that returns a tuple: def min_max(t): return min(t), max(t) max and min are built-in functions that find the largest and smallest elements of a sequence. min_max computes both and returns a tuple of two values.

</details>

---

## t02 — có đáp án — status `answered`

**Câu hỏi:** What do you call a function that builds and returns a new object without changing any of the objects it was given?

**Đáp án chuẩn:** A pure function.  
**Trang gold:** 178, 182

**Query agent đã tìm:** `pure function modifier builds returns new object`; `pure function glossary`

**Câu trả lời của agent:**

> A function that creates and returns a new object without modifying any of the objects passed to it as arguments is called a pure function [B:thinkpython2:p178:001][B:thinkpython2:p182:000]. In addition to not modifying its arguments, a pure function has no side effects, such as displaying a value or getting user input, other than returning a value [B:thinkpython2:p178:001].

<details><summary>Citation 1: <code>B:thinkpython2:p178:001</code> (trang 178)</summary>

16.2 Pure functions In the next few sections, we’ll write two functions that add time values. They demonstrate two kinds of functions: pure functions and modifiers. They also demonstrate a development plan I’ll call prototype and patch, which is a way of tackling a complex problem by starting with a simple prototype and incrementally dealing with the complications. Here is a simple prototype of add_time: def add_time(t1, t2): sum = Time() sum.hour = t1.hour + t2.hour sum.minute = t1.minute + t2.minute sum.second = t1.second + t2.second return sum The function creates a new Time object, initializes its attributes, and returns a reference to the new object. This is called a pure function because it does not modify any of the objects passed to it as arguments and it has no effect, like displaying a value or getting user input, other than returning a value. To test this function, I’ll create two Time objects: start contains the start time of a movie, like Monty Python and the Holy Grail, and duration contains the run time of the movie, which is one hour 35 minutes. add_time figures out when the movie will be done.

</details>

<details><summary>Citation 2: <code>B:thinkpython2:p182:000</code> (trang 182)</summary>

16.6 Glossary prototype and patch: A development plan that involves writing a rough draft of a program, testing, and correcting errors as they are found. designed development: A development plan that involves high-level insight into the problem and more planning than incremental development or prototype development. pure function: A function that does not modify any of the objects it receives as arguments. Most pure functions are fruitful. modifier: A function that changes one or more of the objects it receives as arguments. Most modifiers are void; that is, they return None. functional programming style: A style of program design in which the majority of functions are pure. invariant: A condition that should always be true during the execution of a program. assert statement: A statement that checks a condition and raises an exception if it fails.

</details>

---

## t03 — có đáp án — status `answered`

**Câu hỏi:** When an integer is the left operand and a Time object is on the right of +, which special method makes the addition work?

**Đáp án chuẩn:** __radd__ ("right-side add"), invoked when the Time object appears on the right side of the + operator.  
**Trang gold:** 189

**Query agent đã tìm:** `__radd__`

**Câu trả lời của agent:**

> The special method `__radd__`, which stands for "right-side add", makes the addition work when a `Time` object appears on the right side of the `+` operator [B:thinkpython2:p189:000].

<details><summary>Citation 1: <code>B:thinkpython2:p189:000</code> (trang 189)</summary>

>>> start = Time(9, 45) >>> duration = Time(1, 35) >>> print(start + duration) 11:20:00 >>> print(start + 1337) 10:07:17 Unfortunately, this implementation of addition is not commutative. If the integer is the first operand, you get >>> print(1337 + start) TypeError: unsupported operand type(s) for +: 'int' and 'instance' The problem is, instead of asking the Time object to add an integer, Python is asking an integer to add a Time object, and it doesn’t know how. But there is a clever solution for this problem: the special method __radd__, which stands for “right-side add”. This method is invoked when a Time object appears on the right side of the + operator. Here’s the definition: # inside class Time: def __radd__(self, other): return self.__add__(other) And here’s how it’s used: >>> print(1337 + start) 10:07:17 As an exercise, write an add method for Points that works with either a Point object or a tuple: • If the second operand is a Point, the method should return a new Point whose x coordinate is the sum of the x coordinates of the operands, and likewise for the y coordinates.

</details>

---

## t04 — có đáp án — status `answered`

**Câu hỏi:** In the Inheritance chapter, what are class attributes?

**Đáp án chuẩn:** Variables defined inside a class but outside of any method; they are associated with the class object rather than with an instance.  
**Trang gold:** 194, 202

**Query agent đã tìm:** `class attribute inheritance`

**Câu trả lời của agent:**

> Class attributes are attributes associated with a class object [B:thinkpython2:p202:001]. They are defined inside a class definition but outside of any method [B:thinkpython2:p194:001] [B:thinkpython2:p202:001]. This distinguishes them from instance attributes, which are associated with a particular instance [B:thinkpython2:p194:001].

<details><summary>Citation 1: <code>B:thinkpython2:p202:001</code> (trang 202)</summary>

18.11 Glossary encode: To represent one set of values using another set of values by constructing a mapping between them. class attribute: An attribute associated with a class object. Class attributes are defined inside a class definition but outside any method. instance attribute: An attribute associated with an instance of a class. veneer: A method or function that provides a different interface to another function without doing much computation. inheritance: The ability to define a new class that is a modified version of a previously defined class. parent class: The class from which a child class inherits. child class: A new class created by inheriting from an existing class; also called a “subclass”. IS-A relationship: A relationship between a child class and its parent class. HAS-A relationship: A relationship between two classes where instances of one class contain references to instances of the other. dependency: A relationship between two classes where instances of one class use instances of the other class, but do not store them as attributes.

</details>

<details><summary>Citation 2: <code>B:thinkpython2:p194:001</code> (trang 194)</summary>

18.2 Class attributes In order to print Card objects in a way that people can easily read, we need a mapping from the integer codes to the corresponding ranks and suits. A natural way to do that is with lists of strings. We assign these lists to class attributes: # inside class Card: suit_names = ['Clubs', 'Diamonds', 'Hearts', 'Spades'] rank_names = [None, 'Ace', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King'] def __str__(self): return '%s of %s' % (Card.rank_names[self.rank], Card.suit_names[self.suit]) Variables like suit_names and rank_names, which are defined inside a class but outside of any method, are called class attributes because they are associated with the class object Card. This term distinguishes them from variables like suit and rank, which are called instance attributes because they are associated with a particular instance. Both kinds of attribute are accessed using dot notation. For example, in __str__, self is a Card object, and self.rank is its rank. Similarly, Card is a class object, and Card.rank_names is a list of strings associated with the class.

</details>

---

## t05 — có đáp án — status `abstain`

**Câu hỏi:** In the Analysis of Algorithms appendix, what limitation does the hashtable implementation have regarding keys?

**Đáp án chuẩn:** It only works with hashable keys; mutable types like lists and dictionaries are unhashable.  
**Trang gold:** 229

**Query agent đã tìm:** `hashtable key limitation`; `Hashtable limitation key`; `hashable keys hashtable`

**Câu trả lời của agent:**

> INSUFFICIENT_EVIDENCE: The passages do not contain details on the limitation of the hashtable implementation regarding keys.

---

## t06 — có đáp án — status `answered`

**Câu hỏi:** How does a generator expression differ from a list comprehension in when it produces its values?

**Đáp án chuẩn:** It does not compute all values at once; it waits to be asked (lazy evaluation via next or a for loop).  
**Trang gold:** 207

**Query agent đã tìm:** `generator expression list comprehension`

**Câu trả lời của agent:**

> Unlike a list comprehension, a generator expression does not compute its values all at once; instead, it waits to be asked [B:thinkpython2:p207:001].

<details><summary>Citation 1: <code>B:thinkpython2:p207:001</code> (trang 207)</summary>

19.3 Generator expressions Generator expressions are similar to list comprehensions, but with parentheses instead of square brackets: >>> g = (x**2 for x in range(5)) >>> g <generator object <genexpr> at 0x7f4c45a786c0> The result is a generator object that knows how to iterate through a sequence of values. But unlike a list comprehension, it does not compute the values all at once; it waits to be asked. The built-in function next gets the next value from the generator: >>> next(g) 0 >>> next(g) 1 When you get to the end of the sequence, next raises a StopIteration exception. You can also use a for loop to iterate through the values: >>> for val in g: ... print(val) 4 9 16 The generator object keeps track of where it is in the sequence, so the for loop picks up where next left off. Once the generator is exhausted, it continues to raise StopIteration: >>> next(g) StopIteration Generator expressions are often used with functions like sum, max, and min: >>> sum(x**2 for x in range(5)) 30 19.4 any and all Python provides a built-in function, any, that takes a sequence of boolean values and returns True if any of the values are True. It works on lists:

</details>

---

## tu1 — THIẾU evidence — status `abstain`

**Câu hỏi:** How do async and await let you run several coroutines concurrently?

**Vì sao thiếu evidence:** Chapter 19 covers generator expressions, but the book has no asyncio, async/await, coroutines or concurrency.

**Query agent đã tìm:** `async await coroutine`; `concurrent`; `async`

**Câu trả lời của agent:**

> INSUFFICIENT_EVIDENCE: information about async, await, and running coroutines concurrently.

---

## tu2 — THIẾU evidence — status `abstain`

**Câu hỏi:** In a child class, how do you use super() to call the parent class's __init__ method?

**Vì sao thiếu evidence:** Chapter 18 (Inheritance) explains parent/child classes and overriding, but super() is never used or mentioned.

**Query agent đã tìm:** `super __init__`; `super()`; `super`

**Câu trả lời của agent:**

> INSUFFICIENT_EVIDENCE: How to use super() to call a parent class's __init__ method.

---
