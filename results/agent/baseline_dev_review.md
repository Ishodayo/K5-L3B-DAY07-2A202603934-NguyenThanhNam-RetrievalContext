# Bảng chấm tay — `baseline` / dev

Đọc từng câu, đối chiếu câu trả lời với đáp án chuẩn và với **text của từng chunk được trích**, rồi điền file CSV cùng tên. Thang điểm: BENCHMARK.md §3. Chunk ID có dạng `B:thinkpython2:pTTT:NNN` (TTT = trang PDF; trang in = trang PDF − 22).

## d03 — có đáp án — status `answered`

**Câu hỏi:** What does the // operator do in Python?

**Đáp án chuẩn:** It is floor division: it divides two numbers and rounds down to an integer.  
**Trang gold:** 61, 69

**Query agent đã tìm:** `// operator floor division`

**Câu trả lời của agent:**

> The `//` operator is the floor division operator, which divides two numbers and rounds down (toward negative infinity) to an integer [B:thinkpython2:p061:001] [B:thinkpython2:p069:000].

<details><summary>Citation 1: <code>B:thinkpython2:p061:001</code> (trang 61)</summary>

5.1 Floor division and modulus The floor division operator, //, divides two numbers and rounds down to an integer. For example, suppose the run time of a movie is 105 minutes. You might want to know how long that is in hours. Conventional division returns a floating-point number: >>> minutes = 105 >>> minutes / 60 1.75 But we don’t normally write hours with decimal points. Floor division returns the integer number of hours, rounding down: >>> minutes = 105 >>> hours = minutes // 60 >>> hours 1 To get the remainder, you could subtract off one hour in minutes: >>> remainder = minutes - hours * 60 >>> remainder 45 An alternative is to use the modulus operator, %, which divides two numbers and returns the remainder. >>> remainder = minutes % 60 >>> remainder 45 The modulus operator is more useful than it seems. For example, you can check whether one number is divisible by another—if x % y is zero, then x is divisible by y.

</details>

<details><summary>Citation 2: <code>B:thinkpython2:p069:000</code> (trang 69)</summary>

5.13 Glossary floor division: An operator, denoted //, that divides two numbers and rounds down (toward negative infinity) to an integer. modulus operator: An operator, denoted with a percent sign (%), that works on integers and returns the remainder when one number is divided by another. boolean expression: An expression whose value is either True or False. relational operator: One of the operators that compares its operands: ==, !=, >, <, >=, and <=. logical operator: One of the operators that combines boolean expressions: and, or, and not. conditional statement: A statement that controls the flow of execution depending on some condition. condition: The boolean expression in a conditional statement that determines which branch runs. compound statement: A statement that consists of a header and a body. The header ends with a colon (:). The body is indented relative to the header. branch: One of the alternative sequences of statements in a conditional statement. chained conditional: A conditional statement with a series of alternative branches. nested conditional: A conditional statement that appears in one of the branches of another conditional statement.

</details>

---

## d13 — có đáp án — status `answered`

**Câu hỏi:** What does the pickle module do?

**Đáp án chuẩn:** It translates almost any type of object into a string suitable for storage in a database, and translates strings back into objects.  
**Trang gold:** 164

**Query agent đã tìm:** `pickle module`

**Câu trả lời của agent:**

> The `pickle` module translates almost any type of object into a string suitable for storage in a database, and then translates strings back into objects [B:thinkpython2:p164:000]. Pickling and then unpickling has the same effect as copying the object, which allows non-strings to be stored in a database [B:thinkpython2:p164:000].

<details><summary>Citation 1: <code>B:thinkpython2:p164:000</code> (trang 164)</summary>

14.7 Pickling A limitation of dbm is that the keys and values have to be strings or bytes. If you try to use any other type, you get an error. The pickle module can help. It translates almost any type of object into a string suitable for storage in a database, and then translates strings back into objects. pickle.dumps takes an object as a parameter and returns a string representation (dumps is short for “dump string”): >>> import pickle >>> t = [1, 2, 3] >>> pickle.dumps(t) b'\x80\x03]q\x00(K\x01K\x02K\x03e.' The format isn’t obvious to human readers; it is meant to be easy for pickle to interpret. pickle.loads (“load string”) reconstitutes the object: >>> t1 = [1, 2, 3] >>> s = pickle.dumps(t1) >>> t2 = pickle.loads(s) >>> t2 [1, 2, 3] Although the new object has the same value as the old, it is not (in general) the same object: >>> t1 == t2 True >>> t1 is t2 False In other words, pickling and then unpickling has the same effect as copying the object. You can use pickle to store non-strings in a database. In fact, this combination is so common that it has been encapsulated in a module called shelve.

</details>

---

## du1 — THIẾU evidence — status `abstain`

**Câu hỏi:** How do you use the with statement to open a file so that Python closes it automatically?

**Vì sao thiếu evidence:** Chapter 14 (Files) opens files with open() and closes them with close(); the book never uses or explains the with statement / context managers.

**Query agent đã tìm:** `with statement open file`; `with statement`; `with open`

**Câu trả lời của agent:**

> INSUFFICIENT_EVIDENCE: information on how to use the with statement to open a file.

---

## d01 — có đáp án — status `answered`

**Câu hỏi:** What three kinds of errors can occur in a Python program?

**Đáp án chuẩn:** Syntax errors, runtime errors and semantic errors.  
**Trang gold:** 35

**Query agent đã tìm:** `three kinds of errors`

**Câu trả lời của agent:**

> The three kinds of errors that can occur in a program are syntax errors, runtime errors, and semantic errors [B:thinkpython2:p035:001].

<details><summary>Citation 1: <code>B:thinkpython2:p035:001</code> (trang 35)</summary>

2.8 Debugging Three kinds of errors can occur in a program: syntax errors, runtime errors, and semantic errors. It is useful to distinguish between them in order to track them down more quickly. Syntax error: “Syntax” refers to the structure of a program and the rules about that structure. For example, parentheses have to come in matching pairs, so (1 + 2) is legal, but 8) is a syntax error. If there is a syntax error anywhere in your program, Python displays an error message and quits, and you will not be able to run the program. During the first few weeks of your programming career, you might spend a lot of time tracking down syntax errors. As you gain experience, you will make fewer errors and find them faster. Runtime error: The second type of error is a runtime error, so called because the error does not appear until after the program has started running. These errors are also called exceptions because they usually indicate that something exceptional (and bad) has happened. Runtime errors are rare in the simple programs you will see in the first few chapters, so it might be a while before you encounter one.

</details>

---

## d02 — có đáp án — status `answered`

**Câu hỏi:** Why are errors that only show up while a program is running also referred to as exceptions?

**Đáp án chuẩn:** Because they usually indicate that something exceptional (and bad) has happened.  
**Trang gold:** 35

**Query agent đã tìm:** `exceptions runtime error running`

**Câu trả lời của agent:**

> Errors that only appear while a program is running are called exceptions because they usually indicate that something exceptional (and bad) has happened [B:thinkpython2:p035:001].

<details><summary>Citation 1: <code>B:thinkpython2:p035:001</code> (trang 35)</summary>

2.8 Debugging Three kinds of errors can occur in a program: syntax errors, runtime errors, and semantic errors. It is useful to distinguish between them in order to track them down more quickly. Syntax error: “Syntax” refers to the structure of a program and the rules about that structure. For example, parentheses have to come in matching pairs, so (1 + 2) is legal, but 8) is a syntax error. If there is a syntax error anywhere in your program, Python displays an error message and quits, and you will not be able to run the program. During the first few weeks of your programming career, you might spend a lot of time tracking down syntax errors. As you gain experience, you will make fewer errors and find them faster. Runtime error: The second type of error is a runtime error, so called because the error does not appear until after the program has started running. These errors are also called exceptions because they usually indicate that something exceptional (and bad) has happened. Runtime errors are rare in the simple programs you will see in the first few chapters, so it might be a while before you encounter one.

</details>

---

## d04 — có đáp án — status `answered`

**Câu hỏi:** How can I check whether one whole number divides evenly into another?

**Đáp án chuẩn:** Use the modulus operator: if x % y is zero, then x is divisible by y.  
**Trang gold:** 61

**Query agent đã tìm:** `divides evenly modulus operator`

**Câu trả lời của agent:**

> You can check whether one number is divisible by another using the modulus operator (`%`), which divides two numbers and returns the remainder [B:thinkpython2:p061:001]. If `x % y` is zero, then `x` is divisible by `y` [B:thinkpython2:p061:001].

<details><summary>Citation 1: <code>B:thinkpython2:p061:001</code> (trang 61)</summary>

5.1 Floor division and modulus The floor division operator, //, divides two numbers and rounds down to an integer. For example, suppose the run time of a movie is 105 minutes. You might want to know how long that is in hours. Conventional division returns a floating-point number: >>> minutes = 105 >>> minutes / 60 1.75 But we don’t normally write hours with decimal points. Floor division returns the integer number of hours, rounding down: >>> minutes = 105 >>> hours = minutes // 60 >>> hours 1 To get the remainder, you could subtract off one hour in minutes: >>> remainder = minutes - hours * 60 >>> remainder 45 An alternative is to use the modulus operator, %, which divides two numbers and returns the remainder. >>> remainder = minutes % 60 >>> remainder 45 The modulus operator is more useful than it seems. For example, you can check whether one number is divisible by another—if x % y is zero, then x is divisible by y.

</details>

---

## d05 — có đáp án — status `answered`

**Câu hỏi:** Does a function with infinite recursion really run forever in Python?

**Đáp án chuẩn:** No. Python reports an error when the maximum recursion depth is reached (about 1000 frames).  
**Trang gold:** 67

**Query agent đã tìm:** `infinite recursion`

**Câu trả lời của agent:**

> No, a program with infinite recursion does not really run forever in Python [B:thinkpython2:p067:000]. Instead, Python reports an error message (`RuntimeError: Maximum recursion depth exceeded`) when the maximum recursion depth is reached [B:thinkpython2:p067:000].

<details><summary>Citation 1: <code>B:thinkpython2:p067:000</code> (trang 67)</summary>

def recurse(): recurse() In most programming environments, a program with infinite recursion does not really run forever. Python reports an error message when the maximum recursion depth is reached: File "<stdin>", line 2, in recurse File "<stdin>", line 2, in recurse File "<stdin>", line 2, in recurse . . . File "<stdin>", line 2, in recurse RuntimeError: Maximum recursion depth exceeded This traceback is a little bigger than the one we saw in the previous chapter. When the error occurs, there are 1000 recurse frames on the stack! If you encounter an infinite recursion by accident, review your function to confirm that there is a base case that does not make a recursive call. And if there is a base case, check whether you are guaranteed to reach it.

</details>

---

## d06 — có đáp án — status `answered`

**Câu hỏi:** What is the idea of trusting that a called function returns the correct result instead of tracing through its execution?

**Đáp án chuẩn:** The "leap of faith": at a function call you assume the function works correctly and returns the right result.  
**Trang gold:** 79

**Query agent đã tìm:** `leap of faith`

**Câu trả lời của agent:**

> This concept is called the "leap of faith" [B:thinkpython2:p079:001]. Instead of following the flow of execution when coming to a function call, you assume that the function works correctly and returns the right result [B:thinkpython2:p079:001].

<details><summary>Citation 1: <code>B:thinkpython2:p079:001</code> (trang 79)</summary>

6.6 Leap of faith Following the flow of execution is one way to read programs, but it can quickly become overwhelming. An alternative is what I call the “leap of faith”. When you come to a function call, instead of following the flow of execution, you assume that the function works correctly and returns the right result. In fact, you are already practicing this leap of faith when you use built-in functions. When you call math.cos or math.exp, you don’t examine the bodies of those functions. You just assume that they work because the people who wrote the built-in functions were good programmers.

</details>

---

## d07 — có đáp án — status `answered`

**Câu hỏi:** Why do you get an error when you try to change one character of a string with greeting[0] = 'J'?

**Đáp án chuẩn:** Strings are immutable, so you cannot change an existing string; you must create a new one.  
**Trang gold:** 96

**Query agent đã tìm:** `greeting[0] = 'J'`

**Câu trả lời của agent:**

> You get an error because strings are immutable, which means you cannot change an existing string [B:thinkpython2:p096:001]. Attempting to assign a character to an index of a string results in a TypeError stating that a 'str' object does not support item assignment [B:thinkpython2:p096:001].

<details><summary>Citation 1: <code>B:thinkpython2:p096:001</code> (trang 96)</summary>

8.5 Strings are immutable It is tempting to use the [] operator on the left side of an assignment, with the intention of changing a character in a string. For example: >>> greeting = 'Hello, world!' >>> greeting[0] = 'J' TypeError: 'str' object does not support item assignment The “object” in this case is the string and the “item” is the character you tried to assign. For now, an object is the same thing as a value, but we will refine that definition later (Section 10.10). The reason for the error is that strings are immutable, which means you can’t change an existing string. The best you can do is create a new string that is a variation on the original: >>> greeting = 'Hello, world!' >>> new_greeting = 'J' + greeting[1:] >>> new_greeting 'Jello, world!' This example concatenates a new first letter onto a slice of greeting. It has no effect on the original string.

</details>

---

## d08 — có đáp án — status `answered`

**Câu hỏi:** If I need a sorted version of a list but must keep the original list unchanged, what should I do?

**Đáp án chuẩn:** Use the built-in sorted, which returns a new sorted list, or make a copy (e.g. t[:]) before calling sort.  
**Trang gold:** 121, 121

**Query agent đã tìm:** `sorted list original unchanged`

**Câu trả lời của agent:**

> You can use the built-in function `sorted`, which returns a new sorted list and leaves the original list alone [B:thinkpython2:p121:001]. Alternatively, you can make a copy of the original list (such as with a slice) and call the `sort` method on the copy [B:thinkpython2:p121:001].

<details><summary>Citation 1: <code>B:thinkpython2:p121:001</code> (trang 121)</summary>

>>> t = [3, 1, 2] >>> t2 = t[:] >>> t2.sort() >>> t [3, 1, 2] >>> t2 [1, 2, 3] In this example you could also use the built-in function sorted, which returns a new, sorted list and leaves the original alone. >>> t2 = sorted(t) >>> t [3, 1, 2] >>> t2 [1, 2, 3]

</details>

---

## d09 — có đáp án — status `answered`

**Câu hỏi:** Can a list be used as a key in a Python dictionary?

**Đáp án chuẩn:** No. Lists can be dictionary values but not keys, because keys must be hashable and lists are mutable.  
**Trang gold:** 130

**Query agent đã tìm:** `dictionary key list hashable`

**Câu trả lời của agent:**

> No, a list cannot be used as a key in a Python dictionary [B:thinkpython2:p130:001]. Dictionary keys must be hashable, but mutable types like lists are not hashable [B:thinkpython2:p130:001] [B:thinkpython2:p134:001].

<details><summary>Citation 1: <code>B:thinkpython2:p130:001</code> (trang 130)</summary>

TypeError: list objects are unhashable I mentioned earlier that a dictionary is implemented using a hashtable and that means that the keys have to be hashable. A hash is a function that takes a value (of any kind) and returns an integer. Dictionaries use these integers, called hash values, to store and look up key-value pairs. This system works fine if the keys are immutable. But if the keys are mutable, like lists, bad things happen. For example, when you create a key-value pair, Python hashes the key and stores it in the corresponding location. If you modify the key and then hash it again, it would go to a different location. In that case you might have two entries for the same key, or you might not be able to find a key. Either way, the dictionary wouldn’t work correctly. That’s why keys have to be hashable, and why mutable types like lists aren’t. The simplest way to get around this limitation is to use tuples, which we will see in the next chapter.

</details>

<details><summary>Citation 2: <code>B:thinkpython2:p134:001</code> (trang 134)</summary>

11.9 Glossary mapping: A relationship in which each element of one set corresponds to an element of another set. dictionary: A mapping from keys to their corresponding values. key-value pair: The representation of the mapping from a key to a value. item: In a dictionary, another name for a key-value pair. key: An object that appears in a dictionary as the first part of a key-value pair. value: An object that appears in a dictionary as the second part of a key-value pair. This is more specific than our previous use of the word “value”. implementation: A way of performing a computation. hashtable: The algorithm used to implement Python dictionaries. hash function: A function used by a hashtable to compute the location for a key. hashable: A type that has a hash function. Immutable types like integers, floats and strings are hashable; mutable types like lists and dictionaries are not. lookup: A dictionary operation that takes a key and finds the corresponding value. reverse lookup: A dictionary operation that takes a value and finds one or more keys that map to it. raise statement: A statement that (deliberately) raises an exception.

</details>

---

## d10 — có đáp án — status `answered`

**Câu hỏi:** When a global variable refers to a dictionary, in which case must a function declare it with the global statement?

**Đáp án chuẩn:** Only when the function reassigns the variable; adding, removing or replacing elements does not need a global declaration.  
**Trang gold:** 133

**Query agent đã tìm:** `global statement dictionary`

**Câu trả lời của agent:**

> If a global variable refers to a dictionary, a function can add, remove, and replace its elements without declaring the variable, but if the function wants to reassign the variable, it must declare it with the `global` statement [B:thinkpython2:p133:000].

<details><summary>Citation 1: <code>B:thinkpython2:p133:000</code> (trang 133)</summary>

UnboundLocalError: local variable 'count' referenced before assignment Python assumes that count is local, and under that assumption you are reading it before writing it. The solution, again, is to declare count global. def example3(): global count count += 1 If a global variable refers to a mutable value, you can modify the value without declaring the variable: known = {0:0, 1:1} def example4(): known[2] = 1 So you can add, remove and replace elements of a global list or dictionary, but if you want to reassign the variable, you have to declare it: def example5(): global known known = dict() Global variables can be useful, but if you have a lot of them, and you modify them frequently, they can make programs hard to debug.

</details>

---

## d11 — có đáp án — status `answered`

**Câu hỏi:** In the Dictionaries chapter's debugging advice, what is a "sanity check"?

**Đáp án chuẩn:** A self-check that detects results that are "insane", e.g. checking that an average is not greater than the largest element or less than the smallest.  
**Trang gold:** 133

**Query agent đã tìm:** `sanity check`

**Câu trả lời của agent:**

> A "sanity check" is code written to check for errors automatically by detecting results that are "insane" [B:thinkpython2:p133:002]. For example, when computing the average of a list of numbers, a sanity check could verify that the result is not greater than the largest element or less than the smallest element in the list [B:thinkpython2:p133:002].

<details><summary>Citation 1: <code>B:thinkpython2:p133:002</code> (trang 133)</summary>

Write self-checks: Sometimes you can write code to check for errors automatically. For example, if you are computing the average of a list of numbers, you could check that the result is not greater than the largest element in the list or less than the smallest. This is called a “sanity check” because it detects results that are “insane”. Another kind of check compares the results of two different computations to see if they are consistent. This is called a “consistency check”.

</details>

---

## d12 — có đáp án — status `answered`

**Câu hỏi:** In the data structure selection case study, what does the debugging tip called rubberducking suggest?

**Đáp án chuẩn:** Explain the problem to someone else (even a rubber duck); you often find the answer before you finish asking.  
**Trang gold:** 155

**Query agent đã tìm:** `rubber ducking`

**Câu trả lời của agent:**

> Rubberducking suggests explaining your problem to someone else or to an inanimate object such as a rubber duck [B:thinkpython2:p155:002][B:thinkpython2:p156:002]. Articulating the problem can help you find the answer and solve it, even if the rubber duck doesn't know Python [B:thinkpython2:p155:002][B:thinkpython2:p156:002].

<details><summary>Citation 1: <code>B:thinkpython2:p155:002</code> (trang 155)</summary>

13.10 Debugging When you are debugging a program, and especially if you are working on a hard bug, there are five things to try: Reading: Examine your code, read it back to yourself, and check that it says what you meant to say. Running: Experiment by making changes and running different versions. Often if you display the right thing at the right place in the program, the problem becomes obvious, but sometimes you have to build scaffolding. Ruminating: Take some time to think! What kind of error is it: syntax, runtime, or semantic? What information can you get from the error messages, or from the output of the program? What kind of error could cause the problem you’re seeing? What did you change last, before the problem appeared? Rubberducking: If you explain the problem to someone else, you sometimes find the answer before you finish asking the question. Often you don’t need the other person; you could just talk to a rubber duck. And that’s the origin of the wellknown strategy called rubber duck debugging. I am not making this up; see https://en.wikipedia.org/wiki/Rubber_duck_debugging.

</details>

<details><summary>Citation 2: <code>B:thinkpython2:p156:002</code> (trang 156)</summary>

13.11 Glossary deterministic: Pertaining to a program that does the same thing each time it runs, given the same inputs. pseudorandom: Pertaining to a sequence of numbers that appears to be random, but is generated by a deterministic program. default value: The value given to an optional parameter if no argument is provided. override: To replace a default value with an argument. benchmarking: The process of choosing between data structures by implementing alternatives and testing them on a sample of the possible inputs. rubber duck debugging: Debugging by explaining your problem to an inanimate object such as a rubber duck. Articulating the problem can help you solve it, even if the rubber duck doesn’t know Python.

</details>

---

## d14 — có đáp án — status `answered`

**Câu hỏi:** After pickling and then unpickling a list, is the result the same object as the original list?

**Đáp án chuẩn:** No. It has the same value but is not (in general) the same object; the effect is like copying.  
**Trang gold:** 164

**Query agent đã tìm:** `pickle unpickle list object`

**Câu trả lời của agent:**

> No, although the unpickled object has the same value as the original list, it is not (in general) the same object [B:thinkpython2:p164:000]. Pickling and then unpickling has the same effect as copying the object [B:thinkpython2:p164:000].

<details><summary>Citation 1: <code>B:thinkpython2:p164:000</code> (trang 164)</summary>

14.7 Pickling A limitation of dbm is that the keys and values have to be strings or bytes. If you try to use any other type, you get an error. The pickle module can help. It translates almost any type of object into a string suitable for storage in a database, and then translates strings back into objects. pickle.dumps takes an object as a parameter and returns a string representation (dumps is short for “dump string”): >>> import pickle >>> t = [1, 2, 3] >>> pickle.dumps(t) b'\x80\x03]q\x00(K\x01K\x02K\x03e.' The format isn’t obvious to human readers; it is meant to be easy for pickle to interpret. pickle.loads (“load string”) reconstitutes the object: >>> t1 = [1, 2, 3] >>> s = pickle.dumps(t1) >>> t2 = pickle.loads(s) >>> t2 [1, 2, 3] Although the new object has the same value as the old, it is not (in general) the same object: >>> t1 == t2 True >>> t1 is t2 False In other words, pickling and then unpickling has the same effect as copying the object. You can use pickle to store non-strings in a database. In fact, this combination is so common that it has been encapsulated in a module called shelve.

</details>

---

## d15 — có đáp án — status `answered`

**Câu hỏi:** Which function duplicates an object together with every object nested inside it?

**Đáp án chuẩn:** copy.deepcopy, which performs a deep copy (the object, the objects it refers to, and so on).  
**Trang gold:** 174, 175

**Query agent đã tìm:** `deepcopy copy nested object`

**Câu trả lời của agent:**

> The `deepcopy` function (or method) in the `copy` module copies not only an object but also the objects it refers to, performing a deep copy [B:thinkpython2:p174:001].

<details><summary>Citation 1: <code>B:thinkpython2:p174:001</code> (trang 174)</summary>

For most applications, this is not what you want. In this example, invoking grow_rectangle on one of the Rectangles would not affect the other, but invoking move_rectangle on either would affect both! This behavior is confusing and error-prone. Fortunately, the copy module provides a method named deepcopy that copies not only the object but also the objects it refers to, and the objects they refer to, and so on. You will not be surprised to learn that this operation is called a deep copy. >>> box3 = copy.deepcopy(box) >>> box3 is box False >>> box3.corner is box.corner False box3 and box are completely separate objects. As an exercise, write a version of move_rectangle that creates and returns a new Rectangle instead of modifying the old one.

</details>

---

## d16 — có đáp án — status `answered`

**Câu hỏi:** According to the debugging appendix, what does it mean when an AttributeError says an object has NoneType?

**Đáp án chuẩn:** The object is None, so the problem is the object (e.g. a missing return value or using the result of sort), not the attribute name.  
**Trang gold:** 219

**Query agent đã tìm:** `AttributeError NoneType`

**Câu trả lời của agent:**

> If an AttributeError indicates that an object has NoneType, it means that the object is None [B:thinkpython2:p219:001]. In this case, the problem is not the attribute name, but the object itself [B:thinkpython2:p219:001].

<details><summary>Citation 1: <code>B:thinkpython2:p219:001</code> (trang 219)</summary>

• You are passing the wrong number of arguments to a function. For methods, look at the method definition and check that the first parameter is self. Then look at the method invocation; make sure you are invoking the method on an object with the right type and providing the other arguments correctly. KeyError: You are trying to access an element of a dictionary using a key that the dictionary does not contain. If the keys are strings, remember that capitalization matters. AttributeError: You are trying to access an attribute or method that does not exist. Check the spelling! You can use the built-in function vars to list the attributes that do exist. If an AttributeError indicates that an object has NoneType, that means that it is None. So the problem is not the attribute name, but the object. The reason the object is none might be that you forgot to return a value from a function; if you get to the end of a function without hitting a return statement, it returns None. Another common cause is using the result from a list method, like sort, that returns None.

</details>

---

## du2 — THIẾU evidence — status `abstain`

**Câu hỏi:** How do you write a decorator that wraps a function, and what does the @ syntax do?

**Vì sao thiếu evidence:** Functions are covered (ch03, ch06) including functions as arguments, but decorators and the @decorator syntax never appear.

**Query agent đã tìm:** `decorator syntax wrap function`; `decorator`; `memoize`

**Câu trả lời của agent:**

> INSUFFICIENT_EVIDENCE: information on how to write a decorator and what the @ syntax does in Python

---
