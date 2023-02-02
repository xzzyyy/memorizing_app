# common programming topics


## optimization

---

> meaning of _O(func)_

- asymptotic behavior of the function when argument goes to infinity
- describes how execution time or used memory grow with input data growing
    - important only how fast function grows, not specific function
    - _n_ and _2n_ operations algorithms have same complexity _O(n)_, so _O(n/2)_ doesn't make sense

_id_: `o_func`

---

> what is amortized complexity (амортизированная сложность, учётная стоимость)?

- this is time complexity if we average on a lot of cycles
- being amortized allows some cases to have long execution, but if these are rare, average complexity will be as specified

_interviews_: 210326 elvis, 210430 align  
_ref_: [Амортизационный анализ](https://neerc.ifmo.ru/wiki/index.php?title=%D0%90%D0%BC%D0%BE%D1%80%D1%82%D0%B8%D0%B7%D0%B0%D1%86%D0%B8%D0%BE%D0%BD%D0%BD%D1%8B%D0%B9_%D0%B0%D0%BD%D0%B0%D0%BB%D0%B8%D0%B7)

_id_: `amortized_compl`

---

> optimization task

- calculation of cycle-independent pure functions should happen outside the cycle (_2gis_)
- we can apply one of `algorithm` functions with parallel/unsequenced execution policy (_2gis_)
- reserve `vector` size, instead of calling `push_back` if possible (_2gis_)

_interviews_: `210201 2gis`  
_ex_: `interview_tasks/2gis/3.optimization.hpp`  
_id_: `opt`

---

> is it always possible to move function evaluation outside of the cycle, even if it doesn't depend on cycle index?

- only if function is pure: same input values give same output
  - this may be not true if non-local variables affect result (`static` or global)

_interviews: 210201 2gis_  
_ref: [What do you call a function where the same input will always return the same output, but also has side effects?](https://softwareengineering.stackexchange.com/questions/317245/what-do-you-call-a-function-where-the-same-input-will-always-return-the-same-out)_  
_id_: `opt_func_outside_cycle`

---

> integer addition faster than multiplication?

- depends on a lot of factors
- usually yes, but improvement is not worth to consider

_interviews: 210201 2gis_  
_ref: [Is integer multiplication really done at the same speed as addition on a modern CPU?](https://stackoverflow.com/questions/21819682/is-integer-multiplication-really-done-at-the-same-speed-as-addition-on-a-modern)_  
_id_: `opt_add_vs_mult`

---


# design patterns


> design patterns?

- these are good solutions for common programming problems

- singleton
  - one instance class
  - for example we can store configuration values in singleton class
- abstract factory
  - can create different class instances with common interface function
  - in C++ it is possible to add concrete classes with shared libraries without changing abstract factory code
- Pimpl idiom (pointer to implementation idiom) aka opaque pointer
  - allows additional separation of interface from implementation
    - Luxoft -> Citi -> `dosa` -> `dosa_publisher` -> `ProtoPublisher`
    - Qt
	
_id_: `design_patterns`

---

> iterator

- this is entity that allows iteration through elements of container
- in C++ may be not only class, but also pointer to element type (works for `vector` for example)

_id_: `iterator`


# algorithms


> what can be used as iterator for STL algorithms?

- instance of class
- raw pointer if elements are contiguous in memory (`array`, `vector`, `deque`)

_ref_: [Can raw pointers be used instead of iterators with STL algorithms for containers with linear storage?](
https://stackoverflow.com/questions/16445957/can-raw-pointers-be-used-instead-of-iterators-with-stl-algorithms-for-containers)  
_id_: `iterator_for_algo`

---

> how do algorithm functions check if what they got can be used as iterator?

- there is no special check
- iterator should be fit to pass through template instantiation
- raw pointers can be used as iterators for contiguous layout containers

_id_: `algo_iter_check`

---


# unit tests


---

> testing frameworks

- Boost.Test
- Google Test
    - Google Mock  
      framework for imitating the rest of the system during unit tests

_ref_: [What is the difference between gtest and gmock?](
https://stackoverflow.com/questions/13696376/what-is-the-difference-between-gtest-and-gmock)  
_id_: `ut_frameworks`
