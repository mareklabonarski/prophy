#ifndef _PROPHY_RAW_PROPHY_HPP
#define _PROPHY_RAW_PROPHY_HPP

#include <stddef.h>
#include <stdint.h>

namespace prophy
{
namespace raw
{

typedef uint32_t bool_t;

template <typename Tp>
struct alignment
{
    struct finder
    {
        char align;
        Tp t;
    };
    enum { value = sizeof(finder) - sizeof(Tp) };
};

template <typename Tp>
inline Tp* align(Tp* ptr)
{
    enum { mask = alignment<Tp>::value - 1 };
    return reinterpret_cast<Tp*>((reinterpret_cast<uintptr_t>(ptr) + mask) & ~uintptr_t(mask));
}

template <typename To, typename From>
inline To cast(From from)
{
    return align(static_cast<To>(static_cast<void*>(from)));
}

inline void swap(uint8_t*)
{ }

inline void swap(uint16_t* in)
{
    *in = (*in << 8) | (*in >> 8);
}

inline void swap(uint32_t* in)
{
    *in = ((*in << 8) & 0xFF00FF00) | ((*in >> 8) & 0x00FF00FF);
    *in = (*in << 16) | (*in >> 16);
}

inline void swap(uint64_t* in)
{
    *in = ((*in << 8) & 0xFF00FF00FF00FF00ULL ) | ((*in >> 8) & 0x00FF00FF00FF00FFULL );
    *in = ((*in << 16) & 0xFFFF0000FFFF0000ULL ) | ((*in >> 16) & 0x0000FFFF0000FFFFULL );
    *in = (*in << 32) | (*in >> 32);
}

inline void swap(int8_t*)
{ }

inline void swap(int16_t* in)
{
    swap(reinterpret_cast<uint16_t*>(in));
}

inline void swap(int32_t* in)
{
    swap(reinterpret_cast<uint32_t*>(in));
}

inline void swap(int64_t* in)
{
    swap(reinterpret_cast<uint64_t*>(in));
}

inline void swap(float* in)
{
    swap(reinterpret_cast<uint32_t*>(in));
}

inline void swap(double* in)
{
    swap(reinterpret_cast<uint64_t*>(in));
}

template <class T, class U>
class is_convertible
{
    class big_t { char dummy[2]; };
    static char test(U);
    static big_t test(...);
    static T make();
public:
    enum { value = sizeof(test(make())) == sizeof(char) };
};

template <bool, class T = void>
struct enable_if
{};

template <class T>
struct enable_if<true, T>
{
    typedef T type;
};

template <class T>
inline typename enable_if<is_convertible<T, uint32_t>::value, void>::type swap(T* in)
{
    swap(reinterpret_cast<uint32_t*>(in));
}

template <typename Tp>
typename enable_if<!is_convertible<Tp, uint32_t>::value, Tp*>::type swap(Tp*);

template <typename Tp>
inline Tp* swap_n_fixed(Tp* first, size_t n)
{
    while (n--)
    {
        swap(first);
        ++first;
    }
    return first;
}

template <typename Tp>
inline Tp* swap_n_dynamic(Tp* first, size_t n)
{
    while (n--)
    {
        first = swap(first);
    }
    return first;
}

} // namespace raw
} // namespace prophy

#endif  /* _PROPHY_RAW_PROPHY_HPP */