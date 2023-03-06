> # design

- each QA pair should have id to find it in database and for updating and edits to save previous data
- parser will parse `.md`
- it can include some additional formatting converted to `.htm` tags by my script


> input file rules

- `id` should be last tag, file will be separated by them
- headers starting with `#` will be skipped


> test cases for `.md` parser

1. number of qa pairs
2. folder structure, number of `.md` files
3. number of `.htm` files
4. presence of all ids in db
5. some id was in db
6. id inserted
7. id removed
8. number of ids in db


> parser design

- class with state
  - there will be 1 test case for 1 created `QAParser` instance because test cases should be self-contained
  - this means we need class with state stored, not class with static functions
  - above list can be formatted as functions called from test case
- **functions without state**
  - though what I want actually is a function
  - so it's logical that more than one test cases look cumbersome
  - to test it I break it to subfunctions
