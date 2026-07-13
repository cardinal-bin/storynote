from dataclasses import dataclass
from collections.abc import Sequence, Collection, MutableSequence
from typing import Self, ClassVar
from contextvars import ContextVar, Token

from weakref import WeakValueDictionary
from enum import Enum

class Unknown[T]:
    '''
    Special object representing an unknown value of a type.
    '''
    __expected_type: type[T]
    __cache = WeakValueDictionary()

    def __new__(cls, expected_type: type[T]) -> Self:
        new_unknown = cls.__cache.get(
            expected_type,
            None
        )
        if new_unknown is None:
            new_unknown = object.__new__(cls)
            new_unknown.__expected_type = expected_type
            cls.__cache[expected_type] = new_unknown
        return new_unknown
    
    @property
    def expected_type(self) -> type[T]:
        return self.__expected_type

@dataclass
class Variant[T]: 
    '''
    A class representing a number of options for an item
    '''
    options: Sequence[T]
    
    @property
    def distinct_options(self) -> set[T]: # maybe this should return a list, too, so ordering is preserved?
        return set(self.options)
    
    def reduce(self) -> Variant[T]: ... # TODO - reduction logic, this will have to be written after other types are created
    # TODO - for .reduce to work, T will almost certainly need to be restricted to certain types of object, or maybe objects that implement some method (via protocol)

type _TypeOrVariant[T]  = T | Variant[T] 
type _TypeOrUnknown[T]  = T | Unknown[T]
type FuzzyItem[T] = _TypeOrVariant[_TypeOrUnknown[T]]
'''
General purpose type for objects that may be:
    - And individual, known object of some type T
    - An Unknown object with expected type T
    - A Variant contianing one or more possible instances of either known or unknown objects of type T
'''
type Numeric = int | float # it would be nice to implicitly support more types than this, the code almost certainly will, but the numbers module abcs don't work how I want them to.

_current_context: ContextVar[Narrative | None] = ContextVar(name = 'narrative_context', default=None)
@dataclass
class Narrative:
    '''
    Special object that holds all story elements defined 
    '''
    contents: MutableSequence = []

    def __enter__(self) -> Self:
        self.__token = _current_context.set(self)
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        _current_context.reset(self.__token)
        
    def add(self, item) -> None:
        self.contents.append(item)

class NarrativeObject:    
    def __post_init__(self) -> None:
        if (context := _current_context.get()) is not None:
            context.add(self)

@dataclass
class Agent(NarrativeObject):
    '''
    Narrative class for things that (can) do things. 
    '''
    name: FuzzyItem[str]

@dataclass
class Thing(NarrativeObject):
    '''
    Narrative class for things that are just things, i.e. objects in the general non-programming sense.
    Could represent a single object or many identical objects.
    '''
    name: FuzzyItem[str]
    number: FuzzyItem[Numeric] = 1

@dataclass
class Place(NarrativeObject):
    name: FuzzyItem[str]

@dataclass
class State(NarrativeObject):
    contents: Collection # mi

@dataclass
class Change(NarrativeObject):
    before: State
    after: State

@dataclass
class Event:
    change: Change
    agent: FuzzyItem[Agent]
    

@dataclass
class Action(NarrativeObject):
    pass

class RelationshipType(Enum):
    IS = 0
    HAS = 1
    WANTS = 2

@dataclass
class Relationship(NarrativeObject):
    subjects: list[FuzzyItem]
    objects: list[FuzzyItem]
    predicate: FuzzyItem[RelationshipType]

