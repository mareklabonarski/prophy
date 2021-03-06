from collections import namedtuple

import prophy
from prophy.utils import jsonize

import pytest


@pytest.mark.parametrize('ordered, result_no_values, result_values', [
    (True, [
        ('that_enum', 0),
        ('that_union', [('re', 0), ('im', 0)]),
        ('optional_element', None),
        ('fixed_array', [[('re', 0), ('im', 0)], [('re', 0), ('im', 0)], [('re', 0), ('im', 0)]]),
        ('ext_size', None),
        ('dynamic', [])],
     [
        ('that_enum', 2),
        ('that_union', 12345),
        ('optional_element', 666),
        ('fixed_array', [
            [('re', 0), ('im', 0)], [('re', 2), ('im', 22)], [('re', 3), ('im', -33)],
        ]),
        ('ext_size', None),
        ('dynamic', [
            [('re', 45), ('im', 55)]
        ]),
    ]),
    (False,  {
        'dynamic': [],
        'ext_size': None,
        'fixed_array': [
            {'im': 0, 're': 0},
            {'im': 0, 're': 0},
            {'im': 0, 're': 0}
        ],
        'optional_element': None,
        'that_enum': 0,
        'that_union': {'im': 0, 're': 0}
    }, {
        'dynamic': [{'im': 55, 're': 45}],
        'ext_size': None,
        'fixed_array': [
            {'im': 0, 're': 0},
            {'im': 22, 're': 2},
            {'im': -33, 're': 3}
        ],
        'optional_element': 666,
        'that_enum': 2,
        'that_union': 12345
    })
])
def test_jsonize(ordered, result_no_values, result_values):

    class cint16_t(prophy.with_metaclass(prophy.struct_generator, prophy.struct)):
        _descriptor = [
            ('re', prophy.i16),
            ('im', prophy.i16),
        ]

    class TheUnion(prophy.with_metaclass(prophy.union_generator, prophy.union)):
        _descriptor = [
            ('field_with_a_long_name', cint16_t, 1),
            ('other', prophy.i64, 4090),
        ]

    class E1(prophy.with_metaclass(prophy.enum_generator, prophy.enum)):
        _enumerators = [
            ('E1_A', 0),
            ('E1_B_has_a_long_name', 1),
            ('E1_C_desc', 2),
        ]

    class StructMemberKinds(prophy.with_metaclass(prophy.struct_generator, prophy.struct)):
        _descriptor = [
            ('that_enum', E1),
            ('that_union', TheUnion),
            ('optional_element', prophy.optional(prophy.u32)),
            ('fixed_array', prophy.array(cint16_t, size=3)),
            ('ext_size', prophy.i16),
            ('dynamic', prophy.array(cint16_t, bound='ext_size')),
        ]

    s = StructMemberKinds()

    result = jsonize(s, ordered)
    assert result == result_no_values

    s.that_enum = 2
    s.that_union.discriminator = "other"
    s.that_union.other = 12345
    s.optional_element = True
    s.optional_element = 666
    s.fixed_array[1].re = 2
    s.fixed_array[1].im = 22
    s.fixed_array[2].re = 3
    s.fixed_array[2].im = -33
    s.dynamic.add()
    s.dynamic[0].re = 45
    s.dynamic[0].im = 55

    result = jsonize(s, ordered)
    assert result == result_values


def test_jsonize_simple_types():
    MyTuple = namedtuple('MyTuple', ['x', 'y'])
    data = [3.14159, ({1, 2, 3}, {4: "five"}, MyTuple(1, 2))]
    assert jsonize(data) == [3.14159, [set([1, 2, 3]), {4: 'five'}, {'y': 2, 'x': 1}]]


