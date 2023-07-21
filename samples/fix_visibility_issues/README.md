
||| Also eeds to tests some other part of the script ? Maybe not
||| Write the expected output for each jobs (precise the groups)

# Original data

* Item 68345 : public with no group
  * Media 68407 : public with no group
  * Media 68406 : public with groups
  * Media 68405 : private with no group
  * Media 68404 : private with groups
* Item 68343 : public with groups
  * Media 68411 : public with no group
  * Media 68410 : public with groups
  * Media 68409 : private with no group
  * Media 68408 : private with groups
* Item 68342 : private with no group
  * Media 68415 : public with no group
  * Media 68414 : public with groups
  * Media 68413 : private with no group
  * Media 68412 : private with groups
* Item 68341 : private with groups
  * Media 68419 : public with no group
  * Media 68418 : public with groups
  * Media 68417 : private with no group
  * Media 68416 : private with groups

# Transformed data

## By job 9 : Add groups to medias by item id

Using groups : `3359, 3060  , 3313`

* Item 68345 : public with no group
  * Media 68407 : private with provided groups
  * Media 68406 : private with provided groups and original groups
  * Media 68405 : private with provided groups
  * Media 68404 : private with provided groups and original groups
* Item 68343 : public with groups
  * Media 68411 : private with provided groups
  * Media 68410 : private with provided groups and original groups
  * Media 68409 : private with provided groups
  * Media 68408 : private with provided groups and original groups
* Item 68342 : private with no group
  * Media 68415 : private with provided groups
  * Media 68414 : private with provided groups and original groups
  * Media 68413 : private with provided groups
  * Media 68412 : private with provided groups and original groups
* Item 68341 : private with groups
  * Media 68419 : private with provided groups
  * Media 68418 : private with provided groups and original groups
  * Media 68417 : private with provided groups
  * Media 68416 : private with provided groups and original groups