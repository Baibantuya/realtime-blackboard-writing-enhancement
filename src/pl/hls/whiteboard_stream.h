#pragma once
#ifdef WHITEBOARD_NATIVE
#include <deque>
#include <stdexcept>
namespace wb {
template<typename T> class stream {
    std::deque<T> queue;
public:
    void write(T value){queue.push_back(value);}
    T read(){if(queue.empty())throw std::runtime_error("HLS stream underflow");T value=queue.front();queue.pop_front();return value;}
};
}
#else
#include <hls_stream.h>
namespace wb {using hls::stream;}
#endif
