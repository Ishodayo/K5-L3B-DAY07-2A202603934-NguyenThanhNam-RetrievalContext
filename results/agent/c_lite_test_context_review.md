# Chấm context 0/1/2 — `c_lite` / test

Đọc context cuối agent nhận được (các chunk dưới), so với đáp án chuẩn và evidence gold. **0** = không có evidence · **1** = có nhưng thiếu điều kiện hoặc nguồn · **2** = đủ evidence và nguồn.

## t01 — What does the built-in function divmod return?

**Đáp án chuẩn:** A tuple of two values: the quotient and the remainder.  
**Evidence gold:** p139: “The built-in function divmod takes two arguments and returns a tuple of two values, the quotient and remainder.”

**Context cuối:** 5 chunk, 4040 ký tự

<details><summary><code>B:thinkpython2:p139:001</code> (trang 139)</summary>

12.3 Tuples as return values Strictly speaking, a function can only return one value, but if the value is a tuple, the effect is the same as returning multiple values. For example, if you want to divide two integers and compute the quotient and remainder, it is inefficient to compute x//y and then x%y. It is better to compute them both at the same time. The built-in function divmod takes two arguments and returns a tuple of two values, the quotient and remainder. You can store the result as a tuple: >>> t = divmod(7, 3) >>> t (2, 1) Or use tuple assignment to store the elements separately: >>> quot, rem = divmod(7, 3) >>> quot 2 >>> rem 1 Here is an example of a function that returns a tuple: def min_max(t): return min(t), max(t) max and min are built-in functions that find the largest and smallest elements of a sequence. min_max computes both and returns a tuple of two values.

</details>

<details><summary><code>B:thinkpython2:p179:001</code> (trang 179)</summary>

16.3 Modifiers Sometimes it is useful for a function to modify the objects it gets as parameters. In that case, the changes are visible to the caller. Functions that work this way are called modifiers. increment, which adds a given number of seconds to a Time object, can be written naturally as a modifier. Here is a rough draft: def increment(time, seconds): time.second += seconds if time.second >= 60: time.second -= 60 time.minute += 1 if time.minute >= 60: time.minute -= 60 time.hour += 1 The first line performs the basic operation; the remainder deals with the special cases we saw before. Is this function correct? What happens if seconds is much greater than sixty? In that case, it is not enough to carry once; we have to keep doing it until time.second is less than sixty. One solution is to replace the if statements with while statements. That would make the function correct, but not very efficient. As an exercise, write a correct version of increment that doesn’t contain any loops.

</details>

<details><summary><code>B:thinkpython2:p179:002</code> (trang 179)</summary>

Anything that can be done with modifiers can also be done with pure functions. In fact, some programming languages only allow pure functions. There is some evidence that programs that use pure functions are faster to develop and less error-prone than programs that use modifiers. But modifiers are convenient at times, and functional programs tend to be less efficient.

</details>

<details><summary><code>B:thinkpython2:p160:001</code> (trang 160)</summary>

14.3 Format operator The argument of write has to be a string, so if we want to put other values in a file, we have to convert them to strings. The easiest way to do that is with str: >>> x = 52 >>> fout.write(str(x)) An alternative is to use the format operator, %. When applied to integers, % is the modulus operator. But when the first operand is a string, % is the format operator. The first operand is the format string, which contains one or more format sequences, which specify how the second operand is formatted. The result is a string. For example, the format sequence '%d' means that the second operand should be formatted as a decimal integer: >>> camels = 42 >>> '%d' % camels '42' The result is the string '42', which is not to be confused with the integer value 42. A format sequence can appear anywhere in the string, so you can embed a value in a sentence:

</details>

<details><summary><code>B:thinkpython2:p160:002</code> (trang 160)</summary>

>>> 'I have spotted %d camels.' % camels 'I have spotted 42 camels.' If there is more than one format sequence in the string, the second argument has to be a tuple. Each format sequence is matched with an element of the tuple, in order. The following example uses '%d' to format an integer, '%g' to format a floating-point number, and '%s' to format a string: >>> 'In %d years I have spotted %g %s.' % (3, 0.1, 'camels') 'In 3 years I have spotted 0.1 camels.'

</details>

---

## t02 — What do you call a function that builds and returns a new object without changing any of the objects it was given?

**Đáp án chuẩn:** A pure function.  
**Evidence gold:** p178: “This is called a pure function because it does not modify any of the objects passed to it as arguments” · p182: “pure function: A function that does not modify any of the objects it receives as arguments.”

**Context cuối:** 10 chunk, 9048 ký tự

<details><summary><code>B:thinkpython2:p174:000</code> (trang 174)</summary>

y 0.0x 0.0 width height 100.0 corner 200.0 box 100.0 200.0 width height corner box2 Figure 15.3: Object diagram. >>> p1 == p2 False The is operator indicates that p1 and p2 are not the same object, which is what we expected. But you might have expected == to yield True because these points contain the same data. In that case, you will be disappointed to learn that for instances, the default behavior of the == operator is the same as the is operator; it checks object identity, not object equivalence. That’s because for programmer-defined types, Python doesn’t know what should be considered equivalent. At least, not yet. If you use copy.copy to duplicate a Rectangle, you will find that it copies the Rectangle object but not the embedded Point. >>> box2 = copy.copy(box) >>> box2 is box False >>> box2.corner is box.corner True Figure 15.3 shows what the object diagram looks like. This operation is called a shallow copy because it copies the object and any references it contains, but not the embedded objects.

</details>

<details><summary><code>B:thinkpython2:p174:001</code> (trang 174)</summary>

For most applications, this is not what you want. In this example, invoking grow_rectangle on one of the Rectangles would not affect the other, but invoking move_rectangle on either would affect both! This behavior is confusing and error-prone. Fortunately, the copy module provides a method named deepcopy that copies not only the object but also the objects it refers to, and the objects they refer to, and so on. You will not be surprised to learn that this operation is called a deep copy. >>> box3 = copy.deepcopy(box) >>> box3 is box False >>> box3.corner is box.corner False box3 and box are completely separate objects. As an exercise, write a version of move_rectangle that creates and returns a new Rectangle instead of modifying the old one.

</details>

<details><summary><code>B:thinkpython2:p119:001</code> (trang 119)</summary>

10.12 List arguments When you pass a list to a function, the function gets a reference to the list. If the function modifies the list, the caller sees the change. For example, delete_head removes the first element from a list: def delete_head(t): del t[0] Here’s how it is used: >>> letters = ['a', 'b', 'c'] >>> delete_head(letters) >>> letters ['b', 'c'] The parameter t and the variable letters are aliases for the same object. The stack diagram looks like Figure 10.5. Since the list is shared by two frames, I drew it between them. It is important to distinguish between operations that modify lists and operations that create new lists. For example, the append method modifies a list, but the + operator creates a new list. Here’s an example using append: >>> t1 = [1, 2] >>> t2 = t1.append(3) >>> t1 [1, 2, 3] >>> t2 None

</details>

<details><summary><code>B:thinkpython2:p120:000</code> (trang 120)</summary>

The return value from append is None. Here’s an example using the + operator: >>> t3 = t1 + [4] >>> t1 [1, 2, 3] >>> t3 [1, 2, 3, 4] The result of the operator is a new list, and the original list is unchanged. This difference is important when you write functions that are supposed to modify lists. For example, this function does not delete the head of a list: def bad_delete_head(t): t = t[1:] # WRONG! The slice operator creates a new list and the assignment makes t refer to it, but that doesn’t affect the caller. >>> t4 = [1, 2, 3] >>> bad_delete_head(t4) >>> t4 [1, 2, 3] At the beginning of bad_delete_head, t and t4 refer to the same list. At the end, t refers to a new list, but t4 still refers to the original, unmodified list. An alternative is to write a function that creates and returns a new list. For example, tail returns all but the first element of a list: def tail(t): return t[1:] This function leaves the original list unmodified. Here’s how it is used: >>> letters = ['a', 'b', 'c'] >>> rest = tail(letters) >>> rest ['b', 'c']

</details>

<details><summary><code>B:thinkpython2:p173:000</code> (trang 173)</summary>

15.5 Objects are mutable You can change the state of an object by making an assignment to one of its attributes. For example, to change the size of a rectangle without changing its position, you can modify the values of width and height: box.width = box.width + 50 box.height = box.height + 100 You can also write functions that modify objects. For example, grow_rectangle takes a Rectangle object and two numbers, dwidth and dheight, and adds the numbers to the width and height of the rectangle: def grow_rectangle(rect, dwidth, dheight): rect.width += dwidth rect.height += dheight Here is an example that demonstrates the effect: >>> box.width, box.height (150.0, 300.0) >>> grow_rectangle(box, 50, 100) >>> box.width, box.height (200.0, 400.0) Inside the function, rect is an alias for box, so when the function modifies rect, box changes. As an exercise, write a function named move_rectangle that takes a Rectangle and two numbers named dx and dy. It should change the location of the rectangle by adding dx to the x coordinate of corner and adding dy to the y coordinate of corner.

</details>

<details><summary><code>B:thinkpython2:p179:001</code> (trang 179)</summary>

16.3 Modifiers Sometimes it is useful for a function to modify the objects it gets as parameters. In that case, the changes are visible to the caller. Functions that work this way are called modifiers. increment, which adds a given number of seconds to a Time object, can be written naturally as a modifier. Here is a rough draft: def increment(time, seconds): time.second += seconds if time.second >= 60: time.second -= 60 time.minute += 1 if time.minute >= 60: time.minute -= 60 time.hour += 1 The first line performs the basic operation; the remainder deals with the special cases we saw before. Is this function correct? What happens if seconds is much greater than sixty? In that case, it is not enough to carry once; we have to keep doing it until time.second is less than sixty. One solution is to replace the if statements with while statements. That would make the function correct, but not very efficient. As an exercise, write a correct version of increment that doesn’t contain any loops.

</details>

<details><summary><code>B:thinkpython2:p179:002</code> (trang 179)</summary>

Anything that can be done with modifiers can also be done with pure functions. In fact, some programming languages only allow pure functions. There is some evidence that programs that use pure functions are faster to develop and less error-prone than programs that use modifiers. But modifiers are convenient at times, and functional programs tend to be less efficient.

</details>

<details><summary><code>B:thinkpython2:p180:000</code> (trang 180)</summary>

In general, I recommend that you write pure functions whenever it is reasonable and resort to modifiers only if there is a compelling advantage. This approach might be called a functional programming style. As an exercise, write a “pure” version of increment that creates and returns a new Time object rather than modifying the parameter.

</details>

<details><summary><code>B:thinkpython2:p178:001</code> (trang 178)</summary>

16.2 Pure functions In the next few sections, we’ll write two functions that add time values. They demonstrate two kinds of functions: pure functions and modifiers. They also demonstrate a development plan I’ll call prototype and patch, which is a way of tackling a complex problem by starting with a simple prototype and incrementally dealing with the complications. Here is a simple prototype of add_time: def add_time(t1, t2): sum = Time() sum.hour = t1.hour + t2.hour sum.minute = t1.minute + t2.minute sum.second = t1.second + t2.second return sum The function creates a new Time object, initializes its attributes, and returns a reference to the new object. This is called a pure function because it does not modify any of the objects passed to it as arguments and it has no effect, like displaying a value or getting user input, other than returning a value. To test this function, I’ll create two Time objects: start contains the start time of a movie, like Monty Python and the Holy Grail, and duration contains the run time of the movie, which is one hour 35 minutes. add_time figures out when the movie will be done.

</details>

<details><summary><code>B:thinkpython2:p178:002</code> (trang 178)</summary>

>>> start = Time() >>> start.hour = 9 >>> start.minute = 45 >>> start.second = 0 >>> duration = Time() >>> duration.hour = 1 >>> duration.minute = 35 >>> duration.second = 0 >>> done = add_time(start, duration) >>> print_time(done) 10:80:00 The result, 10:80:00 might not be what you were hoping for. The problem is that this function does not deal with cases where the number of seconds or minutes adds up to more than sixty. When that happens, we have to “carry” the extra seconds into the minute column or the extra minutes into the hour column. Here’s an improved version:

</details>

---

## t03 — When an integer is the left operand and a Time object is on the right of +, which special method makes the addition work?

**Đáp án chuẩn:** __radd__ ("right-side add"), invoked when the Time object appears on the right side of the + operator.  
**Evidence gold:** p189: “the special method __radd__, which stands for “right-side add”. This method is invoked when a Time object appears on the right side of the + operator.”

**Context cuối:** 5 chunk, 3825 ký tự

<details><summary><code>B:thinkpython2:p188:001</code> (trang 188)</summary>

17.8 Type-based dispatch In the previous section we added two Time objects, but you also might want to add an integer to a Time object. The following is a version of __add__ that checks the type of other and invokes either add_time or increment: # inside class Time: def __add__(self, other): if isinstance(other, Time): return self.add_time(other) else: return self.increment(other) def add_time(self, other): seconds = self.time_to_int() + other.time_to_int() return int_to_time(seconds) def increment(self, seconds): seconds += self.time_to_int() return int_to_time(seconds) The built-in function isinstance takes a value and a class object, and returns True if the value is an instance of the class. If other is a Time object, __add__ invokes add_time. Otherwise it assumes that the parameter is a number and invokes increment. This operation is called a type-based dispatch because it dispatches the computation to different methods based on the type of the arguments. Here are examples that use the + operator with different types:

</details>

<details><summary><code>B:thinkpython2:p189:000</code> (trang 189)</summary>

>>> start = Time(9, 45) >>> duration = Time(1, 35) >>> print(start + duration) 11:20:00 >>> print(start + 1337) 10:07:17 Unfortunately, this implementation of addition is not commutative. If the integer is the first operand, you get >>> print(1337 + start) TypeError: unsupported operand type(s) for +: 'int' and 'instance' The problem is, instead of asking the Time object to add an integer, Python is asking an integer to add a Time object, and it doesn’t know how. But there is a clever solution for this problem: the special method __radd__, which stands for “right-side add”. This method is invoked when a Time object appears on the right side of the + operator. Here’s the definition: # inside class Time: def __radd__(self, other): return self.__add__(other) And here’s how it’s used: >>> print(1337 + start) 10:07:17 As an exercise, write an add method for Points that works with either a Point object or a tuple: • If the second operand is a Point, the method should return a new Point whose x coordinate is the sum of the x coordinates of the operands, and likewise for the y coordinates.

</details>

<details><summary><code>B:thinkpython2:p189:001</code> (trang 189)</summary>

• If the second operand is a tuple, the method should add the first element of the tuple to the x coordinate and the second element to the y coordinate, and return a new Point with the result.

</details>

<details><summary><code>B:thinkpython2:p187:002</code> (trang 187)</summary>

17.7 Operator overloading By defining other special methods, you can specify the behavior of operators on programmer-defined types. For example, if you define a method named __add__ for the Time class, you can use the + operator on Time objects. Here is what the definition might look like:

</details>

<details><summary><code>B:thinkpython2:p188:000</code> (trang 188)</summary>

# inside class Time: def __add__(self, other): seconds = self.time_to_int() + other.time_to_int() return int_to_time(seconds) And here is how you could use it: >>> start = Time(9, 45) >>> duration = Time(1, 35) >>> print(start + duration) 11:20:00 When you apply the + operator to Time objects, Python invokes __add__. When you print the result, Python invokes __str__. So there is a lot happening behind the scenes! Changing the behavior of an operator so that it works with programmer-defined types is called operator overloading. For every operator in Python there is a corresponding special method, like __add__. For more details, see http://docs.python.org/3/reference/ datamodel.html#specialnames. As an exercise, write an add method for the Point class.

</details>

---

## t04 — In the Inheritance chapter, what are class attributes?

**Đáp án chuẩn:** Variables defined inside a class but outside of any method; they are associated with the class object rather than with an instance.  
**Evidence gold:** p194: “which are defined inside a class but outside of any method, are called class attributes because they are associated with the class object” · p202: “class attribute: An attribute associated with a class object. Class attributes are defined inside a class definition but outside any method.”

**Context cuối:** 5 chunk, 4668 ký tự

<details><summary><code>B:thinkpython2:p202:001</code> (trang 202)</summary>

18.11 Glossary encode: To represent one set of values using another set of values by constructing a mapping between them. class attribute: An attribute associated with a class object. Class attributes are defined inside a class definition but outside any method. instance attribute: An attribute associated with an instance of a class. veneer: A method or function that provides a different interface to another function without doing much computation. inheritance: The ability to define a new class that is a modified version of a previously defined class. parent class: The class from which a child class inherits. child class: A new class created by inheriting from an existing class; also called a “subclass”. IS-A relationship: A relationship between a child class and its parent class. HAS-A relationship: A relationship between two classes where instances of one class contain references to instances of the other. dependency: A relationship between two classes where instances of one class use instances of the other class, but do not store them as attributes.

</details>

<details><summary><code>B:thinkpython2:p203:000</code> (trang 203)</summary>

class diagram: A diagram that shows the classes in a program and the relationships between them. multiplicity: A notation in a class diagram that shows, for a HAS-A relationship, how many references there are to instances of another class. data encapsulation: A program development plan that involves a prototype using global variables and a final version that makes the global variables into instance attributes.

</details>

<details><summary><code>B:thinkpython2:p194:001</code> (trang 194)</summary>

18.2 Class attributes In order to print Card objects in a way that people can easily read, we need a mapping from the integer codes to the corresponding ranks and suits. A natural way to do that is with lists of strings. We assign these lists to class attributes: # inside class Card: suit_names = ['Clubs', 'Diamonds', 'Hearts', 'Spades'] rank_names = [None, 'Ace', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King'] def __str__(self): return '%s of %s' % (Card.rank_names[self.rank], Card.suit_names[self.suit]) Variables like suit_names and rank_names, which are defined inside a class but outside of any method, are called class attributes because they are associated with the class object Card. This term distinguishes them from variables like suit and rank, which are called instance attributes because they are associated with a particular instance. Both kinds of attribute are accessed using dot notation. For example, in __str__, self is a Card object, and self.rank is its rank. Similarly, Card is a class object, and Card.rank_names is a list of strings associated with the class.

</details>

<details><summary><code>B:thinkpython2:p195:000</code> (trang 195)</summary>

list suit_names list rank_names Card type 1 11 suit rank card1 Card Figure 18.1: Object diagram. Every card has its own suit and rank, but there is only one copy of suit_names and rank_names. Putting it all together, the expression Card.rank_names[self.rank] means “use the attribute rank from the object self as an index into the list rank_names from the class Card, and select the appropriate string.” The first element of rank_names is None because there is no card with rank zero. By including None as a place-keeper, we get a mapping with the nice property that the index 2 maps to the string '2', and so on. To avoid this tweak, we could have used a dictionary instead of a list. With the methods we have so far, we can create and print cards: >>> card1 = Card(2, 11) >>> print(card1) Jack of Hearts Figure 18.1 is a diagram of the Card class object and one Card instance. Card is a class object; its type is type. card1 is an instance of Card, so its type is Card. To save space, I didn’t draw the contents of suit_names and rank_names.

</details>

<details><summary><code>B:thinkpython2:p193:000</code> (trang 193)</summary>

Chapter 18 Inheritance The language feature most often associated with object-oriented programming is inheritance. Inheritance is the ability to define a new class that is a modified version of an existing class. In this chapter I demonstrate inheritance using classes that represent playing cards, decks of cards, and poker hands. If you don’t play poker, you can read about it at http://en.wikipedia.org/wiki/Poker, but you don’t have to; I’ll tell you what you need to know for the exercises. Code examples from this chapter are available from https://thinkpython.com/code/ Card.py.

</details>

---

## t05 — In the Analysis of Algorithms appendix, what limitation does the hashtable implementation have regarding keys?

**Đáp án chuẩn:** It only works with hashable keys; mutable types like lists and dictionaries are unhashable.  
**Evidence gold:** p229: “A limitation of this implementation is that it only works with hashable keys. Mutable types like lists and dictionaries are unhashable.”

**Context cuối:** 9 chunk, 9712 ký tự

<details><summary><code>B:thinkpython2:p223:000</code> (trang 223)</summary>

Appendix B Analysis of Algorithms This appendix is an edited excerpt from Think Complexity, by Allen B. Downey, also published by O’Reilly Media (2012). When you are done with this book, you might want to move on to that one. Analysis of algorithms is a branch of computer science that studies the performance of algorithms, especially their run time and space requirements. See http://en.wikipedia. org/wiki/Analysis_of_algorithms. The practical goal of algorithm analysis is to predict the performance of different algorithms in order to guide design decisions. During the 2008 United States Presidential Campaign, candidate Barack Obama was asked to perform an impromptu analysis when he visited Google. Chief executive Eric Schmidt jokingly asked him for “the most efficient way to sort a million 32-bit integers.” Obama had apparently been tipped off, because he quickly replied, “I think the bubble sort would be the wrong way to go.” See http://www.youtube.com/watch?v=k4RRi_ntQc8. This is true: bubble sort is conceptually simple but slow for large datasets. The answer Schmidt was probably looking for is “radix sort” (http://en.wikipedia.org/wiki/ Radix_sort)1.

</details>

<details><summary><code>B:thinkpython2:p223:001</code> (trang 223)</summary>

The goal of algorithm analysis is to make meaningful comparisons between algorithms, but there are some problems: • The relative performance of the algorithms might depend on characteristics of the hardware, so one algorithm might be faster on Machine A, another on Machine B. The general solution to this problem is to specify a machine model and analyze the number of steps, or operations, an algorithm requires under a given model. • Relative performance might depend on the details of the dataset. For example, some sorting algorithms run faster if the data are already partially sorted; other algorithms 1But if you get a question like this in an interview, I think a better answer is, “The fastest way to sort a million integers is to use whatever sort function is provided by the language I’m using. Its performance is good enough for the vast majority of applications, but if it turned out that my application was too slow, I would use a profiler to see where the time was being spent. If it looked like a faster sort algorithm would have a significant effect on performance, then I would look around for a good implementation of radix sort.”

</details>

<details><summary><code>B:thinkpython2:p230:002</code> (trang 230)</summary>

The next add costs 9 units, but then we can add 7 more before the next resize, so the total is 30 units for the first 16 adds. After 32 adds, the total cost is 62 units, and I hope you are starting to see a pattern. After n adds, where n is a power of two, the total cost is 2n − 2 units, so the average work per add is a little less than 2 units. When n is a power of two, that’s the best case; for other values of n the average work is a little higher, but that’s not important. The important thing is that it is O(1). Figure B.1 shows how this works graphically. Each block represents a unit of work. The columns show the total work for each add in order from left to right: the first two adds cost 1 unit each, the third costs 3 units, etc.

</details>

<details><summary><code>B:thinkpython2:p231:000</code> (trang 231)</summary>

Figure B.1: The cost of a hashtable add. The extra work of rehashing appears as a sequence of increasingly tall towers with increasing space between them. Now if you knock over the towers, spreading the cost of resizing over all adds, you can see graphically that the total cost after n adds is 2n − 2. An important feature of this algorithm is that when we resize the HashTable it grows geometrically; that is, we multiply the size by a constant. If you increase the size arithmetically—adding a fixed number each time—the average time per add is linear. You can download my implementation of HashMap from https://thinkpython.com/ code/Map.py, but remember that there is no reason to use it; if you want a map, just use a Python dictionary.

</details>

<details><summary><code>B:thinkpython2:p228:000</code> (trang 228)</summary>

B.4 Hashtables To explain how hashtables work and why their performance is so good, I start with a simple implementation of a map and gradually improve it until it’s a hashtable. I use Python to demonstrate these implementations, but in real life you wouldn’t write code like this in Python; you would just use a dictionary! So for the rest of this chapter, you have to imagine that dictionaries don’t exist and you want to implement a data structure that maps from keys to values. The operations you have to implement are: add(k, v): Add a new item that maps from key k to value v. With a Python dictionary, d, this operation is written d[k] = v. get(k): Look up and return the value that corresponds to key k. With a Python dictionary, d, this operation is written d[k] or d.get(k). For now, I assume that each key only appears once. The simplest implementation of this interface uses a list of tuples, where each tuple is a key-value pair. class LinearMap: def __init__(self): self.items = [] def add(self, k, v): self.items.append((k, v)) def get(self, k): for key, val in self.items: if key == k:

</details>

<details><summary><code>B:thinkpython2:p228:001</code> (trang 228)</summary>

return val raise KeyError add appends a key-value tuple to the list of items, which takes constant time. get uses a for loop to search the list: if it finds the target key it returns the corresponding value; otherwise it raises a KeyError. So get is linear. An alternative is to keep the list sorted by key. Then get could use a bisection search, which is O(log n). But inserting a new item in the middle of a list is linear, so this might not be the best option. There are other data structures that can implement add and get in log time, but that’s still not as good as constant time, so let’s move on. One way to improve LinearMap is to break the list of key-value pairs into smaller lists. Here’s an implementation called BetterMap, which is a list of 100 LinearMaps. As we’ll see in a second, the order of growth for get is still linear, but BetterMap is a step on the path toward hashtables: class BetterMap: def __init__(self, n=100): self.maps = [] for i in range(n): self.maps.append(LinearMap())

</details>

<details><summary><code>B:thinkpython2:p230:000</code> (trang 230)</summary>

self.resize() self.maps.add(k, v) self.num += 1 def resize(self): new_maps = BetterMap(self.num * 2) for m in self.maps.maps: for k, v in m.items: new_maps.add(k, v) self.maps = new_maps __init__ creates a BetterMap and initializes num, which keeps track of the number of items. get just dispatches to BetterMap. The real work happens in add, which checks the number of items and the size of the BetterMap: if they are equal, the average number of items per LinearMap is 1, so it calls resize. resize makes a new BetterMap, twice as big as the previous one, and then “rehashes” the items from the old map to the new.

</details>

<details><summary><code>B:thinkpython2:p230:001</code> (trang 230)</summary>

Rehashing is necessary because changing the number of LinearMaps changes the denominator of the modulus operator in find_map. That means that some objects that used to hash into the same LinearMap will get split up (which is what we wanted, right?). Rehashing is linear, so resize is linear, which might seem bad, since I promised that add would be constant time. But remember that we don’t have to resize every time, so add is usually constant time and only occasionally linear. The total amount of work to run add n times is proportional to n, so the average time of each add is constant time! To see how this works, think about starting with an empty HashTable and adding a sequence of items. We start with 2 LinearMaps, so the first 2 adds are fast (no resizing required). Let’s say that they take one unit of work each. The next add requires a resize, so we have to rehash the first two items (let’s call that 2 more units of work) and then add the third item (one more unit). Adding the next item costs 1 unit, so the total so far is 6 units of work for 4 items. The next add costs 5 units, but the next three are only one unit each, so the total is 14 units for the first 8 adds.

</details>

<details><summary><code>B:thinkpython2:p229:000</code> (trang 229)</summary>

def find_map(self, k): index = hash(k) % len(self.maps) return self.maps[index] def add(self, k, v): m = self.find_map(k) m.add(k, v) def get(self, k): m = self.find_map(k) return m.get(k) __init__ makes a list of n LinearMaps. find_map is used by add and get to figure out which map to put the new item in, or which map to search. find_map uses the built-in function hash, which takes almost any Python object and returns an integer. A limitation of this implementation is that it only works with hashable keys. Mutable types like lists and dictionaries are unhashable. Hashable objects that are considered equivalent return the same hash value, but the converse is not necessarily true: two objects with different values can return the same hash value. find_map uses the modulus operator to wrap the hash values into the range from 0 to len(self.maps), so the result is a legal index into the list. Of course, this means that many different hash values will wrap onto the same index. But if the hash function spreads things out pretty evenly (which is what hash functions are designed to do), then we expect n/100 items per LinearMap.

</details>

---

## t06 — How does a generator expression differ from a list comprehension in when it produces its values?

**Đáp án chuẩn:** It does not compute all values at once; it waits to be asked (lazy evaluation via next or a for loop).  
**Evidence gold:** p207: “unlike a list comprehension, it does not compute the values all at once; it waits to be asked.”

**Context cuối:** 5 chunk, 4605 ký tự

<details><summary><code>B:thinkpython2:p207:001</code> (trang 207)</summary>

19.3 Generator expressions Generator expressions are similar to list comprehensions, but with parentheses instead of square brackets: >>> g = (x**2 for x in range(5)) >>> g <generator object <genexpr> at 0x7f4c45a786c0> The result is a generator object that knows how to iterate through a sequence of values. But unlike a list comprehension, it does not compute the values all at once; it waits to be asked. The built-in function next gets the next value from the generator: >>> next(g) 0 >>> next(g) 1 When you get to the end of the sequence, next raises a StopIteration exception. You can also use a for loop to iterate through the values: >>> for val in g: ... print(val) 4 9 16 The generator object keeps track of where it is in the sequence, so the for loop picks up where next left off. Once the generator is exhausted, it continues to raise StopIteration: >>> next(g) StopIteration Generator expressions are often used with functions like sum, max, and min: >>> sum(x**2 for x in range(5)) 30 19.4 any and all Python provides a built-in function, any, that takes a sequence of boolean values and returns True if any of the values are True. It works on lists:

</details>

<details><summary><code>B:thinkpython2:p208:000</code> (trang 208)</summary>

>>> any([False, False, True]) True But it is often used with generator expressions: >>> any(letter == 't' for letter in 'monty') True That example isn’t very useful because it does the same thing as the in operator. But we could use any to rewrite some of the search functions we wrote in Section 9.3. For example, we could write avoids like this: def avoids(word, forbidden): return not any(letter in forbidden for letter in word) The function almost reads like English, “word avoids forbidden if there are not any forbidden letters in word.” Using any with a generator expression is efficient because it stops immediately if it finds a True value, so it doesn’t have to evaluate the whole sequence. Python provides another built-in function, all, that returns True if every element of the sequence is True. As an exercise, use all to re-write uses_all from Section 9.3.

</details>

<details><summary><code>B:thinkpython2:p213:001</code> (trang 213)</summary>

19.10 Glossary conditional expression: An expression that has one of two values, depending on a condition. list comprehension: An expression with a for loop in square brackets that yields a new list. generator expression: An expression with a for loop in parentheses that yields a generator object. multiset: A mathematical entity that represents a mapping between the elements of a set and the number of times they appear. factory: A function, usually passed as a parameter, used to create objects.

</details>

<details><summary><code>B:thinkpython2:p206:001</code> (trang 206)</summary>

19.2 List comprehensions In Section 10.7 we saw the map and filter patterns. For example, this function takes a list of strings, maps the string method capitalize to the elements, and returns a new list of strings: def capitalize_all(t): res = [] for s in t: res.append(s.capitalize()) return res We can write this more concisely using a list comprehension: def capitalize_all(t): return [s.capitalize() for s in t] The bracket operators indicate that we are constructing a new list. The expression inside the brackets specifies the elements of the list, and the for clause indicates what sequence we are traversing. The syntax of a list comprehension is a little awkward because the loop variable, s in this example, appears in the expression before we get to the definition. List comprehensions can also be used for filtering. For example, this function selects only the elements of t that are upper case, and returns a new list: def only_upper(t): res = [] for s in t: if s.isupper(): res.append(s) return res

</details>

<details><summary><code>B:thinkpython2:p207:000</code> (trang 207)</summary>

We can rewrite it using a list comprehension def only_upper(t): return [s for s in t if s.isupper()] List comprehensions are concise and easy to read, at least for simple expressions. And they are usually faster than the equivalent for loops, sometimes much faster. So if you are mad at me for not mentioning them earlier, I understand. But, in my defense, list comprehensions are harder to debug because you can’t put a print statement inside the loop. I suggest that you use them only if the computation is simple enough that you are likely to get it right the first time. And for beginners that means never.

</details>

---
